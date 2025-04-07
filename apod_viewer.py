import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import apod_desktop

# Initialize APOD cache
apod_desktop.init_apod_cache()

# Create the main window
root = tk.Tk()
root.title("NASA APOD Viewer")
root.geometry("800x600")

# Frame for date input
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Enter APOD Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)
date_entry = tk.Entry(frame_top)
date_entry.pack(side=tk.LEFT, padx=5)
fetch_button = tk.Button(frame_top, text="Fetch APOD", command=lambda: fetch_apod())
fetch_button.pack(side=tk.LEFT, padx=5)

# Frame for APOD image
frame_image = tk.Frame(root)
frame_image.pack(pady=10)

apod_image_label = tk.Label(frame_image)
apod_image_label.pack()

# Frame for APOD info
frame_info = tk.Frame(root)
frame_info.pack(pady=10)

apod_title_label = tk.Label(frame_info, text="", font=("Arial", 14, "bold"))
apod_title_label.pack()
apod_explanation_label = tk.Label(frame_info, text="", wraplength=600, justify="left")
apod_explanation_label.pack()

# Buttons to set as wallpaper and view cached images
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

set_wallpaper_button = tk.Button(frame_buttons, text="Set as Wallpaper", command=lambda: set_as_wallpaper())
set_wallpaper_button.pack(side=tk.LEFT, padx=5)

view_cache_button = tk.Button(frame_buttons, text="View Cached APODs", command=lambda: show_cached_apods())
view_cache_button.pack(side=tk.LEFT, padx=5)

# Function to fetch and display APOD
def fetch_apod():
    apod_date = date_entry.get().strip()
    if not apod_date:
        messagebox.showerror("Error", "Please enter a valid date (YYYY-MM-DD)")
        return

    apod_id = apod_desktop.add_apod_to_cache(apod_date)
    if apod_id == 0:
        messagebox.showerror("Error", "Failed to fetch APOD.")
        return

    display_apod(apod_id)

# Function to display APOD image and info
def display_apod(apod_id):
    apod_info = apod_desktop.get_apod_info(apod_id)
    if not apod_info:
        messagebox.showerror("Error", "No APOD information found.")
        return

    file_path = apod_info['file_path']
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "Image file not found.")
        return

    img = Image.open(file_path)
    img.thumbnail((500, 500))
    img = ImageTk.PhotoImage(img)

    apod_image_label.config(image=img)
    apod_image_label.image = img

    apod_title_label.config(text=apod_info['title'])
    apod_explanation_label.config(text=apod_info['explanation'])

# Function to set wallpaper
def set_as_wallpaper():
    apod_id = apod_desktop.get_apod_id_from_db(date_entry.get().strip())
    if apod_id:
        apod_info = apod_desktop.get_apod_info(apod_id)
        apod_desktop.image_lib.set_desktop_background_image(apod_info['file_path'])
        messagebox.showinfo("Success", "Wallpaper updated!")
    else:
        messagebox.showerror("Error", "No APOD selected.")

# Function to display cached APODs
def show_cached_apods():
    cached_apods = apod_desktop.get_all_apod_titles()
    if not cached_apods:
        messagebox.showinfo("No Cache", "No cached APODs found.")
        return

    top = tk.Toplevel(root)
    top.title("Cached APODs")
    top.geometry("400x300")

    listbox = tk.Listbox(top)
    for title in cached_apods:
        listbox.insert(tk.END, title)
    listbox.pack(fill=tk.BOTH, expand=True)

# Run the Tkinter main loop
root.mainloop()
