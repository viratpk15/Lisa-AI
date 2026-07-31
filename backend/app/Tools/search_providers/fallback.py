"""
Jarvis AIOS — Fallback & Open Search Provider
--------------------------------------------

Zero-config fallback provider for public API search, weather queries, and offline mode.
Uses DuckDuckGo HTML scraping to return real results when no API keys are configured.
"""

import json
import logging
import urllib.request
import urllib.parse
from typing import List, Any

from app.Tools.search_providers.base import SearchProvider, SearchResult

logger = logging.getLogger(__name__)


class FallbackProvider(SearchProvider):
    """Fallback Search Provider handling public APIs, Weather, and offline notices."""

    @property
    def name(self) -> str:
        return "fallback"

    def _execute_search(self, query: str, num_results: int = 5, **kwargs: Any) -> List[SearchResult]:
        q_lower = query.lower()

        # 1. Special Handling for Weather Queries (Open-Meteo Public API)
        if any(kw in q_lower for kw in ["weather", "rain", "temperature", "forecast", "channapatna"]):
            try:
                location = "Channapatna"
                lat, lon = 12.6518, 77.2084
                weather_url = (
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                    f"&current_weather=true&hourly=precipitation_probability,temperature_2m"
                )
                req = urllib.request.Request(weather_url, headers={"User-Agent": "JarvisAIOS/1.0"})
                with self._open(req) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    curr = data.get("current_weather", {})
                    temp = curr.get("temperature", "N/A")
                    wind = curr.get("windspeed", "N/A")
                    prob = data.get("hourly", {}).get("precipitation_probability", [0])[0]

                    snippet = (
                        f"Live Weather Forecast for {location}: "
                        f"Temperature: {temp}°C, Wind Speed: {wind} km/h, "
                        f"Rain/Precipitation Probability: {prob}%."
                    )
                    return [
                        SearchResult(
                            title=f"Live Weather Forecast — {location}",
                            snippet=snippet,
                            url="https://open-meteo.com",
                            source="Open-Meteo Weather API",
                        )
                    ]
            except Exception as e:
                logger.warning("Open-Meteo weather fetch error: %s", str(e))

        # 2. DuckDuckGo HTML scraping — real results, no API key required
        try:
            import re
            encoded_q = urllib.parse.quote(query)
            ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
            req = urllib.request.Request(
                ddg_url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
                    ),
                    "Accept-Language": "en-US,en;q=0.9",
                },
            )
            with self._open(req) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            results: List[SearchResult] = []

            # Parse result blocks: title + snippet from DuckDuckGo HTML
            blocks = re.findall(
                r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
                r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
                html,
                re.DOTALL,
            )

            for url, raw_title, raw_snippet in blocks[:num_results]:
                title = re.sub(r"<[^>]+>", "", raw_title).strip()
                snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()
                # Unwrap DuckDuckGo redirect URLs to actual destination
                if "uddg=" in url:
                    try:
                        match = re.search(r"uddg=([^&]+)", url)
                        if match:
                            url = urllib.parse.unquote(match.group(1))
                    except Exception:
                        pass
                if title and snippet:
                    results.append(SearchResult(title=title, snippet=snippet, url=url, source="DuckDuckGo"))

            if results:
                logger.info("[FALLBACK] DuckDuckGo returned %d results for query='%s'", len(results), query)
                return results

            logger.warning("[FALLBACK] DuckDuckGo returned no parseable results for query='%s'", query)

        except Exception as e:
            logger.warning("[FALLBACK] DuckDuckGo fetch error: %s", str(e))

        # 3. Hard fallback — network or parse failure
        return [
            SearchResult(
                title=f"Search: {query}",
                snippet=(
                    f"No live search results available for '{query}'. "
                    "Configure TAVILY_API_KEY, BRAVE_API_KEY, or SERPER_API_KEY for full search support."
                ),
                url=f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}",
                source="No Provider",
            )
        ]
