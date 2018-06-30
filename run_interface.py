import tkinter as tk
#import tkinter.ttk as ttk
#from tkinter import messagebox, filedialog, scrolledtext
#import json
import os

import tkinter_classes as tkcls



root = tk.Tk()
app = tkcls.Window(root)
root.mainloop()
# save preferences after closing
app.saveInit()
if os.path.isfile(app.tempfile.name):
    os.remove(app.tempfile.name)