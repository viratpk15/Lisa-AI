"""
Jarvis AIOS — SQLAlchemy Data Models for Deployment Studio Subsystem.

Defines schemas for:
- DeploymentEnvironmentModel: Deployment stages (dev, staging, production).
- DeploymentTargetModel: Infrastructure providers (Docker, K8s, Railway, Render, Fly, AWS, GCP, Azure, Self-hosted).
- DeploymentReleaseModel: Deployment releases (Blue/Green, Canary, Direct) and health state.
- SecretVaultEntryModel: Encrypted environment variables and secrets at rest.
- DatabaseBackupModel: Database backup snapshot metadata and restore tracking.
- DeploymentAuditLogModel: Audit trail of deployment, rollback, and vault actions.
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


class DeploymentEnvironmentModel(Base):
    """SQLAlchemy model for Deployment Environments."""

    __tablename__ = "deployment_environments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    env_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tier: Mapped[str] = mapped_column(String(50), nullable=False, default="production")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    targets: Mapped[List["DeploymentTargetModel"]] = relationship("DeploymentTargetModel", back_populates="environment", cascade="all, delete-orphan")
    releases: Mapped[List["DeploymentReleaseModel"]] = relationship("DeploymentReleaseModel", back_populates="environment", cascade="all, delete-orphan")
    secrets: Mapped[List["SecretVaultEntryModel"]] = relationship("SecretVaultEntryModel", back_populates="environment", cascade="all, delete-orphan")
    backups: Mapped[List["DatabaseBackupModel"]] = relationship("DatabaseBackupModel", back_populates="environment", cascade="all, delete-orphan")


class DeploymentTargetModel(Base):
    """SQLAlchemy model for Deployment Infrastructure Target Providers."""

    __tablename__ = "deployment_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    env_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deployment_environments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    environment: Mapped["DeploymentEnvironmentModel"] = relationship("DeploymentEnvironmentModel", back_populates="targets")


class DeploymentReleaseModel(Base):
    """SQLAlchemy model for Deployment Release Rollouts."""

    __tablename__ = "deployment_releases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    release_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    env_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deployment_environments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False, default="blue_green")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running", index=True)
    rollout_duration_s: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    environment: Mapped["DeploymentEnvironmentModel"] = relationship("DeploymentEnvironmentModel", back_populates="releases")
    audit_logs: Mapped[List["DeploymentAuditLogModel"]] = relationship("DeploymentAuditLogModel", back_populates="release", cascade="all, delete-orphan")


class SecretVaultEntryModel(Base):
    """SQLAlchemy model for Encrypted Secrets at rest."""

    __tablename__ = "secret_vault_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    env_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deployment_environments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    secret_key: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    environment: Mapped["DeploymentEnvironmentModel"] = relationship("DeploymentEnvironmentModel", back_populates="secrets")

    __table_args__ = (
        Index("idx_secret_env_key", "env_id", "secret_key", unique=True),
    )


class DatabaseBackupModel(Base):
    """SQLAlchemy model for Database Backup Snapshots."""

    __tablename__ = "database_backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    env_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deployment_environments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    environment: Mapped["DeploymentEnvironmentModel"] = relationship("DeploymentEnvironmentModel", back_populates="backups")


class DeploymentAuditLogModel(Base):
    """SQLAlchemy model for Deployment Audit Trail Logs."""

    __tablename__ = "deployment_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    release_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("deployment_releases.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    operator_user: Mapped[str] = mapped_column(String(100), nullable=False, default="admin")
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    release: Mapped[Optional["DeploymentReleaseModel"]] = relationship("DeploymentReleaseModel", back_populates="audit_logs")
