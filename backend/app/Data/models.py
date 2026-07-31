"""
Jarvis AIOS
-----------
SQLAlchemy Data Models

Defines infrastructure ORM schemas for users, sessions, messages, memory embeddings,
and execution state for PostgreSQL (Supabase) and database migration support.
Modernized to SQLAlchemy 2.x Mapped[...] syntax.
"""

from typing import List, Optional
from sqlalchemy import (
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Data.base import Base


class SessionAttachmentModel(Base):
    """SQLAlchemy model for session document attachment registry."""

    __tablename__ = "session_attachments"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)


class UserModel(Base):
    """SQLAlchemy model for user authentication storage."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    sessions: Mapped[List["SessionModel"]] = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")


class SessionModel(Base):
    """SQLAlchemy model for chat sessions and conversation threads."""

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), default="New Conversation", nullable=False)
    pinned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)
    last_accessed: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    user: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="sessions")
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel", back_populates="session", cascade="all, delete-orphan"
    )
    message_embeddings: Mapped[List["MessageEmbeddingModel"]] = relationship(
        "MessageEmbeddingModel", back_populates="session", cascade="all, delete-orphan"
    )
    summary_embedding: Mapped[Optional["SummaryEmbeddingModel"]] = relationship(
        "SummaryEmbeddingModel", back_populates="session", uselist=False,
        cascade="all, delete-orphan",
    )
    execution_state: Mapped[Optional["ExecutionStateModel"]] = relationship(
        "ExecutionStateModel", back_populates="session", uselist=False,
        cascade="all, delete-orphan",
    )


class MessageModel(Base):
    """SQLAlchemy model for conversation chat messages."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(255), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(100), nullable=False)
    order_in_session: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    session: Mapped["SessionModel"] = relationship("SessionModel", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_session_order", "session_id", "order_in_session"),
        Index("idx_messages_session_id", "session_id", "id"),
    )


class MessageEmbeddingModel(Base):
    """SQLAlchemy model for message vector embeddings."""

    __tablename__ = "message_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(255), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    session: Mapped["SessionModel"] = relationship("SessionModel", back_populates="message_embeddings")

    __table_args__ = (
        Index("idx_embeddings_session_pos", "session_id", "position"),
    )


class SummaryEmbeddingModel(Base):
    """SQLAlchemy model for conversation summary vector embeddings."""

    __tablename__ = "summary_embeddings"

    session_id: Mapped[str] = mapped_column(String(255), ForeignKey("sessions.session_id", ondelete="CASCADE"), primary_key=True)
    embedding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    session: Mapped["SessionModel"] = relationship("SessionModel", back_populates="summary_embedding")


class ExecutionStateModel(Base):
    """SQLAlchemy model for plan execution state persistence."""

    __tablename__ = "execution_state"

    session_id: Mapped[str] = mapped_column(String(255), ForeignKey("sessions.session_id", ondelete="CASCADE"), primary_key=True)
    current_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_step: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completed_steps: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    pending_steps: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    execution_status: Mapped[str] = mapped_column(String(50), nullable=False, default="idle")
    updated_at: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    session: Mapped["SessionModel"] = relationship("SessionModel", back_populates="execution_state")


# ---------------------------------------------------------------------------
# RAG Subsystem SQLAlchemy Persistence Models
# ---------------------------------------------------------------------------

class KnowledgeBaseModel(Base):
    """SQLAlchemy model for Knowledge Base metadata."""

    __tablename__ = "knowledge_bases"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    embedding_provider: Mapped[str] = mapped_column(String(100), nullable=False, default="local")
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False, default="text-embedding-3-small")
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False, default=1536)
    vector_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    datasets: Mapped[List["DatasetModel"]] = relationship("DatasetModel", back_populates="knowledge_base", cascade="all, delete-orphan")


class DatasetModel(Base):
    """SQLAlchemy model for Dataset collections within a Knowledge Base."""

    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    kb_id: Mapped[str] = mapped_column(String(255), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    knowledge_base: Mapped["KnowledgeBaseModel"] = relationship("KnowledgeBaseModel", back_populates="datasets")
    documents: Mapped[List["DocumentModel"]] = relationship("DocumentModel", back_populates="dataset", cascade="all, delete-orphan")


class DocumentModel(Base):
    """SQLAlchemy model for ingested files and documents."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(255), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False, default="txt")
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    checksum: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ingested_at: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    dataset: Mapped["DatasetModel"] = relationship("DatasetModel", back_populates="documents")
    chunks: Mapped[List["ChunkModel"]] = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan")


class ChunkModel(Base):
    """SQLAlchemy model for document text chunks."""

    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(255), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    chunk_hash: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    metadata_payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    # Relationships
    document: Mapped["DocumentModel"] = relationship("DocumentModel", back_populates="chunks")
    embedding: Mapped[Optional["RAGEmbeddingModel"]] = relationship("RAGEmbeddingModel", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_chunks_doc_idx", "document_id", "chunk_index"),
    )


class RAGEmbeddingModel(Base):
    """SQLAlchemy model for chunk vector embeddings."""

    __tablename__ = "rag_embeddings"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    chunk_id: Mapped[str] = mapped_column(String(255), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False, default="local")
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="text-embedding-3-small")
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False, default=1536)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    vector_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    vector_store_id: Mapped[str] = mapped_column(String(100), nullable=False, default="sqlite_vector")
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    chunk: Mapped["ChunkModel"] = relationship("ChunkModel", back_populates="embedding")


class RetrievalTraceModel(Base):
    """SQLAlchemy model for retrieval trace analytics."""

    __tablename__ = "retrieval_traces"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    kb_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    raw_query: Mapped[str] = mapped_column(Text, nullable=False)
    alpha_used: Mapped[float] = mapped_column(Float, nullable=False, default=0.50)
    top_k_requested: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    executed_at: Mapped[str] = mapped_column(String(100), nullable=False)


class RAGEvaluationModel(Base):
    """SQLAlchemy model for RAG quality evaluation records."""

    __tablename__ = "rag_evaluations"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    context_recall: Mapped[float] = mapped_column(Float, nullable=False, default=0.94)
    context_precision: Mapped[float] = mapped_column(Float, nullable=False, default=0.91)
    faithfulness: Mapped[float] = mapped_column(Float, nullable=False, default=0.98)
    answer_relevance: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    mrr: Mapped[float] = mapped_column(Float, nullable=False, default=0.89)
    ndcg: Mapped[float] = mapped_column(Float, nullable=False, default=0.92)
    evaluated_at: Mapped[str] = mapped_column(String(100), nullable=False)
