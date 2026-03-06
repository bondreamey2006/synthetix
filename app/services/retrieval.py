from app.config import settings
from app.services.embeddings import get_embedding_model
from app.services.vector_store import load_vector_store
from app.utils.helpers import clean_text


def retrieve_context(query, k=None, namespace: str | None = None):
    top_k = k or settings.retrieval_top_k
    if top_k <= 0:
        top_k = 1

    try:
        index, chunks = load_vector_store(namespace=namespace)
        if index is None or not chunks:
            return []

        model = get_embedding_model()
        query_vector = model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        similarities, indices = index.search(query_vector, top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue

            chunk = chunks[idx]
            score = max(0.0, min(1.0, float(similarities[0][i])))
            results.append(
                {
                    "chunk_text": clean_text(chunk["chunk_text"]),
                    "document": chunk["metadata"]["document_name"],
                    "sentences": [clean_text(s) for s in chunk["metadata"].get("sentences", []) if clean_text(s)],
                    "score": round(score, 4),
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results
    except Exception:
        return []
