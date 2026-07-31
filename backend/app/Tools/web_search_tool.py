"""
Jarvis AIOS
--------------------
Web Search Tool — Production Implementation

Wraps SearchProviderFactory and exposes search as a registered Tool.
Features:
  - TTL cache (configurable via SEARCH_CACHE_TTL)
  - Automatic retry on transient network errors
  - Source quality ranking
  - URL and snippet deduplication
  - API key security redaction in logs/errors
"""

import os
import time
import logging
from typing import Any, Dict, List, Optional

from app.Config import settings
from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel
from app.Tools.search_providers.factory import SearchProviderFactory

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Source quality ranking — lower index = higher quality
# ---------------------------------------------------------------------------
_SOURCE_QUALITY_ORDER = [
    "docs.", "documentation", "readthedocs", "developer.", "developers.",
    "github.com", "github.io",
    "arxiv.org", "scholar.google", "researchgate",
    "openai.com", "anthropic.com", "google.com", "microsoft.com",
    "tavily (synthesized)", "google (direct answer)",
]


def _source_rank(result: Dict[str, Any]) -> int:
    """Lower return value = higher quality (sort ascending)."""
    url = (result.get("url") or "").lower()
    src = (result.get("source") or "").lower()
    for rank, marker in enumerate(_SOURCE_QUALITY_ORDER):
        if marker in url or marker in src:
            return rank
    return len(_SOURCE_QUALITY_ORDER)


# ---------------------------------------------------------------------------
# TTL Cache
# ---------------------------------------------------------------------------

class SearchCache:
    """In-memory TTL search result cache."""

    def __init__(self, ttl_seconds: float) -> None:
        self.ttl = ttl_seconds
        self._cache: Dict[str, tuple[float, Dict[str, Any]]] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self._cache:
            created_at, val = self._cache[key]
            if time.time() - created_at < self.ttl:
                return val
            del self._cache[key]
        return None

    def set(self, key: str, val: Dict[str, Any]) -> None:
        self._cache[key] = (time.time(), val)


_SEARCH_CACHE = SearchCache(ttl_seconds=settings.SEARCH_CACHE_TTL)


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

_DEFAULT_KEY = object()

