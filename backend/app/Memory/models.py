"""
Jarvis AIOS — SQLAlchemy Data Models for Memory Studio Subsystem.

Defines schemas for:
- EpisodicEventModel: Task execution milestones, retry logs, and tool execution snapshots.
- MemoryEntityModel: Named entities for the Semantic Knowledge Graph.
- MemoryRelationModel: Directed triples (Subject -> Predicate -> Object) for Semantic Graph.
Modernized to SQLAlchemy 2.x Mapped[...] syntax.
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.Data.models import SessionModel

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Data.base import Base


class EpisodicEventModel(Base):
    """SQLAlchemy model for Episodic Memory event logs and execution snapshots."""

    __tablename__ = "episodic_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    step_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    outcome: Mapped[str] = mapped_column(String(50), nullable=False, default="success")
    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.75)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    retrieval_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    pinned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationship
    session: Mapped["SessionModel"] = relationship("SessionModel", backref="episodic_events")

    __table_args__ = (
        Index("idx_episodic_session_step", "session_id", "step_index"),
    )


class MemoryEntityModel(Base):
    """SQLAlchemy model for Semantic Memory entity nodes."""

    __tablename__ = "memory_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_category: Mapped[str] = mapped_column(String(100), nullable=False, default="Concept", index=True)
    attributes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="{}")
    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    retrieval_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    pinned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    subject_relations: Mapped[List["MemoryRelationModel"]] = relationship(
        "MemoryRelationModel",
        foreign_keys="[MemoryRelationModel.subject_entity_id]",
        back_populates="subject_entity",
        cascade="all, delete-orphan",
    )
    object_relations: Mapped[List["MemoryRelationModel"]] = relationship(
        "MemoryRelationModel",
        foreign_keys="[MemoryRelationModel.object_entity_id]",
        back_populates="object_entity",
        cascade="all, delete-orphan",
    )


class MemoryRelationModel(Base):
    """SQLAlchemy model for Semantic Memory entity-relation triples."""

    __tablename__ = "memory_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("memory_entities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    object_entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("memory_entities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    subject_entity: Mapped["MemoryEntityModel"] = relationship(
        "MemoryEntityModel", foreign_keys=[subject_entity_id], back_populates="subject_relations"
    )
    object_entity: Mapped["MemoryEntityModel"] = relationship(
        "MemoryEntityModel", foreign_keys=[object_entity_id], back_populates="object_relations"
    )
