import streamlit as st
# Apne existing RAG search function ko direct import karein
# (Apni file structure ke hisaab se path adjust kar sakte hain)
try:
    from api.main import perform_rag_search # ya jo aapka main search logic function hai
except ImportError:
    perform_rag_search = None

st.title("🧵 Textile Export RAG System")
st.write("Search textile export data, queries, and document embeddings:")

query = st.text_input("Enter your query:", placeholder="e.g., What are the top cotton export regulations?")

if query:
    with st.spinner("Searching export data..."):
        try:
            # Direct Python execution - No backend HTTP requests needed!
            if perform_rag_search:
                response = perform_rag_search(query)
                st.success("Results Retrieved Successfully!")
                st.write(response)
            else:
                st.error("Search module load nahi ho saka. Path verify karein.")
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
