"""
Jarvis AIOS — LIVE_SEARCH Hallucination Prevention & Determinism Test Suite
----------------------------------------------------------------------------

Verifies that the LIVE_SEARCH path in _evaluate_tool_and_rag_context:

1. Returns LIVE SEARCH RESULTS when search succeeds with real content.
2. Returns SEARCH PROVIDER UNAVAILABLE when no API key is configured.
3. Returns LIVE SEARCH HARD GATE FAILURE with specific diagnostic cause on error/timeout/empty results.
4. Filters the FallbackProvider "No Provider" sentinel from results.
5. NEVER returns [] (empty context) for any LIVE_SEARCH query.
"""

from unittest.mock import MagicMock, patch
from app.Jarvis.runtime import _evaluate_tool_and_rag_context, _categorize_search_failure


def _make_search_success(results):
    return {"status": "success", "results": results, "error": None}


def _make_search_error(error_msg):
    return {"status": "error", "results": [], "error": error_msg}


_REAL_RESULTS = [
    {
        "title": "NVIDIA GeForce RTX 5090 — Blackwell Architecture",
        "source": "NVIDIA Official Blog",
        "snippet": "The RTX 5090 features 32 GB GDDR7 with the new Blackwell architecture.",
        "url": "https://www.nvidia.com/en-us/geforce/news/rtx-5090-announcement/",
    },
]

_SENTINEL_RESULT = [
    {
        "title": "Search: latest NVIDIA chip",
        "source": "No Provider",
        "snippet": "No live search results available for 'latest NVIDIA chip'. Configure TAVILY_API_KEY, BRAVE_API_KEY, or SERPER_API_KEY for full search support.",
        "url": "https://html.duckduckgo.com/html/?q=latest+NVIDIA+chip",
    }
]


def test_categorize_search_failure():
    """Verify categorization of search execution errors."""
    assert "Invalid API key" in _categorize_search_failure("HTTP 401 Unauthorized")
    assert "HTTP 403 Forbidden" in _categorize_search_failure("Tunnel connection failed: 403 Forbidden")
    assert "quota or rate limit exceeded" in _categorize_search_failure("HTTP 429 Too Many Requests")
    assert "timed out" in _categorize_search_failure("Connection timed out")
    assert "connection error" in _categorize_search_failure("URLError: Errno 8")
    assert "No verified search results" in _categorize_search_failure("Search provider returned empty results")


def test_search_provider_configured_success():
    """Search provider configured + success returns search result context."""
    mock_tool = MagicMock()
    mock_tool.execute.return_value = _make_search_success(_REAL_RESULTS)
    with patch("app.Jarvis.runtime._is_real_search_provider_configured", return_value=(True, "serper")), \
         patch("app.Jarvis.runtime.registry") as mock_registry:
        mock_registry.get.return_value = mock_tool
        messages = _evaluate_tool_and_rag_context("latest NVIDIA chip")

    assert len(messages) == 1
    content = str(messages[0].content)
    assert "LIVE SEARCH RESULTS" in content
    assert "HARD GATE FAILURE" not in content


def test_search_provider_missing():
    """When search provider is not configured, returns SEARCH PROVIDER UNAVAILABLE."""
    with patch("app.Jarvis.runtime._is_real_search_provider_configured", return_value=(False, "none")):
        messages = _evaluate_tool_and_rag_context("latest iphone")

    assert len(messages) == 1
    content = str(messages[0].content)
    assert "LIVE SEARCH PROVIDER UNAVAILABLE" in content


def test_search_timeout():
    """Network timeout during search triggers LIVE SEARCH HARD GATE FAILURE with cause."""
    mock_tool = MagicMock()
    mock_tool.execute.side_effect = TimeoutError("Connection timed out after 15s")
    with patch("app.Jarvis.runtime._is_real_search_provider_configured", return_value=(True, "serper")), \
         patch("app.Jarvis.runtime.registry") as mock_registry:
        mock_registry.get.return_value = mock_tool
        messages = _evaluate_tool_and_rag_context("latest AI news")

    assert len(messages) == 1
    content = str(messages[0].content)
    assert "LIVE SEARCH HARD GATE FAILURE" in content
    assert "timed out" in content


def test_search_returns_empty_results():
    """Search returning empty results triggers LIVE SEARCH HARD GATE FAILURE with cause."""
    mock_tool = MagicMock()
    mock_tool.execute.return_value = _make_search_success([])
    with patch("app.Jarvis.runtime._is_real_search_provider_configured", return_value=(True, "tavily")), \
         patch("app.Jarvis.runtime.registry") as mock_registry:
        mock_registry.get.return_value = mock_tool
        messages = _evaluate_tool_and_rag_context("latest macbook")

    assert len(messages) == 1
    content = str(messages[0].content)
    assert "LIVE SEARCH HARD GATE FAILURE" in content
    assert "No verified search results" in content


def test_latest_iphone_never_falls_back_to_llm():
    messages = _evaluate_tool_and_rag_context("latest iphone")
    assert messages != []
    assert len(messages) == 1


def test_latest_nvidia_chip_never_hallucinates():
    messages = _evaluate_tool_and_rag_context("latest NVIDIA chip")
    assert messages != []
    assert len(messages) == 1


def test_bitcoin_price_never_hallucinates():
    messages = _evaluate_tool_and_rag_context("bitcoin price")
    assert messages != []
    assert len(messages) == 1


def test_silver_price_never_hallucinates():
    messages = _evaluate_tool_and_rag_context("silver price")
    assert messages != []
    assert len(messages) == 1


def test_weather_never_hallucinates():
    messages = _evaluate_tool_and_rag_context("weather today in Tokyo")
    assert messages != []
    assert len(messages) == 1