class WebSearchTool(Tool):
    """
    Production-ready Web Search Tool.

    Delegates to SearchProviderFactory (which uses SearchIntentClassifier for
    Serper-first / Tavily-agentic routing). Supports TTL caching, retry,
    source quality ranking, and snippet/URL deduplication.
    """

    def __init__(self, api_key: Any = _DEFAULT_KEY) -> None:
        self.api_key = api_key
        meta = ToolMetadata(
            name="web_search",
            display_name="Web Search Engine",
            description=(
                "Search the web for real-time information, news, documentation, "
                "and technical research. Automatically selects Serper for factual "
                "queries and Tavily for research/agentic queries."
            ),
            category="web",
            tags=["search", "web", "google", "news", "research"],
            version="3.0.0",
            author="Jarvis AIOS Core",
            permission_level=PermissionLevel.USER,
            requires_approval=False,
            timeout_seconds=settings.SEARCH_TIMEOUT,
            parameter_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term or query string.",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return.",
                        "default": settings.SEARCH_MAX_RESULTS,
                    },
                },
                "required": ["query"],
            },
        )
        super().__init__(metadata=meta)

        # Last search context for conversation follow-up reuse
        self._last_query: Optional[str] = None
        self._last_results: List[Dict[str, Any]] = []

    def _sanitize_error(self, error_str: Optional[str]) -> Optional[str]:
        """Redact API keys from error messages."""
        if not error_str:
            return None
        for env_k in ["SEARCH_API_KEY", "TAVILY_API_KEY", "BRAVE_API_KEY", "SERPER_API_KEY"]:
            val = os.environ.get(env_k) or getattr(settings, env_k, None)
            if val and len(val) > 4:
                error_str = error_str.replace(val, "[REDACTED_API_KEY]")
        return error_str

    def execute(self, **kwargs: Any) -> Any:
        """
        Execute a web search, returning structured results.

        Expected kwargs:
            query (str): Search query string. Required.
            num_results (int): Max results to return. Defaults to SEARCH_MAX_RESULTS.

        Checks TTL cache first. On cache miss, selects provider via
        SearchProviderFactory (which runs SearchIntentClassifier) and
        executes with 1-retry on transient network errors.
        """
        query: str = kwargs.get("query", "")
        num_results: int = int(kwargs.get("num_results", settings.SEARCH_MAX_RESULTS))

        if self.api_key is None:
            return {
                "query": query,
                "provider": "none",
                "configured": False,
                "status": "not_configured",
                "results": [],
                "message": "Search engine API keys are not configured.",
            }

        if not query:
            return {"query": "", "status": "error", "error": "query parameter is required", "results": []}

        clean_query = query.strip()
        cache_key = f"wsearch:{clean_query.lower()}:{num_results}"

        live_keywords = ["gold", "silver", "platinum", "commodity", "stock", "nifty", "sensex", "crypto", "bitcoin", "weather", "temperature", "forecast", "forex", "exchange rate"]
        is_live = any(kw in clean_query.lower() for kw in live_keywords)

        # ── Cache hit (bypassed for live queries) ──────────────────────────
        if not is_live:
            cached = _SEARCH_CACHE.get(cache_key)
            if cached:
                logger.info(
                    "[SEARCH] cache=HIT provider=%s query='%s' results=%d",
                    cached.get("provider"), clean_query[:50], len(cached.get("results", []))
                )
                return cached
        else:
            logger.info("[SEARCH] Live query detected — BYPASSING CACHE for query='%s'", clean_query[:50])

        logger.info("[SEARCH] cache=MISS query='%s'", clean_query[:50])

        # ── Provider selection via factory + classifier ────────────────────
        key_arg = None if self.api_key is _DEFAULT_KEY else (self.api_key or "")
        provider = SearchProviderFactory.get_provider(query=clean_query, api_key=key_arg)

        # ── Execute with 1-retry on transient errors ───────────────────────
        response = provider.search(clean_query, num_results=num_results)

        if response.status == "error" and response.error:
            err_lower = (response.error or "").lower()
            is_transient = any(t in err_lower for t in ["timeout", "urlopen", "connection", "reset"])
            if is_transient:
                logger.warning("[SEARCH] Transient error, retrying once: %s", response.error[:80])
                time.sleep(0.5)
                response = provider.search(clean_query, num_results=num_results)

        res_dict = response.to_dict()
        sanitized_error = self._sanitize_error(res_dict.get("error"))

        # ── URL deduplication ──────────────────────────────────────────────
        seen_urls: set[str] = set()
        seen_snippets: set[str] = set()
        dedup_results: List[Dict[str, Any]] = []
        for r in res_dict.get("results", []):
            url = r.get("url") or ""
            snippet_key = (r.get("snippet") or "")[:80].lower()
            if url not in seen_urls and snippet_key not in seen_snippets:
                seen_urls.add(url)
                if snippet_key:
                    seen_snippets.add(snippet_key)
                dedup_results.append(r)

        # ── Quality ranking ────────────────────────────────────────────────
        dedup_results.sort(key=_source_rank)

        logger.info(
            "[SEARCH] provider=%s latency=%.0fms cache=MISS status=%s results=%d",
            res_dict["provider"], res_dict["latency_ms"],
            res_dict["status"], len(dedup_results),
        )

        output: Dict[str, Any] = {
            "query": clean_query,
            "configured": True,
            "provider": res_dict["provider"],
            "status": res_dict["status"],
            "latency_ms": res_dict["latency_ms"],
            "results": dedup_results,
            "error": sanitized_error,
            "cached": False,
        }

        # Store for conversation memory reuse
        self._last_query = clean_query
        self._last_results = dedup_results

        # Cache successful results
        if res_dict["status"] == "success" and dedup_results:
            _SEARCH_CACHE.set(cache_key, {**output, "cached": True, "latency_ms": 0.0})

        return output
