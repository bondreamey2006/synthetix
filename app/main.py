from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.routes import router as api_router
from app.config import settings
from app.services.ingestion import build_vector_index, load_documents
from app.services.vector_store import load_vector_store
from app.utils.logging_config import setup_logging

app = FastAPI(title="Document Q&A RAG System", version="1.0.0")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "web" / "static"
INDEX_FILE = BASE_DIR / "web" / "templates" / "index.html"
logger = setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    max_age=settings.session_max_age_seconds,
    same_site="lax",
    https_only=False,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))

# This connects your /ask endpoint to the main app
app.include_router(api_router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def ensure_index_on_startup():
    try:
        index, chunks = load_vector_store()
        if index is not None and chunks:
            return

        docs = load_documents()
        if docs:
            build_vector_index()
            logger.info("Vector index built at startup.")
    except Exception:
        logger.exception("Startup indexing failed; app will continue and fallback safely.")

@app.get("/", response_class=HTMLResponse)
def root():
    return INDEX_FILE.read_text(encoding="utf-8")


@app.get("/health")
def health():
    index, chunks = load_vector_store()
    return {
        "status": "ok",
        "indexed_documents": bool(index is not None and chunks),
    }
