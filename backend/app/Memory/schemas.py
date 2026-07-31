# backend/app/Memory/schemas.py
"""
Jarvis AIOS — Pydantic Schemas for Memory Studio REST API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Memory Item / Timeline Schemas
# ---------------------------------------------------------------------------

class MemoryItemResponse(BaseModel):
    id: str
    session_id: str
    tier: str  # 'working', 'conversation', 'episodic', 'semantic', 'long_term'
    content: str
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    tokens: int = 0
    ttl_seconds: Optional[int] = None
    created_at: str


class MemoryDetailResponse(BaseModel):
    item: MemoryItemResponse
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class FlushWorkingPayload(BaseModel):
    session_id: str


# ---------------------------------------------------------------------------
# Semantic Knowledge Graph Schemas
# ---------------------------------------------------------------------------

class EntityNode(BaseModel):
    id: int
    name: str
    category: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: str


class RelationEdge(BaseModel):
    id: int
    subject_id: int
    object_id: int
    relation: str
    confidence: float = 1.0


class KnowledgeGraphResponse(BaseModel):
    nodes: List[EntityNode] = Field(default_factory=list)
    edges: List[RelationEdge] = Field(default_factory=list)


class AddRelationPayload(BaseModel):
    subject_name: str
    subject_category: str = "Concept"
    predicate: str
    object_name: str
    object_category: str = "Concept"
    confidence: float = 1.0


# ---------------------------------------------------------------------------
# Vector Projection / Embedding Explorer Schemas
# ---------------------------------------------------------------------------

class VectorPoint(BaseModel):
    id: str
    session_id: str
    text_preview: str
    x: float
    y: float
    tier: str


class VectorProjectionResponse(BaseModel):
    session_id: str
    points: List[VectorPoint] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Recall Bench Schemas
# ---------------------------------------------------------------------------

class RecallSearchPayload(BaseModel):
    session_id: str
    query: str
    top_k: int = 5
    alpha: float = 0.5  # 1.0 = pure dense, 0.0 = pure sparse
    tiers: List[str] = Field(default_factory=lambda: ["conversation", "long_term"])


class RankedMemoryHit(BaseModel):
    memory_id: str
    tier: str
    content: str
    dense_score: float
    sparse_score: float
    rrf_score: float


class RecallResultsResponse(BaseModel):
    query: str
    total_hits: int
    latency_ms: float
    results: List[RankedMemoryHit] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Context Window / Token Budget Schemas
# ---------------------------------------------------------------------------

class TokenBreakdown(BaseModel):
    system_prompt: int = 1024
    conversation_history: int = 2048
    recalled_long_term: int = 1024
    working_buffer: int = 512
    headroom: int = 3584


class ContextWindowResponse(BaseModel):
    session_id: str
    max_tokens: int = 8192
    used_tokens: int = 4608
    headroom: int = 3584
    breakdown: TokenBreakdown
    assembled_prompt: str


class CompressMemoryPayload(BaseModel):
    session_id: str
    strategy: str = "summarize"  # 'summarize' or 'trim'


class CompressionStatusResponse(BaseModel):
    session_id: str
    status: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int


# ---------------------------------------------------------------------------
# Analytics & Data Ops Schemas
# ---------------------------------------------------------------------------

class MemoryAnalyticsResponse(BaseModel):
    session_id: str
    total_items: int
    avg_latency_ms: float
    cache_hit_rate: float
    token_usage_pct: float
    tier_distribution: Dict[str, int]


class ExportMemoryPayload(BaseModel):
    session_id: str


class ImportSummaryResponse(BaseModel):
    session_id: str
    status: str
    imported_messages: int
    imported_events: int
    imported_entities: int


class SuccessStatusResponse(BaseModel):
    status: str = "success"
    message: str = "Operation completed successfully"
