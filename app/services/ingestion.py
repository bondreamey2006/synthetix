from __future__ import annotations

import re
from pathlib import Path
from threading import RLock
from PyPDF2 import PdfReader
from app.config import settings
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embeddings
from app.services.vector_store import clear_vector_store, save_vector_store
from app.utils.logging_config import setup_logging

logger = setup_logging()
_INDEX_BUILD_LOCK = RLock()


def extract_text_from_pdf(file_path: Path) -> str:
    text = ""
    try:
        reader = PdfReader(str(file_path))
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    except Exception as exc:
        logger.error(f"Error reading PDF {file_path.name}: {exc}")
    return text


def _safe_filename(filename: str) -> str:
    base = Path(filename).name
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "_", base)
    return cleaned or "uploaded_file"


def get_docs_path(docs_folder: str | None = None, user_id: str | None = None) -> Path:
    base = Path(docs_folder or settings.docs_folder)
    folder = base / user_id if user_id else base
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def is_allowed_file(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in settings.allowed_upload_extensions


def load_documents(docs_folder: str | None = None, user_id: str | None = None) -> list[dict]:
    docs_path = get_docs_path(docs_folder, user_id=user_id)
    documents: list[dict] = []

    for file_path in docs_path.iterdir():
        if not file_path.is_file() or not is_allowed_file(file_path.name):
            continue

        content = ""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            content = extract_text_from_pdf(file_path)
        elif suffix in {".txt", ".md"}:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception as exc:
                logger.error(f"Error reading {file_path.name}: {exc}")

        if content.strip():
            documents.append(
                {
                    "content": content,
                    "metadata": {"document_name": file_path.name},
                }
            )
            logger.info(f"Loaded: {file_path.name}")

    return documents


def save_uploaded_file(filename: str, data: bytes, docs_folder: str | None = None, user_id: str | None = None) -> str:
    safe_name = _safe_filename(filename)
    docs_path = get_docs_path(docs_folder, user_id=user_id)
    target_path = docs_path / safe_name
    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1
    while target_path.exists():
        target_path = docs_path / f"{stem}_{counter}{suffix}"
        counter += 1

    target_path.write_bytes(data)
    return target_path.name


def build_vector_index(docs_folder: str | None = None, user_id: str | None = None) -> dict:
    with _INDEX_BUILD_LOCK:
        docs = load_documents(docs_folder, user_id=user_id)
        if not docs:
            clear_vector_store(namespace=user_id)
            return {
                "ingested_documents": 0,
                "generated_chunks": 0,
            }

        chunks = chunk_text(docs)
        if not chunks:
            raise ValueError("No chunks could be created from uploaded documents.")

        embeddings = generate_embeddings(chunks)
        save_vector_store(embeddings, chunks, namespace=user_id)
        return {
            "ingested_documents": len(docs),
            "generated_chunks": len(chunks),
        }


def list_document_files(docs_folder: str | None = None, user_id: str | None = None) -> list[str]:
    docs_path = get_docs_path(docs_folder, user_id=user_id)
    files = [
        path.name
        for path in docs_path.iterdir()
        if path.is_file() and is_allowed_file(path.name)
    ]
    files.sort()
    return files


def delete_documents(filenames: list[str], docs_folder: str | None = None, user_id: str | None = None) -> dict:
    with _INDEX_BUILD_LOCK:
        docs_path = get_docs_path(docs_folder, user_id=user_id)
        deleted: list[str] = []
        for name in filenames:
            safe_name = _safe_filename(name)
            target = docs_path / safe_name
            if target.exists() and target.is_file():
                target.unlink()
                deleted.append(target.name)

        result = build_vector_index(docs_folder, user_id=user_id)
        return {
            "deleted_files": deleted,
            "remaining_files": list_document_files(docs_folder, user_id=user_id),
            "ingested_documents": result["ingested_documents"],
            "generated_chunks": result["generated_chunks"],
        }


def clear_all_documents(docs_folder: str | None = None, user_id: str | None = None) -> dict:
    with _INDEX_BUILD_LOCK:
        docs_path = get_docs_path(docs_folder, user_id=user_id)
        deleted: list[str] = []
        for path in docs_path.iterdir():
            if path.is_file() and is_allowed_file(path.name):
                path.unlink()
                deleted.append(path.name)

        clear_vector_store(namespace=user_id)
        return {
            "deleted_files": sorted(deleted),
            "remaining_files": [],
            "ingested_documents": 0,
            "generated_chunks": 0,
        }
