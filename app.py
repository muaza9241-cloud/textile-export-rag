import streamlit as st
import requests

# Page Config
st.set_page_config(page_title="Textile Export RAG", layout="wide")

st.title("🧵 Textile Export RAG System")
st.write("Search textile export data, queries, and document embeddings:")

# Render API URL
BACKEND_URL = "https://textile-export-rag.onrender.com/query"

# Search Input Box
query = st.text_input("Enter your query:", placeholder="e.g., What are the top cotton export regulations?")

if query:
    with st.spinner("Searching backend knowledge base..."):
        try:
            # Send request to Render Backend
            response = requests.post(BACKEND_URL, json={"query": query})
            
            if response.status_code == 200:
                result = response.json()
                st.success("Results Retrieved!")
                st.subheader("Answer / Context:")
                st.write(result.get("answer", result))
            else:
                st.error(f"Backend Error: {response.status_code}")
        except Exception as e:
            st.error(f"Could not connect to backend API: {e}")
