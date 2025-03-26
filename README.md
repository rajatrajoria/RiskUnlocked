🚀 RiskyGPT - AI-Powered Financial Risk Assessment
📌 Table of Contents
Introduction

Demo

Inspiration

What It Does

How We Built It

Challenges We Faced

How to Run

Tech Stack

APIs & Data Sources

Installation Guide

Team

🎯 Introduction
RiskyGPT is an AI-powered risk assessment tool that evaluates financial transactions based on sanctions lists, geopolitical risk, and sentiment analysis from news sources. It helps financial analysts, auditors, and compliance teams detect high-risk entities and suspicious transactions.

🎥 Demo
🔗 Live Demo (if applicable)
📹 Video Demo (if applicable)
🖼️ Screenshots:



💡 Inspiration
With increasing financial fraud, money laundering, and sanction evasions, organizations need an AI-powered risk assessment system that automates entity verification, transaction monitoring, and risk classification using LLMs, news sentiment analysis, and global sanction lists.

⚙️ What It Does
🔍 Risk Score Calculation - Analyzes entities and transactions for sanction violations and geopolitical risk.

📰 News Sentiment Analysis - Uses Google News API + FinBERT to detect negative press coverage.

⚖️ Sanctions & Compliance - Cross-checks entities with OFAC, UN, FATF, EU, OpenSanctions API.

🤖 AI Chatbot - Interactive risk assessment chatbot using Ollama (Mistral-7B) + Gemini LLM.

🔎 Entity Recognition - Extracts company details using NER-based classification.

🛠️ How We Built It
🔹 Backend: Python for API development
🔹 Frontend: Streamlit UI for real-time risk analysis
🔹 AI Models: Mistral-7B (via Ollama), Gemini LLM, ProsusAI/FinBERT
🔹 Data Processing: FAISS for similarity search, Named Entity Recognition (NER)
🔹 APIs Used: OpenSanctions, Google News API, SEC EDGAR, Offshore Trust API

🚧 Challenges We Faced
⚠️ Large Model Latency: Mistral-7B required optimizations for faster inference.

📄 Data Processing Complexity: Handling unstructured news and entity recognition required NER-based classifiers.

🌐 API Limitations: Google News API rate limits required caching strategies.

🔧 Deployment Issues: Streamlit + Ollama setup needed proper environment configurations.

🏃 How to Run
1️⃣ Install Dependencies
sh
Copy
Edit
pip install -r requirements.txt
2️⃣ Install Ollama (For Local LLM Model)
Download and install Ollama:

sh
Copy
Edit
curl -fsSL https://ollama.ai/install.sh | sh
Verify installation:

sh
Copy
Edit
ollama list
3️⃣ Download and Setup Models
sh
Copy
Edit
ollama pull mistral
4️⃣ Run the Streamlit UI
sh
Copy
Edit
streamlit run bot.py
5️⃣ Expected Output
✅ RiskyGPT UI Loads
✅ Transaction Analysis & Risk Scoring
✅ Interactive Chatbot for Risk Queries

🏗️ Tech Stack
Frontend: Streamlit

Backend: Python

LLMs: Mistral-7B via Ollama, Gemini LLM

News Sentiment Analysis: ProsusAI/FinBERT

Entity Recognition: NER-based Classification

APIs & Data Sources: Google News API, OpenSanctions, SEC EDGAR, Offshore Trust API

🌍 APIs & Data Sources
🌐 Sanctions & Compliance:

OFAC (Office of Foreign Assets Control)

EU & UN Security Council Sanctions

FATF (Financial Action Task Force) AML Risk Lists

OpenSanctions API

📊 Financial Data & Verification:

GLEIF (Global Legal Entity Identifier Foundation)

SEC EDGAR (U.S. Financial Filings)

Offshore Trust API (Shell company detection)

📰 News Sentiment Analysis:

Google News API (Real-time news tracking)

ProsusAI/FinBERT (Finance-focused sentiment classification)

📈 Risk Scoring Parameters:

CPI (Corruption Perceptions Index)

GTI (Global Terrorism Index)

AML Risk Assessment Models

🔧 Installation Guide
1️⃣ Clone the Repository
sh
Copy
Edit
git clone https://github.com/your-repo.git
cd your-repo
2️⃣ Install Python Dependencies
sh
Copy
Edit
pip install -r requirements.txt
3️⃣ Install Ollama & Download Mistral Model
sh
Copy
Edit
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral
4️⃣ Run the Application
sh
Copy
Edit
streamlit run bot.py
👥 Team
Archit Lall - GitHub | LinkedIn

Teammate 2 - GitHub | LinkedIn

🚀 Future Enhancements
✅ Integrate GPT-4 Turbo for better chatbot interaction
✅ Deploy on cloud infrastructure (AWS/GCP)