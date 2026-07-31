"""
Jarvis AIOS — Search Provider Base Interface & Schema
-----------------------------------------------------

Abstract Base Class and data models for all Web Search Providers.
"""

import time
import urllib.request
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from app.Config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Standardized search result model."""
    title: str
    snippet: str
    url: str
    published_date: Optional[str] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "snippet": self.snippet,
            "url": self.url,
            "published_date": self.published_date,
            "source": self.source,
        }


@dataclass
class SearchResponse:
    """Standardized search response wrapper."""
    query: str
    provider: str
    status: str
    results: List[SearchResult] = field(default_factory=list)
    latency_ms: float = 0.0
    error: Optional[str] = None
    http_status: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "provider": self.provider,
            "status": self.status,
            "results": [r.to_dict() for r in self.results],
            "latency_ms": round(self.latency_ms, 2),
            "error": self.error,
            "http_status": self.http_status,
        }


# Pre-built no-proxy opener — bypasses https_proxy / HTTPS_PROXY env vars for
# all external search API calls. Scoped only to this module; does not affect
# any other network traffic in the process.
_NO_PROXY_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class SearchProvider:
    """Abstract Base Class for Web Search Providers."""

    def __init__(self, api_key: Optional[str] = None, timeout: Optional[float] = None) -> None:
        self.api_key = api_key
        self.timeout = timeout if timeout is not None else settings.SEARCH_TIMEOUT

    @property
    def name(self) -> str:
        raise NotImplementedError

    def _open(self, req: urllib.request.Request) -> Any:
        """Open an HTTP request bypassing any system proxy configuration."""
        return _NO_PROXY_OPENER.open(req, timeout=self.timeout)

    def search(self, query: str, num_results: int = 5, **kwargs: Any) -> SearchResponse:
        """Synchronous search wrapper with timing."""
        start_time = time.time()
        try:
            results = self._execute_search(query, num_results=num_results, **kwargs)
            latency = (time.time() - start_time) * 1000.0
            return SearchResponse(
                query=query,
                provider=self.name,
                status="success",
                results=results,
                latency_ms=latency,
                http_status=200,
            )
        except urllib.error.HTTPError as exc:
            latency = (time.time() - start_time) * 1000.0
            logger.error("[SEARCH-FAILURE] provider=%s query='%s' http_status=%d error='%s'", self.name, query, exc.code, str(exc))
            return SearchResponse(
                query=query,
                provider=self.name,
                status="error",
                results=[],
                latency_ms=latency,
                error=f"HTTP {exc.code}: {exc.reason}",
                http_status=exc.code,
            )
        except Exception as exc:
            latency = (time.time() - start_time) * 1000.0
            logger.error("[SEARCH-FAILURE] provider=%s query='%s' error='%s'", self.name, query, str(exc))
            return SearchResponse(
                query=query,
                provider=self.name,
                status="error",
                results=[],
                latency_ms=latency,
                error=str(exc),
            )

    def _execute_search(self, query: str, num_results: int = 5, **kwargs: Any) -> List[SearchResult]:
        raise NotImplementedError
