import os
import sqlite3
import hashlib
import requests
import re
from datetime import date
import sys
from PIL import Image
import image_lib

# NASA APOD API Key (Replace with your own key)
API_KEY = "DEMO_KEY"

# Full paths of the image cache folder and database
script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')
image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

def main():
    """Main function to fetch and cache APOD image."""
    apod_date = get_apod_date()
    init_apod_cache()
    apod_id = add_apod_to_cache(apod_date)
    apod_info = get_apod_info(apod_id)

    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Get the APOD date from the command line or use today's date."""
    if len(sys.argv) > 1:
        try:
            return date.fromisoformat(sys.argv[1])
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            sys.exit(1)
    return date.today()

def init_apod_cache():
    """Initialize the image cache directory and database."""
    os.makedirs(image_cache_dir, exist_ok=True)
    conn = sqlite3.connect(image_cache_db)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apod_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            explanation TEXT,
            file_path TEXT,
            sha256 TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def add_apod_to_cache(apod_date):
    """Download and cache APOD image from NASA API."""
    apod_data = fetch_apod_data(apod_date)
    if not apod_data:
        return 0

    image_url = apod_data['url']
    image_title = apod_data['title']
    explanation = apod_data['explanation']

    file_path = determine_apod_file_path(image_title, image_url)
    image_data = download_image(image_url)

    if not image_data:
        return 0

    sha256_hash = hashlib.sha256(image_data).hexdigest()
    existing_id = get_apod_id_from_db(sha256_hash)
    if existing_id:
        print("APOD already in cache.")
        return existing_id

    with open(file_path, 'wb') as f:
        f.write(image_data)

    return add_apod_to_db(image_title, explanation, file_path, sha256_hash)

def fetch_apod_data(apod_date):
    """Fetch APOD metadata from NASA API."""
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={apod_date}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("media_type") == "image":
            return data
        else:
            print("APOD is not an image.")
    else:
        print("Failed to fetch APOD data.")
    return None

def download_image(url):
    """Download image from a given URL."""
    response = requests.get(url, stream=True)
    return response.content if response.status_code == 200 else None

def determine_apod_file_path(image_title, image_url):
    """Generate a sanitized file path for saving APOD image."""
    ext = os.path.splitext(image_url)[-1]
    sanitized_title = re.sub(r'\W+', '_', image_title.strip())
    return os.path.join(image_cache_dir, sanitized_title + ext)

def add_apod_to_db(title, explanation, file_path, sha256):
    """Store APOD metadata in the database."""
    conn = sqlite3.connect(image_cache_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO apod_cache (title, explanation, file_path, sha256) VALUES (?, ?, ?, ?)",
                   (title, explanation, file_path, sha256))
    conn.commit()
    apod_id = cursor.lastrowid
    conn.close()
    return apod_id

def get_apod_id_from_db(image_sha256):
    """Check if APOD image exists in cache by SHA-256."""
    conn = sqlite3.connect(image_cache_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM apod_cache WHERE sha256 = ?", (image_sha256,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def get_apod_info(image_id):
    """Retrieve APOD metadata from the database."""
    conn = sqlite3.connect(image_cache_db)
    cursor = conn.cursor()
    cursor.execute("SELECT title, explanation, file_path FROM apod_cache WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    conn.close()
    return {'title': row[0], 'explanation': row[1], 'file_path': row[2]} if row else {}

if __name__ == '__main__':
    main()
