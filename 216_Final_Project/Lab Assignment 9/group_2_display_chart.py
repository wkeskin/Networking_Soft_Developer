#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 3, 2025

@author: lissettegorrin

group_2_display_chart.py
Lab 9 – Interactive Chart Display (Bar & Line)

COMP216 - SEC 401
Networking for Software Developers - Winter 2025

Group 2:
    Aiko Bislig
    Jacob Ferreira
    Lissette Gorrin Rodriguez
    Samer Aljundi Al Fattouhi Aljundi
    Wardatul Keskin

Lab 9 - Interactive Chart Display (Bar & Line)
"""

import tkinter as tk
from group2_data_generator import SensorDataGenerator

# -------------------------------
# ChartDisplay Class: GUI Display
# -------------------------------
class ChartDisplayApp(tk.Tk):
    """
    GUI application to display temperature sensor data using Bar and Line chart.
    User can select starting index to display range of data.
    """

    def __init__(self):
        super().__init__()
        self.title("Temperature Chart Display (°C)")
        self.geometry("500x550")
        self.configure(bg='white')

        # Generate 20 static temperature values from SensorDataGenerator
        self.sensor = SensorDataGenerator(sensor_type="temperature", min_value=18, max_value=30)
        self.data = [round(self.sensor.value, 1) for _ in range(20)]

        # Default range (first 6 values)
        self.start_index = 0
        self.display_values = self.data[self.start_index:self.start_index + 6]

        self.create_widgets()
        self.draw_chart()

    def create_widgets(self):
        """Initialize all GUI widgets."""
        # Title Label
        title = tk.Label(self, text="Temperature Sensor Data (°C)", font=("Arial", 16, "bold"), bg='white')
        title.pack(pady=10)

        # Canvas for chart
        self.canvas = tk.Canvas(self, width=450, height=300, bg='white', highlightthickness=1, highlightbackground='black')
        self.canvas.pack(pady=10)

        # Input Frame
        input_frame = tk.Frame(self, bg='white')
        input_frame.pack(pady=10)

        # Entry and Button
        tk.Label(input_frame, text="Start Index (0-19):", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=5)
        self.entry = tk.Entry(input_frame, width=5, font=("Arial", 10))
        self.entry.pack(side=tk.LEFT, padx=5)
        tk.Button(input_frame, text="Update", command=self.update_chart).pack(side=tk.LEFT, padx=5)

        # Info Label
        self.info_label = tk.Label(self, text="", font=("Arial", 10, "italic"), bg='white', fg='black')
        self.info_label.pack()

        # Legend
        legend = tk.Label(self, text="Bar: Temperature Value | Line: Temperature Trend", fg='blue', bg='white', font=("Arial", 9))
        legend.pack(pady=5)

    def draw_chart(self):
        """Draw the bar and line chart."""
        self.canvas.delete("all")

        # Dimensions
        bar_width = 50
        spacing = 15
        x_start = 30
        base_y = 250

        max_temp = max(self.data) + 2
        min_temp = min(self.data) - 2

        # Draw Bars & Line
        points = []
        for i, value in enumerate(self.display_values):
            x0 = x_start + i * (bar_width + spacing)
            x1 = x0 + bar_width
            bar_height = (value - min_temp) / (max_temp - min_temp) * 200

            # Draw bar
            self.canvas.create_rectangle(x0, base_y - bar_height, x1, base_y, fill='green', outline='black')

            # Draw value text
            self.canvas.create_text((x0 + x1) / 2, base_y + 15, text=str(value), font=("Arial", 10))

            # For line chart
            points.append(((x0 + x1) / 2, base_y - bar_height))

        # Draw line
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], fill='red', width=2)

        # Update data range info
        end_index = self.start_index + len(self.display_values)
        self.info_label.config(text=f"Data range: {self.start_index + 1}-{end_index}", fg='black')

    def update_chart(self):
        """Button handler to update chart based on Entry."""
        try:
            index = int(self.entry.get())
            if 0 <= index <= 19:
                self.start_index = index
                self.display_values = self.data[self.start_index:self.start_index + 6]
                self.draw_chart()
            else:
                self.info_label.config(text="Index must be between 0 and 19.", fg='red')
        except ValueError:
            self.info_label.config(text="Invalid input! Enter a number.", fg='red')

# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    app = ChartDisplayApp()
    app.mainloop()
