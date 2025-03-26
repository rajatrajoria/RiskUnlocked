import requests
import json
from fuzzywuzzy import process

SEC_COMPANY_DB_URL = "https://www.sec.gov/files/company_tickers.json"

def get_cik_by_name(company_name):
    """
    Fetches the best-matching CIK for a given company name.

    :param company_name: The name of the company to search for.
    :return: A tuple (Company Name, CIK) or None if not found.
    """
    headers = {"User-Agent": "your@email.com"}  # SEC requires a valid User-Agent

    try:
        response = requests.get(SEC_COMPANY_DB_URL, headers=headers)

        if response.status_code != 200:
            print(f"SEC API error: {response.status_code}")
            return None

        data = response.json()
        companies = {c["title"]: str(c["cik_str"]).zfill(10) for c in data.values()}

        # Use fuzzy matching to get the closest company name
        best_match, score = process.extractOne(company_name, companies.keys())

        if score > 80:  # Only return if match confidence is high
            return best_match, companies[best_match]
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from SEC: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    
def get_sector(cik):
    cik = str(cik).zfill(10)  # Ensure CIK is 10 digits
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": "your@email.com"}  # SEC requires this format

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"SEC API error: {response.status_code}")
            return None

        data = response.json()

        # Debugging: Print response keys if sicDescription is missing
        if "sicDescription" not in data:
            print("Unexpected response structure:", data.keys())
            return "Unknown"
        return data["sicDescription"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from SEC: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
def getSectors(companies, entity_types):
    obj={}
    for company, entity_type in zip(companies, entity_types):
        if entity_type.lower() not in ["individual", "pep"]:  # Exclude individuals and PEPs
            ciks = get_cik_by_name(company)
            sector = get_sector(ciks[1])
            obj[company] = sector
    return obj