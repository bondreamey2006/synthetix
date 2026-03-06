from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.utils.logging_config import setup_logging

logger = setup_logging()


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model_name, token=settings.hf_token)

def generate_embeddings(chunks):
    logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    if not chunks:
        return []

    model = get_embedding_model()
    texts = [c["chunk_text"] for c in chunks]
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings
