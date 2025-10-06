# src/config.py

import os
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

# --- Guardian API Configuration ---
# Safely get the API key from the environment variables
API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://content.guardianapis.com/search'

# A basic check to ensure the API key is loaded.
if not API_KEY:
    raise ValueError("API_KEY not found. Please ensure it is set in your .env file.")