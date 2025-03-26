import requests
from transformers import pipeline

def check_shell_company(company_name):
    """Check if the entity appears in the Offshore Leaks Database."""
    payload = {
        "queries": {
            "q0": {
                "type": "Entity",
                "query": company_name,
                "properties": [{"pid": "name", "v": company_name, "limit": 10}]
            }
        }
    }
    headers = {"Content-Type": "application/json"}
    url = "https://offshoreleaks.icij.org/api/v1/reconcile"
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 201:
            data = response.json().get("q0", {}).get("result", [])
            for candidate in data:
                if candidate.get("name", "").lower() == company_name.lower() and candidate.get("score", 0) > 0.9:
                    description = candidate.get("description", "")
                    if "extracted from the" in description:
                        evidence = description.split("extracted from the")[1].strip().rstrip(".")
                        return True, evidence
                    return True, None
            return False, None
        else:
            return False, None
    except requests.RequestException:
        return False, None

def classify_entity(entity_name):
    """Classify an entity using NLP and databases."""
    labels = ["Corporation", "Non-Profit", "Shell Company", "Government Agency"]
    
    is_shell, evidence = check_shell_company(entity_name)
    if is_shell:
        return {'sequence': entity_name, 'label': 'Shell Company', 'score': 0.95, 'supporting_evidence': evidence}
    
    classifier = pipeline("zero-shot-classification", model="FacebookAI/roberta-large-mnli")
    result = classifier(entity_name, candidate_labels=labels)
    max_score_index = result['scores'].index(max(result['scores']))
    
    return {
        'sequence': entity_name,
        'label': result['labels'][max_score_index],
        'score': result['scores'][max_score_index],
        'supporting_evidence': None
    }