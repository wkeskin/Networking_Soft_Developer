#file: wk03c1_gui.py
#create a window with a single label

from tkinter import Tk
from tkinter.ttk import Label

root = Tk()
label = Label(
    root,                   #parent container
    text='Hello world'      #to show on label
)
label.pack()

root.mainloop()