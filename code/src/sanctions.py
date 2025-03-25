import os
import json
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load API keys from the .env file
load_dotenv()
OFAC_API_KEY = os.getenv("OFAC_API_KEY")  
OPENSANCTIONS_API_KEY = os.getenv("OPENSANCTIONS_API_KEY")  
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

# API endpoints for sanction screening
OFAC_API_URL = "https://api.ofac-api.com/v4/screen"
OPENSANCTIONS_API_URL = "https://api.opensanctions.org/match/sanctions"


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
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print("Error:", response.status_code, response.text)
            return None
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
            results = {case["name"]: data.get(f"q{i+1}", {}).get("results", []) for i, case in enumerate(cases)}
            return results
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching OpenSanctions data: {e}")
        return None


def risk_analysis_llm(ofac_response, open_sanctions_response, model_name="gemini-1.5-pro", max_tokens=1000, temperature=0.7):
    try:
        combined_data = {
            "OFAC Screening Results": ofac_response,
            "OpenSanctions Screening Results": open_sanctions_response
        }
        json_output_str = json.dumps(combined_data, indent=2)
        
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
{json_output_str}
"""
        # Configure Gemini API with API key from .env
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt, generation_config={"temperature": temperature, "max_output_tokens": max_tokens})
        return response.text if response else "Error: No response from the model"
    except Exception as e:
        return f"Error in risk_analysis_llm: {e}"


def getSanctionReports(cases):
    screening_result_from_ofac = screen_entities_ofac(cases)
    screening_result_from_openSanctionsAPI = screen_entities_openSanctionsAPI(cases)
    response = risk_analysis_llm(screening_result_from_ofac, screening_result_from_openSanctionsAPI)
    return response
  


if __name__ == "__main__":
    cases = [
        {"name": "Al-Qaeda", "type": "organization"},
        {"name": "Austenship Management Private Ltd", "type": "organization"},
        {"name": "Mansoor Ali", "type": "person"}
    ]
    print(getSanctionReports(cases))
    
    
