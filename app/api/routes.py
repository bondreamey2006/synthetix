from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from app.models.schemas import (
    DeleteDocumentsRequest,
    DeleteDocumentsResponse,
    DocumentsListResponse,
    QuestionRequest,
    QueryResponse,
    UploadResponse,
)
from app.config import settings
from app.services.rag_pipeline import run_rag_pipeline
from app.services.ingestion import (
    build_vector_index,
    clear_all_documents,
    delete_documents,
    is_allowed_file,
    list_document_files,
    save_uploaded_file,
)
from app.utils.logging_config import setup_logging

router = APIRouter()
logger = setup_logging()


def _get_user_id(request: Request) -> str:
    user_id = request.session.get("user_id")
    if not user_id:
        user_id = uuid4().hex
        request.session["user_id"] = user_id
    return user_id

@router.post("/ask", response_model=QueryResponse)
async def ask_question(payload: QuestionRequest, request: Request):
    user_id = _get_user_id(request)
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if len(question) > settings.max_question_chars:
        raise HTTPException(
            status_code=400,
            detail=f"Question exceeds max length of {settings.max_question_chars} characters.",
        )

    try:
        result = run_rag_pipeline(question, namespace=user_id)
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "score": result["score"],
        }
    except Exception:
        logger.exception("Unhandled error in /ask route")
        raise HTTPException(
            status_code=500,
            detail="Unable to process the request right now.",
        )


@router.post("/upload-documents", response_model=UploadResponse)
async def upload_documents(request: Request, files: list[UploadFile] = File(...)):
    user_id = _get_user_id(request)
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    if len(files) > settings.max_upload_files:
        raise HTTPException(
            status_code=400,
            detail=f"Upload up to {settings.max_upload_files} files at a time.",
        )

    buffered_files: list[tuple[str, bytes]] = []
    max_file_bytes = settings.max_upload_file_mb * 1024 * 1024

    for file in files:
        filename = file.filename or ""
        if not filename or not is_allowed_file(filename):
            await file.close()
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type for '{filename}'. Allowed: {', '.join(settings.allowed_upload_extensions)}",
            )

        size = 0
        parts: list[bytes] = []
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > max_file_bytes:
                await file.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{filename}' exceeds {settings.max_upload_file_mb}MB.",
                )
            parts.append(chunk)
        await file.close()
        buffered_files.append((filename, b"".join(parts)))

    saved_files: list[str] = []
    try:
        for filename, data in buffered_files:
            saved_name = save_uploaded_file(filename, data, user_id=user_id)
            saved_files.append(saved_name)

        result = build_vector_index(user_id=user_id)
        return {
            "saved_files": saved_files,
            "ingested_documents": result["ingested_documents"],
            "generated_chunks": result["generated_chunks"],
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unhandled error in /upload-documents route")
        raise HTTPException(status_code=500, detail="Failed to process uploaded documents.")


@router.get("/documents", response_model=DocumentsListResponse)
async def list_documents(request: Request):
    user_id = _get_user_id(request)
    return {"files": list_document_files(user_id=user_id)}


@router.post("/documents/delete", response_model=DeleteDocumentsResponse)
async def delete_selected_documents(payload: DeleteDocumentsRequest, request: Request):
    user_id = _get_user_id(request)
    if not payload.filenames:
        raise HTTPException(status_code=400, detail="No filenames provided.")
    result = delete_documents(payload.filenames, user_id=user_id)
    return result


@router.post("/documents/clear", response_model=DeleteDocumentsResponse)
async def clear_documents(request: Request):
    user_id = _get_user_id(request)
    result = clear_all_documents(user_id=user_id)
    return result


@router.get("/session")
async def get_session(request: Request):
    user_id = _get_user_id(request)
    return {"user_id": user_id}
