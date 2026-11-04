# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 17:04:24 2025

@author: Group 02
"""

import tkinter as tk
from tkinter import ttk, messagebox

class StudentFormApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Centennial College")
        self.geometry("400x300")
        self.resizable(True, True)
        
        # Apply style for frame, labels, radio buttons, checkbuttons, and buttons background color
        style = ttk.Style()
        style.configure("Custom.TFrame", background="lightblue")
        style.configure("Custom.TLabel", background="lightblue")
        style.configure("Custom.TRadiobutton", background="lightblue")
        style.configure("Custom.TCheckbutton", background="lightblue")
        style.configure("Custom.TButton", background="lightblue")
        
        # Frame for all widgets
        self.main_frame = ttk.Frame(self, padding=10, relief="ridge", style="Custom.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Labels
        ttk.Label(self.main_frame, text="ICET Student Registration Survey", font=("Arial", 16, "bold"), foreground="navy", style="Custom.TLabel").grid(row=0, column=0, columnspan=3, pady=5, sticky=tk.NSEW)
        ttk.Label(self.main_frame, text="Full Name:", style="Custom.TLabel").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.main_frame, text="Residency:", style="Custom.TLabel").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.main_frame, text="Program:", style="Custom.TLabel").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.main_frame, text="Courses:", style="Custom.TLabel").grid(row=6, column=0, sticky=tk.W, pady=2)
        
        # Entry for Full Name
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.main_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=2, column=1, pady=2, sticky=tk.W)
        
        # Radio Buttons for Residency
        self.residency_var = tk.StringVar(value="dom")
        ttk.Radiobutton(self.main_frame, text="Domestic", variable=self.residency_var, value="dom", style="Custom.TRadiobutton").grid(row=3, column=1, sticky=tk.W)
        ttk.Radiobutton(self.main_frame, text="International", variable=self.residency_var, value="intl", style="Custom.TRadiobutton").grid(row=4, column=1, sticky=tk.W)
        
        # Combobox for Programs
        self.program_var = tk.StringVar()
        self.program_combobox = ttk.Combobox(self.main_frame, textvariable=self.program_var, values=["AI", "Gaming", "Health", "Software"])
        self.program_combobox.grid(row=5, column=1, pady=2, sticky=tk.W)
        self.program_combobox.current(0)
        
        # Checkbuttons for Courses
        self.course_vars = {
            "Programming I": tk.StringVar(value=""),
            "Web Page Design": tk.StringVar(value=""),
            "Software Engineering": tk.StringVar(value="")
        }
        ttk.Checkbutton(self.main_frame, text="Programming I", variable=self.course_vars["Programming I"], onvalue="COMP100", offvalue="", style="Custom.TCheckbutton").grid(row=6, column=1, sticky=tk.W)
        ttk.Checkbutton(self.main_frame, text="Web Page Design", variable=self.course_vars["Web Page Design"], onvalue="COMP213", offvalue="", style="Custom.TCheckbutton").grid(row=7, column=1, sticky=tk.W)
        ttk.Checkbutton(self.main_frame, text="Software Engineering", variable=self.course_vars["Software Engineering"], onvalue="COMP120", offvalue="", style="Custom.TCheckbutton").grid(row=8, column=1, sticky=tk.W)
        
        # Buttons Frame for Alignment
        self.button_frame = ttk.Frame(self.main_frame, style="Custom.TFrame")
        self.button_frame.grid(row=10, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        # Buttons inside frame aligned center
        ttk.Button(self.button_frame, text="Reset", command=self.reset_form, style="Custom.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(self.button_frame, text="OK", command=self.show_details, style="Custom.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(self.button_frame, text="Exit", command=self.destroy, style="Custom.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Initialize form
        self.reset_form()
    
    def reset_form(self):
        """Resets the form to the initial state."""
        self.name_var.set("")
        self.residency_var.set("dom")
        self.program_combobox.current(0)
        for var in self.course_vars.values():
            var.set("")
    
    def show_details(self):
        """Displays a message box with form details."""
        courses_selected = [name for name, var in self.course_vars.items() if var.get()]
        messagebox.showinfo("Student Details",
                            f"Name: {self.name_var.get()}\n"
                            f"Residency: {self.residency_var.get()}\n"
                            f"Program: {self.program_var.get()}\n"
                            f"Courses: {', '.join(courses_selected) if courses_selected else 'None'}")

if __name__ == "__main__":
    app = StudentFormApp()
    app.mainloop()
