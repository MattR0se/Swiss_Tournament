import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog, scrolledtext
import json
import os

import swiss_tournament as swiss

version = '0.3'

def error(number):
    error_dict = {
            0: 'ERROR: No event found.',
            1: 'ERROR: Add Players first!',
            2: 'ERROR: DCI already entered!',
            3: 'ERROR: Please enter a name!',
            4: 'ERROR: No tournament started!',
            5: 'ERROR: Failed to load ',
            6: 'No DCI entered.\nA random number will be assigned as DCI.',
            7: 'hier kommt später noch was',
            8: 'ERROR: Field can\'t be empty!',
            9: 'ERROR: Results are still missing.',
            10: 'ERROR: Results are still missing. Results entered for tables: '
            }
    return error_dict[number]

formats = ['Standard', 'Modern', 'Legacy', 'Vintage', 'Booster Draft', 
           'Sealed Deck', 'Team Unified Constructed - Standard', 
           'Team Unified Constructed - Modern',
           'Team Unified Constructed - Legacy',
           'Team Unified Constructed - Vintage', 'Team Trios Constructed', 
           'Block Constructed', 'Two Headed Giant', 'Conspiracy Draft', 
           'Team Booster Draft', 'Team Sealed Deck', 'Pauper', 'Commander',
           'Cube Draft', 'Casual']


