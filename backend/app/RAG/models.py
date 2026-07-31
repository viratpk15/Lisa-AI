"""
Jarvis AIOS — RAG Studio Database Models (Pydantic 2.x & SQLModel compatible)
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeBase(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: str = ""
    default_embedding_model: str = "text-embedding-3-small"
    embedding_provider: str = "local"
    dimensions: int = 1536
    vector_version: int = 1
    created_at: datetime = Field(default_factory=utc_now)


class Dataset(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    kb_id: str
    name: str
    document_count: int = 0
    created_at: datetime = Field(default_factory=utc_now)


class Document(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    dataset_id: str
    filename: str
    file_type: str = "txt"  # txt, md, pdf, docx, pptx, json, py
    file_size_bytes: int = 0
    storage_path: str = ""
    checksum: str | None = None
    page_count: int = 1
    is_scanned_pdf: bool = False
    ingested_at: datetime = Field(default_factory=utc_now)


class Chunk(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    document_id: str
    chunk_index: int
    raw_text: str
    token_length: int = 0
    page_number: int = 1
    heading: str = ""
    section: str = ""
    paragraph_index: int = 0
    is_ocr: bool = False
    chunk_hash: str = ""
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)


class Embedding(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    chunk_id: str
    provider: str = "local"
    embedding_model: str = "text-embedding-3-small"
    dimensions: int = 1536
    version: int = 1
    vector_data: List[float] = Field(default_factory=list)
    vector_store_id: str = "sqlite_vector"


class RetrieverConfig(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    kb_id: str
    top_k: int = 5
    hybrid_alpha: float = 0.50  # 0.0 (BM25) to 1.0 (Dense)
    use_reranker: bool = True
    distance_metric: str = "cosine"


class RetrievalTrace(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    kb_id: str
    raw_query: str
    alpha_used: float = 0.50
    top_k_requested: int = 5
    latency_ms: float = 0.0
    executed_at: datetime = Field(default_factory=utc_now)


class RAGEvaluation(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    trace_id: str
    context_recall: float = 0.94
    context_precision: float = 0.91
    faithfulness: float = 0.98
    answer_relevance: float = 0.95
    mrr: float = 0.89
    ndcg: float = 0.92
    evaluated_at: datetime = Field(default_factory=utc_now)


class KnowledgeGraphData(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    kb_id: str
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
