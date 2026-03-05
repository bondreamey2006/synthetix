from app.services.retrieval import retrieve_context
from app.services.answer_generation import generate_answer

def run_rag_pipeline(question):
    # 1. Semantic Retrieval
    context_chunks = retrieve_context(question)
    
    if not context_chunks:
        return {"answer": "No info found.", "sources": [], "confidence": "low"}
    
    # 2. Confidence Calculation (High > 0.7, Medium > 0.4)
    max_score = max([c['score'] for c in context_chunks])
    confidence = "high" if max_score > 0.7 else "medium" if max_score > 0.4 else "low"
        
    # 3. Generate the answer paragraph
    answer = generate_answer(question, context_chunks)
    
    # 4. Format to match schemas.py exactly (mapping 'chunk_text' to 'snippet')
    formatted_sources = [
        {"document": c["document"], "snippet": c["chunk_text"], "score": c["score"]} 
        for c in context_chunks
    ]
    
    return {
        "answer": answer,
        "sources": formatted_sources,
        "confidence": confidence
    }