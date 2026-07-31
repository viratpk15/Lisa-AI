"""
Jarvis AIOS — Serper Search Provider
------------------------------------

Production search implementation using Serper Google Search API.
"""

import json
import logging
import urllib.request
import urllib.parse
from typing import List, Any

from app.Tools.search_providers.base import SearchProvider, SearchResult

logger = logging.getLogger(__name__)


class SerperProvider(SearchProvider):
    """Serper Google Search API Provider."""

    @property
    def name(self) -> str:
        return "serper"

    def _execute_search(self, query: str, num_results: int = 5, **kwargs: Any) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("Serper API key is missing.")

        url = "https://google.serper.dev/search"
        payload = {"q": query, "num": num_results}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": self.api_key,
            },
            method="POST",
        )

        with self._open(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        search_results: List[SearchResult] = []

        # Surface Serper's direct answer / knowledge graph as the first result
        answer_snippet = (
            body.get("answerBox", {}).get("answer")
            or body.get("answerBox", {}).get("snippet")
            or body.get("knowledgeGraph", {}).get("description")
        )
        if answer_snippet:
            answer_title = (
                body.get("answerBox", {}).get("title")
                or body.get("knowledgeGraph", {}).get("title")
                or "Direct Answer"
            )
            answer_url = (
                body.get("answerBox", {}).get("link")
                or body.get("knowledgeGraph", {}).get("website", "https://google.com")
            )
            search_results.append(SearchResult(
                title=answer_title,
                snippet=answer_snippet,
                url=answer_url,
                source="Google (Direct Answer)",
            ))

        for item in body.get("organic", []):
            search_results.append(SearchResult(
                title=item.get("title", "Untitled"),
                snippet=item.get("snippet", ""),
                url=item.get("link", ""),
                published_date=item.get("date"),
                source="Google via Serper",
            ))

        return search_results
