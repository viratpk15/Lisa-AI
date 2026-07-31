# backend/app/Memory/repository.py
"""
Jarvis AIOS — Memory Studio Repository Layer.

Handles database operations for:
- Sessions & Conversation Messages (MessageModel)
- Episodic Events (EpisodicEventModel)
- Semantic Knowledge Graph (MemoryEntityModel, MemoryRelationModel)
- Vector Embeddings (MessageEmbeddingModel, SummaryEmbeddingModel)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.Data.models import MessageModel
from app.Memory.models import EpisodicEventModel, MemoryEntityModel, MemoryRelationModel


# ---------------------------------------------------------------------------
# Episodic Events CRUD
# ---------------------------------------------------------------------------

def create_episodic_event(
    session: Session,
    session_id: str,
    event_type: str,
    payload_json: str = "{}",
    outcome: str = "success",
    run_id: Optional[str] = None,
    step_index: int = 0,
) -> EpisodicEventModel:
    event = EpisodicEventModel(
        session_id=session_id,
        run_id=run_id,
        step_index=step_index,
        event_type=event_type,
        payload_json=payload_json,
        outcome=outcome,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def list_episodic_events(session: Session, session_id: str) -> List[EpisodicEventModel]:
    stmt = (
        select(EpisodicEventModel)
        .where(EpisodicEventModel.session_id == session_id)
        .order_by(EpisodicEventModel.id.asc())
    )
    return list(session.scalars(stmt).all())


def get_episodic_event(session: Session, event_id: int) -> Optional[EpisodicEventModel]:
    return session.get(EpisodicEventModel, event_id)


def delete_episodic_event(session: Session, event_id: int) -> bool:
    event = get_episodic_event(session, event_id)
    if event:
        session.delete(event)
        session.commit()
        return True
    return False


# ---------------------------------------------------------------------------
# Semantic Knowledge Graph CRUD
# ---------------------------------------------------------------------------

def get_or_create_entity(
    session: Session,
    user_id: Optional[int],
    name: str,
    category: str = "Concept",
    attributes_json: str = "{}",
) -> MemoryEntityModel:
    stmt = select(MemoryEntityModel).where(
        MemoryEntityModel.entity_name == name,
        MemoryEntityModel.user_id == user_id,
    )
    entity = session.scalars(stmt).first()
    if not entity:
        entity = MemoryEntityModel(
            user_id=user_id,
            entity_name=name,
            entity_category=category,
            attributes_json=attributes_json,
        )
        session.add(entity)
        session.commit()
        session.refresh(entity)
    return entity


def add_relation(
    session: Session,
    subject_entity_id: int,
    object_entity_id: int,
    relation_type: str,
    confidence: float = 1.0,
) -> MemoryRelationModel:
    rel = MemoryRelationModel(
        subject_entity_id=subject_entity_id,
        object_entity_id=object_entity_id,
        relation_type=relation_type,
        confidence=confidence,
    )
    session.add(rel)
    session.commit()
    session.refresh(rel)
    return rel


def list_entities(
    session: Session,
    user_id: Optional[int] = None,
    status_filter: Optional[str] = None,
) -> List[MemoryEntityModel]:
    stmt = select(MemoryEntityModel)
    if user_id is not None:
        stmt = stmt.where(MemoryEntityModel.user_id == user_id)
    if status_filter:
        stmt = stmt.where(MemoryEntityModel.status == status_filter)
    return list(session.scalars(stmt.order_by(MemoryEntityModel.pinned.desc(), MemoryEntityModel.id.desc())).all())


def search_entities(session: Session, user_id: Optional[int], query: str) -> List[MemoryEntityModel]:
    pattern = f"%{query}%"
    stmt = (
        select(MemoryEntityModel)
        .where(
            MemoryEntityModel.user_id == user_id,
            (MemoryEntityModel.entity_name.ilike(pattern)) | (MemoryEntityModel.attributes_json.ilike(pattern)),
        )
        .order_by(MemoryEntityModel.pinned.desc(), MemoryEntityModel.importance_score.desc())
    )
    return list(session.scalars(stmt).all())


def delete_entity(session: Session, entity_id: int) -> bool:
    entity = session.get(MemoryEntityModel, entity_id)
    if entity:
        session.delete(entity)
        session.commit()
        return True
    return False


def pin_entity(session: Session, entity_id: int, pinned: bool = True) -> Optional[MemoryEntityModel]:
    entity = session.get(MemoryEntityModel, entity_id)
    if entity:
        entity.pinned = 1 if pinned else 0
        session.commit()
        session.refresh(entity)
    return entity


def update_entity_status(session: Session, entity_id: int, new_status: str) -> Optional[MemoryEntityModel]:
    entity = session.get(MemoryEntityModel, entity_id)
    if entity:
        entity.status = new_status
        session.commit()
        session.refresh(entity)
    return entity


def list_relations(session: Session) -> List[MemoryRelationModel]:
    stmt = select(MemoryRelationModel).order_by(MemoryRelationModel.id.asc())
    return list(session.scalars(stmt).all())


# ---------------------------------------------------------------------------
# Conversation & Embedding Accessors
# ---------------------------------------------------------------------------

def get_session_messages(session: Session, session_id: str) -> List[MessageModel]:
    stmt = (
        select(MessageModel)
        .where(MessageModel.session_id == session_id)
        .order_by(MessageModel.order_in_session.asc())
    )
    return list(session.scalars(stmt).all())


def delete_message(session: Session, message_id: int) -> bool:
    msg = session.get(MessageModel, message_id)
    if msg:
        session.delete(msg)
        session.commit()
        return True
    return False
