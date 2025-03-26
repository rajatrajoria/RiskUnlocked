import pytest
from src.probabilistic_risk_calc import calculate_risk_score

# Tolerance for floating-point comparisons
TOLERANCE = 0.01

@pytest.mark.parametrize(
    "initial_risk_score, transaction_amount_input, transaction_frequency_input, expected_range",
    [
        (0.8, 7500, 45, (60.0, 90.0)),  # Medium amount, low frequency
        (0.6, 12000, 300, (70.0, 95.0)),  # High amount, medium frequency
        (0.9, 25000, 600, (85.0, 100.0)),  # High amount, high frequency
        (0.4, 1500, 20, (30.0, 60.0)),  # Low amount, low frequency
        (0.7, 18000, 500, (75.0, 95.0)),  # Medium-high amount, high frequency
        (0.5, 3000, 100, (40.0, 65.0)),  # Low amount, medium frequency
        (0.3, 9000, 350, (50.0, 80.0)),  # Medium amount, medium-high frequency
        (0.9, 1000, 10, (40.0, 70.0)),  # Low amount, very low frequency
        (0.2, 35000, 750, (85.0, 100.0)),  # Max amount and frequency
        (0.1, 0, 0, (5.0, 30.0)),  # Minimum possible inputs
    ],
)
def test_calculate_risk_score(initial_risk_score, transaction_amount_input, transaction_frequency_input, expected_range):
    final_risk_score = calculate_risk_score(initial_risk_score, transaction_amount_input, transaction_frequency_input)
    
    # Convert risk score to percentage
    final_risk_score_percentage = final_risk_score * 100
    
    # Assert that the final risk score is within the expected range
    assert expected_range[0] <= final_risk_score_percentage <= expected_range[1], \
        f"Final risk score {final_risk_score_percentage:.2f}% is not within expected range {expected_range}"
