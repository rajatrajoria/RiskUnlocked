import pytest
from src.entity_classification import check_shell_company, classify_entity


# Mock the requests.post method to avoid making real API calls
@pytest.fixture
def mock_requests_post(mocker):
    return mocker.patch("app.entity_utils.requests.post")


# Mock the transformer pipeline
@pytest.fixture
def mock_pipeline(mocker):
    return mocker.patch("app.entity_utils.pipeline")


# --- Tests for check_shell_company ---
def test_check_shell_company_found(mock_requests_post):
    """Test check_shell_company when a shell company is found."""
    mock_response = mock_requests_post.return_value
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "q0": {
            "result": [
                {
                    "name": "Fake Shell Corp",
                    "score": 0.95,
                    "description": "Entity extracted from the Panama Papers.",
                }
            ]
        }
    }

    result, evidence = check_shell_company("Fake Shell Corp")
    assert result is True
    assert evidence == "Panama Papers"


def test_check_shell_company_not_found(mock_requests_post):
    """Test check_shell_company when no match is found."""
    mock_response = mock_requests_post.return_value
    mock_response.status_code = 201
    mock_response.json.return_value = {"q0": {"result": []}}

    result, evidence = check_shell_company("Legit Company")
    assert result is False
    assert evidence is None


def test_check_shell_company_request_exception(mock_requests_post):
    """Test check_shell_company when a request exception occurs."""
    mock_requests_post.side_effect = Exception("Request Error")

    result, evidence = check_shell_company("Error Company")
    assert result is False
    assert evidence is None


# --- Tests for classify_entity ---
def test_classify_entity_shell_company(mock_requests_post):
    """Test classify_entity when the entity is a shell company."""
    mock_response = mock_requests_post.return_value
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "q0": {
            "result": [
                {
                    "name": "Shell Corp",
                    "score": 0.95,
                    "description": "Entity extracted from the Paradise Papers.",
                }
            ]
        }
    }

    result = classify_entity("Shell Corp")
    assert result["label"] == "Shell Company"
    assert result["score"] == 0.95
    assert result["supporting_evidence"] == "Paradise Papers"


def test_classify_entity_normal_case(mock_requests_post, mock_pipeline):
    """Test classify_entity for a normal entity with NLP classification."""
    mock_requests_post.return_value.status_code = 201
    mock_requests_post.return_value.json.return_value = {"q0": {"result": []}}

    mock_classifier = mock_pipeline.return_value
    mock_classifier.return_value = {
        "sequence": "Legit Company",
        "labels": ["Corporation", "Non-Profit", "Shell Company", "Government Agency"],
        "scores": [0.85, 0.05, 0.03, 0.02],
    }

    result = classify_entity("Legit Company")
    assert result["label"] == "Corporation"
    assert result["score"] == 0.85
    assert result["supporting_evidence"] is None


def test_classify_entity_no_match(mock_requests_post, mock_pipeline):
    """Test classify_entity when no classification is matched."""
    mock_requests_post.return_value.status_code = 201
    mock_requests_post.return_value.json.return_value = {"q0": {"result": []}}

    mock_classifier = mock_pipeline.return_value
    mock_classifier.return_value = {
        "sequence": "Unknown Entity",
        "labels": ["Corporation", "Non-Profit", "Shell Company", "Government Agency"],
        "scores": [0.0, 0.0, 0.0, 0.0],
    }

    result = classify_entity("Unknown Entity")
    assert result["label"] == "Corporation"  # Defaults to the first label
    assert result["score"] == 0.0
    assert result["supporting_evidence"] is None
