from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="Document Q&A RAG System", version="1.0.0")

# This connects your /ask endpoint to the main app
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "RAG System is Online. Go to /docs for the API interface."}