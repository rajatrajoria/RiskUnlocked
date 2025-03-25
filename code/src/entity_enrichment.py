import requests

GLEIF_API = "https://api.gleif.org/api/v1"

def query_gleif(entity_name):
    """Fetches entity details from the GLEIF database."""
    params = {"filter[entity.legalName]": entity_name}
    url = f"{GLEIF_API}/lei-records"
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        gleif_data = response.json().get("data", [])
        return gleif_data[0] if gleif_data else {}
    return {}

def map_iso3166_country(country_code):
    """Fetch country name from ISO 3166 using GLEIF API."""
    url = f"{GLEIF_API}/countries/{country_code}"
    response = requests.get(url)

    if response.status_code == 200:
        gleif_data = response.json().get("data", [])
        return gleif_data if gleif_data else country_code
    return country_code