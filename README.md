# SmartQnA - Document Q&A RAG System

FastAPI + FAISS RAG web app that answers only from provided documents and returns citations.

## Features
- Upload multiple `.txt`, `.md`, `.pdf` documents directly from the web UI
- Manage uploaded files from the UI (refresh, delete selected, clear all)
- Session-isolated user workspaces (uploads and index are separated per browser session)
- Chunk + embed using `sentence-transformers/all-MiniLM-L6-v2`
- FAISS cosine-similarity retrieval
- Claim-grounded answer generation with `google/flan-t5-base`
- Mandatory fallback when answer is not found
- Claim-level full-sentence citations with similarity score

## Security Defaults
- Request question length is validated server-side
- Backend does not log user question contents by default
- Frontend does not display raw backend error payloads
- CORS + Trusted Host restrictions are enabled via environment variables

## Quick Start
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Start API server:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
3. Open `http://127.0.0.1:8000` in your browser.
4. Upload files from the UI using "Upload and Index".
5. Ask questions once indexing completes.

## Environment Variables
- `DOCS_FOLDER` (default: `docs`)
- `VECTOR_STORE_DIR` (default: `vector_store`)
- `RETRIEVAL_TOP_K` (default: `5`)
- `MIN_RELEVANCE_SCORE` (default: `0.25`)
- `MIN_CLAIM_SUPPORT_SCORE` (default: `0.35`)
- `MIN_ANSWER_SCORE` (default: `0.52`)
- `MAX_QUESTION_CHARS` (default: `1000`)
- `MAX_UPLOAD_FILES` (default: `10`)
- `MAX_UPLOAD_FILE_MB` (default: `15`)
- `ALLOWED_UPLOAD_EXTENSIONS` (default: `.txt,.md,.pdf`)
- `ALLOWED_ORIGINS` (default: `http://localhost:8000,http://127.0.0.1:8000`)
- `ALLOWED_HOSTS` (default: `*`)
- `SESSION_SECRET` (default: `change-this-in-production`)
- `SESSION_MAX_AGE_SECONDS` (default: `2592000`)
- `HF_TOKEN` (optional, recommended for faster Hugging Face downloads)

## Deployment Notes
- Run behind HTTPS reverse proxy (Nginx/Caddy/Cloudflare).
- Configure `ALLOWED_HOSTS` to your real domain.
- Configure `ALLOWED_ORIGINS` to your real frontend origin.
- Keep uploaded files on persistent storage (mounted disk/object store) in production.
- For multi-worker deployments, keep one shared `DOCS_FOLDER` and `VECTOR_STORE_DIR`.
- Set a strong `SESSION_SECRET` in production.

## MongoDB Setup (Metadata Only)
This project currently stores uploaded files and vector indexes on disk.  
Use MongoDB to store metadata and tracking data.

1. Create MongoDB instance:
- Use MongoDB Atlas free tier (or local MongoDB).
- Create database: `smartqna`.
- Create DB user and password.

2. Get your connection string:
- Example: `mongodb+srv://<user>:<password>@<cluster>/smartqna?retryWrites=true&w=majority`

3. Add environment variables:
- `MONGODB_URI=<your_connection_string>`
- `MONGODB_DB=smartqna`

4. Install MongoDB client dependency:
```bash
pip install pymongo[srv]
```

5. Recommended collections:
- `documents`
- `indexes`
- `queries`
- `sessions` (optional)
- `users` (optional, if login is added)

6. Recommended `documents` fields:
- `user_id`
- `filename`
- `stored_path`
- `mime_type`
- `size_bytes`
- `uploaded_at`
- `status` (`uploaded`, `indexed`, `deleted`, `failed`)
- `chunk_count`

7. Recommended `indexes` fields:
- `user_id`
- `vector_store_path`
- `doc_count`
- `updated_at`

8. Recommended `queries` fields:
- `user_id`
- `question`
- `answer`
- `score`
- `confidence`
- `source_docs`
- `created_at`

9. Suggested DB indexes:
- `documents`: `{ user_id: 1, filename: 1 }`
- `indexes`: `{ user_id: 1 }`
- `queries`: `{ user_id: 1, created_at: -1 }`

10. Integration flow:
- On upload: save file to disk + insert metadata in `documents`.
- On indexing complete: update `documents` status/chunk counts + upsert in `indexes`.
- On ask: log Q/A metadata in `queries`.
- On delete/clear: update/delete relevant `documents` and `indexes` metadata.
