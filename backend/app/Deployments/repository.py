# backend/app/Deployments/repository.py
"""
Jarvis AIOS — Repository Data Access Layer for Deployment Studio.
"""

import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.Deployments.models import (
    DeploymentEnvironmentModel,
    DeploymentTargetModel,
    DeploymentReleaseModel,
    SecretVaultEntryModel,
    DatabaseBackupModel,
    DeploymentAuditLogModel,
)
from app.Deployments.vault import encrypt_secret


def seed_default_environments(db: Session) -> None:
    """Populate default environments (prod, staging, dev) if missing."""
    existing_prod = db.execute(
        select(DeploymentEnvironmentModel).where(DeploymentEnvironmentModel.env_id == "prod")
    ).scalar_one_or_none()
    if existing_prod:
        return

    envs = [
        DeploymentEnvironmentModel(env_id="prod", name="Production Environment", tier="production", is_active=True),
        DeploymentEnvironmentModel(env_id="staging", name="Staging Pre-Release", tier="staging", is_active=True),
        DeploymentEnvironmentModel(env_id="dev", name="Local Development", tier="dev", is_active=True),
    ]
    for env in envs:
        db.add(env)
    db.flush()

    # Add default target config for production
    target = DeploymentTargetModel(
        env_id=envs[0].id,
        provider_type="docker",
        config_json=json.dumps({"replicas": 3, "port": 8000}),
        status="active",
    )
    db.add(target)

    # Add initial secret entry
    secret = SecretVaultEntryModel(
        env_id=envs[0].id,
        secret_key="OPENAI_API_KEY",
        encrypted_value=encrypt_secret("sk-proj-demo-key-123456789"),
    )
    db.add(secret)

    # Add initial release
    rel = DeploymentReleaseModel(
        release_id="rel_v1_7_0",
        env_id=envs[0].id,
        version_tag="v1.7.0",
        strategy="blue_green",
        status="healthy",
        rollout_duration_s=4.2,
    )
    db.add(rel)
    db.commit()


# ---------------------------------------------------------------------------
# Environments & Targets CRUD
# ---------------------------------------------------------------------------

def list_environments(db: Session) -> List[DeploymentEnvironmentModel]:
    seed_default_environments(db)
    return db.execute(select(DeploymentEnvironmentModel).order_by(DeploymentEnvironmentModel.id.asc())).scalars().all()


def get_environment_by_id(db: Session, env_id: str) -> Optional[DeploymentEnvironmentModel]:
    seed_default_environments(db)
    return db.execute(
        select(DeploymentEnvironmentModel).where(DeploymentEnvironmentModel.env_id == env_id)
    ).scalar_one_or_none()


def create_environment(
    db: Session, env_id: str, name: str, tier: str = "production"
) -> DeploymentEnvironmentModel:
    env = DeploymentEnvironmentModel(env_id=env_id, name=name, tier=tier, is_active=True)
    db.add(env)
    db.commit()
    db.refresh(env)
    return env


def list_targets(db: Session) -> List[DeploymentTargetModel]:
    seed_default_environments(db)
    return db.execute(select(DeploymentTargetModel)).scalars().all()


def create_target(
    db: Session, env_db_id: int, provider_type: str, config: Dict[str, Any]
) -> DeploymentTargetModel:
    target = DeploymentTargetModel(
        env_id=env_db_id,
        provider_type=provider_type,
        config_json=json.dumps(config),
        status="active",
    )
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


# ---------------------------------------------------------------------------
# Releases & Rollback
# ---------------------------------------------------------------------------

def create_release(
    db: Session,
    env_db_id: int,
    release_id: str,
    version_tag: str,
    strategy: str = "blue_green",
    status: str = "healthy",
    rollout_duration_s: float = 3.5,
) -> DeploymentReleaseModel:
    rel = DeploymentReleaseModel(
        release_id=release_id,
        env_id=env_db_id,
        version_tag=version_tag,
        strategy=strategy,
        status=status,
        rollout_duration_s=rollout_duration_s,
    )
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def list_releases(db: Session, env_id: Optional[str] = None) -> List[DeploymentReleaseModel]:
    seed_default_environments(db)
    query = select(DeploymentReleaseModel).order_by(DeploymentReleaseModel.id.desc())
    return db.execute(query).scalars().all()


# ---------------------------------------------------------------------------
# Secret Vault & Backups
# ---------------------------------------------------------------------------

def list_secrets(db: Session, env_db_id: int) -> List[SecretVaultEntryModel]:
    return db.execute(
        select(SecretVaultEntryModel).where(SecretVaultEntryModel.env_id == env_db_id)
    ).scalars().all()


def save_secret(db: Session, env_db_id: int, secret_key: str, raw_val: str) -> SecretVaultEntryModel:
    existing = db.execute(
        select(SecretVaultEntryModel).where(
            SecretVaultEntryModel.env_id == env_db_id,
            SecretVaultEntryModel.secret_key == secret_key,
        )
    ).scalar_one_or_none()

    enc_val = encrypt_secret(raw_val)
    if existing:
        existing.encrypted_value = enc_val
        entry = existing
    else:
        entry = SecretVaultEntryModel(env_id=env_db_id, secret_key=secret_key, encrypted_value=enc_val)
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return entry


def create_backup(db: Session, env_db_id: int, snapshot_name: str, path: str, size: int) -> DatabaseBackupModel:
    backup = DatabaseBackupModel(
        env_id=env_db_id,
        snapshot_name=snapshot_name,
        storage_path=path,
        size_bytes=size,
    )
    db.add(backup)
    db.commit()
    db.refresh(backup)
    return backup


def list_backups(db: Session) -> List[DatabaseBackupModel]:
    seed_default_environments(db)
    return db.execute(select(DatabaseBackupModel).order_by(DatabaseBackupModel.id.desc())).scalars().all()


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------

def record_audit_log(
    db: Session, action: str, operator: str = "admin", release_id: Optional[int] = None, details: Dict[str, Any] = {}
) -> DeploymentAuditLogModel:
    log_entry = DeploymentAuditLogModel(
        release_id=release_id,
        action=action,
        operator_user=operator,
        details_json=json.dumps(details),
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def list_audit_logs(db: Session) -> List[DeploymentAuditLogModel]:
    return db.execute(select(DeploymentAuditLogModel).order_by(DeploymentAuditLogModel.id.desc())).scalars().all()
