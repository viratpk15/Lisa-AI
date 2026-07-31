"""
Jarvis AIOS — Live Tool Registry
--------------------------------

Central registry for domain-specific live information tools.
Dispatches queries dynamically based on classified domain intent.
"""

import logging
from typing import Dict, Any

from app.Tools.live_information.contracts import ToolResult
from app.Tools.live_information.tools.commodity_tool import CommodityTool
from app.Tools.live_information.tools.stock_tool import StockTool
from app.Tools.live_information.tools.crypto_tool import CryptoTool
from app.Tools.live_information.tools.weather_tool import WeatherTool
from app.Tools.live_information.tools.forex_tool import ForexTool

logger = logging.getLogger(__name__)


class LiveToolRegistry:
    """Registry managing dynamic dispatch of specialized live information tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {
            "commodity": CommodityTool(),
            "stocks": StockTool(),
            "crypto": CryptoTool(),
            "weather": WeatherTool(),
            "forex": ForexTool(),
        }

    def dispatch(self, domain: str, query: str) -> ToolResult:
        """
        Dynamically dispatches query to the registered domain tool.

        Args:
            domain: Domain string ("commodity", "stocks", "crypto", "weather", "forex").
            query: Raw user query string.

        Returns:
            ToolResult contract.
        """
        tool = self._tools.get(domain.lower())
        if not tool:
            # Fallback to commodity tool for generic price queries or commodity default
            logger.info("[LIVE-REGISTRY] Domain '%s' not registered, falling back to commodity tool", domain)
            tool = self._tools["commodity"]

        logger.info("[LIVE-REGISTRY] Dispatching query to domain tool '%s' for domain '%s'", tool.__class__.__name__, domain)
        return tool.execute(query)


live_tool_registry = LiveToolRegistry()
