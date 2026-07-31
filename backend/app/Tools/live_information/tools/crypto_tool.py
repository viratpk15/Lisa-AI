"""
Jarvis AIOS — Live Crypto Tool
------------------------------

Fetches live cryptocurrency prices (BTC, ETH, SOL), parses structured payload,
validates through CryptoValidator, and returns ToolResult.
"""

import re
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from app.Tools.live_information.contracts import ToolResult
from app.Tools.live_information.validators.crypto_validator import CryptoValidator
from app.Tools.search_providers.factory import SearchProviderFactory

logger = logging.getLogger(__name__)


class CryptoTool:
    """Tool for fetching and validating cryptocurrency prices."""

    def __init__(self) -> None:
        self.validator = CryptoValidator()

    def execute(self, query: str) -> ToolResult:
        logger.info("[CRYPTO-TOOL] Executing live search for query='%s'", query)
        expanded_query = f"live crypto price USD CoinMarketCap CoinGecko today {query}"
        provider = SearchProviderFactory.get_provider(query=expanded_query)
        search_res = provider.search(query=expanded_query, num_results=5)

        if search_res.status != "success" or not search_res.results:
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source=provider.name,
                error=search_res.error or "Search returned no crypto data",
            )

        payload, source_used = self._parse_snippets(query, search_res.results)

        if not payload:
            return ToolResult(
                success=False,
                verified=False,
                confidence=0.0,
                source=provider.name,
                error="Could not parse verified crypto price from search response",
            )

        is_valid, confidence, reason = self.validator.validate(payload, source_used)
        if not is_valid or confidence < 0.8:
            return ToolResult(
                success=True,
                verified=False,
                confidence=confidence,
                source=source_used,
                payload=payload,
                error=f"Crypto validation failed: {reason}",
            )

        return ToolResult(
            success=True,
            verified=True,
            confidence=confidence,
            source=source_used,
            timestamp=datetime.now(timezone.utc),
            payload=payload,
        )

    def _parse_snippets(self, query: str, results: list) -> tuple[Dict[str, Any], str]:
        q_lower = query.lower()
        crypto_name = "Bitcoin" if "btc" in q_lower or "bitcoin" in q_lower else ("Ethereum" if "eth" in q_lower or "ethereum" in q_lower else "Crypto")

        for r in results:
            text = f"{r.title} {r.snippet}"
            source = r.source or r.url or "CoinMarketCap"
            # Regex for Crypto price e.g. "Bitcoin is trading at $65,420.50" or "BTC price: $65,420"
            m = re.search(r'(?:bitcoin|btc|ethereum|eth|crypto|[\w]+)\s*(?:is trading at|price|at|:)?\s*\$\s*([\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
            if m:
                p_str = m.group(1).replace(",", "")
                try:
                    price_val = float(p_str)
                    return {
                        "asset": crypto_name,
                        "symbol": crypto_name[:5].upper(),
                        "price_numeric": price_val,
                        "currency": "USD",
                        "formatted_string": f"{crypto_name}: ${price_val:,} USD",
                    }, source
                except ValueError:
                    pass

        return {}, ""
