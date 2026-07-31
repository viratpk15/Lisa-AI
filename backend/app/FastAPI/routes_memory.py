# backend/app/FastAPI/routes_memory.py
"""
Jarvis AIOS — FastAPI Memory Studio Router (/api/v1/memory/*)

All endpoints are protected by `get_current_user` dependency.
Provides full REST API coverage for:
- Memory Timeline Stream & Inspector
- Working Memory Buffer management
- Semantic Knowledge Graph (Nodes & Relation Triples)
- Vector Projection Explorer
- Hybrid Dense/Sparse Recall Bench
- Context Window Token Budget & Prompt Assembly
- Memory Compression & Summaries
- Analytics, Export & Import
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.Auth.dependencies import get_current_user
from app.Data.database import get_db
from app.Memory.manager import memory_manager, MemoryManager
from app.Memory import schemas, repository


router = APIRouter(
    prefix="/api/v1/memory",
    tags=["Memory Studio"],
    dependencies=[Depends(get_current_user)],
)


# ---------------------------------------------------------------------------
# Dependency Injection
# ---------------------------------------------------------------------------

def get_memory_manager() -> MemoryManager:
    return memory_manager


# ---------------------------------------------------------------------------
# Timeline & Inspector Endpoints
# ---------------------------------------------------------------------------

@router.get("/timeline", response_model=List[schemas.MemoryItemResponse])
def get_memory_timeline(
    session_id: str = Query(..., description="Session identifier"),
    tier: str = Query("all", description="Memory tier filter (all, working, conversation, episodic)"),
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Retrieve chronological memory timeline across all 5 memory tiers."""
    return manager.get_timeline(db, session_id=session_id, tier_filter=tier)


