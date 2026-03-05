import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_context(query, k=5):
    try:
        # Load the index and metadata
        index = faiss.read_index("vector_store/index.faiss")
        with open("vector_store/metadata.pkl", "rb") as f:
            chunks = pickle.load(f)

        # Encode the user's question
        query_vector = model.encode([query]).astype('float32')
        
        # Search for matches
        distances, indices = index.search(query_vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                # Calculate a simple score (higher is better)
                score = float(1 / (1 + distances[0][i]))
                results.append({
                    "chunk_text": chunks[idx]["chunk_text"],
                    "document": chunks[idx]["metadata"]["document_name"],
                    "score": round(score, 2)
                })
        return results
    except Exception as e:
        print(f"Retrieval error: {e}")
        return []