import os
import json
import requests
from dotenv import load_dotenv

# Load API keys
load_dotenv()
HF_API_KEY = os.getenv("HUGGING_FACE_API_KEY") 
OFAC_API_KEY = os.getenv("OFAC_API_KEY")  
OPENSANCTIONS_API_KEY = os.getenv("OPENSANCTIONS_API_KEY")  

OFAC_API_URL = "https://api.ofac-api.com/v4/screen"
OPENSANCTIONS_API_URL = "https://api.opensanctions.org/match/sanctions"
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

def screen_entities_ofac(cases):
    payload = {
        "apiKey": OFAC_API_KEY,
        "minScore": 95,
        "source": ["all"],
        "types": ["person", "organization"],
        "cases": cases
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(OFAC_API_URL, json=payload, headers=headers)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error in OFAC screening: {e}")
        return None

def screen_entities_openSanctionsAPI(cases):
    headers = {
        "Accept": "application/json",
        "Authorization": f"ApiKey {OPENSANCTIONS_API_KEY}"
    }
    payload = {
        "queries": {
            f"q{i+1}": {
                "schema": "Person" if case["type"].lower() == "person" else "Company",
                "properties": {"name": [case["name"]]}
            }
            for i, case in enumerate(cases)
        }
    }
    try:
        response = requests.post(OPENSANCTIONS_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json().get("responses", {})
            return {case["name"]: data.get(f"q{i+1}", {}).get("results", []) for i, case in enumerate(cases)}
        else:
            return None
    except Exception as e:
        print(f"Error fetching OpenSanctions data: {e}")
        return None

def summarize_sanctions_data(ofac_response, open_sanctions_response):
    """ Extracts key details to keep the JSON size small """
    summary = {}
    
    if ofac_response:
        summary["OFAC Screening"] = [
            {"Entity": entity.get("name"), "Risk": entity.get("riskLevel", "Unknown"), 
             "Sanctioned By": entity.get("sanctioningBodies", "N/A")}
            for entity in ofac_response.get("cases", [])
        ]

    if open_sanctions_response:
        summary["OpenSanctions"] = [
            {"Entity": name, "Matches": len(matches)}
            for name, matches in open_sanctions_response.items()
        ]
    
    return json.dumps(summary, indent=2)

def risk_analysis_huggingface(ofac_response, open_sanctions_response):
    try:
        # Reduce JSON size
        summarized_data = summarize_sanctions_data(ofac_response, open_sanctions_response)

        prompt = f"""You are a risk analysis expert specializing in identifying potential financial, legal, and security risks based on sanctions data that I will be providing you. You will carefully analyze the following raw JSON response, which contains details about various entities from multiple sources (OFAC and OpenSanctions). Your task is to determine whether the entities involved are risky and, if so, provide a well-reasoned justification with supporting evidences. You be like an Explainable AI.
A possbile response format can be something like:
Sanction Analysis:

Entity Name
- Risk Score: (0-1)?
- Justification and Evidence: (should include List of sanctioning bodies and any other details available, Reason for sanctions such as Terrorism, money laundering, fraud, etc., and any Additional insights like alias details, past violations, associated organizations, if any)

... (if more entities involved, use the same format)

Overall Risk Score (Sanction based) for the transaction:
- Final Risk Level: (in 0-1)
- Confidence Level: (in 0-1;  how much confidence do you have on the Final Risk Level)
- Justification: Justify everything, be as much detailed as possible, consideration of all individual entity risk levels, explanation of why this transaction should be flagged or cleared, Any patterns or red flags in the provided data, or anything. Think out of the box and think like an expert

Here is the JSON output from the sanctions screening:
{summarized_data}
"""

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 30000, "temperature": 0.5}  # Smaller input
        }

        response = requests.post(HF_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error in risk_analysis_huggingface: {e}"

def getSanctionReports(cases):
    screening_result_from_ofac = screen_entities_ofac(cases)
    screening_result_from_openSanctionsAPI = screen_entities_openSanctionsAPI(cases)
    return risk_analysis_huggingface(screening_result_from_ofac, screening_result_from_openSanctionsAPI)

if __name__ == "__main__":
    cases = [
        {"name": "Austenship Management Private Ltd", "type": "organization"},
        {"name": "Flux Maritime", "type": "organization"}
    ]
    print(getSanctionReports(cases))
