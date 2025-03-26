import pytest
from unittest.mock import patch
import pandas as pd
from src.geo_risk_analysis import (
    load_cpi_data,
    load_aml_data,
    load_gti_data,
    load_fatf_data,
    calculate_transaction_risk,
)

# --- Test Constants ---
MOCK_CPI_DATA = {"Myanmar": 20, "Pakistan": 25, "Iran": 15, "Syria": 10}
MOCK_AML_DATA = {"Myanmar": 6.5, "Pakistan": 7.2, "Iran": 8.1, "Syria": 9.0}
MOCK_GTI_DATA = {"Myanmar": 5.0, "Pakistan": 6.3, "Iran": 7.4, "Syria": 8.0}
MOCK_FATF_LIST = {"Iran": "Black", "Syria": "Grey"}

LATEST_YEAR = 2024


# --- Mock DataFrame Generation ---
@pytest.fixture
def mock_cpi_df():
    data = {"Country": list(MOCK_CPI_DATA.keys()), str(LATEST_YEAR): list(MOCK_CPI_DATA.values())}
    return pd.DataFrame(data).set_index("Country")


@pytest.fixture
def mock_aml_df():
    data = {"Country": list(MOCK_AML_DATA.keys()), "Score": list(MOCK_AML_DATA.values())}
    return pd.DataFrame(data).set_index("Country")


@pytest.fixture
def mock_gti_df():
    data = {"Country": list(MOCK_GTI_DATA.keys()), "Score": list(MOCK_GTI_DATA.values())}
    return pd.DataFrame(data).set_index("Country")


@pytest.fixture
def mock_fatf_df():
    data = {"Countries": list(MOCK_FATF_LIST.keys()), "Category": list(MOCK_FATF_LIST.values())}
    return pd.DataFrame(data).set_index("Countries")


# --- Test Load Functions ---
@patch("app.risk_engine.pd.read_csv")
def test_load_cpi_data(mock_read_csv, mock_cpi_df):
    """Test loading CPI data."""
    mock_read_csv.return_value = mock_cpi_df
    cpi_scores, latest_year = load_cpi_data()
    assert cpi_scores == MOCK_CPI_DATA
    assert latest_year == str(LATEST_YEAR)


@patch("app.risk_engine.pd.read_csv")
def test_load_aml_data(mock_read_csv, mock_aml_df):
    """Test loading AML data."""
    mock_read_csv.return_value = mock_aml_df
    aml_scores = load_aml_data()
    assert aml_scores == MOCK_AML_DATA


@patch("app.risk_engine.pd.read_csv")
def test_load_gti_data(mock_read_csv, mock_gti_df):
    """Test loading GTI data."""
    mock_read_csv.return_value = mock_gti_df
    gti_scores = load_gti_data()
    assert gti_scores == MOCK_GTI_DATA


@patch("app.risk_engine.pd.read_csv")
def test_load_fatf_data(mock_read_csv, mock_fatf_df):
    """Test loading FATF list data."""
    mock_read_csv.return_value = mock_fatf_df
    fatf_list = load_fatf_data()
    assert fatf_list == MOCK_FATF_LIST


# --- Test Transaction Risk Calculation ---
def test_calculate_transaction_risk():
    """Test transaction risk score calculation between two countries."""
    risk_score = calculate_transaction_risk(
        "Myanmar", "Iran", MOCK_CPI_DATA, MOCK_AML_DATA, MOCK_GTI_DATA, MOCK_FATF_LIST
    )
    # Expected Risk Calculation:
    # CPI Risk -> (100 - 20) + (100 - 15) / 2 = 82.5
    # AML Risk -> (6.5 + 8.1) / 2 = 7.3
    # GTI Risk -> (5.0 + 7.4) / 2 = 6.2
    # Weighted Risk -> (0.4 * 82.5) + (0.3 * 7.3) + (0.3 * 6.2) = 33 + 2.19 + 1.86 ≈ 37.05
    # FATF Penalty -> 20 (for Iran as Blacklisted)
    expected_risk_score = round(37.05 + 20, 2)  # 57.05
    assert risk_score == expected_risk_score


def test_calculate_transaction_risk_no_fatf_penalty():
    """Test risk calculation when no FATF penalty applies."""
    risk_score = calculate_transaction_risk(
        "Myanmar", "Pakistan", MOCK_CPI_DATA, MOCK_AML_DATA, MOCK_GTI_DATA, {}
    )
    # CPI Risk -> (100 - 20) + (100 - 25) / 2 = 77.5
    # AML Risk -> (6.5 + 7.2) / 2 = 6.85
    # GTI Risk -> (5.0 + 6.3) / 2 = 5.65
    expected_risk_score = round((0.4 * 77.5) + (0.3 * 6.85) + (0.3 * 5.65), 2)  # ≈ 33.96
    assert risk_score == expected_risk_score


def test_calculate_transaction_risk_with_grey_penalty():
    """Test risk calculation with FATF Grey penalty."""
    risk_score = calculate_transaction_risk(
        "Syria", "Pakistan", MOCK_CPI_DATA, MOCK_AML_DATA, MOCK_GTI_DATA, MOCK_FATF_LIST
    )
    # CPI Risk -> (100 - 10) + (100 - 25) / 2 = 82.5
    # AML Risk -> (9.0 + 7.2) / 2 = 8.1
    # GTI Risk -> (8.0 + 6.3) / 2 = 7.15
    # Weighted Risk + FATF Penalty
    expected_risk_score = round((0.4 * 82.5) + (0.3 * 8.1) + (0.3 * 7.15) + 10, 2)  # ≈ 54.74
    assert risk_score == expected_risk_score


def test_calculate_transaction_risk_default_values():
    """Test risk calculation with default values for unknown countries."""
    risk_score = calculate_transaction_risk(
        "Unknown1", "Unknown2", MOCK_CPI_DATA, MOCK_AML_DATA, MOCK_GTI_DATA, {}
    )
    # Default CPI -> 50
    # Default AML -> 5.0
    # Default GTI -> 2.5
    expected_risk_score = round((0.4 * 50) + (0.3 * 5.0) + (0.3 * 2.5), 2)  # ≈ 22.75
    assert risk_score == expected_risk_score


def test_calculate_transaction_risk_black_and_grey():
    """Test transaction risk with both Black and Grey list penalties."""
    risk_score = calculate_transaction_risk(
        "Iran", "Syria", MOCK_CPI_DATA, MOCK_AML_DATA, MOCK_GTI_DATA, MOCK_FATF_LIST
    )
    # Base risk + 20 (Black) + 10 (Grey) => +30 penalty
    expected_risk_score = round((0.4 * 82.5) + (0.3 * 8.1) + (0.3 * 7.15) + 30, 2)  # ≈ 74.74
    assert risk_score == expected_risk_score
