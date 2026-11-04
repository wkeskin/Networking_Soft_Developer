#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 6, 2025

@author: aikobislig

group_2_dynamic_chart.py
Lab 10 – Display a Dynamic Line Chart

COMP216 - SEC 401
Networking for Software Developers - Winter 2025

Group 2:
    Aiko Bislig
    Jacob Ferreira
    Lissette Gorrin Rodriguez
    Samer Aljundi Al Fattouhi Aljundi
    Wardatul Keskin

Lab 10 – Display a Dynamic Line Chart
"""

import tkinter as tk       # GUI library
import threading           # For background updating
import time                # Delay between updates
import random              # To generate new values

# Main GUI application class
class DynamicTemperatureApp(tk.Tk):
    """
    GUI app to show temperature using both bar and line chart dynamically.
    """

    def __init__(self):
        super().__init__()  # Initialize the main Tkinter window
        self.title("Dynamic Temperature Chart")
        self.geometry("550x530")  # Set window size
        self.configure(bg="white")  # Set background color

        self.data = [round(random.uniform(0, 30), 1) for _ in range(20)]  # Start with 20 random temperatures
        self.current_hour = 13  # Stores the current time and starts at 1pm by default

        # Create frame for chart and legend
        self.chart_frame = tk.Frame(self, bg="white")  # Create container
        self.chart_frame.pack(pady=(10, 0))  # Add padding at top

        # Create chart title
        tk.Label( self.chart_frame, text="Hourly Temperature", font=("Arial", 18, "bold"), bg="white", fg="DarkOrange1").pack()

        # Create canvas for the chart
        self.canvas = tk.Canvas( self.chart_frame, width=650, height=380, bg="white", highlightthickness=0 )
        self.canvas.pack(pady=10, padx=20)  # Add spacing

        # Set up legend
        self.setup_legend()

        # Set up the thread for updates in the background
        thread = threading.Thread(target=self.update_loop) # Create a thread and set the target to the update_loop method
        thread.daemon = True  # Set deamon property to true to automatically close thread when GUI closes
        thread.start() # Start thread

    def setup_legend(self):
        """
        Creates a small legend that explains the meaning of bar and line
        """

        # Create frame to hold legend items
        legend_frame = tk.Frame(self.chart_frame, bg="gray95", bd=1)
        legend_frame.pack(anchor="w", padx=30, pady=(10, 20))  # Align left

        # Frame for (temperature value) bar  in legend
        bar_row = tk.Frame(legend_frame, bg="gray95")
        bar_row.pack(anchor="w", pady=2, padx=5)

        # Set up & create visual representation for (temperature value) bar in legend
        bar_color = tk.Canvas(bar_row, width=15, height=10, bg="gray95", highlightthickness=0)
        bar_color.create_rectangle(1, 1, 14, 9, fill="lightblue", outline="DodgerBlue2")  # Colored bar box
        bar_color.pack(side="left")

        # Create label for (temperature value) bar in legend
        tk.Label(bar_row, text="Bar: Temperature Value", font=("Arial", 9), bg="gray95").pack(side="left", padx=5)

        # Frame for (temperature trend) line in legend
        line_row = tk.Frame(legend_frame, bg="gray95")
        line_row.pack(anchor="w", pady=2, padx=5)

        # Set up & create visual representation for (temperature trend) line in legend
        line_color = tk.Canvas(line_row, width=15, height=10, bg="gray95", highlightthickness=0)
        line_color.create_line(0, 5, 15, 5, fill="DarkOrange1", width=2)  # Colored line
        line_color.pack(side="left")

        # Create label for (temperature trend) line in legend
        tk.Label(line_row, text="Line: Temperature Trend", font=("Arial", 9), bg="gray95").pack(side="left", padx=5)

    def update_loop(self):
        """
        Continuously updates the temperature list and redraws the chart every 0.5 seconds.
        """

        while True:
            try:
                self.data.pop(0)  # Remove the first item in the list of values
                self.data.append(round(random.uniform(0, 30), 1))  # Add a new random value to the end of the list

                # Moves hour forward by 1, if current hour reaches 24(midnight), resets time back to 0
                self.current_hour += 1
                if self.current_hour == 24:
                    self.current_hour = 0

                self.draw_chart()  # Call the method to display list on the canvas (Redraw the chart)
                time.sleep(0.5)  # Sleep for a half a second
            except Exception as e:
                print("Error during update.", e)

    def format_hour_label(self, hour):
        """
        Convert 24-hour time to 12-hour AM/PM format
        """
        if hour == 0:
            number = 12
            suffix = "AM"
        elif hour < 12:
            number = hour
            suffix = "AM"
        elif hour == 12:
            number = 12
            suffix = "PM"
        else:
            number = hour - 12
            suffix = "PM"

        return str(number) + suffix

    def draw_chart(self):
        """
        Redraws the chart with bars, line, axes and labels.
        """

        self.canvas.delete("all")  # Clear old drawings

        # Stores values for bar/line chart sizing and scaling
        values = self.data[-10:]  # Only use the recent 10 values from data list
        canvas_width = 650
        canvas_height = 380
        canvas_padding_left = 60
        canvas_padding_right = 30
        x_axis_line_start_position = canvas_height - 60
        bar_height_per_celsius = 10
        bar_spacing = 25
        bar_width = ((canvas_width - canvas_padding_left - canvas_padding_right) / len(values)) - bar_spacing

        # Draw y-axis line
        self.canvas.create_line(canvas_padding_left, 10, canvas_padding_left, x_axis_line_start_position, width=2)

        # Calculates end position of the x-axis line (right edge of chart)
        last_bar_end = (9 * (bar_width + 10)) + canvas_padding_left + bar_width + 20

        # Draw y-axis values (temperature values in celsius)
        for number in range(0, 31, 5):
            y = x_axis_line_start_position - number * bar_height_per_celsius
            self.canvas.create_text(canvas_padding_left - 15, y, text=str(number), font=("Arial", 8))

        # Draw label for y-axis
        y_axis_height = x_axis_line_start_position - 10
        self.canvas.create_text(canvas_padding_left - 50, 10 + y_axis_height / 2, text="Temperature (°C)", angle=90, font=("Arial", 10, "bold"), fill="DarkOrange1")

        # Draw label for x-axis
        self.canvas.create_text( (canvas_padding_left + last_bar_end) / 2, x_axis_line_start_position + 50, text="Time", font=("Helvetica", 10, "bold"), fill="DarkOrange1")

        points = []  # Store points (x,y positions) for line chart

        # Find the hour label for the first temperature value on the x-axis
        start_hour = self.current_hour - 9  # Subtract the number of hours that are shown on the chart after the first bar from the current hour value
        if start_hour < 0:  # If the result is negative, keep the values within a 24-hour clock
            start_hour += 24

        # For all 10 temperature values, calculate the x-axis hours and display the temperature values as bars and store the values as points too
        for i in range(10):
            value = values[i]
            bar_left_side = i * (bar_width + 10) + canvas_padding_left + 10
            bar_right_side = bar_left_side + bar_width
            bar_bottom_side = x_axis_line_start_position
            bar_top_side = bar_bottom_side - value * bar_height_per_celsius

            # Draw bar to represent temperature value
            self.canvas.create_rectangle(bar_left_side, bar_top_side, bar_right_side, bar_bottom_side, fill="lightblue", outline="DodgerBlue2")

            # Calculate and draw label for x-axis value (hour)
            label_hour = start_hour + i # Add i hours to the start hour
            if label_hour >= 24:    # If the hour of the label is greater than 24, subtract 24 to keep the values within a 24-hour clock
                label_hour -= 24
            label = self.format_hour_label(label_hour)
            bar_mid_bottom = (bar_left_side + bar_right_side) / 2
            self.canvas.create_text(bar_mid_bottom, x_axis_line_start_position + 20, text=label, font=("Arial", 8))

            points.append((bar_mid_bottom, bar_top_side))  # Store point for line chart

        # Draw x-axis line
        self.canvas.create_line(canvas_padding_left, x_axis_line_start_position, last_bar_end, x_axis_line_start_position, width=2)

        # Draw line for temperature trend
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], fill="DarkOrange1", width=2)

# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    app = DynamicTemperatureApp()
    app.mainloop()
