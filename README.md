# Document Q&A RAG System

A production-quality Retrieval-Augmented Generation (RAG) system built with FastAPI, FAISS, and Hugging Face Transformers.

## Features
- **Document Ingestion:** Supports PDF, TXT, and MD.
- **Vector Search:** Uses FAISS for high-speed retrieval.
- **LLM Integration:** Uses Flan-T5 for grounded answer generation.
- **Citations:** Returns document sources and confidence scores.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Place documents in the `docs/` folder.
3. Run ingestion: `python test_ingest.py`
4. Start API: `uvicorn app.main:app --reload`