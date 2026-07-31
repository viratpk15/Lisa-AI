# backend/app/tests/test_FastAPI/test_memory_api.py
"""
Jarvis AIOS — FastAPI Memory Studio Integration Tests (/api/v1/memory/*).
"""

from fastapi.testclient import TestClient
from app.main import app
from app.Auth.dependencies import get_current_user


def mock_get_current_user():
    return {"sub": "test_user@jarvis.ai", "user_id": 1}


app.dependency_overrides[get_current_user] = mock_get_current_user
client = TestClient(app)


def test_api_get_memory_timeline():
    res = client.get("/api/v1/memory/timeline?session_id=sess_api_test")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_get_working_memory():
    res = client.get("/api/v1/memory/working?session_id=sess_api_test")
    assert res.status_code == 200
    assert "scratchpad" in res.json()


def test_api_flush_working_memory():
    res = client.post("/api/v1/memory/working/flush", json={"session_id": "sess_api_test"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_api_get_knowledge_graph():
    res = client.get("/api/v1/memory/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data


def test_api_get_vector_embeddings():
    res = client.get("/api/v1/memory/embeddings?session_id=sess_api_test")
    assert res.status_code == 200
    data = res.json()
    assert "points" in data


def test_api_recall_memories():
    payload = {"session_id": "sess_api_test", "query": "vector search", "top_k": 3, "alpha": 0.5}
    res = client.post("/api/v1/memory/recall", json=payload)
    assert res.status_code == 200
    assert "results" in res.json()


def test_api_context_window():
    res = client.get("/api/v1/memory/context-window?session_id=sess_api_test")
    assert res.status_code == 200
    assert "breakdown" in res.json()


def test_api_compress_memory():
    res = client.post("/api/v1/memory/compress", json={"session_id": "sess_api_test", "strategy": "summarize"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_api_memory_analytics():
    res = client.get("/api/v1/memory/analytics?session_id=sess_api_test")
    assert res.status_code == 200
    assert "cache_hit_rate" in res.json()
