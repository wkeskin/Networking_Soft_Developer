'''
Created for COMP216

Downloads an image and display the image data in a GUI
'''

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import requests

def retrieve_image(image_url):
    response = requests.get(image_url)          #Make a HTTP GET request to fetch a response object with an image
    image_data = response.content               #Retrieve the image payload from the response object
    return image_data                           #Return the image data in binary format

if __name__ == "__main__":
    url = 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'
    image = retrieve_image(url)
    
    root = tk.Tk()                              #Create a main window in Tkinter
    image_label = tk.Label(root)                #Create a display box 
    image_label.pack(pady=10)
    image = PhotoImage(data=image)              #Create a new image object; Note: PhotoImage widget only supports the GIF, PGM, PPM, and PNG file formats 
    image_label.config(root, image=image)       #Configure to display with image data 
    
    root.mainloop()                             #Generate an infinite loop to keep the application running

