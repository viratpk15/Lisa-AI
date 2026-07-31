"""
Jarvis AIOS — Live Information Contracts
----------------------------------------

Canonical Pydantic models for live information tools and responses.
All domain tools in the live information pipeline return ToolResult.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """
    Standard contract for all live information tools.

    Fields:
        success: Whether the tool execution completed without technical error.
        verified: Whether domain validation passed (units, bounds, source trust).
        confidence: Confidence score between 0.0 and 1.0.
        source: Name or URL of the data provider (e.g. IBJA, NSE, Open-Meteo).
        timestamp: ISO timestamp of data retrieval.
        payload: Structured domain data (e.g., price, unit, currency, asset).
        error: Optional error string if execution or validation failed.
    """

    success: bool
    verified: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = "Unknown"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
