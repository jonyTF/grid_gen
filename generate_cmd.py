import os
import math

#-----------
# Constants
#-----------

# for vertical video
w_to_h = 16/9
h_to_w = 9/16

#-----------
# User defined values
#-----------
rows = 4
cols = (3,3,4,2)
padding = 10
directory = './vids'
start = '1:30'
end = ''
output_file = 'output_xd.mov'
canvas_height = 1080

assert len(cols) == rows

#----------
# Functions
#----------
def get_total_width(cols, vid_width):
  return padding + cols*(vid_width+padding)

#-----------
# Calculated values
#-----------
vid_index_offset = 1 # The input index to start at (since background is at index 0)
vid_height = round( (canvas_height-padding)/rows - padding )
vid_width = round( vid_height * h_to_w )
canvas_width = get_total_width(max(cols), vid_width)


input_str = ''
if start: input_str += f'-ss {start} '
if end: input_str += f'-to {end} '
input_str += f'-i color=c=black:s={canvas_width}x{canvas_height}:r=30 '


crop_str = ''
overlay_str = ''
vid_index = 0
cur_row = 0
cur_col = 0
for filename in os.listdir(directory):
  if filename.endswith('.mov'):
    vid_num = vid_index + vid_index_offset
    if start: input_str += f'-ss {start} '
    if end: input_str += f'-to {end} '

    input_str += f'-i {os.path.join(directory, filename)} '
    crop_str += f'[{vid_num}:v]setpts=PTS-STARTPTS, crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale={vid_width}x{vid_height}[v{vid_num}];'

    xStart = round( (canvas_width - get_total_width(cols[cur_row], vid_width)) / 2 )
    x = xStart + padding + cur_col*(vid_width+padding)
    y = padding + cur_row*(vid_height+padding)

    overlay_str += '[0:v]' if vid_index == 0 else f'[tmp{vid_num-1}]' 
    overlay_str += f'[v{vid_num}]overlay='
    overlay_str += 'repeatlast=0:' if end else 'shortest=1:'  
    overlay_str += f'x={x}:y={y}[tmp{vid_num}];' 

    vid_index += 1
    cur_col += 1
    if cur_col >= cols[cur_row]:
      cur_col = 0
      cur_row += 1

overlay_str = overlay_str[:-1]
final_output = f'[tmp{vid_index - 1 + vid_index_offset}]'

filter_complex = crop_str + overlay_str

cmd = f'ffmpeg -y -f lavfi {input_str} -filter_complex "{filter_complex}" -map "{final_output}" {output_file}'
print(cmd)
