import pytest
from unittest.mock import patch
from src.process_transaction import process_transaction


@pytest.fixture
def mock_ner():
    """Mocked NER response for unstructured text."""
    return [
        {"entity_group": "ORG", "word": "ABC Corp", "score": 0.98},
        {"entity_group": "PER", "word": "John Doe", "score": 0.95}
    ]


@pytest.fixture
def sample_transaction():
    """Sample transaction with all fields."""
    return {
        "Transaction ID": "TX12345",
        "Payer Name": "John Doe",
        "Receiver Name": "XYZ Ltd",
        "Transaction Details": "Payment made to XYZ Ltd for services."
    }


@pytest.fixture
def text_transaction():
    """Sample unstructured transaction text."""
    return (
        "Transaction ID: TX56789\n"
        "Payer Name: \"Alice Smith\"\n"
        "Receiver Name: \"DEF Corp\"\n"
        "Transaction Details: Alice transferred funds to DEF Corp."
    )


@pytest.fixture
def empty_transaction():
    """Empty transaction with no details."""
    return {}


@pytest.fixture
def mock_classification():
    """Mocked classification response for entities."""
    return {
        "sequence": "XYZ Ltd",
        "label": "Corporate",
        "score": 0.97,
        "supporting_evidence": "GLEIF"
    }


@pytest.fixture
def mock_gleif_data():
    """Mocked GLEIF data."""
    return {
        "attributes": {
            "entity": {
                "legalAddress": {
                    "country": "US"
                }
            }
        }
    }


@pytest.fixture
def mock_iso_mapping():
    """Mocked ISO 3166 country mapping."""
    return {
        "attributes": {
            "name": "United States"
        }
    }


@pytest.fixture
def mock_pep():
    """Mocked PEP response."""
    return False


# ✅ Test with structured transaction data
@patch("main.pipeline")
@patch("main.merge_entities")
@patch("main.classify_entity")
@patch("main.query_gleif")
@patch("main.map_iso3166_country")
@patch("main.is_pep")
def test_process_structured_transaction(
    mock_is_pep, mock_iso_mapping, mock_gleif_data, mock_classification, mock_merge_entities, mock_ner, sample_transaction
):
    mock_ner.return_value = lambda *args, **kwargs: mock_ner
    mock_merge_entities.return_value = [("ABC Corp", "ORG"), ("John Doe", "PER")]
    mock_is_pep.return_value = False
    mock_classification.return_value = {
        "sequence": "XYZ Ltd",
        "label": "Corporate",
        "score": 0.97,
        "supporting_evidence": "GLEIF"
    }
    mock_gleif_data.return_value = mock_gleif_data
    mock_iso_mapping.return_value = mock_iso_mapping

    result = process_transaction(sample_transaction)

    assert result["Transaction ID"] == "TX12345"
    assert "John Doe" in result["Extracted Entity"]
    assert "XYZ Ltd" in result["Extracted Entity"]
    assert "Corporate" in result["Entity Type"]
    assert result["Confidence Score"] > 0
    assert "United States" in result["Countries"]


# ✅ Test with unstructured transaction data
@patch("main.pipeline")
@patch("main.merge_entities")
@patch("main.classify_entity")
@patch("main.query_gleif")
@patch("main.map_iso3166_country")
@patch("main.is_pep")
def test_process_unstructured_transaction(
    mock_is_pep, mock_iso_mapping, mock_gleif_data, mock_classification, mock_merge_entities, mock_ner, text_transaction
):
    mock_ner.return_value = lambda *args, **kwargs: mock_ner
    mock_merge_entities.return_value = [("DEF Corp", "ORG"), ("Alice Smith", "PER")]
    mock_is_pep.return_value = False
    mock_classification.return_value = {
        "sequence": "DEF Corp",
        "label": "Corporate",
        "score": 0.97,
        "supporting_evidence": "GLEIF"
    }
    mock_gleif_data.return_value = mock_gleif_data
    mock_iso_mapping.return_value = mock_iso_mapping

    result = process_transaction(text_transaction)

    assert result["Transaction ID"] == "TX56789"
    assert "Alice Smith" in result["Extracted Entity"]
    assert "DEF Corp" in result["Extracted Entity"]
    assert "Corporate" in result["Entity Type"]
    assert result["Confidence Score"] > 0
    assert "United States" in result["Countries"]


# ✅ Test with empty transaction
def test_process_empty_transaction(empty_transaction):
    result = process_transaction(empty_transaction)
    assert result["Transaction ID"] == "Unknown"
    assert result["Extracted Entity"] == []
    assert result["Entity Type"] == []
    assert result["Confidence Score"] == 0.0
    assert result["Countries"] == []


# ✅ Test with PEP entity
@patch("main.is_pep")
@patch("main.pipeline")
@patch("main.merge_entities")
def test_process_pep_entity(mock_merge_entities, mock_ner, mock_is_pep, sample_transaction):
    mock_ner.return_value = lambda *args, **kwargs: mock_ner
    mock_merge_entities.return_value = [("John Doe", "PER")]
    mock_is_pep.return_value = True

    result = process_transaction(sample_transaction)

    assert "John Doe" in result["Extracted Entity"]
    assert "PEP" in result["Entity Type"]
    assert "OpenSanctions" in result["Supporting Evidence"]
    assert result["Confidence Score"] > 0


# ✅ Test multiple entities and confidence averaging
@patch("main.pipeline")
@patch("main.merge_entities")
@patch("main.classify_entity")
@patch("main.query_gleif")
@patch("main.map_iso3166_country")
@patch("main.is_pep")
def test_multiple_entities_confidence(
    mock_is_pep, mock_iso_mapping, mock_gleif_data, mock_classification, mock_merge_entities, mock_ner, sample_transaction
):
    mock_ner.return_value = lambda *args, **kwargs: mock_ner
    mock_merge_entities.return_value = [("ABC Corp", "ORG"), ("John Doe", "PER")]
    mock_is_pep.side_effect = [False, False]
    mock_classification.side_effect = [
        {"sequence": "ABC Corp", "label": "Corporate", "score": 0.92, "supporting_evidence": "GLEIF"},
        {"sequence": "John Doe", "label": "Individual", "score": 0.95, "supporting_evidence": None},
    ]
    mock_gleif_data.return_value = mock_gleif_data
    mock_iso_mapping.return_value = mock_iso_mapping

    result = process_transaction(sample_transaction)

    assert len(result["Extracted Entity"]) == 2
    assert round(result["Confidence Score"], 2) == round((0.92 + 0.95) / 2, 2)


# ✅ Test when no entities are detected
@patch("main.pipeline")
@patch("main.merge_entities")
def test_no_entities_detected(mock_merge_entities, mock_ner, sample_transaction):
    mock_ner.return_value = lambda *args, **kwargs: []
    mock_merge_entities.return_value = []

    result = process_transaction(sample_transaction)

    assert result["Extracted Entity"] == []
    assert result["Confidence Score"] == 0.0
