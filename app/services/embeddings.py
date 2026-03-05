from sentence_transformers import SentenceTransformer
from app.utils.logging_config import setup_logging

logger = setup_logging()
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(chunks):
    logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    texts = [c["chunk_text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings