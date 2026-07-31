"""
Jarvis AIOS — Multi-Agent Structured Logger
------------------------------------------

Structured JSON logger for task execution duration, retries, success, and selected tools.
"""

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger("app.Observability.structured_logger")


def log_task_execution(
    task_id: str,
    agent_id: str,
    duration_ms: float,
    retries: int,
    success: bool,
    selected_tools: List[str] | None = None,
    extra: Dict[str, Any] | None = None,
) -> None:
    """Log structured multi-agent execution payload."""
    payload = {
        "event": "multi_agent_task_execution",
        "task_id": task_id,
        "agent_id": agent_id,
        "execution_duration_ms": round(duration_ms, 2),
        "retries": retries,
        "success": success,
        "selected_tools": selected_tools or [],
    }
    if extra:
        payload["extra"] = extra

    if success:
        logger.info("[STRUCTURED-LOG] %s", json.dumps(payload))
    else:
        logger.error("[STRUCTURED-LOG] %s", json.dumps(payload))
