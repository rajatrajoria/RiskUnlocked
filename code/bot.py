import streamlit as st
import json
import ollama
import os
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
# Paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_file = os.path.join(root_dir, "datasets", "result.json")  # JSON file storing risk analysis

# Load risk data from JSON
def load_risk_data():
    try:
        with open(data_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading risk data: {e}")
        return {}

# Extract context from JSON
def extract_risk_context(risk_data):
    context = ""
    if "transaction_risk_analysis" in risk_data:
        analysis = risk_data["transaction_risk_analysis"]
        for entity in analysis.get("entities", []):
            context += (
                f"\nEntity: {entity['name']}\n"
                f"Risk Score: {entity['risk_score']}\n"
                f"Sanctions: {entity['justification_and_evidence'].get('reason_for_sanctions', 'N/A')}\n"
                f"Additional Insights: {json.dumps(entity['justification_and_evidence'].get('additional_insights', {}), indent=2)}\n"
            )
    return context

# Generate chatbot response
def get_chatbot_response(user_input, risk_context):
    response = ollama.chat(model="mistral", messages=[
        {"role": "system", "content": "You are a financial risk assessment chatbot. Use the provided risk analysis data to answer user questions accurately."},
        {"role": "user", "content": f"Context:\n{risk_context}\n\nUser: {user_input}"}
    ])
    return response["message"]["content"]

# Load risk data
risk_data = load_risk_data()
risk_context = extract_risk_context(risk_data)

# Streamlit UI Layout
st.set_page_config(page_title="RiskyGPT", layout="wide")

# Custom Styling
st.markdown(
    """
    <style>
        body { background-color: #121212; color: #ff4c4c; }
        .stTextArea textarea, .stTextInput input { background-color: #1e1e1e !important; color: #ff4c4c !important; border: 1px solid #ff4c4c !important; }
        .stButton button { background-color: #ff4c4c !important; color: white !important; font-size: 16px !important; font-weight: bold !important; }
        .stButton button:hover { background-color: #d43f3f !important; }
        .stMarkdown h1, .stMarkdown h2 { color: #ff4c4c; }
        .chat-container { position: fixed; bottom: 20px; right: 20px; width: 300px; border: 2px solid #ff4c4c; padding: 10px; border-radius: 10px; background-color: #1e1e1e; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown("<h1>🔍 RiskyGPT</h1>", unsafe_allow_html=True)
st.markdown("#### Enter a transaction record (JSON or plain text)")

# User input for transactions
transaction_input = st.text_area("Paste transaction data here", height=150)

# Analyze Transaction Button
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

            # Mock risk analysis
            risk_score = 0.7  # Example score
            justification = "This transaction is flagged due to potential links with a high-risk entity in the sanctions database."

            st.markdown("<h2>🛑 Risk Analysis Result</h2>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="chat-container">
                    <p><b>⚠ Risk Score:</b> {risk_score}</p>
                    <p><b>📜 Justification:</b> {justification}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# Chatbot UI (Right Floating Chatbox)
st.sidebar.markdown("<h2>💬 RiskyGPT Chatbot</h2>", unsafe_allow_html=True)

# Store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous messages
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.sidebar.markdown(f"👤 **User:** {chat['content']}")
    else:
        st.sidebar.markdown(f"🤖 **RiskyGPT:** {chat['content']}")

# User input for chat
chat_input = st.sidebar.text_input("Ask me anything about the risk analysis:")

# Handle chat input
if st.sidebar.button("Send"):
    if chat_input.strip() == "":
        st.sidebar.error("Please enter a message.")
    else:
        with st.spinner("Thinking..."):
            bot_response = get_chatbot_response(chat_input, risk_context)
            
            # Store conversation history
            st.session_state.chat_history.append({"role": "user", "content": chat_input})
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

            # Refresh chat properly
            st.rerun()  # ✅ **Fixed: Proper rerun function**
