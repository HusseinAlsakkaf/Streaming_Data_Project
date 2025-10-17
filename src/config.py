# src/config.py ( for both local and Lambda environment configuration)

import os
from dotenv import load_dotenv

# This will load the .env file ONLY when running locally  with Lambda, it does nothing

load_dotenv()

# --- Guardian API Configuration ---
# On Lambda, this will be set as an environment variable by Terraform from terraform.tfvars
# Locally, it will be loaded from the .env file.
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://content.guardianapis.com/search"

# --- AWS Configuration ---
# These will also be set by Terraform on Lambda environment
AWS_REGION = os.getenv(
    "AWS_REGION", "eu-west-2"
)  # Default to eu-west-2 ( hard coded unless provided otherwise)
KINESIS_STREAM_NAME = os.getenv(
    "KINESIS_STREAM_NAME", "guardian_content"
)  # Default to guardian_content ( set in main.tf)

if not API_KEY:
    raise ValueError(
        "API_KEY not found. Please set it in your .env file or Lambda environment variables."
    )