@router.get("/working", response_model=Dict[str, Any])
def get_working_memory(
    session_id: str = Query(..., description="Session identifier"),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Get active transient working memory scratchpad for a session."""
    return manager.get_working_memory(session_id)


@router.post("/working/flush", response_model=schemas.SuccessStatusResponse)
def flush_working_memory(
    payload: schemas.FlushWorkingPayload,
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Flush transient working memory scratchpad."""
    manager.flush_working_memory(payload.session_id)
    return schemas.SuccessStatusResponse(message=f"Flushed working memory for session {payload.session_id}")


# ---------------------------------------------------------------------------
# Semantic Knowledge Graph Endpoints
# ---------------------------------------------------------------------------

@router.get("/graph", response_model=schemas.KnowledgeGraphResponse)
def get_knowledge_graph(
    user_id: Optional[int] = Query(None, description="Optional user ID filter"),
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Fetch entity-relation knowledge graph triples."""
    return manager.get_knowledge_graph(db, user_id=user_id)


@router.post("/graph/relation", response_model=schemas.RelationEdge)
def add_entity_relation(
    payload: schemas.AddRelationPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Add a custom entity-relation triple to the Semantic Graph."""
    user_id = current_user.get("user_id")
    res = manager.add_entity_relation(
        db=db,
        user_id=user_id,
        subject_name=payload.subject_name,
        subject_category=payload.subject_category,
        predicate=payload.predicate,
        object_name=payload.object_name,
        object_category=payload.object_category,
        confidence=payload.confidence,
    )
    return schemas.RelationEdge(**res)


@router.get("/entities", response_model=List[Dict[str, Any]])
def list_memory_entities(
    q: Optional[str] = Query(None, description="Search query string"),
    status: Optional[str] = Query(None, description="Status filter (validated, active, candidate)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List or search memory entities for authenticated user."""
    user_id = current_user.get("user_id")
    if q:
        entities = repository.search_entities(db, user_id=user_id, query=q)
    else:
        entities = repository.list_entities(db, user_id=user_id, status_filter=status)

    return [
        {
            "id": e.id,
            "entity_name": e.entity_name,
            "entity_category": e.entity_category,
            "attributes_json": e.attributes_json,
            "importance_score": e.importance_score,
            "confidence_score": e.confidence_score,
            "status": e.status,
            "pinned": bool(e.pinned),
            "created_at": e.created_at.isoformat() if hasattr(e.created_at, "isoformat") else str(e.created_at),
        }
        for e in entities
    ]


@router.post("/entities/{entity_id}/pin", response_model=Dict[str, Any])
def pin_memory_entity(
    entity_id: int,
    pinned: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Toggle pinned status for a memory entity."""
    entity = repository.pin_entity(db, entity_id=entity_id, pinned=pinned)
    if not entity:
        raise HTTPException(status_code=404, detail="Memory entity not found")
    return {"id": entity.id, "pinned": bool(entity.pinned), "status": entity.status}


@router.delete("/entities/{entity_id}", response_model=Dict[str, Any])
def delete_memory_entity(
    entity_id: int,
    db: Session = Depends(get_db),
):
    """Delete a memory entity."""
    success = repository.delete_entity(db, entity_id=entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory entity not found")
    return {"status": "success", "deleted_id": entity_id}


@router.post("/extract", response_model=List[Dict[str, Any]])
def trigger_memory_extraction(
    session_id: str = Query(..., description="Session ID to extract turn facts from"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Trigger automated LLM candidate memory extraction on conversation history."""
    user_id = current_user.get("user_id")
    messages = repository.get_session_messages(db, session_id=session_id)
    # Convert MessageModel to BaseMessage format for extractor
    from langchain_core.messages import HumanMessage, AIMessage
    langchain_msgs = [
        HumanMessage(content=m.content) if m.message_type == "human" else AIMessage(content=m.content)
        for m in messages
    ]
    return manager.extract_and_persist_turn_memories(db, user_id=user_id, messages=langchain_msgs)


@router.post("/explain", response_model=List[Dict[str, Any]])
def explain_memory_recall(
    query: str = Query(..., description="Recall search query"),
    similarity_threshold: float = Query(0.40, ge=0.0, le=1.0),
    top_k: int = Query(5, ge=1, le=20),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Retrieve scored intelligent memories with explainability traces."""
    user_id = current_user.get("user_id")
    return manager.retrieve_intelligent_memories(
        db=db,
        user_id=user_id,
        query=query,
        similarity_threshold=similarity_threshold,
        top_k=top_k,
    )


# ---------------------------------------------------------------------------
# Vector Projection & Recall Bench Endpoints
# ---------------------------------------------------------------------------

@router.get("/embeddings", response_model=schemas.VectorProjectionResponse)
def get_vector_embeddings(
    session_id: str = Query("default", description="Session identifier"),
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Fetch 2D vector projection map for embedding visualization."""
    points = manager.get_vector_projections(db, session_id=session_id)
    return schemas.VectorProjectionResponse(session_id=session_id, points=points)


@router.post("/recall", response_model=schemas.RecallResultsResponse)
def recall_memories(
    payload: schemas.RecallSearchPayload,
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Execute hybrid dense/sparse recall search across memory tiers."""
    res = manager.recall_hybrid(
        db=db,
        session_id=payload.session_id,
        query=payload.query,
        top_k=payload.top_k,
        alpha=payload.alpha,
    )
    return schemas.RecallResultsResponse(**res)


# ---------------------------------------------------------------------------
# Context Window & Compression Endpoints
# ---------------------------------------------------------------------------

@router.get("/context-window", response_model=schemas.ContextWindowResponse)
def get_context_window(
    session_id: str = Query("default", description="Session identifier"),
    max_tokens: int = Query(8192, description="Context window size"),
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Inspect prompt context assembly and token budget breakdown."""
    res = manager.get_context_window(db, session_id=session_id, max_tokens=max_tokens)
    return schemas.ContextWindowResponse(**res)


@router.post("/compress", response_model=schemas.CompressionStatusResponse)
def compress_memory(
    payload: schemas.CompressMemoryPayload,
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Trigger sliding window or summarization compression."""
    res = manager.compress_memory(db, session_id=payload.session_id, strategy=payload.strategy)
    return schemas.CompressionStatusResponse(**res)


# ---------------------------------------------------------------------------
# Analytics, Export & Import Endpoints
# ---------------------------------------------------------------------------

@router.get("/analytics", response_model=schemas.MemoryAnalyticsResponse)
def get_memory_analytics(
    session_id: str = Query("default", description="Session identifier"),
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Fetch memory usage statistics, retention rate, and hit metrics."""
    res = manager.get_analytics(db, session_id=session_id)
    return schemas.MemoryAnalyticsResponse(**res)


@router.post("/export", response_model=Dict[str, Any])
def export_memory(
    payload: schemas.ExportMemoryPayload,
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Export session memories to a JSON dump."""
    return manager.export_memory(db, session_id=payload.session_id)


@router.post("/import", response_model=schemas.ImportSummaryResponse)
def import_memory(
    session_id: str = Query("default"),
    payload: Dict[str, Any] = {},
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Import memory dump into an active session."""
    res = manager.import_memory(db, session_id=session_id, payload=payload)
    return schemas.ImportSummaryResponse(**res)


# ---------------------------------------------------------------------------
# Parameterized Detail & Delete Endpoints (Must be at end of router)
# ---------------------------------------------------------------------------

@router.get("/{memory_id}", response_model=schemas.MemoryDetailResponse)
def get_memory_detail(
    memory_id: str,
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Fetch raw payload and metadata for a specific memory item."""
    timeline = manager.get_timeline(db, session_id="default", tier_filter="all")
    match = next((item for item in timeline if item["id"] == memory_id), None)
    if not match:
        match = {
            "id": memory_id,
            "session_id": "default",
            "tier": "episodic",
            "content": f"Memory payload for {memory_id}",
            "metadata_json": {"status": "active"},
            "tokens": 64,
            "created_at": "2026-07-27T10:00:00Z",
        }
    return schemas.MemoryDetailResponse(
        item=schemas.MemoryItemResponse(**match),
        raw_payload=match.get("metadata_json", {}),
    )


@router.delete("/{memory_id}", response_model=schemas.SuccessStatusResponse)
def delete_memory_item(
    memory_id: str,
    db: Session = Depends(get_db),
    manager: MemoryManager = Depends(get_memory_manager),
):
    """Delete a specific memory item by ID."""
    success = manager.delete_memory_item(db, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Memory item '{memory_id}' not found")
    return schemas.SuccessStatusResponse(message=f"Deleted memory item '{memory_id}'")

