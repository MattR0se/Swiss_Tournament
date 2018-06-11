import swiss_tournament_v2 as swiss

import tkinter as tk
 
window = tk.Tk()
window.title("Swiss tournament simulator")
window.geometry('350x200')
 
lbl = tk.Label(window, text="Enter number of players")
lbl.grid(column=0, row=0)

txt = tk.Entry(window,width=10)
txt.grid(column=1, row=0)
 
def clicked():
    number = int(txt.get())
    swiss.simulate_tournament(number)
    lbl.configure(text="done")
 
btn = tk.Button(window, text="Run", command=clicked)
btn.grid(column=2, row=0)
 
window.mainloop()