import os
import subprocess
import re

def get_vids_to_fix(directory):
  filecount = 0
  with open('to_fix.txt', 'w') as f:
    for subdir, dirs, files in os.walk(directory):
      for file in files:
        if not file.endswith('.py') and not file.endswith('.txt'):
          filecount += 1
          complete_filepath = os.path.join(subdir, file)
          if not (file.endswith('.mov') or file.endswith('.mp4') or file.endswith('.MOV') or file.endswith('.MP4')):
            print(complete_filepath)
            f.write(complete_filepath + '\n')
          else:
            # check framerate
            output = subprocess.run(['ffmpeg', '-i', complete_filepath], capture_output=True, text=True)
            #print(output.stderr)
            m = re.search('([\d.k]+) fps', output.stderr)
            if m:
              fps = round(float(m.group(1).replace('k', '000')))
              if fps != 30 and fps != 60:
                print(complete_filepath, ' FPS:', fps)
                f.write(complete_filepath + '\n')
            else: 
              print('could not find FPS for ', complete_filepath)

  print('FINAL FILECOUNT: ', filecount)

def fix_vids():
  with open('to_fix.txt', 'r') as f_to_fix:
    lines = [item.strip('\n') for item in f_to_fix.readlines()]
  with open('fixed.txt', 'a') as f_fixed:
    print(lines)
    for i in range(len(lines)):
      filepath = lines[0]
      new_path = '.'.join(filepath.split('.')[:-1]) + '_FIXED.mov'
      cmd = ['ffmpeg', '-y', '-i', filepath, '-r', '30', new_path]
      print(cmd)
      subprocess.run(cmd)
      f_fixed.write(lines.pop(0) + '\n')
      
      with open('to_fix.txt', 'w') as f_to_fix:
        f_to_fix.writelines('%s\n' % item for item in lines)

      #exit()

def move_old_vids(directory):
  with open('fixed.txt', 'r') as f_fixed:
    lines = [item.strip('\n') for item in f_fixed.readlines()]
    for filepath in lines:
      filename = filepath.split('\\')[-1]
      os.rename(filepath, os.path.join(directory, filename))


directory = 'D:\\JonathanLiu\\Videos\\Davinci Resolve\\Virtual Choir Spring 2021\\Seasons of Love\\Upload your video here (File responses)'
#get_vids_to_fix(directory)
#fix_vids()
move_old_vids(directory + '/../old')