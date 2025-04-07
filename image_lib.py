import ctypes
import os
from PIL import Image

def set_desktop_background_image(image_path):
    """Sets the desktop wallpaper (Windows only)."""
    if os.name == "nt":  # Windows
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    else:
        print("Wallpaper setting is only supported on Windows.")

def save_image(image_data, file_path):
    """Saves image data to a file."""
    with open(file_path, 'wb') as f:
        f.write(image_data)

def open_image(file_path):
    """Opens an image using PIL."""
    img = Image.open(file_path)
    img.show()
