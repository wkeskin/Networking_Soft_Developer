from tkinter import *
from tkinter.ttk import *

class RegistrationApp(Tk) :

    def __init__(self, title):
        Tk.__init__(self)           #call the base constructor
        self.title(title)           #sets the title of the main window

        self.iconbitmap('Internet.ico')

        sizer = Canvas(width=900, height=400)   #to force the size of the main window
        sizer.pack()

        container = Frame(self)
        container.place(
            relx=0.05,              ##distance from left of parent
            rely=0.05,              #distance from top of parent
            relwidth=0.9,           #width of the widget (relative to parent)
            relheight=0.9)          #height of the widget (relative to parent)

        self.create_styles()
        self.create_ui(container)


    def create_styles(self):
        style = Style()
        style.configure(
            'TFrame',
            background='sky blue',
            padding=(2, 2, 6, 6)
        )
        style.configure('TLabel', background='#ff80c1', padding=(2, 2, 4, 4))
        style.configure('TButton', background='gray', foreground='goldenrod', padding=(2, 2, 4, 4), ipadding=(5, 5, 5, 5))
    def create_ui(self, parent):
        #1st frame
        frame = Frame(parent)
        frame.place(relx=0.05, rely=0, relwidth=0.9, relheight=0.2)
        Label(frame, text='Registration Form', style='Heading.TLabel').pack(expand=True)
        # Label(frame, text='Registration Form', style='Heading.TLabel').place(relx=0.15, rely=0, relwidth=0.7, relheight=0.9)

        #2nd frame
        frame = Frame(parent)
        frame.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.6)
        #first column
        Label(frame, text='Name').place(relx=0, rely=0, relwidth=0.25, relheight=0.3)
        Label(frame, text='Program').place(relx=0, rely=0.33, relwidth=0.25, relheight=0.3)
        Label(frame, text='2nd row').place(relx=0, rely=0.66, relwidth=0.25, relheight=0.3)
        # Label(frame, text='2nd row').place(relx=0, rely=0, relwidth=0.45, relheight=0.3)

        #second column
        Entry(frame, text='2nd row').place(relx=0.25, rely=0, relwidth=0.5, relheight=0.3)
        Entry(frame, text='2nd row').place(relx=0.25, rely=0.33, relwidth=0.5, relheight=0.3)
        Entry(frame, text='2nd row').place(relx=0.25, rely=0.66, relwidth=0.5, relheight=0.3)
        
        #third column 
        Label(frame, text='2nd row').place(relx=0.75, rely=0, relwidth=0.25, relheight=0.3)
        Label(frame, text='2nd row').place(relx=0.75, rely=0.33, relwidth=0.25, relheight=0.3)
        Label(frame, text='2nd row').place(relx=0.75, rely=0.66, relwidth=0.25, relheight=0.3)
        
        #3th frame
        frame = Frame(parent)
        frame.place(relx=0.05, rely=0.8, relwidth=0.9, relheight=0.2)
        Button(frame, text='3rd row').place(relx=0.1, rely=0.1, relwidth=0.3, relheight=0.8)
        Button(frame, text='3rd row').place(relx=0.6, rely=0.1, relwidth=0.3, relheight=0.8)

# test harness
app = RegistrationApp('My Awesome GUI')
app.mainloop()