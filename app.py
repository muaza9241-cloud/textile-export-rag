import os
import pickle
import chromadb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rank_bm25 import BM25Okapi

app = FastAPI(title="Textile Export RAG API")

CHROMA_DB_DIR = "data/chroma_db"
BM25_INDEX_PATH = "data/bm25_index.pkl"

# Load ChromaDB Client
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = chroma_client.get_collection(name="export_docs")

# Load BM25 Index
bm25_data = {}
if os.path.exists(BM25_INDEX_PATH):
    with open(BM25_INDEX_PATH, "rb") as f:
        bm25_data = pickle.load(f)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get("/")
def home():
    return {"message": "Textile Export RAG API is running!"}

@app.post("/search")
def search(request: QueryRequest):
    query = request.query
    top_k = request.top_k

    # Dense Retrieval (ChromaDB Vector Search)
    vector_results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    # Sparse Retrieval (BM25 Keyword Search)
    bm25_results = []
    if "bm25" in bm25_data:
        bm25_index = bm25_data["bm25"]
        tokenized_query = query.lower().split()
        scores = bm25_index.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        for idx in top_indices:
            bm25_results.append({
                "doc_id": bm25_data["ids"][idx],
                "document": bm25_data["documents"][idx],
                "metadata": bm25_data["metadatas"][idx],
                "score": float(scores[idx])
            })

    return {
        "query": query,
        "vector_search_results": vector_results,
        "keyword_search_results": bm25_results
    }