class Window(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master

        self.event = None
        self.filename = None
        self.last_opened = None
        self.page_info = None
        
        #declare some tk variables
        self.var_event_name = tk.StringVar()
        self.var_event_info = tk.StringVar()
        self.var_event_format = tk.StringVar()
        self.var_no_of_players = tk.StringVar()
        self.var_no_of_rounds = tk.StringVar()

        self.init_window()
        with open('temp.txt', 'w') as f:
            self.tempfile = f

    def init_window(self):
        self.loadWindow()
        self.master.title('Swiss Tournament App')
        #self.pack(fill=tk.BOTH, expand=1)
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)

        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label='New Tournament...', 
                                  command=self.newEvent)
        self.filemenu.add_command(label='Save As...', command=self.saveFile, 
                                  state='disabled')
        self.filemenu.add_command(label='Open...', command=self.onOpen)
        if self.last_opened:
            self.filemenu.add_command(label='Open Recent', 
                                      command=self.openRecent)
        else:
            self.filemenu.add_command(label='Open Recent', 
                                      command=self.openRecent, state='disabled')
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Exit Program', command=self.clientExit)
        self.menu.add_cascade(label='File', menu=self.filemenu)

        self.editmenu = tk.Menu(self.menu, tearoff=0)
        self.editmenu.add_command(label='Add Players', command=self.addPlayer, 
                                  state='disabled')
        self.editmenu.add_command(label='Edit Players', command=self.editPlayer, 
                                  state='disabled')
        self.editmenu.add_command(label='Remove Players', 
                                  command=self.underConstruction, 
                                  state='disabled')
        self.editmenu.add_command(label='Edit Results', 
                                  command=self.underConstruction,
                                  state='disabled')
        self.editmenu.add_command(label='Edit Event Information', 
                                  state='disabled', command=self.editInfo)
        self.menu.add_cascade(label='Edit', menu=self.editmenu)

        self.toolsmenu = tk.Menu(self.menu, tearoff=0)
        self.toolsmenu.add_command(label='Start Tournament', 
                                   command=self.startTournament, 
                                   state='disabled')
        self.toolsmenu.add_command(label='Start next Round', 
                                   command=self.startRound, 
                                   state='disabled')
        self.toolsmenu.add_command(label='Enter Result', state='disabled', 
                                   command=self.enterResult)
        self.toolsmenu.add_command(label='Show Standings', 
                                   command=self.showStandings, 
                                   state='disabled')
        self.menu.add_cascade(label='Tools',menu=self.toolsmenu)

        self.printingmenu = tk.Menu(self.menu, tearoff=0)
        self.printingmenu.add_command(label='Print Seatings...',
                                      command=lambda: self.printOut(
                                     self.event.print_seatings), 
                                      state='disabled')
        self.printingmenu.add_command(label='Print Pairings...',
                                      command=lambda: self.printOut(
                                     self.event.print_pairings), 
                                      state='disabled')
        self.printingmenu.add_command(label='Print Standings...',
                                      command=lambda: self.printOut(
                                     self.event.print_standings), 
                                      state='disabled')
        self.menu.add_cascade(label='Print', menu=self.printingmenu)

        self.app_config = tk.Menu(self.menu, tearoff=0)
        self.app_config.add_command(label='Tournament Presets', 
                                    command=self.underConstruction)
        self.app_config.add_command(label='Preferences', 
                                    command=self.underConstruction)
        self.menu.add_cascade(label='Options', menu=self.app_config)

        self.helpmenu = tk.Menu(self.menu, tearoff=0)
        self.helpmenu.add_command(label='Help Index', 
                                  command=self.underConstruction)
        self.helpmenu.add_command(label='About...', command=self.versionInfo)
        self.menu.add_cascade(label='Help', menu=self.helpmenu)

        #place a Notebook (tabs)
        self.nb = ttk.Notebook(self.master)
        self.nb.pack(fill=tk.BOTH, expand=1)
        
        # Adds main tab to the notebook
        self.page_main = ttk.Frame(self.nb)
        self.nb.add(self.page_main, text='Console')
        #place text widget
        self.txt = scrolledtext.ScrolledText(self.page_main)
        # disable text editing by user
        self.txt.bind('<Key>', lambda e: 'break')
        self.txt.pack(fill=tk.BOTH, expand=1)
        
                  
    def addInfoTab(self):
        if not self.event or self.page_info:
            # if no event exists or the info tab already exists, return
            return
        #adds info tab and labels
        self.page_info = ttk.Frame(self.nb)
        self.nb.add(self.page_info, text='Event Information')
        # configure the grid
        col_count, row_count = self.page_info.grid_size()
        for col in range(col_count):
            self.page_info.grid_columnconfigure(col, minsize=20)    
        for row in range(row_count):
            self.page_info.grid_rowconfigure(row, minsize=20)
        
        row = 0
        self.var_event_name.set(self.event.event_name)
        tk.Label(self.page_info, text='Event Name: ').grid(row=row, column=0, 
                sticky=tk.W)
        tk.Label(self.page_info, textvariable=self.var_event_name).grid(row=row, 
                column=1, sticky=tk.W) 
        row += 1
        
        self.var_event_info.set(self.event.event_information)
        tk.Label(self.page_info, text='Event Information: ').grid(row=row, 
                column=0, sticky=tk.W)
        tk.Label(self.page_info, textvariable=self.var_event_info).grid(
                row=row, column=1, sticky=tk.W)
        row += 1
        
        self.var_event_format.set(self.event.format)
        tk.Label(self.page_info, text='Event Format: ').grid(row=row, column=0, 
                sticky=tk.W)
        tk.Label(self.page_info, textvariable=self.var_event_format).grid(row=row, 
                column=1, sticky=tk.W) 
        row += 1
        
        self.var_no_of_players.set(len(self.event.players))
        tk.Label(self.page_info, text='Number of players: ').grid(row=row, 
                column=0, sticky=tk.W)
        tk.Label(self.page_info, textvariable=self.var_no_of_players).grid(row=row, 
                column=1, sticky=tk.W)
        row += 1
        
        self.var_no_of_rounds.set(self.event.no_of_rounds)
        tk.Label(self.page_info, text='Number of rounds: ').grid(row=row, column=0, 
                sticky=tk.W)
        tk.Label(self.page_info, textvariable=self.var_no_of_rounds).grid(row=row, 
                column=1, sticky=tk.W)
    
    
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
                    text = error(5) + text
                self.println(text)
            except:
                text = fl
                text = error(5) + text
                self.println(text)


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


    def openRecent(self):
        self.event = swiss.tournament()
        self.event = self.event.load_tournament(self.last_opened)
        if self.event:
            text = self.last_opened
            text = 'Successfully loaded ' + text
            self.println(text)
        else:
            self.println(error(5) + str(self.last_opened))
        self.addInfoTab()
        self.checkOptions()


    def clientExit(self):
        #self.saveWindow()
        self.master.destroy()


    def versionInfo(self):
        messagebox.showinfo('About',
                            'Swiss Tournament App\nVersion {}\n'.format(version)
                            + '© Christian Post')


    def saveWindow(self):
        data = {'last_opened': self.last_opened,
                'filename': self.filename
                }
        with open('data.json', 'w') as f:
            json.dump(data, f)


    def loadWindow(self):
        try:
            with open('data.json') as f:
                data = json.load(f)
            self.last_opened = data['last_opened']
            self.filename = data['filename']
        except:
            self.last_opened = ''


    def newEvent(self):
        if self.event:
            # ask the user if they want to save the current tournament
            # before overwriting
            pass
        self.event = swiss.tournament()
        self.popup_info = popupInfo(self, self.master)
        self.master.wait_window(self.popup_info.top)
        self.txt.delete('1.0', tk.END)
        self.println('New Tournament started. Tournament-ID: {}'.format(
                self.event.tournament_id))
        self.addInfoTab()
        self.checkOptions()


    def addPlayer(self):
        if not self.event:
            messagebox.showinfo('Error', error(4))
            return
        self.popup_addPlayer = popupPlayers(self, self.master)
        self.master.wait_window(self.popup_addPlayer.top)
        self.checkOptions()

    
    def editInfo(self):
        if not self.event:
            messagebox.showinfo('Error', error(4))
            return
        self.popup_info = popupInfo(self, self.master)
        self.master.wait_window(self.popup_info.top)
        self.checkOptions()


    def editPlayer(self):
        self.popup_editPlayer = editPlayerWindow(self, self.master)
        self.master.wait_window(self.popup_editPlayer.top)
        self.checkOptions()


    def showPlayers(self):
        self.event.sort_players('name')
        self.println('\nPlayers in this tournament:')
        for player in self.event.players:
            self.println(player.name + ' ' + player.dci)


    def showStandings(self):
        text = self.event.print_standings()
        self.println(text)


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
                self.println(error(10) + str(missings))
            else:
                self.println(error(9))
        self.checkOptions()
        
        
    def enterResult(self):
        self.popup_enterResult = popupResult(self, self.master)
        self.master.wait_window(self.popup_enterResult.top)
        self.checkOptions()


    def println(self, text):
        self.txt.insert(tk.END, text + '\n')
        # automatically jump to the bottom of the text window
        self.txt.see(tk.END)


    def printOut(self, action):
        if self.event:
            # save seatings/pairings etc to a text file
            text = action()
            with open('temp.txt', 'w') as self.tempfile:
                self.tempfile.write(text)

            os.startfile(self.tempfile.name)
            
    def underConstruction(self):
        messagebox.showinfo('Ups', error(7))


    def checkOptions(self):
        if self.event:
            self.filemenu.entryconfig(1, state="normal") # Save Event
            self.editmenu.entryconfig(0, state="normal") # Add Player
            self.editmenu.entryconfig(4, state="normal") # Edit event info
            if len(self.event.players) > 0:
                self.editmenu.entryconfig(1, state="normal") # Edit Player
                self.editmenu.entryconfig(2, state="normal") # Remove Player
                self.toolsmenu.entryconfig(0, state="normal") # Start Tournament
                self.printingmenu.entryconfig(0, state="normal") # Print Seatings
                if self.event.no_of_rounds > 0:
                    self.toolsmenu.entryconfig(1, state="normal") # Start Round
                    if len(self.event.pairings) > 0:
                        self.toolsmenu.entryconfig(2, state="normal") # Enter Result
                        self.toolsmenu.entryconfig(3, state="normal") # Show Standings
                        self.printingmenu.entryconfig(1, state="normal") # Print Pairings
                        self.printingmenu.entryconfig(2, state="normal") # Print Standings
                    else:
                        self.toolsmenu.entryconfig(2, state="disabled")
                        self.toolsmenu.entryconfig(3, state="disabled")
                        self.printingmenu.entryconfig(1, state="disabled")
                        self.printingmenu.entryconfig(2, state="disabled")
                else:
                    self.toolsmenu.entryconfig(1, state="disabled")
            else:
                self.editmenu.entryconfig(1, state="disabled")
                self.editmenu.entryconfig(2, state="disabled")
                self.toolsmenu.entryconfig(0, state="disabled")
                self.printingmenu.entryconfig(0, state="disabled")                
        else:
            self.filemenu.entryconfig(1, state="disabled")
            self.editmenu.entryconfig(0, state="disabled")
            self.editmenu.entryconfig(4, state="disabled")
            
                  

