# backend/app/tests/test_FastAPI/test_models_api.py
"""
Jarvis AIOS — FastAPI REST Integration Tests for Model Studio.
"""

from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_list_providers():
    res = client.get("/api/v1/models/providers")
    assert res.status_code == 200
    providers = res.json()
    assert isinstance(providers, list)
    assert len(providers) >= 15


def test_api_list_model_registry():
    res = client.get("/api/v1/models/registry")
    assert res.status_code == 200
    models = res.json()
    assert isinstance(models, list)
    assert any(m["model_id"] == "gemini-2.5-flash" for m in models)


def test_api_list_routing_policies():
    res = client.get("/api/v1/models/routing-policies")
    assert res.status_code == 200
    policies = res.json()
    assert isinstance(policies, list)


def test_api_run_benchmark():
    res = client.post("/api/v1/models/benchmark", json={"model_id": "gemini-2.5-flash", "prompt_tokens": 50, "completion_tokens": 100})
    assert res.status_code == 200
    data = res.json()
    assert data["model_id"] == "gemini-2.5-flash"
    assert "total_latency_ms" in data


def test_api_cost_estimate():
    res = client.post("/api/v1/models/cost-estimate", json={"model_id": "gemini-2.5-flash", "prompt_tokens": 1000, "completion_tokens": 500, "monthly_requests": 1000})
    assert res.status_code == 200
    data = res.json()
    assert "estimated_monthly_cost" in data


def test_api_model_analytics():
    res = client.get("/api/v1/models/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_providers" in data
    assert "default_model" in data
