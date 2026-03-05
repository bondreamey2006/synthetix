from fastapi import APIRouter
from app.models.schemas import QuestionRequest, QueryResponse
from app.services.rag_pipeline import run_rag_pipeline

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QuestionRequest):
    # Get the raw results from your pipeline
    result = run_rag_pipeline(request.question)
    
    # Return exactly the keys you requested
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "confidence": result["confidence"]
    }