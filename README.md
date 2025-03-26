# 🚀 RiskyGPT - AI-Powered Financial Risk Assessment

## Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [APIs & Data Sources](#apis--data-sources)
- [Team](#team)

---

## 🎯 Introduction

RiskyGPT is an AI-powered risk assessment tool that evaluates financial transactions based on sanctions lists, geopolitical risk, and sentiment analysis from news sources. It helps financial analysts, auditors, and compliance teams detect high-risk entities and suspicious transactions.

---

## 🎥 Demo

- **Video Demo & Presentation:** [📂 Google Drive](YOUR_DRIVE_LINK_HERE)  
---

## 💡 Inspiration

With increasing financial fraud, money laundering, and sanction evasions, organizations need an AI-powered risk assessment system that automates entity verification, transaction monitoring, and risk classification using LLMs, news sentiment analysis, and global sanction lists.

---

## ⚙️ What It Does

- **🔍 Risk Score Calculation:**  
  Analyzes entities and transactions for sanction violations and geopolitical risk.

- **📰 News Sentiment Analysis:**  
  Uses Google News API and FinBERT to detect negative press coverage.

- **⚖️ Sanctions & Compliance:**  
  Cross-checks entities with OFAC, UN, FATF, EU, and OpenSanctions API.

- **🤖 AI Chatbot:**  
  Provides an interactive risk assessment chatbot using Ollama (Mistral-7B) and Gemini LLM.

- **🔎 Entity Recognition:**  
  Extracts company details using NER-based classification.

---

## 🛠️ How We Built It

- **Backend:** Python for API development  
- **Frontend:** Streamlit UI for real-time risk analysis  
- **AI Models:**  
  - Mistral-7B (via Ollama)  
  - Gemini LLM  
  - ProsusAI/FinBERT  
- **Data Processing:**  
  - FAISS for similarity search  
  - Named Entity Recognition (NER)  
- **APIs Used:**  
  - OpenSanctions  
  - Google News API  
  - SEC EDGAR  
  - Offshore Trust API

---

## 🚧 Challenges We Faced

- **Large Model Latency:**  
  Mistral-7B required optimizations for faster inference.

- **Data Processing Complexity:**  
  Handling unstructured news and entity recognition required NER-based classifiers.

- **API Limitations:**  
  Google News API rate limits required caching strategies.

- **Deployment Issues:**  
  Streamlit + Ollama setup needed proper environment configurations.

---

## 🔧 How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/riskygpt.git
   cd riskygpt
2. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
3. **Install Ollama (For Local LLM Model)**  
   - **Download and Install Ollama:**  
     ```bash
     curl -fsSL https://ollama.ai/install.sh | sh
     ```
   - **Verify Installation:**  
     ```bash
     ollama list
     ```
   - **Download and Setup Models:**  
     ```bash
     ollama pull mistral
     ```

4. **Run the Streamlit UI**  
   ```bash
   streamlit run bot.py
   ```

5. **Expected Output**  
   - ✅ RiskyGPT UI Loads  
   - ✅ Transaction Analysis & Risk Scoring  
   - ✅ Interactive Chatbot for Risk Queries  

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python  
- **LLMs:**  
  - Mistral-7B via Ollama  
  - Gemini LLM  
- **News Sentiment Analysis:** ProsusAI/FinBERT  
- **Entity Recognition:** NER-based Classification  

---

## 🌍 APIs & Data Sources

### Sanctions & Compliance
- OFAC (Office of Foreign Assets Control)  
- EU & UN Security Council Sanctions  
- FATF (Financial Action Task Force) AML Risk Lists  
- OpenSanctions API  

### Financial Data & Verification
- GLEIF (Global Legal Entity Identifier Foundation for PEP detection)  
- SEC EDGAR (U.S. Financial Filings)  
- Offshore Trust API (Shell company detection)  

### News Sentiment Analysis
- Google News API (Real-time news tracking)  
- ProsusAI/FinBERT (Finance-focused sentiment classification)  

### Risk Scoring Parameters
- CPI (Corruption Perceptions Index)  
- GTI (Global Terrorism Index)  
- AML Risk Assessment Models  

---
## 👥 Team

- **Archit Lall** - [GitHub](#) | [LinkedIn](#)  
- **Atharva A. Muglikar** - [GitHub](#) | [LinkedIn](#)  
- **Kaushal Baid** - [GitHub](#) | [LinkedIn](#)  
- **Rajat Rajoria** - [GitHub](#) | [LinkedIn](#)  
- **Ritabrata Das** - [GitHub](#) | [LinkedIn](#)  
---

## 🚀 Future Enhancements

- ✅ Integrate GPT-4 Turbo for better chatbot interaction  
- ✅ Deploy on cloud infrastructure (AWS/GCP)  