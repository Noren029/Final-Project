import os
import sys
import re
import hashlib
import sqlite3
import requests
from datetime import datetime, date
from PIL import Image
from io import BytesIO
import platform
import ctypes

# NASA API Key 
API_KEY = 'yKp2aWaDVrsa6oONdv4Bh8ZTtQRxIfWdGG3ssjei'

# Image cache path
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'apod_cache')
DB_PATH = os.path.join(CACHE_DIR, 'apod_cache.db')


def validate_date(apod_date_str):
    try:
        apod_date = datetime.strptime(apod_date_str, "%Y-%m-%d").date()
        if apod_date < date(1995, 6, 16):
            raise ValueError("Date cannot be before 1995-06-16.")
        if apod_date > date.today():
            raise ValueError("Date cannot be in the future.")
        return apod_date
    except ValueError as e:
        print(f"Invalid date: {e}")
        sys.exit(1)


def init_cache():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        print(f" Created image cache directory: {CACHE_DIR}")
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS apod_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        explanation TEXT,
                        file_path TEXT,
                        sha256 TEXT UNIQUE
                    )''')
        conn.commit()
        conn.close()
        print(f" Created database at: {DB_PATH}")


def get_apod_info(apod_date):
    print(f" Getting APOD for {apod_date} from NASA API...")
    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': API_KEY,
        'date': apod_date.isoformat(),
        'thumbs': True
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] API request failed: {response.text}")
        sys.exit(1)


def download_image(url):
    print(f" Downloading image from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("[ERROR] Failed to download image.")
        return None


def get_image_filename(title, url):
    ext = os.path.splitext(url)[1]
    clean_title = re.sub(r'[^A-Za-z0-9_]', '', title.replace(' ', '_').strip())
    return f"{clean_title}{ext}"


def save_image(image_data, title, url):
    hash_val = hashlib.sha256(image_data).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM apod_cache WHERE sha256 = ?", (hash_val,))
    if c.fetchone():
        print(" Image already exists in cache.")
        conn.close()
        return None

    filename = get_image_filename(title, url)
    full_path = os.path.join(CACHE_DIR, filename)

    with open(full_path, 'wb') as f:
        f.write(image_data)

    print(f" Saved image to: {full_path}")

    c.execute("INSERT INTO apod_cache (title, explanation, file_path, sha256) VALUES (?, ?, ?, ?)",
              (title, apod_data['explanation'], full_path, hash_val))
    conn.commit()
    conn.close()
    print(" Added image info to database.")

    return full_path


def set_desktop_background(image_path):
    if platform.system() == "Windows":
        print(f" Setting desktop background to {image_path}")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)


if __name__ == '__main__':
    #  Parse date from command-line or use today
    apod_date = date.today()
    if len(sys.argv) > 1:
        apod_date = validate_date(sys.argv[1])
    else:
        print(f" No date provided, using today's date: {apod_date}")

    # Initialize cache and DB
    init_cache()

    #  Fetch APOD info
    apod_data = get_apod_info(apod_date)

    print(f" Title: {apod_data['title']}")
    print(f" Explanation: {apod_data['explanation']}")

    #   Get image URL
    if apod_data['media_type'] == 'image':
        image_url = apod_data['hdurl'] if 'hdurl' in apod_data else apod_data['url']
    elif apod_data['media_type'] == 'video':
        image_url = apod_data['thumbnail_url']
    else:
        print("[ERROR] Unsupported media type.")
        sys.exit(1)

    print(f" Image URL: {image_url}")

    # Download and save image
    image_data = download_image(image_url)
    if image_data:
        saved_path = save_image(image_data, apod_data['title'], image_url)
        if saved_path:
            set_desktop_background(saved_path)