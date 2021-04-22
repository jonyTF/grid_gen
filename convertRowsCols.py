ROW, COL = range(2)
def convertRowsCols(rc, width, height, which):
  if which == ROW:
    num = width / (height / rc * 9/16)
  else:
    num = height / (width / rc * 16/9)
  print(f"{width}x{height}, {rc} {'rows' if which == ROW else 'cols'} ==> {num} {'cols' if which == ROW else 'rows'}")
  return num

convertRowsCols(2, 1920, 1080, ROW)
