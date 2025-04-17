'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''

import requests
from datetime import date

# Replace this with your actual API key from https://api.nasa.gov
API_KEY = 'yKp2aWaDVrsa6oONdv4Bh8ZTtQRxIfWdGG3ssjei'  

def main():
    # Test the module by fetching today's APOD
    apod_date = date.today().isoformat()
    print(f"Fetching APOD for {apod_date}...")
    apod_info = get_apod_info(apod_date)
    if apod_info:
        print("Title:", apod_info.get("title", "No Title"))
        print("Media Type:", apod_info.get("media_type", "N/A"))
        print("Image URL:", get_apod_image_url(apod_info))
    else:
        print("Failed to fetch APOD info.")

def get_apod_info(apod_date):
    """Gets information from the NASA API for the APOD of a given date."""
    url = "https://api.nasa.gov/planetary/apod"
    params = {
        'api_key': API_KEY,
        'date': apod_date,
        'thumbs': True  # Include thumbnail if it's a video
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching APOD info: {e}")
        return None

def get_apod_image_url(apod_info_dict):
    """Returns the image URL from the APOD info dict, handling both images and videos."""
    if apod_info_dict['media_type'] == 'image':
        return apod_info_dict.get('hdurl') or apod_info_dict.get('url')
    elif apod_info_dict['media_type'] == 'video':
        return apod_info_dict.get('thumbnail_url') or apod_info_dict.get('url')
    else:
        return None

if __name__ == '__main__':
    main()
