"""
Jarvis AIOS — Prompt Studio FastAPI Integration Tests
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_prompts_api():
    response = client.get("/api/v1/prompts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_and_get_prompt_api():
    payload = {
        "title": "API Test Prompt",
        "description": "Integration test prompt",
        "system_prompt": "You are a test assistant.",
        "user_prompt": "Hello {{name}}",
        "tags": ["api", "test"],
    }
    create_res = client.post("/api/v1/prompts", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    prompt_id = created_data["prompt"]["id"]

    get_res = client.get(f"/api/v1/prompts/{prompt_id}")
    assert get_res.status_code == 200
    details = get_res.json()
    assert details["prompt"]["title"] == "API Test Prompt"
    assert "name" in details["variables"]


def test_parse_variables_api():
    payload = {"text": "Parse {{item1}} and {{item2}}"}
    res = client.post("/api/v1/prompts/parse-variables", json=payload)
    assert res.status_code == 200
    assert res.json()["variables"] == ["item1", "item2"]


def test_run_playground_api():
    payload = {
        "system_prompt": "System prompt test",
        "user_prompt": "Process {{data}}",
        "variables": {"data": "Test string"},
        "model": "gpt-4o",
    }
    res = client.post("/api/v1/prompts/playground/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "Test string" in data["raw_output"]


def test_analytics_api():
    res = client.get("/api/v1/prompts/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_executions" in data
    assert "avg_latency_ms" in data
