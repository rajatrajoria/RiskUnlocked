import streamlit as st
import json
import time
import random

def analyze_transaction(transaction_text):
    time.sleep(2)  
    response_back = process_transaction(transaction_text)
    print(response_back)
    return risk_score, justification

st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: #ff4c4c;
        }
        .stTextArea textarea, .stTextInput input {
            background-color: #1e1e1e !important;
            color: #ff4c4c !important;
            border: 1px solid #ff4c4c !important;
        }
        .stButton button {
            background-color: #ff4c4c !important;
            color: white !important;
            font-size: 16px !important;
            font-weight: bold !important;
        }
        .stButton button:hover {
            background-color: #d43f3f !important;
        }
        .stMarkdown h1, .stMarkdown h2 {
            color: #ff4c4c;
        }
        .result-box {
            border: 2px solid #ff4c4c;
            padding: 15px;
            border-radius: 8px;
            background-color: #1e1e1e;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1>🔍 RiskUnlocked</h1>", unsafe_allow_html=True)

st.markdown("#### Enter a transaction record (JSON or plain text)")
transaction_input = st.text_area("Paste transaction data here", height=150)

if st.button("Analyze Transaction 🚀"):
    if transaction_input.strip() == "":
        st.error("Please enter a transaction record.")
    else:
        with st.spinner("Processing transaction..."):
            try:
                parsed_input = json.loads(transaction_input)
                transaction_text = json.dumps(parsed_input, indent=2)
            except json.JSONDecodeError:
                transaction_text = transaction_input 

            risk_score, justification = analyze_transaction(transaction_text)

            st.markdown("<h2>🛑 Risk Analysis Result</h2>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="result-box">
                    <p><b>⚠ Risk Score:</b> {risk_score}</p>
                    <p><b>📜 Justification:</b> {justification}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
