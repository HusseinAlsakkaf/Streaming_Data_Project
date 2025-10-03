# api_test.py (Updated to use python-dotenv)

import os
import requests
from dotenv import load_dotenv  # <-- 1. IMPORT THE FUNCTION

load_dotenv()  # <-- 2. LOAD THE .env FILE

# --- From here on, everything is exactly the same! ---

# SECURELY GET API KEY
# os.getenv will now find the API_KEY loaded from your .env file.
API_KEY = os.getenv('API_KEY') # Note: The key in the .env file must match 'API_KEY'

# The base URL for The Guardian's content search endpoint.
BASE_URL = 'https://content.guardianapis.com/search'

def extract_msgs():
    """
    Makes a simple test call to the Guardian API to ensure the key is working.
    """
    if not API_KEY:
        print("ERROR: API_KEY not found in .env file or environment.")
        print("Please ensure your .env file is correctly set up.")
        return
    
    search_query = '"machine learning"'

    params = {
        'q': search_query,
        'page-size': 10,
        'api-key': API_KEY
    }

    print("Connecting to The Guardian API...")

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        print("Connection successful!")
        data = response.json()
        results_list = data['response']['results']

        if results_list:
            print(f"\n--- Found {len(results_list)} articles ---")
            for index, article in enumerate(results_list):
                print(f"{index + 1}. Title: {article['webTitle']}")
        else:
            print("API call was successful, but no articles were found.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if response.status_code == 401:
            print("Authentication failed. Please check your API key.")
    except Exception as err:
        print(f"An other error occurred: {err}")


if __name__ == "__main__":
    extract_msgs()