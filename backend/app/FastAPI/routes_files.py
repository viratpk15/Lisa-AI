"""
Jarvis AIOS
-----------
Files FastAPI Routes

HTTP endpoints for document and attachment uploads.
"""

import logging
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status

from app.Auth.dependencies import get_current_user
from app.Auth.models import User
from app.FastAPI.schemas import AttachmentResponse
from app.RAG.rag_manager import rag_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])


from app.RAG.extractors import DocumentExtractorFactory


def _detect_type(filename: str) -> str:
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext in ["pdf"]:
        return "pdf"
    elif ext in ["docx", "doc"]:
        return "docx"
    elif ext in ["pptx", "ppt"]:
        return "pptx"
    elif ext in ["png", "jpg", "jpeg", "webp", "svg", "gif"]:
        return "image"
    elif ext in ["zip", "tar", "gz", "7z"]:
        return "zip"
    elif ext in ["md", "markdown"]:
        return "markdown"
    elif ext in ["txt"]:
        return "txt"
    else:
        return "code"


def _extract_text_from_file_bytes(file_bytes: bytes, filename: str, att_type: str) -> str:
    """Extract plain text from binary files using RAG 2.0 DocumentExtractorFactory."""
    try:
        extractor = DocumentExtractorFactory.get_extractor(filename=filename, file_type=att_type)
        extracted = extractor.extract(file_bytes=file_bytes, filename=filename)
        return extracted.full_text
    except Exception as exc:
        logger.warning("[FILE-UPLOAD] DocumentExtractorFactory failed for '%s': %s", filename, exc)
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""


@router.post(
    "/upload",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file attachment",
)
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
) -> AttachmentResponse:
    """Handle document/attachment upload, save to disk, connect to RAGManager, and return metadata."""
    file_bytes = await file.read()
    att_id = f"att_{uuid.uuid4().hex[:8]}"
    filename = file.filename or "uploaded_file"
    att_type = _detect_type(filename)

    logger.info("[FILE-UPLOAD] Received file upload name='%s' size=%d bytes session=%s", filename, len(file_bytes), session_id)

    # 1. Save file to disk storage
    upload_dir = Path("./data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / f"{att_id}_{filename}"
    with open(save_path, "wb") as f:
        f.write(file_bytes)
    logger.info("[FILE-UPLOAD] Saved file to storage path: %s", save_path)

    # 2. Extract text & connect to RAG ingestion
    text_content = _extract_text_from_file_bytes(file_bytes, filename, att_type)
    logger.info("[FILE-UPLOAD] Extracted text length: %d chars for '%s'", len(text_content), filename)

    try:
        doc = rag_manager.ingest_document(
            dataset_id="ds_core_docs",
            filename=filename,
            file_type=att_type,
            text=text_content,
            file_bytes=file_bytes,
        )
        logger.info("[FILE-UPLOAD] Ingested document ID '%s' into RAGManager with chunks", doc.id)

        # Bind document ID to session in SessionAttachment registry
        if session_id:
            rag_manager.repo.add_session_attachment(
                session_id=session_id,
                document_id=doc.id,
                filename=filename,
                file_type=att_type,
            )
            logger.info("[FILE-UPLOAD] Bound document ID '%s' (%s) to session '%s'", doc.id, filename, session_id)
    except Exception as exc:
        logger.warning("[FILE-UPLOAD] RAG ingestion error for '%s': %s", filename, str(exc))

    return AttachmentResponse(
        id=att_id,
        name=filename,
        type=att_type,
        sizeBytes=len(file_bytes),
        urlPlaceholder=f"/files/{att_id}/{filename}",
    )
