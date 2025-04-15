from tkinter import *
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import datetime
import os
import apod_desktop

# --- Constants ---
DEFAULT_IMAGE_PATH = 'default.jpg'
ICON_PATH = 'apod_icon.ico'
MIN_DATE = datetime.date(1995, 6, 16)
TODAY = datetime.date.today()

# --- App Setup ---
apod_desktop.init_apod_cache()
root = Tk()
root.title("NASA APOD Viewer")
root.geometry("800x600")
root.iconbitmap(ICON_PATH)
root.minsize(600, 400)

# --- GUI Layout ---
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

top_frame = Frame(main_frame)
top_frame.pack(fill=X)

bottom_frame = Frame(main_frame)
bottom_frame.pack(fill=BOTH, expand=True)

# --- Widgets ---
# Date picker
date_label = Label(top_frame, text="Select Date:")
date_label.pack(side=LEFT)

date_picker = DateEntry(top_frame, mindate=MIN_DATE, maxdate=TODAY, width=12)
date_picker.pack(side=LEFT, padx=5)

def download_apod():
    selected_date = date_picker.get_date()
    try:
        apod_info = apod_desktop.download_apod(selected_date.strftime("%Y-%m-%d"))
        update_display(apod_info)
        update_cached_list()
    except Exception as e:
        messagebox.showerror("Download Error", str(e))

download_btn = Button(top_frame, text="Download APOD", command=download_apod)
download_btn.pack(side=LEFT, padx=5)

# Cached APOD Listbox
cache_frame = Frame(bottom_frame)
cache_frame.pack(side=LEFT, fill=Y, padx=(0, 10))

cached_listbox = Listbox(cache_frame, width=30)
cached_listbox.pack(side=LEFT, fill=Y)

def update_cached_list():
    cached_listbox.delete(0, END)
    for apod in apod_desktop.get_all_cached_apods():
        cached_listbox.insert(END, apod['title'])

def on_select_apod(event):
    selection = cached_listbox.curselection()
    if selection:
        title = cached_listbox.get(selection[0])
        apod_info = apod_desktop.get_apod_by_title(title)
        update_display(apod_info)

cached_listbox.bind('<<ListboxSelect>>', on_select_apod)

# Image & Explanation Display
display_frame = Frame(bottom_frame)
display_frame.pack(side=LEFT, fill=BOTH, expand=True)

image_label = Label(display_frame)
image_label.pack(pady=5)

explanation_text = Text(display_frame, wrap=WORD, height=10)
explanation_text.pack(fill=BOTH, expand=True)

def update_display(apod_info):
    img_path = apod_info['file_path']
    img = Image.open(img_path)
    img = img.resize((400, 300), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(img)
    image_label.config(image=tk_img)
    image_label.image = tk_img  # Prevent garbage collection

    explanation_text.delete(1.0, END)
    explanation_text.insert(END, apod_info['explanation'])

def set_as_wallpaper():
    if hasattr(image_label, 'image'):
        apod_info = apod_desktop.get_apod_by_title(cached_listbox.get(ACTIVE))
        apod_desktop.set_desktop_background(apod_info['file_path'])
        messagebox.showinfo("Success", "Wallpaper set!")
    else:
        messagebox.showwarning("No Image", "No APOD selected to set as wallpaper.")

wallpaper_btn = Button(top_frame, text="Set as Wallpaper", command=set_as_wallpaper)
wallpaper_btn.pack(side=LEFT, padx=5)

# --- Default Image ---
if os.path.exists(DEFAULT_IMAGE_PATH):
    default_info = {
        'file_path': DEFAULT_IMAGE_PATH,
        'explanation': "Please select a date or cached APOD to begin."
    }
    update_display(default_info)

update_cached_list()

# --- Mainloop ---
root.mainloop()
