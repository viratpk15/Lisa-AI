"""
Jarvis AIOS — FastAPI RAG Studio Router (/api/v1/rag/*)

All endpoints are protected by the existing JWT/RBAC dependency `get_current_user`.
Request schemas are defined inline here; structural refactor into schemas.py is
tracked as a minor debt item.
"""

from fastapi import APIRouter, Depends, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.Auth.dependencies import get_current_user
from app.RAG.models import (
    KnowledgeBase,
    Dataset,
    Document,
    Chunk,
    RAGEvaluation,
    KnowledgeGraphData,
)
from app.RAG.rag_manager import RAGManager

router = APIRouter(
    prefix="/api/v1/rag",
    tags=["RAG Studio"],
    dependencies=[Depends(get_current_user)],
)

# Dependency Injection
def get_rag_manager() -> RAGManager:
    return RAGManager()


# Request Schemas
class CreateKBPayload(BaseModel):
    name: str
    description: str = ""


class CreateDatasetPayload(BaseModel):
    kb_id: str
    name: str


class ChunkPreviewPayload(BaseModel):
    text: str
    chunk_size: int = 512
    overlap: int = 50
    strategy: str = "recursive"


class HybridSearchPayload(BaseModel):
    query: str
    kb_id: Optional[str] = None
    top_k: int = 5
    alpha: float = 0.50
    use_reranker: bool = True


class RAGEvalPayload(BaseModel):
    trace_id: str
    query: str
    response: str
    context: str


# Endpoints
@router.get("/knowledge-bases", response_model=List[KnowledgeBase])
def list_knowledge_bases(manager: RAGManager = Depends(get_rag_manager)):
    return manager.list_knowledge_bases()


@router.post("/knowledge-bases", response_model=KnowledgeBase, status_code=201)
def create_knowledge_base(payload: CreateKBPayload, manager: RAGManager = Depends(get_rag_manager)):
    return manager.create_knowledge_base(payload.name, payload.description)


@router.get("/datasets", response_model=List[Dataset])
def list_datasets(kb_id: Optional[str] = None, manager: RAGManager = Depends(get_rag_manager)):
    return manager.list_datasets(kb_id)


@router.post("/datasets", response_model=Dataset, status_code=201)
def create_dataset(payload: CreateDatasetPayload, manager: RAGManager = Depends(get_rag_manager)):
    return manager.create_dataset(payload.kb_id, payload.name)


@router.get("/documents", response_model=List[Document])
def list_documents(dataset_id: Optional[str] = None, manager: RAGManager = Depends(get_rag_manager)):
    return manager.list_documents(dataset_id)


@router.post("/documents/ingest", response_model=Document, status_code=201)
def ingest_document(
    dataset_id: str = Form(...),
    filename: str = Form(...),
    file_type: str = Form("txt"),
    text: str = Form(...),
    manager: RAGManager = Depends(get_rag_manager),
):
    return manager.ingest_document(dataset_id, filename, file_type, text)


@router.get("/chunks", response_model=List[Chunk])
def list_chunks(document_id: Optional[str] = None, manager: RAGManager = Depends(get_rag_manager)):
    return manager.list_chunks(document_id)


@router.post("/chunk-preview")
def preview_chunking(payload: ChunkPreviewPayload, manager: RAGManager = Depends(get_rag_manager)):
    return manager.preview_chunking(
        text=payload.text,
        chunk_size=payload.chunk_size,
        overlap=payload.overlap,
        strategy=payload.strategy,
    )


@router.post("/hybrid-search")
def hybrid_search(payload: HybridSearchPayload, manager: RAGManager = Depends(get_rag_manager)):
    return manager.hybrid_search(
        query=payload.query,
        kb_id=payload.kb_id,
        top_k=payload.top_k,
        alpha=payload.alpha,
        use_reranker=payload.use_reranker,
    )


@router.post("/generate")
def generate_grounded_answer(
    payload: Dict[str, Any], manager: RAGManager = Depends(get_rag_manager)
):
    query = payload.get("query", "Default query")
    chunks = payload.get("chunks", [])
    return manager.generate_grounded_answer(query, chunks)


@router.post("/stream")
async def stream_rag_answer(
    payload: Dict[str, Any], manager: RAGManager = Depends(get_rag_manager)
):
    query = payload.get("query", "What is Jarvis AIOS architecture?")
    return StreamingResponse(
        manager.stream_rag_answer(query), media_type="text/event-stream"
    )


@router.get("/evaluations", response_model=List[RAGEvaluation])
def list_evaluations(manager: RAGManager = Depends(get_rag_manager)):
    return manager.list_evaluations()


@router.post("/evaluations", response_model=RAGEvaluation)
def evaluate_rag_trace(payload: RAGEvalPayload, manager: RAGManager = Depends(get_rag_manager)):
    return manager.evaluate_rag_trace(
        trace_id=payload.trace_id,
        query=payload.query,
        response=payload.response,
        context=payload.context,
    )


@router.get("/analytics")
def get_rag_analytics(manager: RAGManager = Depends(get_rag_manager)):
    return manager.get_analytics()


@router.get("/graph", response_model=KnowledgeGraphData)
def get_knowledge_graph(kb_id: str = "kb_enterprise_01", manager: RAGManager = Depends(get_rag_manager)):
    return manager.get_knowledge_graph(kb_id)
