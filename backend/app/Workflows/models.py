"""
Jarvis AIOS — SQLAlchemy Data Models for Workflow Studio Subsystem.

Defines schemas for:
- WorkflowDefinitionModel: Graph topology (nodes, edges, variables) in JSON & YAML.
- WorkflowVersionModel: Immutable version history of workflow definitions.
- WorkflowExecutionModel: LangGraph execution instances, latency, token usage, and status.
- WorkflowNodeLogModel: Fine-grained per-node execution logs & input/output state snapshots.
Modernized to SQLAlchemy 2.x Mapped[...] syntax.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
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


class WorkflowDefinitionModel(Base):
    """SQLAlchemy model for Workflow Graph Definitions."""

    __tablename__ = "workflow_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    definition_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    definition_yaml: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    versions: Mapped[List["WorkflowVersionModel"]] = relationship("WorkflowVersionModel", back_populates="workflow", cascade="all, delete-orphan")
    executions: Mapped[List["WorkflowExecutionModel"]] = relationship("WorkflowExecutionModel", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowVersionModel(Base):
    """SQLAlchemy model for Workflow Version Control."""

    __tablename__ = "workflow_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    definition_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    workflow: Mapped["WorkflowDefinitionModel"] = relationship("WorkflowDefinitionModel", back_populates="versions")


class WorkflowExecutionModel(Base):
    """SQLAlchemy model for LangGraph Workflow Execution Runs."""

    __tablename__ = "workflow_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running", index=True)
    total_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    workflow: Mapped["WorkflowDefinitionModel"] = relationship("WorkflowDefinitionModel", back_populates="executions")
    logs: Mapped[List["WorkflowNodeLogModel"]] = relationship("WorkflowNodeLogModel", back_populates="execution", cascade="all, delete-orphan")


class WorkflowNodeLogModel(Base):
    """SQLAlchemy model for individual node execution logs & state checkpoints."""

    __tablename__ = "workflow_node_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="success")
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    input_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    output_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    execution: Mapped["WorkflowExecutionModel"] = relationship("WorkflowExecutionModel", back_populates="logs")

    __table_args__ = (
        Index("idx_node_log_exec_time", "execution_id", "timestamp"),
    )
