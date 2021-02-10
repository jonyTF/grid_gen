import os
import uuid
from subprocess import run
import subprocess

class Util():
  def __init__(self, parent):
    self.parent = parent

  def run_cmd(self, cmd, root_dir='./'):
    os.chdir(root_dir)
    return run(cmd, capture_output=True)

  def generate_thumbnail(self, vid_filename):
    """Generates thumbnail for video located at `vid_filename`
    Returns the filepath of the thumbnail 
    """
    thumbnail_path = self.parent.options['thumbnail_path']
    if not os.path.exists(thumbnail_path):
      os.makedirs(thumbnail_path)

    thumbnail_filename = os.path.join(thumbnail_path, uuid.uuid4().hex) + '.jpg'
    cmd = f'ffmpeg -hide_banner -loglevel error -y -i {vid_filename} -vf "crop=x=(iw-ih*9/16)/2:y=0:w=ih*9/16:h=ih, scale=90x160" -frames:v 1 {thumbnail_filename}'
    result = self.run_cmd(cmd)
    if result.returncode != 0:
      return (result.returncode, result.stderr.decode('utf-8'))
    return (result.returncode, thumbnail_filename)

  def getFrameRate(self, filename):
    # Get the frame rate of media file `filename`
    result = subprocess.Popen(['ffmpeg', '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for l in result.stdout.readlines():
        l = l.decode('utf-8')
        if 'Video' in l:
            return float(l[l.rindex(',', 0, l.index('fps'))+1:l.index('fps')].strip())
    raise Exception('Framerate not found for ' + filename)