class popupPlayers():
    def __init__(self, window, master, mode='add'):
        self.window = window
        self.master = master
        self.top = top = tk.Toplevel(master)
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
            messagebox.showinfo('Error', error(2))
            self.top.lift()
            return
        if self.name == ', ':
            messagebox.showinfo('Error', error(3))
            self.top.lift()
            return
        else:
            pl = self.window.event.add_player(self.name, self.dci)
            self.window.var_no_of_players.set(len(self.window.event.players))
            if self.dci == '':
                messagebox.showinfo('Warning', error(6))
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
                        messagebox.showinfo('Warning', error(6))
                        player.dci = player.id
        self.top.destroy()
     
        
        
class popupInfo():
    def __init__(self, window, master):
        self.window = window
        self.master = master
        self.top = top = tk.Toplevel(master)
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
        self.e1.insert(0, self.window.event.event_name)
        self.e2.insert(0, self.window.event.event_information)
        self.b = tk.Button(top,text='Save changes',command=self.cleanup, 
                           state='normal')
        self.b.pack()


    def cleanup(self):
        name = self.e1.get().strip()
        info = self.e2.get().strip()
        if name == '' or info == '':
            messagebox.showinfo('Error', error(8))
            self.top.lift()
            return
        else:
            self.window.event.event_name = name
            self.window.event.event_information = info
            self.window.event.format = self.format.get()
            self.window.var_event_name.set(name)
            self.window.var_event_info.set(info)
            self.window.var_event_format.set(self.format.get())
            string = 'Updated Event Information'
            self.window.println(string)
            self.top.destroy()
            

class popupResult():
    def __init__(self, window, master):
        self.window = window
        self.master = master
        self.top = top = tk.Toplevel(master)
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
        
        '''WORK IN PROGRESS
        results = ['2\n0', '2\n1', '1\n1', '1\n0','0\n1', '1\n2', '0\n2']
        for i in range(len(results)):
            b = tk.Button(top, text=results[i])
            b.grid(row=1, column=i, sticky=tk.W, padx=5)'''
        
        


    def setName(self, arg):
        self.player1.set(self.window.event.pairings[self.table.get()][0].name)
        self.player2.set(self.window.event.pairings[self.table.get()][1].name)
        

    def cleanup(self):
        player1 = self.e1.get().strip()
        player2 = self.e2.get().strip()
        draw = self.e3.get().strip()
        if player1 == '' or player2 == '' or draw == '':
            messagebox.showinfo('Error', error(8))
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



root = tk.Tk()
root.geometry('800x600')
root.resizable(width=False, height=False)
app = Window(root)
root.mainloop()
# save preferences after closing
app.saveWindow()
if os.path.isfile(app.tempfile.name):
    os.remove(app.tempfile.name)
