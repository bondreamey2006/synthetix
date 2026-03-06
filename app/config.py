import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    docs_folder: str = os.getenv("DOCS_FOLDER", "docs")
    vector_store_dir: str = os.getenv("VECTOR_STORE_DIR", "vector_store")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    generation_model_name: str = os.getenv("GENERATION_MODEL_NAME", "google/flan-t5-base")
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    min_relevance_score: float = float(os.getenv("MIN_RELEVANCE_SCORE", "0.25"))
    min_claim_support_score: float = float(os.getenv("MIN_CLAIM_SUPPORT_SCORE", "0.35"))
    min_answer_score: float = float(os.getenv("MIN_ANSWER_SCORE", "0.52"))
    max_question_chars: int = int(os.getenv("MAX_QUESTION_CHARS", "1000"))
    snippet_chars: int = int(os.getenv("SNIPPET_CHARS", "140"))
    max_upload_files: int = int(os.getenv("MAX_UPLOAD_FILES", "10"))
    max_upload_file_mb: int = int(os.getenv("MAX_UPLOAD_FILE_MB", "15"))
    allowed_upload_extensions: tuple[str, ...] = tuple(
        ext.strip().lower()
        for ext in os.getenv("ALLOWED_UPLOAD_EXTENSIONS", ".txt,.md,.pdf").split(",")
        if ext.strip()
    )
    session_secret: str = os.getenv("SESSION_SECRET", "change-this-in-production")
    session_max_age_seconds: int = int(os.getenv("SESSION_MAX_AGE_SECONDS", "2592000"))
    hf_token: str | None = os.getenv("HF_TOKEN")
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000",
        ).split(",")
        if origin.strip()
    )
    allowed_hosts: tuple[str, ...] = tuple(
        host.strip()
        for host in os.getenv("ALLOWED_HOSTS", "*").split(",")
        if host.strip()
    )


settings = Settings()
