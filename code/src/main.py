import os
import json

from process_transaction import process_transaction
from news_fetch import get_news_with_full_content
from news_sentiment_analysis import news_sentiment_analysis_score
from geo_risk_analysis import geo_risk_analysis
from sector import getSectors

def process():
    sample_transaction = {
        "Transaction ID": "TXN001",
        "Payer Name": "Google",
        "Receiver Name": "Microsoft",
        "Transaction Details": "Payment for services rendered",
        "Amount": "$500,000",
        "Receiver Country": "USA"
    }

    #Extraction, Enrichment, Classification
    extraction_result = process_transaction(sample_transaction)

    #News Analysis and Scoring
    # news_data = get_news_with_full_content(extraction_result["Extracted Entity"])
    # news_sentiment_analysis_score()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    scores_file = os.path.join(root_dir,"../../" "artifacts", "arch", "transaction_risk_scores.json")
    with open(scores_file, "r", encoding="utf-8") as f:
        scores = json.load(f)
    extraction_result["Real Time News Analysis of Entities Involved in the transaction"] = scores

    #Geo Risk Analysis and Scoring
    geo_risk = geo_risk_analysis(extraction_result["Countries"])
    extraction_result["Geo Risk Analysis Results of Entities Involved"] = geo_risk

    
    extraction_result["Sectors associated with the entities extracted"] = getSectors(extraction_result["Extracted Entity"])


    #Kaushal will be changing here
    extraction_result["Sanction Analysis of the entitites involved"] = getSanctionReports()


    print(json.dumps(extraction_result, indent=2))


    

























if __name__ == "__main__":
    process()

