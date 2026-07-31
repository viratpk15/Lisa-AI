"""
Jarvis AIOS
--------------------
REST API Integration Tests for Tools Engine (Sprint 6.1B)

Tests GET /api/v1/tools, GET /api/v1/tools/categories, GET /api/v1/tools/{name},
POST /api/v1/tools/{name}/execute, and POST /api/v1/tools/{name}/execute/stream.
"""

from fastapi.testclient import TestClient
from app.FastAPI.routes_tools import router
from app.FastAPI.dependencies import get_current_user
from app.Auth.models import User
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/v1")

# Mock authenticated user
def mock_get_current_user():
    return User(id=1, email="test@example.com", is_active=True, role="USER")

app.dependency_overrides[get_current_user] = mock_get_current_user
client = TestClient(app)


def test_api_list_tools_and_search():
    """Test GET /api/v1/tools endpoint discovery and search filters."""
    response = client.get("/api/v1/tools")
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) >= 5

    # Filter by category
    cat_response = client.get("/api/v1/tools?category=system")
    assert cat_response.status_code == 200
    sys_tools = cat_response.json()
    assert any(t["name"] == "filesystem" for t in sys_tools)

    # Search query
    search_response = client.get("/api/v1/tools?query=calculator")
    assert search_response.status_code == 200
    calc_tools = search_response.json()
    assert len(calc_tools) >= 1
    assert calc_tools[0]["name"] == "calculator"


def test_api_list_categories():
    """Test GET /api/v1/tools/categories endpoint."""
    response = client.get("/api/v1/tools/categories")
    assert response.status_code == 200
    categories = response.json()
    assert "system" in categories
    assert "development" in categories


def test_api_get_tool_details_and_404():
    """Test GET /api/v1/tools/{tool_name} schema and 404 for invalid tool."""
    response = client.get("/api/v1/tools/calculator")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "schema" in data
    assert data["metadata"]["name"] == "calculator"

    # Invalid tool 404
    err_response = client.get("/api/v1/tools/non_existent_tool_123")
    assert err_response.status_code == 404


def test_api_execute_tool():
    """Test POST /api/v1/tools/{tool_name}/execute endpoint returning ToolResult."""
    payload = {
        "arguments": {
            "expression": "100 / 4"
        }
    }
    response = client.post("/api/v1/tools/calculator/execute", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["tool_name"] == "calculator"
    assert result["status"] == "SUCCESS"
    assert result["output"] == 25.0


def test_api_stream_tool_execution():
    """Test POST /api/v1/tools/{tool_name}/execute/stream SSE endpoint."""
    payload = {
        "arguments": {
            "expression": "50 + 50"
        }
    }
    response = client.post("/api/v1/tools/calculator/execute/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "data:" in response.text
