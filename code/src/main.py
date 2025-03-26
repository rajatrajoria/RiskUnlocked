import os
import json

from process_transaction import process_transaction
from news_fetch import get_news_with_full_content
from news_sentiment_analysis import news_sentiment_analysis_score
from geo_risk_analysis import geo_risk_analysis
from sector import getSectors
from sanctions import getSanctionReports
from verdict import verdict
def process():
    sample_transaction = {
        "Transaction ID": "TXN001",
        "Payer Name": "Tesla Inc",
        "Receiver Name": "Microsoft Corporation",
        "Transaction Details": "Payment for services rendered",
        "Amount": "$500,000",
        "Receiver Country": "USA"
    }

    #Extraction, Enrichment, Classification
    extraction_result = process_transaction(sample_transaction)

    #News Analysis and Scoring
    news_data = get_news_with_full_content(extraction_result["Extracted Entity"])
    news_sentiment_analysis_score()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    scores_file = os.path.join(root_dir,"../../" "artifacts", "arch", "transaction_risk_scores.json")
    with open(scores_file, "r", encoding="utf-8") as f:
        scores = json.load(f)
    extraction_result["Real Time News Analysis of Entities Involved in the transaction"] = scores

    #Geo Risk Analysis and Scoring
    geo_risk = geo_risk_analysis(extraction_result["Countries"])
    extraction_result["Geo Risk Analysis Results of Entities Involved"] = geo_risk

    
    extraction_result["Sectors associated with the entities extracted"] = getSectors(extraction_result["Extracted Entity"])

    # Prepare sanction cases list from extracted entities
    sanction_cases = []
    for name, ent_type in zip(extraction_result["Extracted Entity"], extraction_result["Entity Type"]):
        # Convert type to the expected value for sanctions screening
        if ent_type.lower() in ["individual", "pep"]:
            type_value = "person"
        else:
            type_value = "organization"
        sanction_cases.append({"name": name, "type": type_value})

    # Now pass the list to getSanctionReports()
    extraction_result["Sanction Analysis of the entitites involved"] = getSanctionReports(sanction_cases)
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
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    save_path = os.path.join(root_dir, "datasets", "result.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(combined_result, file, indent=4, ensure_ascii=False)



    

























if __name__ == "__main__":
    process()

