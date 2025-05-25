# streamlit_app.py
import streamlit as st
from agent import ask_agent

st.set_page_config(page_title="LifeMoves Policy Assistant", layout="centered")

st.title("📘 LifeMoves Policy Generator")
st.caption("AI assistant for trauma-informed, framework-aligned policy writing.")

# Persistent session thread ID (for memory / LangGraph)
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = "lifemoves-demo"

# Input box
query = st.text_area("Enter your policy request or question:", height=150, placeholder="e.g., Create a visitor policy for family shelters.")

# Run on button click
if st.button("Generate Policy"):
    if query.strip():
        with st.spinner("Drafting policy with Claude..."):
            try:
                response = ask_agent(query, thread_id=st.session_state["thread_id"])
                st.markdown("### 🧠 AI-Generated Policy")
                st.markdown(response)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question or policy instruction.")
