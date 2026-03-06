import faiss
import numpy as np
import pickle
import os
from pathlib import Path
from app.config import settings

VECTOR_DIR = Path(settings.vector_store_dir)


def _paths(namespace: str | None = None) -> tuple[Path, Path, Path]:
    namespace_dir = VECTOR_DIR / namespace if namespace else VECTOR_DIR
    vector_db_path = namespace_dir / "index.faiss"
    metadata_path = namespace_dir / "metadata.pkl"
    return namespace_dir, vector_db_path, metadata_path


def save_vector_store(embeddings, chunks, namespace: str | None = None):
    if len(chunks) == 0 or len(embeddings) == 0:
        raise ValueError("No embeddings/chunks available to save.")

    embeddings_np = np.array(embeddings).astype("float32")
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_np)

    namespace_dir, vector_db_path, metadata_path = _paths(namespace)
    namespace_dir.mkdir(parents=True, exist_ok=True)

    temp_index_path = vector_db_path.with_suffix(".tmp.faiss")
    temp_metadata_path = metadata_path.with_suffix(".tmp.pkl")

    faiss.write_index(index, str(temp_index_path))
    with open(temp_metadata_path, "wb") as f:
        pickle.dump(chunks, f)
    os.replace(temp_index_path, vector_db_path)
    os.replace(temp_metadata_path, metadata_path)

    print("Vector store saved successfully!")


def load_vector_store(namespace: str | None = None):
    _, vector_db_path, metadata_path = _paths(namespace)
    if not vector_db_path.exists() or not metadata_path.exists():
        return None, None

    index = faiss.read_index(str(vector_db_path))
    with open(metadata_path, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


def clear_vector_store(namespace: str | None = None):
    namespace_dir, vector_db_path, metadata_path = _paths(namespace)
    if vector_db_path.exists():
        vector_db_path.unlink()
    if metadata_path.exists():
        metadata_path.unlink()
    if namespace and namespace_dir.exists() and not any(namespace_dir.iterdir()):
        namespace_dir.rmdir()
