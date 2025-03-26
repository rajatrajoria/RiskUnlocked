import pytest
from src.entity_enrichment import query_gleif, map_iso3166_country


# Mock requests.get to avoid real API calls
@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch("app.gleif_utils.requests.get")


# --- Tests for query_gleif ---
def test_query_gleif_success(mock_requests_get):
    """Test query_gleif when entity is found."""
    mock_response = mock_requests_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "id": "1234567890",
                "attributes": {
                    "entity": {
                        "legalName": {"name": "Fake Corp"},
                        "jurisdiction": "US",
                    }
                },
            }
        ]
    }

    result = query_gleif("Fake Corp")
    assert result["id"] == "1234567890"
    assert result["attributes"]["entity"]["legalName"]["name"] == "Fake Corp"
    assert result["attributes"]["entity"]["jurisdiction"] == "US"


def test_query_gleif_not_found(mock_requests_get):
    """Test query_gleif when no entity is found."""
    mock_response = mock_requests_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": []}

    result = query_gleif("Unknown Corp")
    assert result == {}


def test_query_gleif_api_error(mock_requests_get):
    """Test query_gleif when API returns an error."""
    mock_response = mock_requests_get.return_value
    mock_response.status_code = 500

    result = query_gleif("Error Corp")
    assert result == {}


# --- Tests for map_iso3166_country ---
def test_map_iso3166_country_found(mock_requests_get):
    """Test map_iso3166_country with a valid country code."""
    mock_response = mock_requests_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "countries",
            "attributes": {
                "name": "United States",
                "alpha2Code": "US",
            },
        }
    }

    result = map_iso3166_country("US")
    assert result["type"] == "countries"
    assert result["attributes"]["name"] == "United States"
    assert result["attributes"]["alpha2Code"] == "US"


def test_map_iso3166_country_not_found(mock_requests_get):
    """Test map_iso3166_country with an invalid country code."""
    mock_response = mock_requests_get.return_value
    mock_response.status_code = 404

    result = map_iso3166_country("XX")
    assert result == "XX"


def test_map_iso3166_country_api_error(mock_requests_get):
    """Test map_iso3166_country when API returns an error."""
    mock_response = mock_requests_get.return_value
    mock_response.status_code = 500

    result = map_iso3166_country("US")
    assert result == "US"
