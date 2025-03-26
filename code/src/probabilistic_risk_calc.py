import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def calculate_risk_score(initial_risk_score, transaction_amount_input, transaction_frequency_input):
    # === 1. BAYESIAN INFERENCE ===

    # Prior probabilities
    P_fraud = 0.05  # 5% chance of fraud
    P_not_fraud = 1 - P_fraud

    # Likelihood of evidence given fraud
    P_evidence_given_fraud = 0.8  # High amount, unusual location, etc.
    P_evidence_given_not_fraud = 0.1  # Low risk for normal transactions

    # Bayesian update
    P_fraud_given_evidence = (P_evidence_given_fraud * P_fraud) / (
        (P_evidence_given_fraud * P_fraud) + (P_evidence_given_not_fraud * P_not_fraud)
    )

    # === 2. FUZZY LOGIC BASED RISK SCORE ===

    # Define fuzzy variables
    transaction_amount = ctrl.Antecedent(np.arange(0, 35001, 1), 'transaction_amount')
    transaction_frequency = ctrl.Antecedent(np.arange(0, 751, 1), 'transaction_frequency')
    risk_score = ctrl.Consequent(np.arange(0, 101, 1), 'risk_score')

    # Define fuzzy membership functions
    transaction_amount['low'] = fuzz.trimf(transaction_amount.universe, [0, 0, 3000])
    transaction_amount['medium'] = fuzz.trimf(transaction_amount.universe, [2000, 9000, 18000])
    transaction_amount['high'] = fuzz.trimf(transaction_amount.universe, [10000, 20000, 35000])

    transaction_frequency['low'] = fuzz.trimf(transaction_frequency.universe, [0, 0, 100])
    transaction_frequency['medium'] = fuzz.trimf(transaction_frequency.universe, [50, 200, 350])
    transaction_frequency['high'] = fuzz.trimf(transaction_frequency.universe, [250, 500, 750])

    risk_score['low'] = fuzz.trimf(risk_score.universe, [0, 0, 40])
    risk_score['medium'] = fuzz.trimf(risk_score.universe, [30, 50, 70])
    risk_score['high'] = fuzz.trimf(risk_score.universe, [60, 100, 100])

    # Define all possible fuzzy rules with AND and OR
    rules = []
    for amount_level in ['low', 'medium', 'high']:
        for freq_level in ['low', 'medium', 'high']:
            if amount_level == 'high' or freq_level == 'high':
                risk_level = 'high'
            elif amount_level == 'medium' and freq_level == 'medium':
                risk_level = 'medium'
            elif amount_level == 'low' and freq_level == 'low':
                risk_level = 'low'
            else:
                risk_level = 'medium' if amount_level == 'medium' or freq_level == 'medium' else 'low'
            rules.append(ctrl.Rule(transaction_amount[amount_level] & transaction_frequency[freq_level], risk_score[risk_level]))
            rules.append(ctrl.Rule(transaction_amount[amount_level] | transaction_frequency[freq_level], risk_score[risk_level]))

    # Create control system and simulation
    risk_ctrl = ctrl.ControlSystem(rules)
    risk_simulation = ctrl.ControlSystemSimulation(risk_ctrl)

    # Apply boundary checks to inputs
    risk_simulation.input['transaction_amount'] = min(max(transaction_amount_input, 0), 35000)
    risk_simulation.input['transaction_frequency'] = min(max(transaction_frequency_input, 0), 750)

    # Compute fuzzy output
    risk_simulation.compute()

    # Debug check to ensure no KeyError
    if 'risk_score' in risk_simulation.output:
        fuzzy_risk_score = round(risk_simulation.output['risk_score'] / 100, 3)
    else:
        fuzzy_risk_score = 0

    # === 3. COMBINING FUZZY AND BAYESIAN RISK SCORES ===

    # Weighted combination of initial, fuzzy, and Bayesian risk scores
    final_risk_score = round((0.5 * initial_risk_score) + (0.3 * fuzzy_risk_score) + (0.2 * P_fraud_given_evidence), 3)

    # Print results
    print(f"Initial Risk Score: {initial_risk_score}")
    print(f"Transaction Amount: {transaction_amount_input}")
    print(f"Transaction Frequency: {transaction_frequency_input}")
    print(f"Final Combined Risk Score: {final_risk_score * 100:.2f}%")

    return final_risk_score