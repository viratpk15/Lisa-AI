# backend/app/FastAPI/routes_deployments.py
"""
Jarvis AIOS — FastAPI REST Router for Deployment Studio Subsystem (Sprint 6.8B).

Mount Path: /api/v1/deployments

Endpoints:
- GET    /api/v1/deployments/environments
- POST   /api/v1/deployments/environments
- GET    /api/v1/deployments/targets
- POST   /api/v1/deployments/targets
- POST   /api/v1/deployments/rollout
- POST   /api/v1/deployments/rollback
- GET    /api/v1/deployments/secrets
- POST   /api/v1/deployments/secrets
- POST   /api/v1/deployments/backups
- POST   /api/v1/deployments/backups/restore
- GET    /api/v1/deployments/audit-logs
- GET    /api/v1/deployments/{env_id}/health
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.Auth.dependencies import get_current_user
from app.Data.database import get_db
from app.Deployments import schemas
from app.Deployments.manager import deployment_manager, DeploymentManager

router = APIRouter(prefix="/api/v1/deployments", tags=["Deployment Studio"])


def get_deployment_manager() -> DeploymentManager:
    return deployment_manager


# ---------------------------------------------------------------------------
# Environments & Provider Targets Endpoints
# ---------------------------------------------------------------------------

@router.get("/environments", response_model=List[schemas.DeploymentEnvironmentResponse])
def list_environments(
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """List all deployment environments (prod, staging, dev)."""
    return manager.list_environments(db)


@router.post("/environments", response_model=schemas.DeploymentEnvironmentResponse)
def create_environment(
    payload: schemas.EnvironmentCreatePayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Register a new deployment environment."""
    return manager.create_environment(db, env_id=payload.env_id, name=payload.name, tier=payload.tier)


@router.get("/targets", response_model=List[schemas.DeploymentTargetResponse])
def list_targets(
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """List configured deployment provider targets."""
    return manager.list_targets(db)


@router.post("/targets", response_model=schemas.DeploymentTargetResponse)
def register_target(
    payload: schemas.TargetRegisterPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Register a new target provider configuration (Docker, K8s, PaaS, Cloud)."""
    try:
        return manager.register_target(db, env_id=payload.env_id, provider_type=payload.provider_type, config=payload.config)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------------------------------------------------------------------------
# Rollout & Rollback Control Endpoints
# ---------------------------------------------------------------------------

@router.post("/rollout", response_model=schemas.RolloutResponse)
def trigger_rollout(
    payload: schemas.RolloutTriggerPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Trigger Blue/Green or Canary deployment release rollout."""
    try:
        return manager.trigger_rollout(db, env_id=payload.env_id, version_tag=payload.version_tag, strategy=payload.strategy)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/rollback", response_model=Dict[str, Any])
def trigger_rollback(
    payload: schemas.RollbackTriggerPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Trigger zero-downtime one-click rollback to stable release."""
    try:
        return manager.trigger_rollback(db, env_id=payload.env_id, target_release_id=payload.target_release_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------------------------------------------------------------------------
# Secret Vault & Disaster Recovery Backups
# ---------------------------------------------------------------------------

@router.get("/secrets", response_model=List[schemas.SecretVaultEntryResponse])
def list_secrets(
    env_id: str = "prod",
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """List masked secret vault keys."""
    return manager.list_secrets(db, env_id)


@router.post("/secrets", response_model=schemas.SecretVaultEntryResponse)
def save_secret(
    payload: schemas.SecretSavePayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Encrypt and store secret variable at rest in vault."""
    try:
        return manager.save_secret(db, env_id=payload.env_id, secret_key=payload.secret_key, raw_value=payload.raw_value)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/backups", response_model=schemas.DatabaseBackupResponse)
def create_backup(
    env_id: str = "prod",
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Trigger manual database snapshot backup."""
    try:
        return manager.create_backup(db, env_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/backups/restore", response_model=Dict[str, Any])
def restore_backup(
    payload: schemas.BackupRestorePayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Restore database from backup snapshot."""
    return manager.restore_backup(db, payload.snapshot_name)


# ---------------------------------------------------------------------------
# Telemetry Health & Audit Logs (Placed below static paths)
# ---------------------------------------------------------------------------

@router.get("/audit-logs", response_model=List[schemas.DeploymentAuditLogResponse])
def list_audit_logs(
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Fetch deployment operations audit logs."""
    return manager.list_audit_logs(db)


@router.get("/{env_id}/health", response_model=schemas.HealthMetricsResponse)
def get_health_metrics(
    env_id: str,
    db: Session = Depends(get_db),
    manager: DeploymentManager = Depends(get_deployment_manager),
):
    """Fetch live system health telemetry & container probes."""
    return manager.get_health_metrics(db, env_id)
