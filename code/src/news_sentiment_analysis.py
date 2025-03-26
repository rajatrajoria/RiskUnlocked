import json
import re
import torch
import os
from transformers import BertTokenizer, BertForSequenceClassification
from scipy.special import softmax


MODEL_NAME = "ProsusAI/finbert"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME)


RISK_KEYWORDS = {
    "sanctions": 5, "money laundering": 5, "terrorism": 7, "fraud": 5, "organized crime": 5,
    "drug trafficking": 5, "human trafficking": 5, "arms trafficking": 5, "terrorist financing": 5,
    "shell company": 5, "offshore accounts": 5, "Ponzi scheme": 5, "financial fraud": 5,
    "bribery": 4, "embezzlement": 4, "tax evasion": 4, "smuggling": 4, "corruption": 4,
    "scam": 4, "identity theft": 4, "money mule": 4, "dark web": 4, "ransomware": 4,
    "hacking": 4, "forgery": 4, "racketeering": 4, "audit fraud": 4, "whistleblower": 4,
    "blacklisted": 4, "illicit financing": 4, "financial penalties": 4, "economic sanctions": 4
}

MAX_ARTICLE_SCORE = 10

def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = softmax(outputs.logits.numpy()[0])
    neg, neu, pos = scores

    if neg > 0.8:
        return 15  
    elif neg > 0.6:
        return 10  
    elif neg > 0.4:
        return 6  
    elif neu > 0.6:
        return 2  
    else:
        return 1  

def detect_historical_fraud(news_articles, company_name):
    fraud_news_count = sum(
        1 for article in news_articles
        if any(re.search(rf"\b{keyword}\b", article.get("full_content", "").lower()) for keyword in RISK_KEYWORDS)
    )

    HIGH_PROFILE_FRAUD = ["Wirecard", "Enron", "FTX", "Madoff", "Theranos"]
    if company_name in HIGH_PROFILE_FRAUD:
        return 50  

    if fraud_news_count >= 10:
        return 30  
    elif fraud_news_count >= 5:
        return 20  
    elif fraud_news_count >= 2:
        return 10  
    else:
        return 0  

def analyze_risk(company_name, news_articles):
    if not news_articles:
        return 0  

    total_score = 0
    for article in news_articles:
        text = article.get("full_content", f"{article.get('title', '')} {article.get('description', '')}").lower()
        sentiment_risk = analyze_sentiment(text)

        unique_keywords = {keyword for keyword in RISK_KEYWORDS if re.search(rf"\b{keyword}\b", text)}
        keyword_risk = min(sum(RISK_KEYWORDS[keyword] for keyword in unique_keywords), MAX_ARTICLE_SCORE)

        article_score = (sentiment_risk + keyword_risk) / 2  
        total_score += article_score

    normalized_score = (total_score / (len(news_articles) + 1)) * 10
    fraud_boost = detect_historical_fraud(news_articles, company_name)
    final_score = min(100, round(normalized_score + fraud_boost, 2))

    return final_score


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
news_file_path = os.path.join(root_dir, "artifacts", "arch", "news_with_full_content.json")
risk_score_save_path = os.path.join(root_dir, "artifacts", "arch", "transaction_risk_scores.json")


os.makedirs(os.path.dirname(news_file_path), exist_ok=True)
os.makedirs(os.path.dirname(risk_score_save_path), exist_ok=True)


with open(news_file_path, "r", encoding="utf-8") as file:
    news_data = json.load(file)

risk_scores = {company: analyze_risk(company, articles) for company, articles in news_data.items()}


for company, score in risk_scores.items():
    print(f"⚠️ Risk Score for {company}: {score}/100")

with open(risk_score_save_path, "w", encoding="utf-8") as file:
    json.dump(risk_scores, file, indent=4, ensure_ascii=False)

print(f"✅ Risk scores saved to {risk_score_save_path}")
