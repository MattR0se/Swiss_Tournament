import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import json
import os

import swiss_tournament as swiss

class Window(tk.Frame):
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)               
        self.master = master
        self.init_window()
        self.event = None

    def init_window(self):
        self.loadWindow()
        self.master.title("Swiss Tournament App")
        self.pack(fill=tk.BOTH, expand=1)
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        file.add_command(label="New Tournament...", command=self.newEvent)
        file.add_command(label="Save", command=self.saveEvent)
        file.add_command(label="Save As...", command=self.saveFile)
        file.add_command(label="Open...", command=self.onOpen)
        file.add_command(label="Open Recent", command=self.openRecent)
        file.add_separator()
        file.add_command(label="Exit Program", command=self.clientExit)
        menu.add_cascade(label="File", menu=file)

        edit = tk.Menu(menu, tearoff=0)
        edit.add_command(label="Add Players", command=self.addPlayer)
        edit.add_command(label="Edit Players", command=self.editPlayer)
        edit.add_command(label="Remove Players")
        edit.add_command(label="Edit Results")
        menu.add_cascade(label="Edit", menu=edit)
        
        tools = tk.Menu(menu, tearoff=0)
        tools.add_command(label="Start Tournament", command=self.startTournament)
        tools.add_command(label="Start next Round", command=self.createPairings)
        tools.add_command(label="Enter Result")
        tools.add_command(label="Show Standings", command=self.showStandings)
        menu.add_cascade(label="Tools", menu=tools)
        
        printing = tk.Menu(menu, tearoff=0)
        printing.add_command(label="Print Seatings...")
        printing.add_command(label="Print Pairings...")
        printing.add_command(label="Print Standings...")
        menu.add_cascade(label="Print", menu=printing)
        
        helpmenu = tk.Menu(menu, tearoff=0)
        helpmenu.add_command(label="Help Index")
        helpmenu.add_command(label="About...", command=self.versionInfo)
        menu.add_cascade(label="Help", menu=helpmenu)
        
        self.txt = scrolledtext.ScrolledText(self)
        # disable text editing by user
        self.txt.bind("<Key>", lambda e: "break")
        self.txt.pack(fill=tk.BOTH, expand=1)

        
    def onOpen(self):
        ftypes = [('Supported text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.Open(self, initialdir=os.getcwd(), filetypes = ftypes)
        fl = dlg.show()
        self.last_opened = fl
        if fl != '': 
            try:
                self.event = swiss.tournament
                self.event = self.event.load_tournament2(self, fl)
                text = fl
                if self.event:
                    text = 'Successfully loaded ' + text
                    self.println(text)
                else:
                    text = 'failed to load ' + text 
                self.println(text)
            except:
                text = fl
                text = 'failed to load ' + text 
                self.println(text)
    
        
    def saveFile(self):
        dlg = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        if dlg is None:
            return
        fl = dlg.name
        self.event.save_tournament_as(fl)
    
    
    def saveEvent(self):
        try:
            self.event.save_tournament()
        except:
            messagebox.showinfo("Warning", "No tournament to save.")
    
    
    def openRecent(self):
        try:
            self.event = swiss.tournament()
            self.event = self.event.load_tournament2(self.last_opened)
            if self.event:
                text = self.last_opened
                text = 'Successfully loaded ' + text
                self.println(text)
            else:
                self.println('Error loading {}'.format(self.last_opened))
        except:
            pass
        
        
    def clientExit(self):
        self.saveWindow()
        self.master.destroy()
        
        
    def versionInfo(self):
        messagebox.showinfo("About", 
                            "Swiss Tournament App\nVersion 0.1\n© Christian Post")
        
        
    def saveWindow(self):
        data = {"last_opened": self.last_opened,
                }
        with open('data.json', 'w') as f:
            json.dump(data, f)


    def loadWindow(self):
        try:
            with open('data.json') as f:
                data = json.load(f)
            self.last_opened = data["last_opened"]
        except:
            self.last_opened = ''
    
    
    def newEvent(self):
        if self.event:
            # ask the user if they want to save the current tournament
            # before overwriting
            return
        self.event = swiss.tournament()
        self.txt.delete('1.0', tk.END)
       
    
    def addPlayer(self):
        if not self.event:
            messagebox.showinfo("Error", "No tournament started!")
            return
        self.popup_addPlayer = popupWindow(self, self.master)
        self.master.wait_window(self.popup_addPlayer.top)
    
    
    def editPlayer(self):
        if not self.event:
            messagebox.showinfo("Error", "No tournament started!")
            return
        if len(self.event.players) == 0:
            messagebox.showinfo("Error", "Add Players first!")
            return
        self.popup_editPlayer = editPlayerWindow(self, self.master)
        self.master.wait_window(self.popup_editPlayer.top)
        
        
    def showPlayers(self):
        if self.event:
            self.event.sort_players('name')
            self.println('\nPlayers in this tournament:')
            for player in self.event.players:
                self.println(player.name + ' ' + player.dci)
        else:
            self.println('No event found.')
            
    
    def showStandings(self):
        if self.event:
            text = self.event.print_standings(True)
            self.println(text)
        else:
            self.println('No event found.')
            
    
    def startTournament(self):
        if self.event:
            text = self.event.print_seatings()
            self.println(text)
            self.event.calculate_rounds()           
        else:
            self.println('No event found.')
            
            
    def createPairings(self):
        if self.event:
            self.event.new_round()
            text = self.event.print_pairings()
            self.println(text)
        else:
            self.println('No event found.')        
            
            
    def println(self, text):
        self.txt.insert(tk.END, text + '\n')


class popupWindow():
    def __init__(self, window, master, mode='add'):
        self.window = window
        self.master = master
        self.top = top = tk.Toplevel(master)
        self.l1 = tk.Label(top,text="First Name")
        self.l1.pack()
        self.e1 = tk.Entry(top)
        self.e1.pack()
        self.l2 = tk.Label(top,text="Last Name")
        self.l2.pack()
        self.e2 = tk.Entry(top)
        self.e2.pack()
        self.l3 = tk.Label(top,text="DCI")
        self.l3.pack()
        self.e3 = tk.Entry(top)
        self.e3.pack()
        if mode == 'add':
            self.b = tk.Button(top,text='Add Player',command=self.cleanupAdd)
        elif mode == 'edit':
            firstname = ''
            self.id = None
            for player in self.window.event.players:
                #print(str(self.window.popup_editPlayer.player), player.name)
                if self.window.popup_editPlayer.name == player.name:
                    lastname, firstname = player.name.split(', ')
                    dci = player.dci
                    self.id = player.id
            self.e1.insert(0, firstname)
            self.e2.insert(0, lastname)
            self.e3.insert(0, dci)
            self.b = tk.Button(top,text='Save changes',command=self.cleanupEdit)
        self.b.pack()
        
        
    def cleanupAdd(self):
        self.name = self.e2.get().strip() + ', ' + self.e1.get().strip()
        self.dci = self.e3.get().strip()
        if not self.window.event.check_dci(self.dci):
            messagebox.showinfo("Error", "DCI already entered!")
            return
        if self.name == ', ':
            messagebox.showinfo("Error", "Please enter a name!")
            return
        else:
            string = 'Added: ' + self.name + '; DCI ' + self.dci
            self.window.event.add_player(self.name, self.dci)
            self.window.println(string)
            self.top.destroy()
    
    def cleanupEdit(self):
        if self.id:
            self.name = self.e2.get().strip() + ', ' + self.e1.get().strip()
            self.dci = self.e3.get().strip()
            for player in self.window.event.players:
                if player.id == self.id:
                    player.name = self.name
                    player.dci = self.dci
        self.top.destroy()
                
        
        
class editPlayerWindow():
    def __init__(self, window, master):
        self.window = window
        self.master = master
        self.top = top = tk.Toplevel(master)
        self.player = tk.StringVar(top)
        choices = [str(player.name) for player in self.window.event.players]
        print(choices)
        default = str(self.window.event.players[0].name)
        popupMenu = tk.ttk.OptionMenu(top, self.player, default, *choices)
        tk.Label(top, text="Choose a Player to edit:").pack()
        popupMenu.pack()
        button = tk.Button(top, text="Edit", command=self.getPlayer)
        button.pack()
        
    def getPlayer(self):
        self.name = self.player.get()
        self.popup = popupWindow(self.window, self.master, mode='edit')
        
        
        
root = tk.Tk()
root.geometry("800x600")
root.resizable(width=False, height=False)
app = Window(root)
root.mainloop()
