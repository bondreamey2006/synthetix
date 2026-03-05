from pydantic import BaseModel
from typing import List

class QuestionRequest(BaseModel):
    question: str

class SourceCitation(BaseModel):
    document: str
    snippet: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    confidence: str