"""
Jarvis AIOS — Email Tools Security & Execution Guards
-----------------------------------------------------
Enforces:
1. Input body capping to 8,000 characters before LLM inference.
2. Per-user rate limiting: max 60 LLM tool calls per hour.
3. Observability telemetry logging for LLM token usage and latency.
4. Strict JSON extraction and validation helper.
"""

import json
import logging
import re
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)

BODY_CHAR_LIMIT = 8000
MAX_CALLS_PER_HOUR = 60
_user_call_history: Dict[int, List[float]] = defaultdict(list)


def cap_email_body(body: str, limit: int = BODY_CHAR_LIMIT) -> str:
    """Cap email body to maximum character limit."""
    if not body:
        return ""
    if len(body) <= limit:
        return body
    return body[:limit] + "\n...[content truncated to 8000 characters]"


def check_and_record_rate_limit(user_id: int) -> None:
    """Enforce per-user rate limit of max 60 LLM tool calls per hour."""
    now = time.time()
    one_hour_ago = now - 3600.0

    history = _user_call_history[user_id]
    # Filter out calls older than 1 hour
    _user_call_history[user_id] = [ts for ts in history if ts > one_hour_ago]

    if len(_user_call_history[user_id]) >= MAX_CALLS_PER_HOUR:
        raise ValueError("Rate limit exceeded: Maximum 60 email intelligence LLM calls per hour. Please try again later.")

    _user_call_history[user_id].append(now)


def reset_rate_limits_for_test() -> None:
    """Helper to reset rate limits in unit tests."""
    _user_call_history.clear()


def log_llm_telemetry(
    model_name: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    latency_ms: float = 0.0,
) -> None:
    """Record LLM token usage and latency in Observability Manager."""
    try:
        observability_manager.record_llm_usage(
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )
    except Exception as exc:
        logger.debug("Failed to record observability metric: %s", exc)


def extract_json_from_llm(raw_text: str) -> Dict[str, Any]:
    """Parse JSON object from LLM response text, stripping markdown blocks if present.

    Raises:
        ValueError: If JSON is invalid or not a dictionary.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("LLM returned an empty response. Expected valid JSON object.")

    cleaned = raw_text.strip()
    # Check for markdown codeblocks anywhere in the response
    codeblock_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    candidate = codeblock_match.group(1).strip() if codeblock_match else cleaned

    try:
        data = json.loads(candidate)
    except Exception as exc:
        # Search for first '{' and last '}'
        match = re.search(r"(\{.*\})", candidate, re.DOTALL)
        if match:
            json_str = match.group(1)
            # Clean trailing commas before closing braces
            repaired = re.sub(r",\s*([\]}])", r"\1", json_str)
            try:
                data = json.loads(repaired)
            except Exception:
                raise ValueError(f"Malformed LLM response: failed to parse JSON object: {exc}") from exc
        else:
            raise ValueError(f"Malformed LLM response: failed to parse JSON object: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Malformed LLM response: expected JSON object, got {type(data).__name__}.")

    return data
