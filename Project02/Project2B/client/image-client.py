#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMP216 - SEC 401
Networking for Software Developers - Lab 5 Part II
Group 2: 
    Aiko Bislig 
    Jacob Ferreira
    Lissette Gorrin Rodriguez
    Samer Aljundi Al Fattouhi Aljundi
    Wardatul Keskin
Client side GUI
"""
import threading
import queue
import tkinter as tk
from tkinter import  ttk, filedialog, messagebox, scrolledtext
import requests
import os
import io
from PIL import Image, ImageTk
import json

class ImageClient:
    def __init__(self, server_url='http://127.0.0.1:5000'):
        self.server_url = server_url
        self.image_list = []
        self.current_image = None
        self.current_image_data = None
        self.task_queue = queue.Queue()
        self.running = True
        
        # Setup main window
        self.root = tk.Tk()
        self.root.title("Multithreaded Image Client")
        self.root.geometry("950x650")
        self.root.minsize(950, 650)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_widgets()
        self.start_worker_thread()
        self.fetch_image_list()

    def create_widgets(self):
        """Create the GUI widgets with activity log for session info"""
        # Create a main frame to hold everything
        main_frame = ttk.Frame(self.root)  # Changed to ttk.Frame
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frame for controls
        control_frame = ttk.Frame(main_frame, padding=10)  # Changed to ttk.Frame
        control_frame.pack(fill=tk.X)
        
        # Create dropdown for image selection
        ttk.Label(control_frame, text="Select Image:").grid(row=0, column=0, padx=5, pady=5)
        
        self.image_var = tk.StringVar()
        self.image_dropdown = ttk.Combobox(control_frame, textvariable=self.image_var, state="readonly", width=30)  # Changed to ttk.Combobox
        self.image_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.image_dropdown.bind("<<ComboboxSelected>>", self.on_image_selected)
        
        # Create buttons
        self.refresh_button = ttk.Button(control_frame, text="Refresh List", command=self.fetch_image_list)  # Changed to ttk.Button
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.upload_button = ttk.Button(control_frame, text="Upload Image", command=self.upload_image)  # Changed to ttk.Button
        self.upload_button.grid(row=0, column=3, padx=5, pady=5)
        
        self.delete_button = ttk.Button(control_frame, text="Delete Image", command=self.delete_image, state=tk.DISABLED)  # Changed to ttk.Button
        self.delete_button.grid(row=0, column=4, padx=5, pady=5)
        
        self.session_button = ttk.Button(control_frame, text="Session Info", command=self.show_session_info)  # Changed to ttk.Button
        self.session_button.grid(row=0, column=8, padx=5, pady=5)
        
        # Create right panel (for image and activity log)
        right_panel = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)  # Changed to ttk.PanedWindow
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create frame for image display
        self.image_frame = ttk.Frame(right_panel, padding=10)  # Changed to ttk.Frame
        right_panel.add(self.image_frame, weight=3)
        
        # Create canvas for image display (remains tk.Canvas)
        self.canvas = tk.Canvas(self.image_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create frame for image properties
        self.properties_frame = ttk.LabelFrame(main_frame, text="Image Properties", padding=10)  # Changed to ttk.LabelFrame
        self.properties_frame.pack(fill=tk.X, pady=10)
        
        # Create labels for image properties
        self.format_label = ttk.Label(self.properties_frame, text="Format: ")  # Changed to ttk.Label
        self.format_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.size_label = ttk.Label(self.properties_frame, text="Size: ")  # Changed to ttk.Label
        self.size_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.mode_label = ttk.Label(self.properties_frame, text="Mode: ")  # Changed to ttk.Label
        self.mode_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.date_label = ttk.Label(self.properties_frame, text="Date Modified: ")  # Changed to ttk.Label
        self.date_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)  # Changed to ttk.Label
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Format selection
        ttk.Label(control_frame, text="Format:").grid(row=0, column=5)
        self.format_var = tk.StringVar(value="PNG")
        self.format_dropdown = ttk.Combobox(  # Changed to ttk.Combobox
            control_frame, 
            textvariable=self.format_var, 
            values=["PNG", "JPEG", "GIF", "BMP"], 
            state="readonly"
        )
        self.format_dropdown.grid(row=0, column=6)
        
        # Download button
        self.download_button = ttk.Button(  # Changed to ttk.Button
            control_frame, 
            text="Download", 
            command=self.download_image,
            state=tk.DISABLED
        )
        self.download_button.grid(row=0, column=7)

        # Add thread-safe status updates
        self.root.after(100, self.process_queue)

    def download_image(self):
        selected_image = self.image_var.get()
        if not selected_image:
            return
        
        req_format = self.format_var.get().lower()
        save_path = filedialog.asksaveasfilename(
            defaultextension=f".{req_format}",
            filetypes=[(f"{req_format.upper()} files", f"*.{req_format}")],
            initialfile=f"{os.path.splitext(selected_image)[0]}.{req_format}"
        )
        
        if save_path:
            try:
                response = requests.get(
                    f"{self.server_url}/get-image/{selected_image}?format={req_format}",
                    stream=True
                )
                
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(8192):
                            f.write(chunk)
                    messagebox.showinfo("Success", f"Image saved as {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Download failed: {str(e)}")
    def clear_property_labels(self):
        self.format_label['text'] = "Format: "
        self.size_label['text'] = "Size: "
        self.mode_label['text'] = "Mode: "
        self.date_label['text'] = "Date Modified: "
        
    def on_image_selected(self, event=None):
        selected_image = self.image_var.get()
        if selected_image:
            self.delete_button['state'] = tk.NORMAL
            self.download_button['state'] = tk.NORMAL  # Enable download
            self.fetch_and_display_image(selected_image)
    def show_session_info(self):
        """Display current session information from the server"""
        try:
            # Fetch session info from server
            response = requests.get(f"{self.server_url}/session-info")
            
            if response.status_code == 200:
                session_data = response.json()
                info_window = tk.Toplevel(self.root)
                info_window.title("Session Information")
                
                # Create labels for session info
                tk.Label(info_window, text=f"Session ID: {session_data['session_id']}").pack(padx=10, pady=5)
                tk.Label(info_window, text=f"Created: {session_data['session_created']}").pack(padx=10, pady=5)
                tk.Label(info_window, text=f"Last Activity: {session_data['last_activity']}").pack(padx=10, pady=5)
                tk.Label(info_window, text=f"Client IP: {session_data['client_ip']}").pack(padx=10, pady=5)
                
                # Add close button
                tk.Button(info_window, text="Close", command=info_window.destroy).pack(pady=10)
            else:
                messagebox.showerror("Error", f"Failed to get session info: {response.text}")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server: {str(e)}")
    def start_worker_thread(self):
        def worker():
            while self.running:
                try:
                    task = self.task_queue.get(timeout=0.1)
                    task()
                except queue.Empty:
                    continue
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()

    def queue_task(self, task):
        self.task_queue.put(task)

    def process_queue(self):
        while not self.task_queue.empty():
            task = self.task_queue.get()
            task()
        self.root.after(100, self.process_queue)

    def thread_safe_update(func):
        def wrapper(self, *args, **kwargs):
            self.queue_task(lambda: func(self, *args, **kwargs))
        return wrapper

    def fetch_image_list(self):
        self.queue_task(self._fetch_image_list_task)

    @thread_safe_update
    def _fetch_image_list_task(self):
        try:
            self.status_var.set("Fetching image list...")
            response = requests.get(f"{self.server_url}/image-list")
            
            if response.status_code == 200:
                data = response.json()
                self.image_list = data.get('images', [])
                self.image_dropdown['values'] = self.image_list
                status = f"Found {len(self.image_list)} images" if self.image_list else "No images found"
                self.status_var.set(status)
            else:
                self.status_var.set(f"Error: {response.status_code}")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Connection Error", str(e))

    def fetch_and_display_image(self, filename):
        self.queue_task(lambda: self._fetch_image_task(filename))

    def _fetch_image_task(self, filename):
        try:
            self.status_var.set(f"Fetching: {filename}")
            response = requests.get(f"{self.server_url}/get-image/{filename}", stream=True)
            
            if response.status_code == 200:
                image_data = response.content
                self.root.after(0, self._update_image_display, image_data, response.headers)
            else:
                self.status_var.set(f"Error: {response.status_code}")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Fetch Error", str(e))

    def _update_image_display(self, image_data, headers):
        try:
            self.current_image_data = image_data
            img = Image.open(io.BytesIO(image_data))
            
            # Update properties from headers
            self.format_label['text'] = f"Format: {headers.get('X-Image-Format', 'Unknown')}"
            self.size_label['text'] = f"Size: {headers.get('X-Image-Size', 'Unknown')}"
            self.mode_label['text'] = f"Mode: {headers.get('X-Image-Mode', 'Unknown')}"
            self.date_label['text'] = f"Date: {headers.get('X-Image-Date_modified', 'Unknown')}"
            
            self.display_image(img)
            self.status_var.set(f"Displayed: {self.image_var.get()}")
        except Exception as e:
            messagebox.showerror("Display Error", str(e))

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            self.queue_task(lambda: self._upload_task(file_path))

    def _upload_task(self, file_path):
        try:
            self.status_var.set("Uploading...")
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                response = requests.post(f"{self.server_url}/uploads", files=files)
                
            if response.status_code == 200:
                data = response.json()
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", f"Uploaded: {data.get('filename')}"))
                self.fetch_image_list()
            else:
                self.status_var.set(f"Upload failed: {response.text}")
        except Exception as e:
            messagebox.showerror("Upload Error", str(e))

    def delete_image(self):
        if messagebox.askyesno("Confirm", "Delete selected image?"):
            filename = self.image_var.get()
            self.queue_task(lambda: self._delete_task(filename))

    def _delete_task(self, filename):
        try:
            response = requests.delete(f"{self.server_url}/delete-image/{filename}")
            if response.status_code == 200:
                self.root.after(0, self._post_delete_cleanup)
                self.fetch_image_list()
            else:
                self.status_var.set(f"Delete failed: {response.text}")
        except Exception as e:
            messagebox.showerror("Delete Error", str(e))

    def _post_delete_cleanup(self):
        self.image_dropdown['values'] = self.image_list
        self.image_var.set("")
        self.canvas.delete("all")
        self.current_image = None
        self.clear_property_labels()
        self.delete_button['state'] = tk.DISABLED
        self.download_button['state'] = tk.DISABLED

    def on_close(self):
        self.running = False
        self.root.destroy()
    def display_image(self, img):
        """Display the image on the canvas"""
        # Clear previous image
        self.canvas.delete("all")
        
        # Resize image to fit canvas while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas not yet properly sized
            self.root.update()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
        
        img_width, img_height = img.size
        
        # Calculate scaling factor
        width_ratio = canvas_width / img_width
        height_ratio = canvas_height / img_height
        scale_factor = min(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        
        # Resize image
        if new_width > 0 and new_height > 0:
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Keep a reference to prevent garbage collection
        self.current_image = photo
        
        # Calculate position to center the image
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        # Display image
        self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
    def clear_property_labels(self):
        self.format_label['text'] = "Format: "
        self.size_label['text'] = "Size: "
        self.mode_label['text'] = "Mode: "
        self.date_label['text'] = "Date Modified: "
    def on_image_selected(self, event=None):
        selected_image = self.image_var.get()
        if selected_image:
            self.delete_button['state'] = tk.NORMAL
            self.download_button['state'] = tk.NORMAL  # Enable download
            self.fetch_and_display_image(selected_image)
        

    # [Keep existing display_image, clear_property_labels, and other GUI methods]
    def run(self):
        self.root.deiconify()

        """Run the client application"""
        # Setup window resize event
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Start mainloop
        self.root.mainloop()
    
    def on_window_resize(self, event=None):
        """Handle window resize event"""
        # Only process events from the root window
        if event.widget == self.root and self.current_image_data:
            # Reload and display the current image
            img = Image.open(io.BytesIO(self.current_image_data))
            self.display_image(img)

if __name__ == "__main__":
    client = ImageClient()
    client.run()