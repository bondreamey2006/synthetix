from typing import List, Literal
from pydantic import BaseModel, Field
from app.config import settings

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=settings.max_question_chars)

class SourceCitation(BaseModel):
    document: str
    snippet: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    confidence: Literal["high", "medium", "low"]
    score: float = Field(..., ge=0.0, le=1.0)


class UploadResponse(BaseModel):
    saved_files: List[str]
    ingested_documents: int
    generated_chunks: int


class DocumentsListResponse(BaseModel):
    files: List[str]


class DeleteDocumentsRequest(BaseModel):
    filenames: List[str] = Field(default_factory=list)


class DeleteDocumentsResponse(BaseModel):
    deleted_files: List[str]
    remaining_files: List[str]
    ingested_documents: int
    generated_chunks: int
