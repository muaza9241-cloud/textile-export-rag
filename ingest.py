import os
import json
import pickle
from pypdf import PdfReader
import chromadb
from rank_bm25 import BM25Okapi

METADATA_PATH = "data/synthetic/metadata.json"
CHROMA_DB_DIR = "data/chroma_db"
BM25_INDEX_PATH = "data/bm25_index.pkl"

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        return ""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def main():
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    
    try:
        chroma_client.delete_collection("export_docs")
    except Exception:
        pass

    collection = chroma_client.create_collection(name="export_docs")

    print("Loading metadata.json...")
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    documents = []
    metadatas = []
    ids = []
    bm25_corpus = []

    print(f"Processing {len(metadata_list)} documents...")

    for idx, item in enumerate(metadata_list):
        doc_id = item.get("doc_id", f"DOC-{idx}")
        file_path = item.get("file_path", "")

        pdf_text = extract_text_from_pdf(file_path)
        
        if not pdf_text:
            pdf_text = f"Document Type: {item.get('doc_type', '')}, Shipment: {item.get('shipment_id', '')}, Port: {item.get('port', '')}"

        documents.append(pdf_text)
        metadatas.append(item)
        ids.append(doc_id)

        tokens = pdf_text.lower().split()
        bm25_corpus.append(tokens)

    print("Inserting documents into ChromaDB Vector Index...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully indexed {collection.count()} documents in ChromaDB!")

    print("Building BM25 Sparse Keyword Index...")
    bm25_index = BM25Okapi(bm25_corpus)
    
    os.makedirs("data", exist_ok=True)
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump({"bm25": bm25_index, "ids": ids, "documents": documents, "metadatas": metadatas}, f)
    
    print(f"BM25 index saved to {BM25_INDEX_PATH}")
    print("\nStep 1 Complete! Vector & Sparse Index build ho chuka hai.")

if __name__ == "__main__":
    main()