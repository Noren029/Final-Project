import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from datetime import date, datetime
import sqlite3
import apod_desktop

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'apod_cache')
DEFAULT_IMAGE = os.path.join(os.path.dirname(__file__), 'nasa.png')
DB_PATH = os.path.join(CACHE_DIR, 'apod_cache.db')

class APODViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Astronomy Picture of the Day Viewer")
        self.root.geometry("1000x800")
        self.root.iconbitmap(DEFAULT_IMAGE)

        self.create_widgets()
        apod_desktop.init_cache()
        self.load_cached_titles()
        self.display_default_image()

    def create_widgets(self):
        self.image_label = tk.Label(self.root)
        self.image_label.pack(expand=True, fill="both")

        # Explanation Label for the APOD
        self.explanation_label = tk.Label(self.root, text="", wraplength=850, justify="left", anchor="w")
        self.explanation_label.pack(pady=10, padx=10, fill="both")

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", pady=10, padx=10)

        # View Cached Images
        left_frame = tk.LabelFrame(bottom_frame, text="View Cached Image")
        left_frame.pack(side="left", padx=5)

        tk.Label(left_frame, text="Select Image:").pack(side="left")
        self.image_combo = ttk.Combobox(left_frame, state="readonly", width=30)
        self.image_combo.pack(side="left", padx=5)
        self.image_combo.bind("<<ComboboxSelected>>", self.show_selected_image)

        self.set_btn = tk.Button(left_frame, text="Set as Desktop", command=self.set_as_desktop)
        self.set_btn.pack(side="left", padx=5)

        # Download New Image
        right_frame = tk.LabelFrame(bottom_frame, text="Get More Images")
        right_frame.pack(side="right", padx=5)

        tk.Label(right_frame, text="Select Date:").pack(side="left")
        self.date_entry = DateEntry(right_frame, maxdate=date.today(), mindate=date(1995, 6, 16), width=12, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side="left", padx=5)

        self.download_btn = tk.Button(right_frame, text="Download Image", command=self.download_apod)
        self.download_btn.pack(side="left")

    def display_default_image(self):
        self.display_image(DEFAULT_IMAGE)

    def display_image(self, image_path):
        try:
            print(f" Trying to display image: {image_path}")  # Debug line to check image path
            if not os.path.exists(image_path):
                messagebox.showerror("Error", f"Image file not found: {image_path}")
                return
            img = Image.open(image_path)
            img.thumbnail((850, 550))
            self.tk_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            print(f"[ERROR] Image load failed: {e}")

    def load_cached_titles(self):
        if not os.path.exists(DB_PATH):
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT title FROM apod_cache")
            titles = [row[0] for row in c.fetchall()]
            conn.close()

            print(f" Loaded cached titles: {titles}")  # Debug line to ensure titles are loaded correctly
            self.image_combo['values'] = titles  # Populate the combobox with the titles
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cached titles: {e}")
            print(f"[ERROR] DB load titles: {e}")

    def show_selected_image(self, event):
        title = self.image_combo.get()
        if not title:
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT file_path, explanation FROM apod_cache WHERE title = ?", (title,))
            row = c.fetchone()
            conn.close()
            if row:
                self.display_image(row[0])
                self.explanation_label.config(text=row[1])  # Display explanation from DB
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image from database: {e}")
            print(f"[ERROR] Show selected image: {e}")

    def set_as_desktop(self):
        title = self.image_combo.get()
        if not title:
            messagebox.showwarning("Warning", "Please select an image first.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT file_path FROM apod_cache WHERE title = ?", (title,))
            row = c.fetchone()
            conn.close()
            if row:
                apod_desktop.set_desktop_background(row[0])
                messagebox.showinfo("Success", "Desktop background updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set desktop background: {e}")
            print(f"[ERROR] Set desktop background: {e}")

    def download_apod(self):
        try:
            apod_date = self.date_entry.get_date()
            print(f" Selected date: {apod_date}")

            apod_data = apod_desktop.get_apod_info(apod_date)
            print(f" APOD data: {apod_data}")

            if not apod_data:
                messagebox.showerror("Error", "No APOD data found for this date.")
                return

            if apod_data.get('media_type') not in ['image', 'video']:
                messagebox.showerror("Error", "Unsupported media type.")
                return

            image_url = apod_data.get('hdurl') or apod_data.get('url') or apod_data.get('thumbnail_url')
            print(f" Image URL: {image_url}")

            if not image_url:
                messagebox.showerror("Error", "No image URL found.")
                return

            image_data = apod_desktop.download_image(image_url)
            print(f" Image data received: {bool(image_data)}")

            if image_data:
                path = apod_desktop.save_image(image_data, apod_data['title'], image_url)
                print(f" Image saved to: {path}")

                if path:
                    self.load_cached_titles()  # Reload cached titles
                    self.image_combo.set(apod_data['title'])  # Set the newly downloaded image title in the combo box
                    self.display_image(path)  # Display the newly downloaded image
                    self.explanation_label.config(text=apod_data.get('explanation', "No explanation available."))  # Display the explanation
            else:
                messagebox.showerror("Error", "Failed to download image data.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download or save APOD: {e}")
            print(f"[ERROR] Exception in download_apod: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = APODViewer(root)
    root.mainloop()
