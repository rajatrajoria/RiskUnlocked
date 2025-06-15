import streamlit as st
import json
import ollama
import os
import torch

from main import app 
from voice import text_to_speech
torch.classes.__path__ = []

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",".."))
data_file = os.path.join(root_dir, "datasets", "result.json")  

def load_risk_data():
    try:
        if not os.path.exists(data_file):
            raise FileNotFoundError("result.json file not found.")
        with open(data_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"error": "Please enter input transaction data."}


def extract_risk_context(risk_data):
    if isinstance(risk_data, dict) and "error" in risk_data:
        return risk_data["error"]
    
    context = ""
    if isinstance(risk_data, list) and risk_data:
        for item in risk_data:
            findings = item.get("Findings", {})
            transaction_id = findings.get("Transaction ID", "Unknown Transaction")
            context += f"\nTransaction ID: {transaction_id}\n"
            
            entities = findings.get("Extracted Entity", [])
            entity_types = findings.get("Entity Type", [])
            if entities:
                context += "Entities:\n"
                for name, etype in zip(entities, entity_types):
                    context += f"  - {name} ({etype})\n"
            
            news_analysis = findings.get("Real Time News Analysis of Entities Involved in the transaction", {})
            if news_analysis:
                context += "Real Time News Analysis:\n"
                for key, value in news_analysis.items():
                    context += f"  - {key}: {value}\n"
            
            sanction_analysis = findings.get("Sanction Analysis", "N/A")
            context += f"Sanction Analysis: {sanction_analysis}\n"
            context += "\n"
        return context.strip()
    else:
        return "Please enter input transaction data."

def get_chatbot_response(user_input, risk_context):
    if risk_context == "Please enter input transaction data.":
        return risk_context  # Prevents empty response issues
    
    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "system", "content": "You are a financial risk assessment chatbot. Use the provided risk analysis data to answer user questions accurately."},
            {"role": "user", "content": f"Context:\n{risk_context}\n\nUser: {user_input}"}
        ])
        return response["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


risk_data = load_risk_data()
risk_context = extract_risk_context(risk_data)

st.set_page_config(page_title="RiskUnlocked", layout="wide")


st.markdown(
    """
    <style>
        body { background-color: #121212; color: #ff4c4c; }
        .stTextArea textarea, .stTextInput input { background-color: #1e1e1e !important; color: #ff4c4c !important; border: 1px solid #ff4c4c !important; }
        .stButton button { background-color: #ff4c4c !important; color: white !important; font-size: 16px !important; font-weight: bold !important; }
        .stButton button:hover { background-color: #d43f3f !important; }
        .stMarkdown h1, .stMarkdown h2 { color: #ff4c4c; }
        pre {
            overflow-x: hidden;
            white-space: pre-wrap;
            word-break: break-all;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
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

            justification = app(transaction_text)

            st.markdown("<h2>Risk Analysis Result</h2>", unsafe_allow_html=True)
            
            justification_str = json.dumps(justification, indent=4, ensure_ascii=False)
            # Replace the literal "\n" (which appears as "\\n" in the string) with actual newlines
            justification_str = justification_str.replace("\\n", "\n")
            st.markdown("**Justification:**")
            st.markdown(f"```\n{justification_str}\n```")

if st.button("Read out loud"):
    if justification_str != "":
        text_to_speech(justification_str)
    else:
         st.error("Get an output first")


# Chatbot UI (Right Floating Chatbox)
st.sidebar.markdown("<h2>💬 RiskUnlocked Chatbot</h2>", unsafe_allow_html=True)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.sidebar.markdown(f"👤 **User:** {chat['content']}")
    else:
        st.sidebar.markdown(f"🤖 **RiskUnlocked:** {chat['content']}")


chat_input = st.sidebar.text_input("Ask me anything about the risk analysis:")


if st.sidebar.button("Send"):
    if chat_input.strip() == "":
        st.sidebar.error("Please enter a message.")
    else:
        with st.spinner("Thinking..."):
            bot_response = get_chatbot_response(chat_input, risk_context)
            st.session_state.chat_history.append({"role": "user", "content": chat_input})
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            st.rerun()  
