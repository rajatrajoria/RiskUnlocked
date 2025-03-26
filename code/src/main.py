import os
import json
import re

from process_transaction import process_transaction
from news_fetch import get_news_with_full_content
from news_sentiment_analysis import news_sentiment_analysis_score
from geo_risk_analysis import geo_risk_analysis
from sector import getSectors
from sanctions import getSanctionReports
from verdict import verdict

def convert_text_to_transactions(input_text):
    try:
        data = json.loads(input_text)
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Unexpected JSON structure.")
    except json.JSONDecodeError:
        try:
            data = json.loads("[" + input_text + "]")
            return data
        except json.JSONDecodeError as e:
            raise ValueError("Input text is not valid JSON or JSON-like transactions.") from e

def app(transactions):
  final_outputs = []
  combined_results = []
  transactions = convert_text_to_transactions(transactions)
  for transaction in transactions:
    # Extraction, Enrichment, Classification
    extraction_result = process_transaction(transaction)
    print(extraction_result)

    # News Analysis and Scoring
    news_data = get_news_with_full_content(extraction_result["Extracted Entity"])
    news_sentiment_analysis_score()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    scores_file = os.path.join(root_dir,"../../" "artifacts", "arch", "transaction_risk_scores.json")
    with open(scores_file, "r", encoding="utf-8") as f:
        scores = json.load(f)
    extraction_result["Real Time News Analysis of Entities Involved in the transaction"] = scores

    # Geo Risk Analysis and Scoring
    geo_risk = geo_risk_analysis(extraction_result["Countries"])
    extraction_result["Geo Risk Analysis Results of Entities Involved"] = geo_risk   
    extraction_result["Sectors associated with Extracted Entities"] = getSectors(extraction_result["Extracted Entity"], extraction_result["Entity Type"])
    sanction_cases = []
    for name, ent_type in zip(extraction_result["Extracted Entity"], extraction_result["Entity Type"]):
        if ent_type.lower() in ["individual", "pep"]:
            type_value = "person"
        else:
            type_value = "organization"
        sanction_cases.append({"name": name, "type": type_value})
    
    # Sanction Analysis
    extraction_result["Sanction Analysis"] = getSanctionReports(sanction_cases)
    implementation_details = {

"implementation_details": {
    "technology_stack": {
      "backend": "Python (FastAPI) for API development",
      "frontend": "Streamlit UI for real-time risk analysis",
      "LLM_pipeline": "Gemini + Ollama (Mistral-7B) for contextual chatbot & analysis",
      "vector_search": "FAISS for entity name similarity search",
      "news_sentiment_analysis": "Google News API + ProsusAI/FinBERT for sentiment classification",
      "entity_recognition": "NER-based classification & extraction using classifier NER"
    },
    "data_sources": {
      "sanctions_lists": [
        "OFAC (Office of Foreign Assets Control)",
        "UN Security Council Sanctions List",
        "EU Sanctions List",
        "Swiss SECO Sanctions List",
        "OpenSanctions API (for consolidated global sanctions data)"
      ],
      "financial_records": [
        "SEC EDGAR (For U.S.-based companies' financial reports)",
        "GLEIF (For legal entity verification)",
        "Offshore Trust API (For identifying shell companies and offshore structures)"
      ],
      "risk_scoring_indexes": {
        "CPI": "Corruption Perceptions Index (Transparency International)",
        "FATF": "Financial Action Task Force (AML/CFT risk assessment)",
        "GTI": "Global Terrorism Index (Terror financing risk assessment)",
        "AML": "Anti-Money Laundering risk assessment based on multiple global standards"
      },
      "news_and_sentiments": [
        "Google News API (For real-time news monitoring & entity-based sentiment tracking)",
        "ProsusAI/FinBERT (For finance-specific sentiment classification using BERT)"
      ]
    },
    "risk_scoring_parameters": {
      "factors_considered": [
        "Presence on sanctions lists",
        "Ownership & shell company detection",
        "Geopolitical risk (Country-based weightage)",
        "Negative news sentiment & legal cases",
        "Terror financing & AML compliance (GTI, FATF, CPI indexes)"
      ],
      "calculation_logic": "Weighted scoring based on factors, aggregated for final risk score.",
      "thresholds": {
        "high_risk": "Above 0.65",
        "medium_risk": "Between 0.4 and 0.65",
        "low_risk": "Below 0.4"
      }
    }
  }
    } 

    verdict_response = verdict(extraction_result)
    print(json.dumps(verdict_response, indent=4))

    combined_result = {
        "Findings" : extraction_result,
        "implementation_details" : implementation_details
    }
    combined_results.append(combined_result)
    
    
    final_output = {
        "Transaction ID": extraction_result["Transaction ID"],
        "Extracted Entity": extraction_result["Extracted Entity"],
        "Entity Type": extraction_result["Entity Type"],
        "Supporting Evidence": extraction_result["Supporting Evidence"],
        "Transaction Risk Analysis": verdict_response
    }

    print(json.dumps(final_output, indent=4))
    final_outputs.append(final_output)
  root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
  save_path = os.path.join(root_dir, "datasets", "result.json")
  os.makedirs(os.path.dirname(save_path), exist_ok=True)
  with open(save_path, "w", encoding="utf-8") as file:
      json.dump(combined_results, file, indent=4, ensure_ascii=False)
  return final_outputs

if __name__ == "__main__":
    sample_transaction = {}
    app(sample_transaction)