'''
Library of useful functions for working with images.
'''
import requests
import hashlib
import os
import platform
import ctypes
from pathlib import Path

def main():
    # Basic test to download an image and save it
    test_url = 'GET https://api.nasa.gov/planetary/apod'
    print("Downloading test image...")
    image_data = download_image(test_url)
    if image_data:
        test_path = os.path.join(Path.home(), 'apod_test.jpg')
        if save_image_file(image_data, test_path):
            print(f"Image saved to: {test_path}")
            print("Setting as wallpaper...")
            if set_desktop_background_image(test_path):
                print("Wallpaper set successfully.")
            else:
                print("Failed to set wallpaper.")
        else:
            print("Failed to save image.")
    else:
        print("Failed to download image.")

def download_image(image_url):
    """Downloads an image from a specified URL.
    Returns binary data, or None on failure.
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        return None

def save_image_file(image_data, image_path):
    """Saves binary image data to disk."""
    try:
        with open(image_path, 'wb') as file:
            file.write(image_data)
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

def set_desktop_background_image(image_path):
    """Sets the desktop background image."""
    system = platform.system()
    try:
        if system == 'Windows':
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            return True
        
        else:
            print("Unsupported OS.")
            return False
    except Exception as e:
        print(f"Error setting wallpaper: {e}")
        return False

def get_image_sha256(image_data):
    """Returns SHA-256 hash of binary image data."""
    return hashlib.sha256(image_data).hexdigest()

def scale_image(image_size, max_size=(800, 600)):
    """Calculates the dimensions of an image scaled to a maximum width and/or height while maintaining the aspect ratio."""
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()