import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog, scrolledtext
import json
import os

import swiss_tournament as swiss


version = '0.4'


# List of Format Names
formats = ['Standard', 'Modern', 'Legacy', 'Vintage', 'Booster Draft', 
           'Sealed Deck', 'Team Unified Constructed - Standard', 
           'Team Unified Constructed - Modern',
           'Team Unified Constructed - Legacy',
           'Team Unified Constructed - Vintage', 'Team Trios Constructed', 
           'Block Constructed', 'Two Headed Giant', 'Conspiracy Draft', 
           'Team Booster Draft', 'Team Sealed Deck', 'Pauper', 'Commander',
           'Cube Draft', 'Casual']



class Window(tk.Frame):
    # the main program window
    def __init__(self, master=None):
        #tk.Frame.__init__(self, master)
        self.master = master
        
        # main window settings
        self.master.geometry('800x600')
        self.master.resizable(width=False, height=False)

        # initialize some variables
        self.event = None
        self.filename = None
        
        # build the main window
        self.init_window()
        # create txt file for storing temporary data for printing
        # could probably done in the printOut method
        with open('temp.txt', 'w') as f:
            self.tempfile = f
            
            
    def init_window(self):
        # load some initial data from text file
        self.loadInit()
        
        self.master.title('Swiss Tournament App')
        
        # initialize the menu row
        self.menu = Menu(self.master, self)
        self.master.config(menu=self.menu)
        #place a Notebook with tabs
        self.nb = ttk.Notebook(self.master)
        self.nb.pack(fill=tk.BOTH, expand=1)
        
        
    def loadInit(self):
        try:
            with open('data.json') as f:
                data = json.load(f)
            self.last_opened = data['last_opened']
            self.filename = data['filename']
        except:
            self.last_opened = None
            self.filename = None
            
            
    def update(self):
        self.nb.update()
        self.checkOptions()
            
                   
    def saveInit(self):
        data = {'last_opened': self.last_opened,
                'filename': self.filename
                }
        with open('data.json', 'w') as f:
            json.dump(data, f)
            
    
    def println(self, text):
        txt = self.nb.tab_console.txt
        txt.insert(tk.END, text + '\n')
        # automatically jump to the bottom of the text window
        txt.see(tk.END)
        
    def checkOptions(self):
        if self.event:
            self.menu.filemenu.entryconfig(1, state="normal") # Save Event
            self.menu.editmenu.entryconfig(0, state="normal") # Add Player
            self.menu.editmenu.entryconfig(4, state="normal") # Edit event info
            if len(self.event.players) > 0:
                self.menu.entryconfig(1, state="normal") # Edit Player
                self.menu.editmenu.entryconfig(2, state="normal") # Remove Player
                self.menu.toolsmenu.entryconfig(0, state="normal") # Start Tournament
                self.menu.printingmenu.entryconfig(0, state="normal") # Print Seatings
                if self.event.no_of_rounds > 0:
                    self.menu.toolsmenu.entryconfig(1, state="normal") # Start Round
                    if len(self.event.pairings) > 0:
                        self.menu.toolsmenu.entryconfig(2, state="normal") # Enter Result
                        self.menu.toolsmenu.entryconfig(3, state="normal") # Show Standings
                        self.menu.printingmenu.entryconfig(1, state="normal") # Print Pairings
                        self.menu.printingmenu.entryconfig(2, state="normal") # Print Standings
                    else:
                        self.menu.toolsmenu.entryconfig(2, state="disabled")
                        self.menu.toolsmenu.entryconfig(3, state="disabled")
                        self.menu.printingmenu.entryconfig(1, state="disabled")
                        self.menu.printingmenu.entryconfig(2, state="disabled")
                else:
                    self.menu.toolsmenu.entryconfig(1, state="disabled")
            else:
                self.menu.editmenu.entryconfig(1, state="disabled")
                self.menu.editmenu.entryconfig(2, state="disabled")
                self.menu.toolsmenu.entryconfig(0, state="disabled")
                self.menu.printingmenu.entryconfig(0, state="disabled")                
        else:
            self.menu.filemenu.entryconfig(1, state="disabled")
            self.menu.editmenu.entryconfig(0, state="disabled")
            self.menu.editmenu.entryconfig(4, state="disabled")
            
            
