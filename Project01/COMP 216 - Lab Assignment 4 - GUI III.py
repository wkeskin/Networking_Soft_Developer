# author : Narendra
# filename: wk03c1_gui_all.py
# date: May 30, 2021
# app to demonstrate the following widgets: 
# Button, Label, Entry, Frame, Radiobutton, 
# Combobox, LabelFrame, and Checkbutton 
# using the pack layout manager

from tkinter import *
from tkinter.ttk import *

class MyApp(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title('All widgets')
        # Canvas(self, width=400, height=600).pack()
        # container = Frame(self)
        # container.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)
        self.create_ui()
        self.create_styles()
        self.set_vars()

    def create_ui(self, parent=None):
        if not parent: parent = self
        Button(                             # no way to easily change the text on this button                                
            parent,                         # all widget needs a host container
            text='My Button'                # text to go on this widget
            ).pack()                        # actually put this widget inside the host
                                            # you may also use grid or place
        Label(
            parent, text='Label "fill=X"'
            ).pack(fill=X)                  # stretch this in the horizontal direction

        self.button_var = StringVar()       # there are also IntVar, BoolVar, DoubleVar
        self.button_var.set('Alternate button')
        Button(
            parent, 
            textvariable=self.button_var    # this facilitates changing the text
            ).pack()
        
        self.label_var = StringVar()
        Label(parent, textvariable=self.label_var).pack()

        self.entry_var = StringVar()       
        Entry(parent, textvariable=self.entry_var).pack()

        panel = Frame(relief=RAISED)        # create a container for some widgets
        self.vehicle = StringVar()
        Radiobutton(
            panel,                          # this host container
            text='Honda', 
            variable=self.vehicle,          # the variable that this widget works with
            value='honda'                   # the value of the variable when this control is set
            ).pack() 
        Radiobutton(panel, text='Toyota', variable=self.vehicle, value='toyota').pack()
        Radiobutton(panel, text='Ford', variable=self.vehicle, value='ford').pack()
        panel.pack(fill=X)                  # stretch in the horizontal direction

        self.output = Text(                 # this widget does not work with variables
            parent,                         # you must use get(), insert() and delete()
            height=5)                
        self.output.pack()

        self.colors = StringVar()
        self.combobox = Combobox(parent)
        self.combobox['values'] = ('Red', 'Green', 'Blue')
        self.combobox.pack()

        self.trudeau = StringVar()
        self.biden = StringVar()
        self.modi = StringVar()
        panel = LabelFrame(
            parent, 
            text='Select your favorite leaders', 
            relief=GROOVE)                  # style for the border
        Checkbutton(
            panel, 
            variable=self.trudeau,          # the variable that works with this control
            text='Mr. Trudeau', 
            onvalue='justin_trudeau',       # value of the variable if checked
            offvalue=''                     # value of the variable if unchecked
            ).pack()  #textvariable will allow you to change the text on this widget
        Checkbutton(panel, variable=self.biden, text='Mr. Biden', onvalue='joe_biden', offvalue='').pack()
        Checkbutton(panel, variable=self.modi, text='Mr. Modi', onvalue='narendra_modi', offvalue='').pack()
        panel.pack(
            fill=BOTH,                      # stretch in both directions
            expand=True)                    # expand if there is extra room

    def set_vars(self):
        self.label_var.set('Alternate label')
        self.entry_var.set('My entry')
        self.vehicle.set('toyota') 
        self.trudeau.set('justin_trudeau')
        self.output.insert(1.0, '''This is a long
long, long string.
It can go on forever
        ''')

    def create_styles(self):
        style = Style()
        style.theme_use('alt')
        style.configure('.', padding=(20, 10, 10, 10))#, ipadding=(5, 5, 30, 40))



app = MyApp()                               # instantiate the application
app.mainloop()                              # run the event processing loop