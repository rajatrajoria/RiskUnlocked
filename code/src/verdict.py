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



def verdict(extraction_result):
    try:

        prompt = f"""
        AI-Driven Transaction Risk Analysis System
        Role & Objective
        You are a financial risk analyst specializing in forensic transaction analysis. Your task is to assess the risk level of a given transaction by evaluating multiple factors, identifying potential fraud, and providing a well-reasoned justification for the risk score. The transaction details include multiple entities, transaction amounts, and additional metadata from various risk intelligence sources.

        Objective
        Analyze the provided transaction data and determine whether it poses a financial, legal, or compliance risk. Consider all available information, detect hidden patterns, and justify your findings using data-driven reasoning. Your output should include both a numerical risk score and a detailed textual justification explaining how the score was derived.

        Data Sources & Their Importance
        You have access to the following risk intelligence sources:

        Sanctions & Watchlists (OFAC, OpenSanctions, FATF)

        Verify if any entity is on sanctions lists and assess the severity of sanctions.

        Consider sanctioning bodies such as the UN, EU, US Treasury, and World Bank.

        Identify reasons for sanctions such as money laundering, terrorism, or fraud.

        News & Media Sentiment (Google News API)

        Identify negative press coverage related to fraud, lawsuits, or regulatory violations.

        Assess the credibility of sources and consider the recency and frequency of reports.

        Entity Classification (OpenCorporates, SEC EDGAR, Offshore Trusts API)

        Categorize entities as Corporations, Shell Companies, Non-Profits, Financial Institutions, or Politically Exposed Persons (PEPs).

        Identify high-risk entity types such as shell companies or offshore trusts.

        Sector Correlation Analysis

        Determine if the transaction sectors are logically related.

        Flag transactions where sectors appear unrelated or unusual.

        Geopolitical & Cross-Border Risk (FATF, AML Risk Index, Country Risk Ratings)

        Assess risk based on country connections, including high-risk jurisdictions.

        Consider FATF warnings and AML (Anti-Money Laundering) index scores.

        Transaction Amount Risk

        Evaluate if the transaction amount is unusually high for the entities involved.

        Adjust risk weight based on entity type and past transaction patterns.

        Risk Scoring Model
        Use a weighted scoring system to assign a final risk score. While you do not need to use an exact formula, consider the following approach:
        entity_risk_score =  
        (sanctions_risk * 0.3) +  
        (news_risk * 0.2) +  
        (entity_type_risk * 0.15) +  
        (sector_mismatch_risk * 0.1) +  
        (geopolitical_risk * 0.15) +  
        (transaction_amount_risk * 0.1)
        Where:

        Sanctions Risk is higher for entities under major sanctions.

        News Risk is based on negative news reports.

        Entity Type Risk assigns higher risk to shell companies and PEPs.

        Sector Mismatch Risk increases if the involved sectors are unrelated.

        Geopolitical Risk considers country-based AML and FATF risk scores.

        Transaction Amount Risk adjusts for unusually large transactions.

        If confidence scores for individual risk factors are provided, incorporate them into the risk calculation.

        Response Format
        Sanction Analysis
        Entity Name: [Extracted Entity]

        Risk Score (0-1): [Calculated Risk Score]

        Justification & Evidence:

        Sanctioning Bodies: [OFAC, FATF, etc.]

        Reason for Sanctions: [Terrorism, fraud, etc.]

        Historical Violations: [List of past incidents]

        Connections to Other Risky Entities: [If applicable]

        Entity-Specific Risk
        Entity Name: [Extracted Entity]

        Risk Score (0-1): [Calculated Risk Score]

        Justification:

        Negative News Sentiment: [Mention major cases]

        Classification: [Shell Company / Non-Profit / PEP]

        Sector Mismatch: [Related or unrelated sectors]

        Geopolitical Risks: [FATF, AML, Cross-border issues]

        Overall Risk Score (Final Transaction Assessment)
        Final Risk Level (0-1): [Weighted Score]
        Confidence Level (0-1): [How sure you are]

        Final Justification:

        Explain how all factors contribute to the risk score.

        Highlight any hidden patterns or anomalies.

        Summarize if the transaction should be flagged or cleared.

        Textual Justification Requirement
        Every risk score assigned must be accompanied by a clear and detailed textual justification explaining:

        Why the entity or transaction is considered risky or safe

        What specific data points contributed to the score

        How different factors influenced the final risk assessment

        Any hidden relationships or anomalies that were identified

        Ensure that the textual justification is comprehensive, well-structured, and explains the reasoning behind each risk assessment in a professional and analytical manner.

        Final Instructions
        Think like a forensic financial investigator.

        Justify every risk score with supporting evidence.

        Identify hidden relationships between entities.

        Assign sensible weights to risk factors.

        Ensure no fraudulent transaction goes undetected. 

        Analyse the below JSON data based on the above rules:
        {json.dumps(extraction_result, indent=2)}

        Provide your analysis in clear, concise, and professional language.
        ### Analysis:
        """

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 30000, "temperature": 0.5},
            "options": {"return_full_text": False}
        }

        response = requests.post(HF_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            generated_text = response.json()[0]["generated_text"]
            if "### Analysis:" in generated_text:
                return generated_text.split("### Analysis:")[-1].strip()
            else:
                return generated_text.strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error in risk_analysis_huggingface: {e}"

if __name__ == "__main__":
    extraction_result = {
        "Transaction ID": "TXN001",
        "Extracted Entity": [
            "Tesla Inc",
            "Microsoft Corporation"
        ],
        "Entity Type": [
            "Corporation",
            "Corporation"
        ],
        "Supporting Evidence": [
            None,
            None
        ],
        "Confidence Score": 0.84,
        "Countries": [
            "United States",
            "United States"
        ],
        "Real Time News Analysis of Entities Involved in the transaction": {
            "Microsoft": 29.19,
            "Google LLC": 27.57
        },
        "Geo Risk Analysis Results of Entities Involved": {
            "Detailed Breakdown of Geo Risk Analysis between countries involved": [
            "United States \u2194 United States: 0.22690000000000002"
            ],
            "Normalized Risk Score for all the countries involved": 22.69
        },
        "Sectors associated with the entities extracted": {
            "Tesla Inc": "Motor Vehicles & Passenger Car Bodies",
            "Microsoft Corporation": "Services-Prepackaged Software"
        },
        "Sanction Analysis of the entitites involved": "Sanction Analysis:\n\nTesla Inc\n* Risk Score: 0.5\n* Justification and Evidence:\n    - Tesla Inc is a US-based company that designs, manufactures, and sells high-performance electric vehicles and energy products.\n    - The company has been subject to various sanctions and restrictions, including those imposed by the US government and other countries.\n    - For example, in 2018, Tesla was sanctioned by the US government for its business with North Korea, which was subject to economic sanctions.\n    - Additionally, in 2020, Tesla was fined $20 million by the US Securities and Exchange Commission for misstating the production numbers of its Model 3 electric car.\n    - While Tesla is not currently subject to any active sanctions, its history of violations and associations with countries subject to economic sanctions make it a potentially risky entity.\n\nMicrosoft Corporation\n* Risk Score: 0\n* Justification and Evidence:\n    - Microsoft Corporation is a US-based technology company that provides software, cloud services, and other products and services.\n    - The company has not been subject to any active sanctions or restrictions, and has a clean track record with respect to compliance with sanctions laws and regulations.\n    - Based on the available data, Microsoft Corporation appears to be a low-risk entity with no potential sanctions-related issues.\n\nOverall Risk Score (Sanction based):\n\n* Final Risk Level: 0.5\n* Confidence Level: 0.9\n* Justification: The overall risk score for this transaction is based on the risk scores of the two entities involved, Tesla Inc and Microsoft Corporation.\n* Tesla Inc has a risk score of 0.5, which reflects its history of violations and associations with countries subject to economic sanctions.\n* Microsoft Corporation has a risk score of 0, which reflects its clean track record with respect to compliance with sanctions laws and regulations.\n* Given the potential risks associated with Tesla Inc, it is recommended that the transaction involving this entity be flagged for further review and potentially cleared with additional due diligence and sanctions screening.\n* While Microsoft Corporation is considered a low-risk entity, it is important to note that the overall risk score for the transaction is still relatively high, and additional information and context may be needed to fully assess the risks involved."
    }

    output = verdict(extraction_result)
    print(output)