"""
Tests for POST /chat/stream real-time SSE streaming.
"""

from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.FastAPI.routes import router
from app.LLM.client import LLMClient
from app.Auth.models import User
from app.Auth.dependencies import get_current_user


app = FastAPI()
app.include_router(router)


def test_llm_client_provider_agnostic_stream():
    """Test LLMClient.stream yields string tokens regardless of provider."""
    mock_chunk1 = MagicMock()
    mock_chunk1.content = "Hello"
    mock_chunk2 = MagicMock()
    mock_chunk2.content = " World"

    mock_provider = MagicMock()
    mock_provider.stream.return_value = [mock_chunk1, mock_chunk2]

    client = LLMClient(provider=mock_provider)
    tokens = list(client.stream([{"role": "user", "content": "Hi"}]))

    assert tokens == ["Hello", " World"]
    mock_provider.stream.assert_called_once()


def test_chat_stream_unauthorized():
    """POST /chat/stream without auth headers returns 401 Unauthorized."""
    client = TestClient(app)
    response = client.post(
        "/chat/stream",
        json={"session_id": "test-session", "message": "Hello"},
    )
    assert response.status_code == 401


@patch("app.FastAPI.routes.verify_session_ownership")
@patch("app.Jarvis.runtime.jarvis.chat_stream")
def test_chat_stream_success(mock_chat_stream, mock_verify):
    """POST /chat/stream yields structured SSE event frames."""
    mock_chat_stream.return_value = iter([
        "event: thinking\ndata: {\"status\": \"Thinking...\"}\n\n",
        "event: token\ndata: {\"token\": \"Hello\"}\n\n",
        "event: done\ndata: {\"response\": \"Hello\"}\n\n",
    ])

    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@example.com")
    try:
        client = TestClient(app)
        response = client.post(
            "/chat/stream",
            json={"session_id": "session-123", "message": "Hello"},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        content = response.text
        assert "event: thinking" in content
        assert "event: token" in content
        assert "event: done" in content
    finally:
        app.dependency_overrides.clear()
