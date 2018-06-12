import tkinter as tk
from tkinter import messagebox, filedialog

class Window(tk.Frame):
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)               
        self.master = master
        self.init_window()     
        self.last_opened = ''

    def init_window(self):  
        self.master.title("Swiss Tournament App")
        self.pack(fill=tk.BOTH, expand=1)
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        file.add_command(label="New Tournament...")
        file.add_command(label="Save")
        file.add_command(label="Save As...", command=self.saveFile)
        file.add_command(label="Open...", command=self.onOpen)
        file.add_command(label="Open recent", command=self.openRecent)
        file.add_separator()
        file.add_command(label="Exit Program", command=self.client_exit)
        menu.add_cascade(label="File", menu=file)

        edit = tk.Menu(menu, tearoff=0)
        edit.add_command(label="Undo")
        menu.add_cascade(label="Edit", menu=edit)
        
        helpmenu = tk.Menu(menu, tearoff=0)
        helpmenu.add_command(label="Help Index")
        helpmenu.add_command(label="About...", command=self.version_info)
        menu.add_cascade(label="Help", menu=helpmenu)
        
        self.txt = tk.Text(self)
        self.txt.pack(fill=tk.BOTH, expand=1)
        
        # create a Scrollbar and associate it with txt
        scrollb = tk.Scrollbar(self.txt, command=self.txt.yview)
        scrollb.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt['yscrollcommand'] = scrollb.set
        
    def onOpen(self):   
        ftypes = [('Supported text files', '*.py *.txt'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes = ftypes)
        fl = dlg.show()
        self.last_opened = fl
        if fl != '':
            text = self.readFile(fl)
            self.txt.insert(tk.END, text)
            

    def readFile(self, filename):
        with open(filename, "r") as f:
            text = f.read()       
        return text
    
        
    def saveFile(self):
        f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        text = self.txt.get("1.0","end-1c")
        f.write(text)
        f.close()
    
    
    def openRecent(self):
        with open(self.last_opened, "r") as f:
            text = f.read()       
            self.txt.insert(tk.END, text)
        
        
    def client_exit(self):
        self.master.destroy()
        
        
    def version_info(self):
        messagebox.showinfo("About", "Swiss Tournament App\nVersion 0.1")
        
        
        
root = tk.Tk()
root.geometry("800x600")
root.resizable(width=False, height=False)
app = Window(root)
root.mainloop()