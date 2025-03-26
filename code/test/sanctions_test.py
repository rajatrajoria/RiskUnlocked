import pytest
import requests
import json
from unittest.mock import patch, MagicMock
from src.sanctions import (
    screen_entities_ofac,
    screen_entities_openSanctionsAPI,
    risk_analysis_llm,
    getSanctionReports,
)


# ========================== TEST OFAC SCREENING ==========================

@patch("main.requests.post")
def test_screen_entities_ofac_success(mock_post):
    mock_response = {
        "cases": [
            {"name": "Al-Qaeda", "type": "organization", "matched": True, "score": 98}
        ]
    }
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response

    cases = [{"name": "Al-Qaeda", "type": "organization"}]
    result = screen_entities_ofac(cases)
    assert result == mock_response


@patch("main.requests.post")
def test_screen_entities_ofac_api_error(mock_post):
    mock_post.return_value.status_code = 500
    mock_post.return_value.text = "Internal Server Error"

    cases = [{"name": "Al-Qaeda", "type": "organization"}]
    result = screen_entities_ofac(cases)
    assert result is None


@patch("main.requests.post")
def test_screen_entities_ofac_exception(mock_post):
    mock_post.side_effect = Exception("API request failed")

    cases = [{"name": "Al-Qaeda", "type": "organization"}]
    result = screen_entities_ofac(cases)
    assert result is None


# ========================== TEST OPENSANCTIONS SCREENING ==========================

@patch("main.requests.post")
def test_screen_entities_openSanctionsAPI_success(mock_post):
    mock_response = {
        "responses": {
            "q1": {"results": [{"name": "Al-Qaeda", "type": "Sanctioned Entity"}]},
            "q2": {"results": []},
        }
    }
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response

    cases = [
        {"name": "Al-Qaeda", "type": "organization"},
        {"name": "John Doe", "type": "person"},
    ]
    result = screen_entities_openSanctionsAPI(cases)
    assert result == {
        "Al-Qaeda": [{"name": "Al-Qaeda", "type": "Sanctioned Entity"}],
        "John Doe": [],
    }


@patch("main.requests.post")
def test_screen_entities_openSanctionsAPI_api_error(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"

    cases = [{"name": "Al-Qaeda", "type": "organization"}]
    result = screen_entities_openSanctionsAPI(cases)
    assert result is None


@patch("main.requests.post")
def test_screen_entities_openSanctionsAPI_exception(mock_post):
    mock_post.side_effect = Exception("API request failed")

    cases = [{"name": "Al-Qaeda", "type": "organization"}]
    result = screen_entities_openSanctionsAPI(cases)
    assert result is None


# ========================== TEST RISK ANALYSIS (LLM) ==========================

@patch("main.genai.GenerativeModel.generate_content")
@patch("main.genai.configure")
def test_risk_analysis_llm_success(mock_configure, mock_generate_content):
    mock_response = MagicMock()
    mock_response.text = "Risk analysis results"
    mock_generate_content.return_value = mock_response

    ofac_response = {"cases": [{"name": "Al-Qaeda", "type": "organization"}]}
    open_sanctions_response = {"Al-Qaeda": [{"name": "Al-Qaeda", "type": "Sanctioned Entity"}]}

    result = risk_analysis_llm(ofac_response, open_sanctions_response)
    assert result == "Risk analysis results"


@patch("main.genai.GenerativeModel.generate_content")
def test_risk_analysis_llm_no_response(mock_generate_content):
    mock_generate_content.return_value = None

    ofac_response = {"cases": [{"name": "Al-Qaeda", "type": "organization"}]}
    open_sanctions_response = {"Al-Qaeda": [{"name": "Al-Qaeda", "type": "Sanctioned Entity"}]}

    result = risk_analysis_llm(ofac_response, open_sanctions_response)
    assert result == "Error: No response from the model"


# ========================== TEST GET SANCTION REPORTS ==========================

@patch("main.screen_entities_ofac")
@patch("main.screen_entities_openSanctionsAPI")
@patch("main.risk_analysis_llm")
def test_getSanctionReports_success(mock_risk_analysis_llm, mock_openSanctionsAPI, mock_ofac):
    mock_ofac.return_value = {"cases": [{"name": "Al-Qaeda", "type": "organization"}]}
    mock_openSanctionsAPI.return_value = {"Al-Qaeda": [{"name": "Al-Qaeda", "type": "Sanctioned Entity"}]}
    mock_risk_analysis_llm.return_value = "Final Risk Analysis"

    cases = [{"name": "Al-Qaeda", "type": "organization"}]
    result = getSanctionReports(cases)
    assert result == "Final Risk Analysis"


@patch("main.screen_entities_ofac")
@patch("main.screen_entities_openSanctionsAPI")
def test_getSanctionReports_failure(mock_openSanctionsAPI, mock_ofac):
    mock_ofac.return_value = None
    mock_openSanctionsAPI.return_value = None

    cases = [{"name": "Al-Qaeda", "type": "organization"}]
    result = getSanctionReports(cases)
    assert "Error" in result or result is None
