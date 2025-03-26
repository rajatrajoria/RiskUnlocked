import os
from dotenv import load_dotenv
import requests

load_dotenv()

OPENSANCTIONS_API_KEY = os.getenv("OPENSANCTIONS_API_KEY")

def is_pep(name):
    """Use OpenSanctions API to check if a person is a Politically Exposed Person (PEP)"""
    url = "https://api.opensanctions.org/search/peps"
    params = {"q": name, "api_key": OPENSANCTIONS_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")
    except ValueError as e:
        raise Exception("Failed to parse JSON response")
    if "results" in data and data["results"]:
        return True
    else:
        return False