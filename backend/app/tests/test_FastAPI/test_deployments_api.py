# backend/app/tests/test_FastAPI/test_deployments_api.py
"""
Jarvis AIOS — FastAPI REST Integration Tests for Deployment Studio.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_list_environments():
    res = client.get("/api/v1/deployments/environments")
    assert res.status_code == 200
    envs = res.json()
    assert isinstance(envs, list)
    assert len(envs) >= 1


def test_api_list_targets():
    res = client.get("/api/v1/deployments/targets")
    assert res.status_code == 200
    targets = res.json()
    assert isinstance(targets, list)


def test_api_rollout_and_rollback():
    rollout_res = client.post("/api/v1/deployments/rollout", json={"env_id": "prod", "version_tag": "v1.8.0", "strategy": "blue_green"})
    assert rollout_res.status_code == 200
    r_data = rollout_res.json()
    assert r_data["version_tag"] == "v1.8.0"

    rollback_res = client.post("/api/v1/deployments/rollback", json={"env_id": "prod"})
    assert rollback_res.status_code == 200
    rb_data = rollback_res.json()
    assert rb_data["status"] == "success"


def test_api_secret_vault():
    res = client.get("/api/v1/deployments/secrets?env_id=prod")
    assert res.status_code == 200
    secrets = res.json()
    assert isinstance(secrets, list)


def test_api_health_metrics():
    res = client.get("/api/v1/deployments/prod/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "cpu_percent" in data


def test_api_audit_logs():
    res = client.get("/api/v1/deployments/audit-logs")
    assert res.status_code == 200
    logs = res.json()
    assert isinstance(logs, list)
