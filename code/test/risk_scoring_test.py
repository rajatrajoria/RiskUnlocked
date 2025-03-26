import pytest
import requests
from unittest.mock import patch
from src.risk_scoring import is_pep


# ✅ Mock successful PEP response
@patch("main.requests.get")
def test_is_pep_success(mock_get):
    mock_response = {
        "results": [
            {"id": "123", "name": "John Doe", "type": "PEP"}
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    assert is_pep("John Doe") is True


# ✅ Mock successful non-PEP response
@patch("main.requests.get")
def test_is_not_pep(mock_get):
    mock_response = {"results": []}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    assert is_pep("Alice Smith") is False


# ✅ Test API request failure (e.g., network error)
@patch("main.requests.get")
def test_is_pep_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    with pytest.raises(Exception, match="API request failed: Network error"):
        is_pep("John Doe")


# ✅ Test invalid JSON response
@patch("main.requests.get")
def test_is_pep_invalid_json(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

    with pytest.raises(Exception, match="Failed to parse JSON response"):
        is_pep("John Doe")


# ✅ Test API key is missing
@patch("main.requests.get")
def test_is_pep_missing_api_key(mock_get, monkeypatch):
    monkeypatch.delenv("OPENSANCTIONS_KEY", raising=False)

    with pytest.raises(Exception, match="API request failed"):
        is_pep("John Doe")


# ✅ Test API returns error (non-200 status code)
@patch("main.requests.get")
def test_is_pep_api_error(mock_get):
    mock_get.return_value.status_code = 403
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.RequestException("403 Forbidden")

    with pytest.raises(Exception, match="API request failed: 403 Forbidden"):
        is_pep("John Doe")
