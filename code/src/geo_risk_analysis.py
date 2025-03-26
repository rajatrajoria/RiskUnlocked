import pandas as pd
import os

DEFAULT_CPI = 50    
DEFAULT_AML = 5.0   
DEFAULT_GTI = 2.5  

FATF_BLACK_PENALTY = 20
FATF_GREY_PENALTY = 10

# **Determine Path (Move 2 Levels Up to Root)**
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
datasets_dir = os.path.join(root_dir, "datasets")

# **Load Corruption Perceptions Index (CPI) Data**
def load_cpi_data():
    filepath = os.path.join(datasets_dir, "cpi.csv")
    cpi_df = pd.read_csv(filepath)
    cpi_df.rename(columns={"Jurisdiction": "Country"}, inplace=True)
    cpi_df = cpi_df.set_index("Country").apply(pd.to_numeric, errors='coerce')
    cpi_df.fillna(DEFAULT_CPI, inplace=True)  
    latest_year = max(cpi_df.columns)  
    return cpi_df[latest_year].to_dict(), latest_year

# **Load AML Data**
def load_aml_data():
    filepath = os.path.join(datasets_dir, "aml.csv")
    aml_df = pd.read_csv(filepath)
    aml_df.rename(columns={"Country": "Country"}, inplace=True)
    aml_df.set_index("Country", inplace=True)
    aml_df["Score"] = pd.to_numeric(aml_df["Score"], errors='coerce').fillna(DEFAULT_AML)
    return aml_df["Score"].to_dict()

# **Load Global Terrorism Index (GTI) Data**
def load_gti_data():
    filepath = os.path.join(datasets_dir, "gti.csv")
    gti_df = pd.read_csv(filepath)
    gti_df.rename(columns={"Country": "Country"}, inplace=True)
    gti_df.set_index("Country", inplace=True)
    gti_df["Score"] = pd.to_numeric(gti_df["Score"], errors='coerce').fillna(DEFAULT_GTI)
    return gti_df["Score"].to_dict()

# **Load FATF List Data**
def load_fatf_data():
    filepath = os.path.join(datasets_dir, "fatf.csv")
    fatf_df = pd.read_csv(filepath)
    return fatf_df.set_index("Countries")["Category"].to_dict()  

# **Risk Calculation Function**
def calculate_transaction_risk(country1, country2, cpi_scores, aml_scores, gti_scores, fatf_list):
    cpi1, cpi2 = cpi_scores.get(country1, DEFAULT_CPI), cpi_scores.get(country2, DEFAULT_CPI)
    aml1, aml2 = aml_scores.get(country1, DEFAULT_AML), aml_scores.get(country2, DEFAULT_AML)
    gti1, gti2 = gti_scores.get(country1, DEFAULT_GTI), gti_scores.get(country2, DEFAULT_GTI)

    cpi_risk1, cpi_risk2 = 100 - cpi1, 100 - cpi2
    avg_cpi_risk = (cpi_risk1 + cpi_risk2) / 2
    avg_aml_risk = (aml1 + aml2) / 2
    avg_gti_risk = (gti1 + gti2) / 2

    transaction_risk = (0.4 * avg_cpi_risk) + (0.3 * avg_aml_risk) + (0.3 * avg_gti_risk)

    fatf_penalty = 0
    for country in [country1, country2]:
        if country in fatf_list:
            if fatf_list[country] == "Black":
                fatf_penalty += FATF_BLACK_PENALTY
            elif fatf_list[country] == "Grey":
                fatf_penalty += FATF_GREY_PENALTY

    transaction_risk += fatf_penalty
    return round(transaction_risk, 2)


def geo_risk_analysis(countries):

    cpi_scores, latest_year = load_cpi_data()
    aml_scores = load_aml_data()
    gti_scores = load_gti_data()
    fatf_list = load_fatf_data()

    total_risk = 0
    risk_details = []

    for i in range(len(countries) - 1):
        country1, country2 = countries[i], countries[i + 1]
        risk_score = calculate_transaction_risk(country1, country2, cpi_scores, aml_scores, gti_scores, fatf_list)
        total_risk += risk_score
        risk_details.append(f"{country1} ↔ {country2}: {risk_score/100}")

    max_possible_score = (len(countries) - 1) * 100  
    normalized_score = (total_risk / max_possible_score) * 100  
    normalized_score = round(min(normalized_score, 100), 2)  

    return {
        "Detailed Breakdown of Geo Risk Analysis between countries involved": risk_details,
        "Normalized Risk Score for all the countries involved": normalized_score
    }


if __name__ == "__main__":
    print(geo_risk_analysis(["Iran", "Pakistan"]))
