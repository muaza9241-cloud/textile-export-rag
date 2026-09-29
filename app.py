import streamlit as st

st.set_page_config(page_title="Textile Export RAG", layout="wide")

st.title("🧵 Textile Export RAG System")
st.write("Welcome! Search textile export data below:")

query = st.text_input("Enter your query:")
if query:
    st.info(f"Searching for: {query}")
    # Aapka retrieval backend code yahan connect hoga
