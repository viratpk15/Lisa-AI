"""
Jarvis AIOS — Task Failure Recovery Manager
-------------------------------------------

Captures worker agent failure exceptions, generates structured failure records,
marks task as FAILED, and allows Supervisor to continue execution safely.
"""

import logging
from typing import Any, Dict
from app.Agents.task_model import TaskStatus
from app.Models.tool_result_schema import ToolExecutionRecord

logger = logging.getLogger(__name__)


def handle_worker_failure(
    task_id: str,
    agent_id: str,
    error: Exception | str,
    duration_ms: float = 0.0,
) -> Dict[str, Any]:
    """Capture exception and produce structured failure recovery record."""
    err_str = str(error)
    logger.error("[FAILURE-RECOVERY] Capturing worker failure for Task=%s Agent=%s: %s", task_id, agent_id, err_str)

    record = ToolExecutionRecord(
        task_id=task_id,
        agent=agent_id,
        tool="failure_recovery",
        input={"task_id": task_id},
        output=f"Task failed with error: {err_str}",
        duration_ms=duration_ms,
        success=False,
    )

    return {
        "status": TaskStatus.FAILED,
        "task_id": task_id,
        "agent": agent_id,
        "record": record.model_dump(),
        "error": err_str,
    }
