import faiss
import numpy as np
import pickle
import os

VECTOR_DB_PATH = "vector_store/index.faiss"
METADATA_PATH = "vector_store/metadata.pkl"

def save_vector_store(embeddings, chunks):
    # Create the FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    # Save the index file
    if not os.path.exists("vector_store"):
        os.makedirs("vector_store")
        
    faiss.write_index(index, VECTOR_DB_PATH)
    
    # Save the text chunks separately (FAISS only stores numbers)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(chunks, f)
        
    print("Vector store saved successfully!")

def load_vector_store():
    if not os.path.exists(VECTOR_DB_PATH):
        return None, None
    
    index = faiss.read_index(VECTOR_DB_PATH)
    with open(METADATA_PATH, "rb") as f:
        chunks = pickle.load(f)
        
    return index, chunks