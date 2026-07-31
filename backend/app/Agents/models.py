"""SQLAlchemy ORM models for Agent Studio.

Uses the existing SQLAlchemy Base from `app.Data.base` — consistent with every
other model in the project. Modernized to SQLAlchemy 2.x Mapped[...] syntax.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Data.base import Base


class Agent(Base):
    """An agent definition — the top-level entity in Agent Studio."""

    __tablename__ = "agent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    versions: Mapped[List["AgentVersion"]] = relationship(
        "AgentVersion", back_populates="agent", cascade="all, delete-orphan"
    )
    teams: Mapped[List["AgentTeam"]] = relationship(
        "AgentTeam", back_populates="agent", cascade="all, delete-orphan"
    )


class AgentVersion(Base):
    """A pinned snapshot of an agent's configuration."""

    __tablename__ = "agentversion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey("agent.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    changelog: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="versions")
    prompt_bindings: Mapped[List["AgentPromptBinding"]] = relationship(
        "AgentPromptBinding", back_populates="version", cascade="all, delete-orphan"
    )
    tool_bindings: Mapped[List["AgentToolBinding"]] = relationship(
        "AgentToolBinding", back_populates="version", cascade="all, delete-orphan"
    )
    memory_bindings: Mapped[List["AgentMemoryBinding"]] = relationship(
        "AgentMemoryBinding", back_populates="version", cascade="all, delete-orphan"
    )
    model_bindings: Mapped[List["AgentModelBinding"]] = relationship(
        "AgentModelBinding", back_populates="version", cascade="all, delete-orphan"
    )
    executions: Mapped[List["AgentExecution"]] = relationship(
        "AgentExecution", back_populates="version", cascade="all, delete-orphan"
    )


class AgentPromptBinding(Base):
    """Links a version to a Prompt Studio prompt."""

    __tablename__ = "agentpromptbinding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agentversion.id", ondelete="CASCADE"), nullable=False
    )
    prompt_id: Mapped[int] = mapped_column(Integer, nullable=False)

    version: Mapped["AgentVersion"] = relationship("AgentVersion", back_populates="prompt_bindings")


class AgentToolBinding(Base):
    """Links a version to a registered Tool Engine tool."""

    __tablename__ = "agenttoolbinding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agentversion.id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(String, nullable=False)
    config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    version: Mapped["AgentVersion"] = relationship("AgentVersion", back_populates="tool_bindings")


class AgentMemoryBinding(Base):
    """Links a version to a MemoryManager key."""

    __tablename__ = "agentmemorybinding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agentversion.id", ondelete="CASCADE"), nullable=False
    )
    memory_key: Mapped[str] = mapped_column(String, nullable=False)
    config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    version: Mapped["AgentVersion"] = relationship("AgentVersion", back_populates="memory_bindings")


class AgentModelBinding(Base):
    """Links a version to a model configuration (temperature, model name, etc.)."""

    __tablename__ = "agentmodelbinding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agentversion.id", ondelete="CASCADE"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    parameters_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    version: Mapped["AgentVersion"] = relationship("AgentVersion", back_populates="model_bindings")


class AgentExecution(Base):
    """A single run of an agent version through the LangGraph runtime."""

    __tablename__ = "agentexecution"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agentversion.id", ondelete="CASCADE"), nullable=False
    )
    run_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    version: Mapped["AgentVersion"] = relationship("AgentVersion", back_populates="executions")
    steps: Mapped[List["ExecutionStep"]] = relationship(
        "ExecutionStep", back_populates="execution", cascade="all, delete-orphan"
    )


class ExecutionStep(Base):
    """One step within an agent execution."""

    __tablename__ = "executionstep"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agentexecution.id", ondelete="CASCADE"), nullable=False
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    input_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    execution: Mapped["AgentExecution"] = relationship("AgentExecution", back_populates="steps")


class AgentTeam(Base):
    """A named multi-agent team graph owned by a parent agent."""

    __tablename__ = "agentteam"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey("agent.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="teams")
    nodes: Mapped[List["TeamAgentNode"]] = relationship(
        "TeamAgentNode", back_populates="team", cascade="all, delete-orphan"
    )
    edges: Mapped[List["TeamEdge"]] = relationship(
        "TeamEdge", back_populates="team", cascade="all, delete-orphan"
    )


class TeamAgentNode(Base):
    """A node in a team graph — references an agent version with a canvas position."""

    __tablename__ = "teamagentnode"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("agentteam.id", ondelete="CASCADE"), nullable=False)
    agent_version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agentversion.id", ondelete="CASCADE"), nullable=False
    )
    position_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    team: Mapped["AgentTeam"] = relationship("AgentTeam", back_populates="nodes")
    version: Mapped["AgentVersion"] = relationship("AgentVersion")


class TeamEdge(Base):
    """A directed edge in a team graph with optional conditional routing."""

    __tablename__ = "teamedge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("agentteam.id", ondelete="CASCADE"), nullable=False)
    source_node_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teamagentnode.id", ondelete="CASCADE"), nullable=False
    )
    target_node_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teamagentnode.id", ondelete="CASCADE"), nullable=False
    )
    condition_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    team: Mapped["AgentTeam"] = relationship("AgentTeam", back_populates="edges")
