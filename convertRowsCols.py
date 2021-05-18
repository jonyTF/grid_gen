ROW, COL = range(2)
SQUARE, PORTRAIT, LANDSCAPE = range(3)

def convertRowsCols(rc, width, height, which, orientation):
  if orientation == PORTRAIT:
    # for vertical video
    w_to_h = 16/9
    h_to_w = 9/16
  elif orientation == SQUARE:
    # for square video
    w_to_h = 1
    h_to_w = 1
  elif orientation == LANDSCAPE: 
    # for horizontal video
    w_to_h = 9/16
    h_to_w = 16/9
  else:
    raise BaseException('Orientation not correct!')

  if which == ROW:
    num = width / (height / rc * h_to_w)
  else:
    num = height / (width / rc * w_to_h)
  print(f"{width}x{height}, {rc} {'rows' if which == ROW else 'cols'} ==> {num} {'cols' if which == ROW else 'rows'}")
  return num

convertRowsCols(5, 1920, 1080, ROW, PORTRAIT)
