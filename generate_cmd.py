import os
import math
from types import SimpleNamespace
import json
from util import Util
util = Util(None)

#-----------
# Constants
#-----------
SQUARE, PORTRAIT, LANDSCAPE = range(3)

#-----------
# User defined values
#-----------
root_dir = 'C:\\Users\\JonathanLiu\\Documents\\vids\\PAUSD Seasons of Love\\Renders'
directory = './M. 5-12 half of 6th'
config_path = os.path.join(root_dir, directory, 'config.json')
use_config = False

if use_config and os.path.exists(config_path):
  print('##############USING CONFIG FILE##################')
  with open(config_path) as f:
    config = json.load(f)
else:
  config = {
    'ignore_dirs': ['end'],
    'rows': 5,
    'cols': [14,15,15,15,14],
    'cols_data': {
    },


    # 'cols_data': {
    #   0: ['sop2', 'sop2'] + ['sop1' for i in range(3)] + ['sop2', 'sop2'],
    #   1: ['sop2'] + ['sop1' for i in range(4)] + ['sop2'],
    #   2: ['sop2', 'sop1', 'alto1', 'alto2', 'alto1', 'sop1', 'sop2']
    # },

    'orientation': PORTRAIT,
    'padding': 15,
    #'mask_img': '',
    'mask_img': 'D:\\JonathanLiu\\Videos\\Davinci Resolve\\Virtual Choir Spring 2021\\mask.png',
    'start': '',
    'end': '22',
    'output_file': 'M. 5-12 half of 6th.mov',
    'canvas_height': round(1080),
    'fps': 30,
    'crop_filter_str': '',
    'center_vids': True, # whether to center videos if num cols is less than max num cols
    'transparent_mov': False,
    'save_config': True,
  }
  if config['save_config']:
    with open(config_path, 'w') as json_file:
      json.dump(config, json_file)

config = SimpleNamespace(**config)
# Convert string keys to int keys
config.cols_data = {int(col): value for col, value in config.cols_data.items()}
print(config)

assert len(config.cols) == config.rows, 'rows and cols don\'t match!'
for col in config.cols_data:
  col = int(col)
  assert len(config.cols_data[col]) == config.cols[col], f'cols_data[{col}] does not match cols!'

#-----------------
# Set orientation
#-----------------
if config.orientation == PORTRAIT:
  # for vertical video
  w_to_h = 16/9
  h_to_w = 9/16
elif config.orientation == SQUARE:
  # for square video
  w_to_h = 1
  h_to_w = 1
elif config.orientation == LANDSCAPE: 
  # for horizontal video
  w_to_h = 9/16
  h_to_w = 16/9
else:
  raise BaseException('Orientation not correct!')

#----------
# Defaults
#----------
vcodec = '-vcodec qtrle' if config.transparent_mov and config.output_file.endswith('.mov') else '' # for transparent movs
file_exts = ('.mp4', '.mov', '.jpg', '.png', '.JPG')
default_crop_filter_str = f'crop=x=(iw-ih*{h_to_w})/2:y=0:w=ih*{h_to_w}:h=ih'
if not config.crop_filter_str:
  config.crop_filter_str = default_crop_filter_str

#----------
# Functions
#----------
def get_total_width(cols, vid_width):
  return config.padding + cols*(vid_width+config.padding)

#-----------
# Calculated values
#-----------
background_index = 0
vid_height = round( (config.canvas_height-config.padding)/config.rows - config.padding )
vid_width = round( vid_height * h_to_w )
canvas_width = get_total_width(max(config.cols), vid_width)
canvas_width += 1 if canvas_width % 2 == 1 else 0

print(f'vid_width: {vid_width}, vid_height: {vid_height}')

# input part of ffmpeg command
input_str = ''

filter_complex = ''
# Add mask for the individual videos
if config.mask_img:
  background_index += 1
  input_str += f'-loop 1 -i "{config.mask_img}" '
  

# Add background
if config.start: input_str += f'-ss {config.start} '
if config.end: input_str += f'-to {config.end} '
background_str = f'-f lavfi -i color=c=0x000000@0x00:s={canvas_width}x{config.canvas_height}:r=30,format=rgba '
input_str += background_str

# Change to correct root directory
os.chdir(root_dir)

# Get all the video filepaths
vids = {}
for subdir, dirs, files in os.walk(directory):
  cur_dir = subdir.replace(directory, '')
  if len(cur_dir) > 0 and (cur_dir[0] == '/' or cur_dir[0] == '\\'): cur_dir = cur_dir[1:] # [1:] gets rid of the leading / if there is one

  if 'ignore_dirs' in vars(config) and cur_dir in config.ignore_dirs:
    continue

  for file in files:
    filename = os.path.join(subdir, file)
    if filename.endswith(file_exts):
      if cur_dir not in vids:
        vids[cur_dir] = [filename]
      else:
        vids[cur_dir].append(filename)

