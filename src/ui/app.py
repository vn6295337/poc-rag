# src/ui/app.py
import streamlit as st
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.orchestrator import orchestrate_query

st.title("RAG MVP — Query Interface")

query = st.text_input("Enter your question:")

if st.button("Run Query"):
    if not query.strip():
        st.error("Enter a query.")
    else:
        result = orchestrate_query(query, top_k=3)
        st.subheader("Answer")
        st.write(result.get("answer", ""))

        st.subheader("Citations")
        for c in result.get("citations", []):
            st.write(f"ID: {c['id']} | Score: {c['score']:.4f}")

        # Debug View (raw pipeline output)
        st.subheader("Debug View")
        with st.expander("Show raw pipeline output"):
            st.json(result)

