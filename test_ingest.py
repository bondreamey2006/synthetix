from app.services.ingestion import load_documents
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embeddings
from app.services.vector_store import save_vector_store

docs = load_documents()
chunks = chunk_text(docs)
embeddings = generate_embeddings(chunks)
save_vector_store(embeddings, chunks)