vid_index = 0
for row in range(config.rows):
  for col in range(config.cols[row]):
    # Get the filename of the correct video
    if row in config.cols_data:
      # Reference cols_data
      target_dir = config.cols_data[row].pop(0)
      if target_dir:
        key = ''
        for subdir in vids:
          if target_dir in subdir:
            key = subdir
            break
        assert key, 'Folder "' + target_dir + '" doesn\'t exist!'
        filename = vids[key].pop(0)
      else:
        filename = None
    else:
      # Just iterate through vids
      key = list(vids.keys())[0]
      if len(vids[key]) == 0:
        del vids[key]
      key = list(vids.keys())[0]
      filename = vids[key].pop(0)

    if filename:
      # Video indices start after the background index, thus add background_index + 1
      vid_num = vid_index + (background_index + 1)

      # Set timestamp range of video
      if config.start: input_str += f'-ss {config.start} '
      if config.end: input_str += f'-to {config.end} '

      # Add to the input
      input_str += f'-i "{filename}" '

      # Calculate filter to crop video, perform masking if needed
      filter_complex += f'[{vid_num}:v]fps=fps={config.fps}, setpts=PTS-STARTPTS, {config.crop_filter_str}, scale={vid_width}x{vid_height}'
      if config.mask_img:
        filter_complex += f'[b4mask{vid_num}];'
        filter_complex += f'[0:v]scale={vid_width}:{vid_height}[mask];'
        filter_complex += f'[b4mask{vid_num}][mask]alphamerge'
      filter_complex += f'[v{vid_num}];'

      # Calculate the x and y position of the video relative to the background
      xStart = round( (canvas_width - get_total_width(config.cols[row], vid_width)) / 2 ) if config.center_vids else 0
      x = xStart + config.padding + col*(vid_width+config.padding)
      y = config.padding + row*(vid_height+config.padding)

      # Overlay videos on top of each other
      filter_complex += f'[{background_index}:v]' if vid_index == 0 else f'[tmp{vid_num-1}]' 
      filter_complex += f'[v{vid_num}]overlay='
      filter_complex += 'repeatlast=0:' if config.end else 'shortest=1:'  
      filter_complex += f'x={x}:y={y}[tmp{vid_num}];' 

      # Increment variables
      vid_index += 1


final_output = f'[tmp{vid_index + background_index}]'

filter_complex = filter_complex[:-1] # Get rid of final semicolon

cmd = f'ffmpeg -y {input_str} -filter_complex "{filter_complex}" -map "{final_output}" {vcodec} "{config.output_file}"'

mask_path = os.path.splitext(config.output_file)[0]
create_mask_cmd = f'ffmpeg -y {input_str} -filter_complex "{filter_complex}" -map "{final_output}" -frames:v 1 "{mask_path}.png"'

result = util.run_cmd(create_mask_cmd, root_dir=root_dir)
print(result.stderr.decode('utf-8'))

print(cmd)
print('\n----------------UNUSED VIDEOS-------------------:\n', json.dumps(vids, indent=4, sort_keys=True))
result = util.run_cmd(cmd, root_dir=root_dir)
print(result.stderr.decode('utf-8'))


'''
ffmpeg -loop 1 -i "D:\JonathanLiu\Videos\Davinci Resolve\Virtual Choir Spring 2021\Singing Valentines\mask.png" -ss 0 -to 5 -i "D:\JonathanLiu\Videos\Davinci Resolve\Virtual Choir Spring 2021\Singing Valentines\PILOTS - SINGING VALENTINES  (File responses)\SUBMIT SONG 1 HERE (File responses)\Ava Keck I_m Yours Song - Ava Keck.MOV" -filter_complex "[0:v]alphaextract[a1];[1:v][a1]alphamerge[final]" -map "[final]" -vcodec qtrle output.mov

ffmpeg -y -f lavfi -loop 1 -i "D:\JonathanLiu\Videos\Davinci Resolve\Virtual Choir Spring 2021\Singing Valentines\mask.png" -to 5 -i color=c=0xffffff@0x00:s=9640x1080:r=30,format=rgba -to 5 -i "./song3\V1-0001_signsealeddelievered_eliza 
- Eliza Blake.mov" -to 5 -i "./song3\V2-0001_Signedsealed_eva - Eva Spaid.mov" -to 5 -i "./song3\V3-0001_Signed, Sealed, Delivered (I_m Yours)_Andy Pal - Andrew Pal.mov" -to 5 -i "./song3\V4-0001_Setareh G Signed Sealed Delivered - Setareh Greenwood.mov" -to 5 -i "./song3\V5-0001_IMG_9240 - Samantha Waldbusser.mov" -to 5 -i "./song3\V6-0001_IMG_7981 - Finn Buggy.mov" -to 5 -i "./song3\V7-0001_IMG_3125 - Ella Nelson.mov" -to 5 -i "./song3\V8-0001_IMG_0267 - Kai Wessel.mov" -to 5 -i "./song3\V9-0001_FullSizeRender - Bayaan Mengerink.mov"  -filter_complex "[0:v]alphaextract[alpha];[2:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask2];[b4mask2][alpha]alphamerge[v2];[1:v][v2]overlay=repeatlast=0:x=10:y=10[tmp2];[3:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask3];[b4mask3][alpha]alphamerge[v3];[tmp2][v3]overlay=repeatlast=0:x=1080:y=10[tmp3];[4:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask4];[b4mask4][alpha]alphamerge[v4];[tmp3][v4]overlay=repeatlast=0:x=2150:y=10[tmp4];[5:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask5];[b4mask5][alpha]alphamerge[v5];[tmp4][v5]overlay=repeatlast=0:x=3220:y=10[tmp5];[6:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask6];[b4mask6][alpha]alphamerge[v6];[tmp5][v6]overlay=repeatlast=0:x=4290:y=10[tmp6];[7:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask7];[b4mask7][alpha]alphamerge[v7];[tmp6][v7]overlay=repeatlast=0:x=5360:y=10[tmp7];[8:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask8];[b4mask8][alpha]alphamerge[v8];[tmp7][v8]overlay=repeatlast=0:x=6430:y=10[tmp8];[9:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask9];[b4mask9][alpha]alphamerge[v9];[tmp8][v9]overlay=repeatlast=0:x=7500:y=10[tmp9];[10:v]fps=fps=30, setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=1060x1060[b4mask10];[b4mask10][alpha]alphamerge[v10];[tmp9][v10]overlay=repeatlast=0:x=8570:y=10[tmp10]" -map "[tmp10]"  -vcodec qtrle "song3.mov"
'''