#---------- Menu functions ---------------------------------------------------    
        
    def newEvent(self):
        if self.event:
            # ask the user if they want to save the current tournament
            # before overwriting
            pass
        self.event = swiss.tournament()
        self.popup_info = PopupInfo(self)
        self.master.wait_window(self.popup_info.top)
        self.txt.delete('1.0', tk.END)
        self.println('New Tournament started. Tournament-ID: {}'.format(
                self.event.tournament_id))
        self.addInfoTab()
        self.checkOptions()


    def saveFile(self):
        default = os.path.basename(self.filename)
        ftypes = [('Supported text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.asksaveasfile(mode='w',
                                       initialfile=default,
                                       defaultextension='.txt',
                                       filetypes=ftypes)
        if dlg is None:
            return
        self.filename = dlg.name
        self.event.save_tournament_as(self.filename)

    
    def onOpen(self):
        ftypes = [('Supported text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.Open(self, initialdir=os.getcwd(), filetypes = ftypes)
        fl = dlg.show()
        self.last_opened = fl
        if fl != '':
            try:
                self.event = swiss.tournament
                self.event = self.event.load_tournament(self, fl)
                text = fl
                if self.event:
                    text = 'Successfully loaded ' + text
                    self.println(text)
                    self.addInfoTab()
                    self.checkOptions()
                else:
                    text = 'ERROR: Failed to load ' + text
                self.println(text)
            except:
                text = fl
                text = 'ERROR: Failed to load ' + text
                self.println(text)


    def openRecent(self):
        self.event = swiss.tournament()
        self.event = self.event.load_tournament(self.last_opened)
        if self.event:
            text = self.last_opened
            text = 'Successfully loaded ' + text
            self.println(text)
        else:
            self.println('ERROR: Failed to load ' + str(self.last_opened))
        self.addInfoTab()
        self.checkOptions()


    def clientExit(self):
        #self.saveWindow()
        self.master.destroy()


    def addPlayer(self):
        if not self.event:
            messagebox.showinfo('Error', 'No tournament started')
            return
        self.popup_addPlayer = popupPlayers(self, self.master)
        self.master.wait_window(self.popup_addPlayer.top)
        self.checkOptions()

    
    def editPlayer(self):
        self.popup_editPlayer = editPlayerWindow(self, self.master)
        self.master.wait_window(self.popup_editPlayer.top)
        self.checkOptions()
        
        
    def dropPlayer(self, player):
        txt = 'Do you really want to drop {}?'.format(player.name)
        msg = messagebox.askyesno('Warning', txt)
        if msg:
            pl = self.event.drop_player(player.name)
            print(self.event_info['Dropouts'])
            if pl:
                self.println('{} dropped from the tournament.'.format(player.name))
            else:
                self.println('{} already dropped.'.format(player.name))
        self.update()
        
    
    def editInfo(self):
        if not self.event:
            messagebox.showinfo('Error', 'No tournament started')
            return
        self.popup_info = PopupInfo(self)
        self.master.wait_window(self.popup_info.top)
        self.checkOptions()


    def startTournament(self):
        text = self.event.print_seatings()
        self.println(text)
        self.event.calculate_rounds()
        self.checkOptions()


    def startRound(self):
        self.event.calculate_points()
        rnd = self.event.new_round()
        if rnd:
            text = self.event.print_pairings()
            self.println(text)
        else:
            missings = ''
            if len(self.event.results_entered) > 0:
                for res in self.event.results_entered:
                    missings += (str(res) + ', ')
                self.println('ERROR: Results are still missing. ' 
                             + 'Results entered for tables: ' + str(missings))
            else:
                self.println('Results are still missing')
        self.checkOptions()
        
        
    def enterResult(self):
        self.popup_enterResult = popupResult(self, self.master)
        self.master.wait_window(self.popup_enterResult.top)
        self.checkOptions()
        
        
    def showStandings(self):
        text = self.event.print_standings()
        self.println(text)


    def printOut(self, action):
        if self.event:
            # save seatings/pairings etc to a text file
            text = action()
            with open('temp.txt', 'w') as self.tempfile:
                self.tempfile.write(text)

            os.startfile(self.tempfile.name)
            
            
    def versionInfo(self):
        messagebox.showinfo('About',
                            'Swiss Tournament App\nVersion {}\n'.format(version)
                            + '© Christian Post')

          
    def underConstruction(self):
        messagebox.showinfo('Ups', 'hier kommt noch was')

            
            
class Menu(tk.Menu):
    
    def __init__(self, master, main):
        tk.Menu.__init__(self, master)
        self.master = master
        self.main = main
        
        #ERSETZ ALLE self.master ab hier durch self.main!!!!

        # file menu       
        self.filemenu = tk.Menu(self, tearoff=0)
        self.filemenu.add_command(label='New Tournament...', 
                                  command=self.main.newEvent)
        self.filemenu.add_command(label='Save As...', command=self.main.saveFile, 
                                  state='disabled')
        self.filemenu.add_command(label='Open...', command=self.main.onOpen)
        if self.main.last_opened:
            self.filemenu.add_command(label='Open Recent', 
                                      command=self.main.openRecent)
        else:
            self.filemenu.add_command(label='Open Recent', 
                                      command=self.main.openRecent, state='disabled')
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Exit Program', command=self.main.clientExit)
        self.add_cascade(label='File', menu=self.filemenu)
        
        # edit menu
        self.editmenu = tk.Menu(self, tearoff=0)
        self.editmenu.add_command(label='Add Players', command=self.main.addPlayer, 
                                  state='disabled')
        self.editmenu.add_command(label='Edit Players', command=self.main.editPlayer, 
                                  state='disabled')
        self.editmenu.add_command(label='Drop Players', 
                                  command=self.main.underConstruction, 
                                  state='disabled')
        self.editmenu.add_command(label='Edit Results', 
                                  command=self.main.underConstruction,
                                  state='disabled')
        self.editmenu.add_command(label='Edit Event Information', 
                                  state='disabled', command=self.main.editInfo)
        self.add_cascade(label='Edit', menu=self.editmenu)
        
        # tools menu
        self.toolsmenu = tk.Menu(self, tearoff=0)
        self.toolsmenu.add_command(label='Start Tournament', 
                                   command=self.main.startTournament, 
                                   state='disabled')
        self.toolsmenu.add_command(label='Start next Round', 
                                   command=self.main.startRound, 
                                   state='disabled')
        self.toolsmenu.add_command(label='Enter Result', state='disabled', 
                                   command=self.main.enterResult)
        self.toolsmenu.add_command(label='Show Standings', 
                                   command=self.main.showStandings, 
                                   state='disabled')
        self.add_cascade(label='Tools',menu=self.toolsmenu)
        
        # printing menu
        self.printingmenu = tk.Menu(self, tearoff=0)
        self.printingmenu.add_command(label='Print Seatings...',
                                      command=lambda: self.main.printOut(
                                     self.main.event.print_seatings), 
                                      state='disabled')
        self.printingmenu.add_command(label='Print Pairings...',
                                      command=lambda: self.main.printOut(
                                     self.main.event.print_pairings), 
                                      state='disabled')
        self.printingmenu.add_command(label='Print Standings...',
                                      command=lambda: self.main.printOut(
                                     self.main.event.print_standings), 
                                      state='disabled')
        self.add_cascade(label='Print', menu=self.printingmenu)
        
        # config menu
        self.app_config = tk.Menu(self, tearoff=0)
        self.app_config.add_command(label='Tournament Presets', 
                                    command=self.main.underConstruction)
        self.app_config.add_command(label='Preferences', 
                                    command=self.main.underConstruction)
        self.add_cascade(label='Options', menu=self.app_config)
        
        # help menu
        self.helpmenu = tk.Menu(self, tearoff=0)
        self.helpmenu.add_command(label='Help Index', 
                                  command=self.main.underConstruction)
        self.helpmenu.add_command(label='About...', command=self.main.versionInfo)
        self.add_cascade(label='Help', menu=self.helpmenu)
        
   
#--------------- Tabs ---------------------------------------------------------     
        
class Notebook(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master)
        self.master = master
        self.test = True
        self.tab_players = None
        
        self.tab_console = ConsoleTab(self)
        self.add(self.tab_console, text='Console')
        
    def update(self):
        # Adds player tab to the notebook,
        # if it doesnt already exist and there are players in the tournament
        if not self.tab_players and self.master.event.players:
            self.tab_players = PlayerTab(self)
            self.add(self.tab_players, text='Players')
            self.tab_players.update()
        

class ConsoleTab(ttk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        
        #place text widget
        self.txt = scrolledtext.ScrolledText(self)
        # disable text editing by user
        self.txt.bind('<Key>', lambda e: 'break')
        self.txt.pack(fill=tk.BOTH, expand=1)
        
    
class PlayerTab(ttk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        
    def update(self):
        # clear the previous labels
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text='Name').grid(row=0, column=0, sticky=tk.W)
        tk.Label(self, text='DCI').grid(row=0, column=1, sticky=tk.W, padx=16)
        row = 1
        self.master.event.sort_players('name')
        for player in self.master.event.players:
            l1 = tk.Label(self, text=player.name)
            l1.grid(row=row, column=0, sticky=tk.W)
            l2 = tk.Label(self.page_players, text=str(player.dci))
            l2.grid(row=row, column=1, sticky = tk.W, padx=16)
            b1 = tk.Button(self.page_players, text='EDIT', 
                           command=self.master.editPlayer)
            b1.grid(row=row, column=2, padx=4, pady=1)
            b2 = tk.Button(self.page_players, text='DROP', 
                           command=lambda pl=player: self.master.drop(pl))
            b2.grid(row=row, column=3, padx=4, pady=1)
            row += 1
            
            
#------------- Popup Windows --------------------------------------------------            
            
class PopupInfo(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master          
        self.top = top = tk.Toplevel(master)
        self.top.geometry('250x200')  
        # Labels and entry forms
        self.l1 = tk.Label(top,text='Event Name:')
        self.l1.pack()
        self.e1 = tk.Entry(top)
        self.e1.pack()
        self.l2 = tk.Label(top,text='Event Information:')
        self.l2.pack()
        self.e2 = tk.Entry(top)
        self.e2.pack()
        self.l3 = tk.Label(top,text='Format:')
        self.l3.pack()
        self.format = tk.StringVar()
        default = formats[0]
        self.m1 = ttk.OptionMenu(top, self.format, default, *formats)
        self.m1.pack()
        self.e1.insert(0, self.master.event.event_name)
        self.e2.insert(0, self.master.event.event_information)
        self.b = tk.Button(top,text='Save changes',command=self.cleanup, 
                           state='normal')
        self.b.pack()
    
    
    def cleanup(self):
        name = self.e1.get().strip()
        info = self.e2.get().strip()
        if name == '' or info == '':
            messagebox.showinfo('Error', 'ERROR: Field can\'t be empty!')
            self.top.lift()
            return
        else:
            self.master.event.event_name = name
            self.master.event.event_information = info
            self.master.event.format = self.format.get()
            self.master.update()
            string = 'Updated Event Information'
            self.master.println(string)
            self.top.destroy()
            
#------------- old classes ----------------------------------------------------           



class popupPlayers():
    def __init__(self, window, master, mode='add'):
        self.window = window
        self.master = master
        self.top = top = tk.Toplevel(master)
        self.top.geometry('200x200')
        self.l1 = tk.Label(top,text='First Name')
        self.l1.pack()
        self.e1 = tk.Entry(top)
        self.e1.pack()
        self.l2 = tk.Label(top,text='Last Name')
        self.l2.pack()
        self.e2 = tk.Entry(top)
        self.e2.pack()
        self.l3 = tk.Label(top,text='DCI')
        self.l3.pack()
        self.e3 = tk.Entry(top)
        self.e3.pack()
        if mode == 'add':
            self.b = tk.Button(top,text='Add Player',command=self.cleanupAdd)
        elif mode == 'edit':
            firstname = ''
            self.id = None
            for player in self.window.event.players:
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
            messagebox.showinfo('Error', 'ERROR: DCI already entered!')
            self.top.lift()
            return
        if self.name == ', ':
            messagebox.showinfo('Error', 'Please enter a name')
            self.top.lift()
            return
        else:
            pl = self.window.event.add_player(self.name, self.dci)
            self.window.event_info['Number of Players'][1].set(
                    len(self.window.event.players))
            if self.dci == '':
                messagebox.showinfo('Warning', 'No DCI entered.\nA random number will be assigned as DCI.')
                pl.dci = pl.id
            string = 'Player added: ' + pl.name + '; DCI ' + str(pl.dci)
            self.window.println(string)
            #self.top.destroy()
            self.e1.delete(0, tk.END)
            self.e2.delete(0, tk.END)
            self.e3.delete(0, tk.END)
            self.top.lift()

    def cleanupEdit(self):
        if self.id:
            self.name = self.e2.get().strip() + ', ' + self.e1.get().strip()
            self.dci = self.e3.get().strip()
            for player in self.window.event.players:
                if player.id == self.id:
                    # compare the stored id to the player's id 
                    player.name = self.name
                    if self.dci != '':
                        player.dci = self.dci
                    else:
                        # ask User if they want to generate a fake DCI
                        # if so, use the player's ID as the DCI
                        messagebox.showinfo('Warning', 'No DCI entered.\nA random number will be assigned as DCI.')
                        player.dci = player.id
        self.top.destroy()



class popupResult():
    def __init__(self, window, master):
        self.window = window
        self.master = master
        self.top = top = tk.Toplevel(master)
        self.top.geometry('200x200')
        self.l0 = tk.Label(top,text='Table Number:')
        self.l0.grid(row=0, column=0, sticky=tk.W, columnspan=4)
        # Table Number Menu
        self.table = tk.IntVar()
        choices = [key for key in self.window.event.pairings]
        default = choices[0]
        menu = ttk.OptionMenu(top, self.table, default, *choices, 
                              command=self.setName)
        menu.grid(row=0, column=5, sticky=tk.W, columnspan = 2)
        self.player1, self.player2 = tk.StringVar(), tk.StringVar()
        self.setName(default)
        
        self.l1 = tk.Label(top, text='Wins for:')
        self.l1.grid(row=1, column=0, sticky=tk.W)
        self.l11 = tk.Label(top, textvariable=self.player1)
        self.l11.grid(row=1, column=1, sticky=tk.W)
        self.e1 = tk.Entry(top)
        self.e1.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.l2 = tk.Label(top, text='Wins for:')
        self.l2.grid(row=3, column=0, sticky=tk.W)
        self.l21 = tk.Label(top, textvariable=self.player2)
        self.l21.grid(row=3, column=1, sticky=tk.W)
        self.e2 = tk.Entry(top)
        self.e2.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.l3 = tk.Label(top, text='Draw:')
        self.l3.grid(row=5, column=0, sticky=tk.W)
        self.e3 = tk.Entry(top)
        self.e3.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        self.b = tk.Button(top, text='Enter Result', command=self.cleanup, 
                           state='normal')
        self.b.grid(row=7, column=1, sticky=tk.W)
     

    def setName(self, arg):
        self.player1.set(self.window.event.pairings[self.table.get()][0].name)
        self.player2.set(self.window.event.pairings[self.table.get()][1].name)
        

    def cleanup(self):
        player1 = self.e1.get().strip()
        player2 = self.e2.get().strip()
        draw = self.e3.get().strip()
        if player1 == '' or player2 == '' or draw == '':
            messagebox.showinfo('Error', 'ERROR: Field can\'t be empty!')
            self.top.lift()
            return
        elif (not player1.isnumeric() or
              not player2.isnumeric() or not draw.isnumeric()):
            messagebox.showinfo('Error', 'values have to be numeric')
            self.top.lift()
            return
        else:
            draw =int(draw)
            player1, player2 = int(player1), int(player2)
            self.window.event.enter_result(self.table.get(), 
                                           [player1, player2, draw])
            string = 'Result entered successfully.'
            self.window.println(string)
            self.top.destroy()



class editPlayerWindow():
    def __init__(self, window, master):
        self.window = window
        self.master = master
        self.top = top = tk.Toplevel(master)
        self.top.geometry('200x100')
        self.player = tk.StringVar(top)
        choices = [str(player.name) for player in self.window.event.players]
        default = str(self.window.event.players[0].name)
        popupMenu = ttk.OptionMenu(top, self.player, default, *choices)
        tk.Label(top, text='Choose a Player to edit:').pack()
        popupMenu.pack()
        button = tk.Button(top, text='Edit', command=self.getPlayer)
        button.pack()

    def getPlayer(self):
        self.name = self.player.get()
        self.popup = popupPlayers(self.window, self.master, mode='edit')