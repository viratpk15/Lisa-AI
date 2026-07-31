# backend/app/tests/test_Deployments/test_deployment_studio.py
"""
Jarvis AIOS — Unit Tests for Deployment Studio Subsystem (Sprint 6.8B).
"""

import pytest
import uuid
from app.Data.base import Base
from app.Data.database import engine, SessionLocal
from app.Deployments.manager import deployment_manager
from app.Deployments.vault import encrypt_secret, decrypt_secret, mask_secret


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_vault_encryption_and_masking():
    raw = "sk-proj-super-secret-key-999"
    enc = encrypt_secret(raw)
    assert enc != raw
    dec = decrypt_secret(enc)
    assert dec == raw
    masked = mask_secret(raw)
    assert "sk-p...-999" in masked


def test_environment_creation_and_listing():
    db = SessionLocal()
    e_id = f"env_{uuid.uuid4().hex[:6]}"
    try:
        env = deployment_manager.create_environment(db, env_id=e_id, name="Test Environment", tier="staging")
        assert env["env_id"] == e_id
        all_envs = deployment_manager.list_environments(db)
        assert any(e["env_id"] == e_id for e in all_envs)
    finally:
        db.close()


def test_rollout_and_rollback():
    db = SessionLocal()
    try:
        rollout = deployment_manager.trigger_rollout(db, env_id="prod", version_tag="v1.8.0", strategy="blue_green")
        assert rollout["version_tag"] == "v1.8.0"
        assert rollout["status"] == "healthy"

        rollback = deployment_manager.trigger_rollback(db, env_id="prod")
        assert rollback["status"] == "success"
    finally:
        db.close()


def test_secret_vault_saving_and_masking():
    db = SessionLocal()
    try:
        s = deployment_manager.save_secret(db, env_id="prod", secret_key="TEST_API_KEY", raw_value="sk-1234567890abcdef")
        assert s["secret_key"] == "TEST_API_KEY"
        assert "sk-1...cdef" in s["masked_value"]
    finally:
        db.close()


def test_database_backup_and_restore():
    db = SessionLocal()
    try:
        backup = deployment_manager.create_backup(db, env_id="prod")
        assert "backup_prod" in backup["snapshot_name"]
        restore = deployment_manager.restore_backup(db, snapshot_name=backup["snapshot_name"])
        assert restore["status"] == "success"
    finally:
        db.close()
