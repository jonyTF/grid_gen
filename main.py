# CONCLUSION: I can't use Tk, doesn't come with ANY widgets wtf, going to use PyQt again

import tkinter as tk
from tkinter import ttk
from util import Util

class InputForm(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.parent = parent
    self.init_ui()

  def init_ui(self):
    self.lbl_vids = tk.Label(self, text='Videos')
    self.ent_vids = tk.Entry(self)

    self.lbl_padding = tk.Label(self, text='Padding')
    self.spin_padding = tk.Scale(self, from_=0, to=50, orient=tk.HORIZONTAL, showvalue=False)

    grid_items = [
      [self.lbl_vids, self.ent_vids],
      [self.lbl_padding, self.spin_padding]
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