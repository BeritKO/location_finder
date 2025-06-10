"""
Get coordinates for locations from Google Maps using API or headless browser.

Usage: python location_finder.py
"""
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Add tqdm for progress bar
from tqdm import tqdm


# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def get_coordinates(location):
    """
    Get coordinates for a given location using Google Maps API.

    If API key is not set, use headless browser fallback.
    """
    # Check if API key is set, if not, use browser fallback
    if not API_KEY:
        return get_coordinates_via_browser(location)

    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location, "key": API_KEY}
    response = requests.get(endpoint, params=params)
    data = response.json()

    if data['status'] == 'OK':
        loc = data['results'][0]['geometry']['location']
        return loc['lat'], loc['lng'], f"https://www.google.com/maps/search/?api=1&query={loc['lat']},{loc['lng']}"
    else:
        print(f"API failed for '{location}', falling back to browser.")
        return get_coordinates_via_browser(location)


def get_coordinates_via_browser(location):
    """
    Fallback: Use headless browser to extract coordinates from Google Maps URL.
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        search_url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
        driver.get(search_url)

        # Wait for URL change and skip if more than 120 seconds have passed
        start_time = time.time()
        while driver.current_url == search_url:
            if time.time() - start_time > 120:
                print("Skipping due to timeout.")
                break
            time.sleep(1)


        # Wait for URL change and extract lat/lng from the URL
        current_url = driver.current_url
        driver.quit()

        if '/@' in current_url:
            coord_part = current_url.split('/@')[1].split(',')[0:2]
            lat = float(coord_part[0])
            lng = float(coord_part[1])
            return lat, lng, current_url
        else:
            print(f"Could not extract coordinates for '{location}' from URL.")
            return None, None, None
    except Exception as e:
        print(f"Browser fallback failed for '{location}': {e}")
        return None, None, None


def main():
    """
    Main function to read Excel and fetch coordinates.
    """
    excel_path = os.path.join("data", "locations.xlsx")
    df = pd.read_excel(excel_path)

    if 'Location' not in df.columns:
        raise ValueError("Excel file must have a 'Location' column.")

    df['Latitude'] = None
    df['Longitude'] = None
    df['Link'] = None

    output_path = os.path.join("data", "locations_with_coords.xlsx")

    try:
        # Use tqdm for progress bar with ETA
        for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing locations", unit="loc"):
            location = row['Location']
            lat, lng, location_url = get_coordinates(location)
            df.at[index, 'Latitude'] = lat
            df.at[index, 'Longitude'] = lng
            df.at[index, 'Link'] = location_url
            print(f"{location} → Lat: {lat}, Lng: {lng}")
    except Exception as e:
        print(f"\nException occurred: {e}")
        print("Saving progress before exiting...")
        df.to_excel(output_path, index=False)
        raise
    else:
        df.to_excel(output_path, index=False)
        print(f"\nCoordinates saved to: {output_path}")


if __name__ == "__main__":
    main()
