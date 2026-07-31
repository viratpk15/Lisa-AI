"""
Jarvis AIOS — Tavily Search Provider
------------------------------------

Production search implementation using Tavily API.
Supports both basic (factual) and advanced (agentic/research) search depths.
"""

import json
import logging
import urllib.request
from typing import List, Optional, Any

from app.Tools.search_providers.base import SearchProvider, SearchResult

logger = logging.getLogger(__name__)


class TavilyProvider(SearchProvider):
    """Tavily Search API Provider with basic and advanced (agentic) modes."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        search_depth: str = "basic",
    ) -> None:
        super().__init__(api_key=api_key, timeout=timeout)
        self.search_depth = search_depth  # "basic" | "advanced"

    @property
    def name(self) -> str:
        return "tavily"

    def _execute_search(self, query: str, num_results: int = 5, **kwargs: Any) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("Tavily API key is missing.")

        depth = kwargs.get("search_depth", self.search_depth)
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": num_results,
            "search_depth": depth,
            "include_answer": depth == "advanced",  # surface synthesis answer for research
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self._open(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        search_results: List[SearchResult] = []

        # Surface Tavily's synthesized answer as the first result for research queries
        if depth == "advanced" and body.get("answer"):
            search_results.append(SearchResult(
                title="Tavily Research Summary",
                snippet=body["answer"],
                url="https://tavily.com",
                source="Tavily (Synthesized)",
            ))

        for item in body.get("results", []):
            search_results.append(SearchResult(
                title=item.get("title", "Untitled"),
                snippet=item.get("content", item.get("snippet", "")),
                url=item.get("url", ""),
                published_date=item.get("published_date"),
                source="Tavily",
            ))

        return search_results
