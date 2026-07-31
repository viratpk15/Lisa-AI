"""
Jarvis AIOS — Brave Search Provider
-----------------------------------

Production search implementation using Brave Search API.
"""

import json
import logging
import urllib.request
import urllib.parse
from typing import List, Any

from app.Tools.search_providers.base import SearchProvider, SearchResult

logger = logging.getLogger(__name__)


class BraveProvider(SearchProvider):
    """Brave Search API Provider."""

    @property
    def name(self) -> str:
        return "brave"

    def _execute_search(self, query: str, num_results: int = 5, **kwargs: Any) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("Brave Search API key is missing.")

        params = urllib.parse.urlencode({"q": query, "count": num_results})
        url = f"https://api.search.brave.com/res/v1/web/search?{params}"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
            },
            method="GET",
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            results_data = body.get("web", {}).get("results", [])
            search_results = []
            for item in results_data:
                search_results.append(
                    SearchResult(
                        title=item.get("title", "Untitled"),
                        snippet=item.get("description", ""),
                        url=item.get("url", ""),
                        published_date=item.get("page_age"),
                        source="Brave",
                    )
                )
            return search_results
