# author : Narendra
# filename: wk03c1_gui_interest.py
# date: May 30, 2021

from tkinter import *
from tkinter.ttk import *

class InterestApp(Tk):

    def __init__(self, title):
        Tk.__init__(self)
        self.title(title)
        # Canvas(self, width=400, height=600).pack()
        # container = Frame(self)
        # container.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)
        self.create_ui()
        # self.create_styles()
        # self.set_vars()
        style = Style()
        style.theme_use('clam')
        style.configure('.', bd=4, background='aquamarine', foreground='green')

    def create_ui(self, parent=None):
        if not parent: parent = self

        Label(
            parent, 
            text='Begining Balance:'
            ).grid(sticky=E)                # must be aligned to the right
        Label(parent, text='Annual Interest Rate:').grid(row=1, sticky=E)
        Label(parent, text='Time:').grid(row=2, sticky=E)
        Label(parent, text='Compounding Period:').grid(row=3, sticky=E)
        Label(parent, text='End Balance:').grid(row=4, sticky=E)

        self.start_balance = DoubleVar()
        self.start_balance.set(1_000)
        Entry(
            parent, 
            text='Starting Balance:', 
            textvariable=self.start_balance
            ).grid(
                row=0,                      # goes into the first row
                column=1,                   # goes into the second column
                columnspan=2,               # occupy 2 columns
                sticky=W)                   # must be aligned to the left
        self.interest_rate = DoubleVar()
        self.interest_rate.set(2.25)
        Entry(
            parent, text='Annual Interest Rate:', 
            textvariable=self.interest_rate
            ).grid(columnspan=2, column=1, row=1, sticky=W)
        
        self.period = StringVar()
        self.combobox = Combobox(parent, textvariable=self.period)
        self.combobox['values'] = ('Year', '6 Months', '4 Months', '3 Months')
        self.combobox.grid(columnspan=2, column=1, row=2, sticky=W)
        self.period.set('Years')

        self.years = DoubleVar()
        Entry(
            parent, text='Years:', textvariable=self.years
            ).grid(columnspan=2, column=1, row=3, sticky=W)
        self.end_balance = StringVar()
        Entry(
            parent, text='End Balance:', textvariable=self.end_balance, 
            state=DISABLED                  # disables user interaction
            ).grid(columnspan=2, column=1, row=4, sticky=W)

        Button(parent, text='Calculate', command=self.calculate).grid(row=5, column=1)
        Button(parent, text='Exit',command=self.quit).grid(row=5, column=2)

        for child in parent.winfo_children():
            child.grid_configure(padx=5, pady=3)

    def calculate(self, *args):
        self.end_balance.set(f'${self.start_balance.get()} {self.interest_rate.get()} {self.period.get()} {self.years.get()}')

app = InterestApp('Future Value Calculator')
app.mainloop()        