"""
Integration Tests for FastAPI RAG Studio Endpoints (/api/v1/rag/*)
"""

from fastapi.testclient import TestClient
from app.main import app
from app.Auth.dependencies import get_current_user


def mock_get_current_user():
    return {"sub": "test_user@jarvis.ai", "user_id": 1}


app.dependency_overrides[get_current_user] = mock_get_current_user
client = TestClient(app)


def test_api_list_knowledge_bases():
    response = client.get("/api/v1/rag/knowledge-bases")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Enterprise Architecture KB"


def test_api_list_datasets():
    response = client.get("/api/v1/rag/datasets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_api_chunk_preview():
    payload = {
        "text": "Jarvis AIOS RAG engine integrates dense vectors and sparse BM25 keywords.",
        "chunk_size": 5,
        "overlap": 1,
        "strategy": "recursive",
    }
    response = client.post("/api/v1/rag/chunk-preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_api_hybrid_search():
    payload = {
        "query": "LangGraph execution vector index",
        "top_k": 3,
        "alpha": 0.60,
        "use_reranker": True,
    }
    response = client.post("/api/v1/rag/hybrid-search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["alpha"] == 0.60
    assert len(data["results"]) > 0


def test_api_rag_analytics():
    response = client.get("/api/v1/rag/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "vector_store" in data


def test_api_knowledge_graph():
    response = client.get("/api/v1/rag/graph?kb_id=kb_enterprise_01")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 3
