# backend/app/Deployments/schemas.py
"""
Jarvis AIOS — Pydantic Schemas for Deployment Studio REST API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DeploymentEnvironmentResponse(BaseModel):
    id: int
    env_id: str
    name: str
    tier: str
    is_active: bool
    created_at: datetime


class EnvironmentCreatePayload(BaseModel):
    env_id: str = Field(..., examples=["staging"])
    name: str = Field(..., examples=["Staging Pre-Release Environment"])
    tier: str = Field("staging", examples=["staging"])


class DeploymentTargetResponse(BaseModel):
    id: int
    env_id: int
    provider_type: str
    config: Dict[str, Any]
    status: str
    created_at: datetime


class TargetRegisterPayload(BaseModel):
    env_id: str = Field(..., examples=["prod"])
    provider_type: str = Field(..., examples=["kubernetes"])
    config: Dict[str, Any] = Field(default_factory=dict)


class RolloutTriggerPayload(BaseModel):
    env_id: str = Field("prod", examples=["prod"])
    version_tag: str = Field(..., examples=["v1.8.0"])
    strategy: str = Field("blue_green", examples=["blue_green"])


class RolloutResponse(BaseModel):
    release_id: str
    environment: str
    version_tag: str
    strategy: str
    status: str
    rollout_duration_s: float
    deployed_at: datetime


class RollbackTriggerPayload(BaseModel):
    env_id: str = Field("prod", examples=["prod"])
    target_release_id: Optional[str] = Field(None, examples=["rel_v1_7_0"])


class SecretVaultEntryResponse(BaseModel):
    id: int
    secret_key: str
    masked_value: str
    updated_at: datetime


class SecretSavePayload(BaseModel):
    env_id: str = Field("prod", examples=["prod"])
    secret_key: str = Field(..., examples=["OPENAI_API_KEY"])
    raw_value: str = Field(..., examples=["sk-proj-super-secret-key-12345"])


class DatabaseBackupResponse(BaseModel):
    id: int
    snapshot_name: str
    storage_path: str
    size_bytes: int
    created_at: datetime


class BackupRestorePayload(BaseModel):
    snapshot_name: str = Field(..., examples=["backup_prod_20260727_173000"])


class ContainerProbe(BaseModel):
    name: str
    status: str
    latency_ms: float


class HealthMetricsResponse(BaseModel):
    environment: str
    status: str
    cpu_percent: float
    memory_mb: float
    containers_running: int
    probes: List[ContainerProbe]


class DeploymentAuditLogResponse(BaseModel):
    id: int
    action: str
    operator_user: str
    details: Dict[str, Any]
    timestamp: datetime
