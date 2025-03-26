import pytest
import re
from src.news_sentiment_analysis import analyze_risk, detect_historical_fraud, analyze_sentiment, RISK_KEYWORDS


@pytest.fixture
def sample_articles():
    return [
        {
            "title": "Company under investigation for fraud",
            "description": "The company is facing allegations of money laundering.",
            "full_content": "Authorities are investigating the company for possible fraud and money laundering."
        },
        {
            "title": "New sanctions imposed",
            "description": "Economic sanctions were placed due to financial violations.",
            "full_content": "The government imposed sanctions due to suspected illicit financial activities."
        },
        {
            "title": "Positive quarterly report",
            "description": "The company's revenue grew despite difficult market conditions.",
            "full_content": "The quarterly report shows positive growth and no signs of fraud."
        }
    ]


@pytest.fixture
def high_risk_article():
    return [
        {
            "title": "Company involved in multiple criminal activities",
            "description": "Allegations of money laundering, fraud, and corruption surface.",
            "full_content": "Authorities have uncovered evidence of money laundering, bribery, and fraud."
        }
    ]


@pytest.fixture
def no_risk_articles():
    return [
        {
            "title": "Company launches new product",
            "description": "The company is growing rapidly in the market.",
            "full_content": "The latest product launch has been successful with no allegations of fraud."
        }
    ]


@pytest.fixture
def short_article():
    return [
        {
            "title": "Brief update",
            "description": "No criminal activity detected.",
            "full_content": "Company updates with no fraud or risks."
        }
    ]


# ✅ Test Sentiment Analysis Risk
def test_analyze_sentiment_negative_high():
    text = "This company is facing serious fraud allegations and financial crimes."
    score = analyze_sentiment(text)
    assert score == 15


def test_analyze_sentiment_neutral():
    text = "The company reported steady revenue growth for the quarter."
    score = analyze_sentiment(text)
    assert score == 2


# ✅ Test Keyword Detection Risk
def test_keyword_risk_detection():
    text = "This company is accused of money laundering and tax evasion."
    keyword_risk = sum(RISK_KEYWORDS[keyword] for keyword in RISK_KEYWORDS if re.search(rf"\b{keyword}\b", text))
    assert keyword_risk > 0


def test_no_keyword_risk():
    text = "This is a completely unrelated news article with no risk keywords."
    keyword_risk = sum(RISK_KEYWORDS[keyword] for keyword in RISK_KEYWORDS if re.search(rf"\b{keyword}\b", text))
    assert keyword_risk == 0


# ✅ Test Fraud History Boost
def test_historical_fraud_high_profile():
    score = detect_historical_fraud([], "Wirecard")
    assert score == 50


def test_historical_fraud_with_multiple_articles(sample_articles):
    score = detect_historical_fraud(sample_articles, "Normal Company")
    assert score == 20


def test_historical_fraud_no_match():
    score = detect_historical_fraud([], "Normal Company")
    assert score == 0


# ✅ Test Main Risk Analysis
def test_analyze_risk_high_profile(sample_articles):
    score = analyze_risk("Wirecard", sample_articles)
    assert score > 50


def test_analyze_risk_normal_case(sample_articles):
    score = analyze_risk("Normal Company", sample_articles)
    assert score > 20


def test_analyze_risk_empty_articles():
    score = analyze_risk("Normal Company", [])
    assert score == 0


def test_analyze_risk_no_risky_keywords(no_risk_articles):
    score = analyze_risk("Normal Company", no_risk_articles)
    assert score <= 5


# ✅ Test Article with Multiple Risk Keywords
def test_multiple_keyword_risk(high_risk_article):
    score = analyze_risk("High Risk Company", high_risk_article)
    assert score >= 50


# ✅ Edge Case: Short Article
def test_short_article(short_article):
    score = analyze_risk("Low Risk Company", short_article)
    assert score <= 5
