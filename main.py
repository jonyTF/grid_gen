import tkinter as tk
from util import Util

class InputForm(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.parent = parent
    self.init_ui()

  def init_ui(self):
    self.lbl_vids = tk.Label(self, text='Videos')
    self.ent_vids = tk.Entry(self)

    self.lbl_test = tk.Label(self, text='laksdjflaksjdflkajsdflk')

    grid_items = [
      [self.lbl_vids, self.ent_vids],
      [self.lbl_test]
    ]

    self.columnconfigure(1, minsize=50, weight=1)
    for row, row_items in enumerate(grid_items):
      for col, item in enumerate(row_items):
        item.grid(row=row, column=col, padx=5, pady=5, sticky='e' if col == 0 else 'ew')

class App(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.parent = parent
    self.options = {
      'thumbnail_path': './thumbnails'
    }

    self.util = Util(self)
    self.input_form = InputForm(self)

    self.init_ui()

  def init_ui(self):
    self.input_form.pack(side='top', fill='x')

if __name__ == '__main__':
  root = tk.Tk()
  App(root).pack(fill='both', expand=True)
  root.mainloop()