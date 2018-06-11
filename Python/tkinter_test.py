from tkinter import *

class Window(Frame):
    
    def __init__(self, master=None):
        Frame.__init__(self, master)               
        self.master = master
        self.init_window()
        
    #Creation of init_window
    def init_window(self):
   
        self.master.title("GUI")
        self.pack(fill=BOTH, expand=1)
        menu = Menu(self.master)
        self.master.config(menu=menu)

        file = Menu(menu, tearoff=0)
        file.add_command(label="New Tournament...")
        file.add_command(label="Save")
        file.add_command(label="Save As...")
        file.add_command(label="Open...")
        file.add_command(label="Open last closed")
        file.add_separator()
        file.add_command(label="Exit Program", command=self.client_exit)
        menu.add_cascade(label="File", menu=file)

        # create the file object)
        edit = Menu(menu, tearoff=0)
        edit.add_command(label="Undo")
        menu.add_cascade(label="Edit", menu=edit)
        
    def client_exit(self):
        self.master.destroy()
        
root = Tk()
root.geometry("400x300")
app = Window(root)
root.mainloop()