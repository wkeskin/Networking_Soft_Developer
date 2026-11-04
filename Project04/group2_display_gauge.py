# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 09:46:45 2025

@author: COMP216 - SEC 401
    Networking for Software Developers - Lab 6
    Group 2: 
        Aiko Bislig 
        Jacob Ferreira
        Lissette Gorrin Rodriguez
        Samer Aljundi Al Fattouhi Aljundi
        Wardatul Keskin
        
Lab 7 – Gauge
"""

import tkinter as tk
import math
from group2_data_generator import SensorDataGenerator

class StyledGaugeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Realistic Gauge Display - Temperature")
        self.geometry("400x550")
        self.configure(bg='white')

        self.sensor = SensorDataGenerator(sensor_type="temperature", min_value=18, max_value=30)
        self.value = self.sensor.value
        self.manual_override = False

        self.create_widgets()
        self.update_gauge()
        self.after(2000, self.auto_update)

    def create_widgets(self):
        tk.Label(self, text="Temperature (°C)", font=("Arial", 16), bg='white').pack(pady=10)

        self.canvas = tk.Canvas(self, width=300, height=300, bg='white', highlightthickness=0)
        self.canvas.pack()

        entry_frame = tk.Frame(self, bg='white')
        entry_frame.pack(pady=10)

        tk.Label(entry_frame, text="Set Value (°C):", bg='white').pack(side=tk.LEFT, padx=5)

        self.entry = tk.Entry(entry_frame, width=10, bg='white')
        self.entry.pack(side=tk.LEFT, padx=5)

        tk.Button(entry_frame, text="Update", command=self.update_value).pack(side=tk.LEFT)
        tk.Button(self, text="Reset to Sensor", command=self.reset_value).pack(pady=5)
        
        self.message_label = tk.Label(self, text="", font=("Arial", 10), fg="red", bg="white")
        self.message_label.pack(pady=5)

    def update_value(self):
        try:
            val = float(self.entry.get())
            if 18 <= val <= 30:
                self.value = val
                self.manual_override = True
                self.update_gauge()
                self.message_label.config(text="")
            else:
                self.message_label.config(text="Please enter a value between 18°C and 30°C.")
        except ValueError:
            self.message_label.config(text="Invalid input. Please enter a number.")

    def reset_value(self):
        self.manual_override = False
        self.entry.delete(0, tk.END)
        self.message_label.config(text="")

    def auto_update(self):
        if not self.manual_override:
            self.value = self.sensor.value
            self.update_gauge()
        self.after(2000, self.auto_update)

    def update_gauge(self):
        self.canvas.delete("all")
        center_x, center_y, radius = 150, 150, 120

        # Draw outer circle
        self.canvas.create_oval(center_x - radius, center_y - radius,
                                center_x + radius, center_y + radius,
                                outline='black', width=3)

        # Tick labels and angles
        ticks = ["18°C", "24°C", "30°C"]
        angles = [135, 90, 45]

        for i, angle in enumerate(angles):
            rad = math.radians(angle)
            x = center_x + radius * 0.75 * math.cos(rad)
            y = center_y - radius * 0.75 * math.sin(rad)
            self.canvas.create_text(x, y, text=ticks[i], font=("Arial", 10))

        # Draw needle
        angle = 135 - (self.value - 18) / (30 - 18) * 90  # Map to 135° to 45° range 18 to 30
        angle_rad = math.radians(angle)
        needle_length = radius * 0.7
        x_end = center_x + needle_length * math.cos(angle_rad)
        y_end = center_y - needle_length * math.sin(angle_rad)

        self.canvas.create_line(center_x, center_y, x_end, y_end, fill="red", width=4)
        self.canvas.create_oval(center_x - 8, center_y - 8, center_x + 8, center_y + 8, fill="black")

        # Center label
        self.canvas.create_text(center_x, center_y + 50, text=f"{self.value:.1f}°C", font=("Arial", 14))
        self.canvas.create_text(center_x, center_y + 70, text="TEMPERATURE", font=("Arial", 12, "bold"))

if __name__ == "__main__":
    app = StyledGaugeApp()
    app.mainloop()
