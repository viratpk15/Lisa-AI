"""
Jarvis AIOS — SQLAlchemy Data Models for Model Studio Subsystem.

Defines schemas for:
- ProviderConfigModel: 15+ LLM Provider configurations & encrypted credentials.
- LLMModelConfigModel: Registered language model parameters, context limits & cost rates.
- RoutingPolicyModel: Model routing rules, fallback chains & load balancing.
- BenchmarkRunModel: Latency benchmarks, TTFT, and throughput metrics.
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


class ProviderConfigModel(Base):
    """SQLAlchemy model for LLM Providers & encrypted API key credentials."""

    __tablename__ = "provider_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_api_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationship to models
    models: Mapped[List["LLMModelConfigModel"]] = relationship(
        "LLMModelConfigModel", back_populates="provider", cascade="all, delete-orphan"
    )


class LLMModelConfigModel(Base):
    """SQLAlchemy model for specific LLM configuration parameters."""

    __tablename__ = "llm_model_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("provider_configs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    context_window: Mapped[int] = mapped_column(Integer, nullable=False, default=128000)
    max_output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=4096)
    input_cost_per_1k: Mapped[float] = mapped_column(Float, nullable=False, default=0.0015)
    output_cost_per_1k: Mapped[float] = mapped_column(Float, nullable=False, default=0.0020)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    routing_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationship back to provider
    provider: Mapped["ProviderConfigModel"] = relationship("ProviderConfigModel", back_populates="models")


class RoutingPolicyModel(Base):
    """SQLAlchemy model for Model Studio fallback chains & routing policies."""

    __tablename__ = "routing_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class BenchmarkRunModel(Base):
    """SQLAlchemy model for LLM latency & benchmark historical runs."""

    __tablename__ = "benchmark_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ttft_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="success")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_benchmark_model_date", "model_id", "created_at"),
    )
