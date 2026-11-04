#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 17:28:37 2025

@author: lissettegorrin

group_2_display_bar.py
Lab 7 – Interactive Display (Bar)

COMP216 - SEC 401
Networking for Software Developers - Winter 2025

Group 2:
    Aiko Bislig
    Jacob Ferreira
    Lissette Gorrin Rodriguez
    Samer Aljundi Al Fattouhi Aljundi
    Wardatul Keskin

Lab 7 & 8 - Interactive Display (Bar Display)
"""

from tkinter import Tk, Frame, Canvas, Label, Entry, Button, BOTH, StringVar
from group2_data_generator import SensorDataGenerator
from group_2_email_service import send_email


# -------------------------------
# BarDisplay Class: GUI Display
# -------------------------------
class BarDisplay(Frame):
    def __init__(self, master):
        """Initialize the temperature display with default settings."""
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)
        self.value = 25  # Default temperature
        self.message = StringVar()
        self.manual_override = False  # To stop auto-update if user overrides

        # Sensor Data Generator
        self.sensor = SensorDataGenerator(sensor_type="temperature", min_value=18, max_value=30)

        self.initUI()
        self.auto_update()  # Start automatic data update

    def initUI(self):
        """Build and arrange UI widgets."""
        self.master.title("Temperature Display (°C)")
        self.master.configure(bg="#f0f0f0")  

        # Canvas for temperature bar
        self.canvas = Canvas(self, bg='white', height=150)
        self.canvas.pack(fill=BOTH, padx=20, pady=10)

        # Input label and entry
        self.label = Label(self, text="Enter Temperature (°C):", font=('Arial', 12), bg="#f0f0f0")
        self.label.pack(pady=5)

        self.entry = Entry(self, font=('Arial', 12), justify='center')
        self.entry.pack(pady=5)

        # Update button
        self.btn = Button(self, text=" Update", font=('Arial', 11, 'bold'), bg='#4CAF50', fg='black',
                          command=self.update_value)
        self.btn.pack(pady=5)

        # Reset button
        self.reset_btn = Button(self, text="Reset to Sensor", font=('Arial', 10), bg='gray', fg='black',
                                command=self.reset_value)
        self.reset_btn.pack(pady=5)

        # Info label
        self.info = Label(
            self,
            text="Normal: 20-25°C | Low: <20°C | High: >25°C",
            fg='blue',
            bg="#f0f0f0",
            font=('Arial', 10)
        )
        self.info.pack(pady=5)

        # Message label (error/info)
        self.msg_label = Label(self, textvariable=self.message, fg='red', bg="#f0f0f0", font=('Arial', 10, 'italic'))
        self.msg_label.pack(pady=3)

        self.draw_bar()

    def draw_bar(self):
        """Render the temperature bar dynamically."""
        self.canvas.delete("all")

        max_value = 50
        width = (self.value / max_value) * 300

        # Determine color
        if self.value < 20:
            color = '#2196F3'  
        elif 20 <= self.value <= 25:
            color = '#4CAF50'  
        else:
            color = '#F44336'  

        # Draw bar
        self.canvas.create_rectangle(50, 50, 50 + width, 100, fill=color, outline='black')
        self.canvas.create_text(200, 120, text=f"Current Temperature: {self.value:.1f}°C", font=('Arial', 12))

    def update_value(self):
        """Get temperature input and update the bar."""
        try:
            val_str = self.entry.get().strip()
            if not val_str:
                raise ValueError("Input cannot be empty.")

            val = float(val_str)
            if not 0 <= val <= 50:
                send_email(val, threshold_low=0, threshold_high=50)
                raise ValueError("Temperature must be between 0°C and 50°C.")

            self.value = val
            self.manual_override = True  # Stop auto-update
            self.message.set("Temperature updated successfully.")
            self.msg_label.config(fg='green')
            self.draw_bar()

        except ValueError as ve:
            self.message.set(f"⚠️ {ve}")
            self.msg_label.config(fg='red')

        except Exception as e:
            self.message.set(f" Unexpected error: {e}")
            self.msg_label.config(fg='red')

    def reset_value(self):
        """Reset to auto-update sensor data."""
        self.manual_override = False
        self.message.set("Auto-update resumed from Sensor.")
        self.msg_label.config(fg='green')

    def auto_update(self):
        """Fetch new sensor data every 2 seconds."""
        if not self.manual_override:
            self.value = self.sensor.value
            self.draw_bar()
        self.after(2000, self.auto_update)


# -------------------------------
# Launch the Application
# -------------------------------
if __name__ == '__main__':
    try:
        root = Tk()
        app = BarDisplay(root)
        root.geometry("400x350")
        root.resizable(False, False)  
        root.mainloop()
    except Exception as app_error:
        print(f"Critical UI error: {app_error}")
