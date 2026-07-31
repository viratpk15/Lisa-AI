# backend/app/tests/test_FastAPI/test_workflows_api.py
"""
Jarvis AIOS — FastAPI REST Integration Tests for Workflow Studio.
"""

from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_list_workflows():
    res = client.get("/api/v1/workflows")
    assert res.status_code == 200
    wfs = res.json()
    assert isinstance(wfs, list)
    assert len(wfs) >= 1


def test_api_list_templates():
    res = client.get("/api/v1/workflows/templates")
    assert res.status_code == 200
    templates = res.json()
    assert isinstance(templates, list)
    assert len(templates) >= 3


def test_api_compile_workflow():
    res = client.post("/api/v1/workflows/wf_agent_tool_pipeline/compile")
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["node_count"] >= 1


def test_api_workflow_analytics():
    res = client.get("/api/v1/workflows/wf_agent_tool_pipeline/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_executions" in data


def test_api_export_workflow():
    res = client.post("/api/v1/workflows/export?workflow_id=wf_agent_tool_pipeline")
    assert res.status_code == 200
    data = res.json()
    assert "workflow" in data
