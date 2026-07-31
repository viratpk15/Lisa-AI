"""
Jarvis AIOS — Task Timeout Handler
----------------------------------

Provides bounded execution enforcement and graceful cancellation for worker tasks.
"""

import logging
import concurrent.futures
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


def execute_with_timeout(
    fn: Callable[..., Any],
    timeout_seconds: float = 60.0,
    task_id: str = "task_unknown",
    agent_id: str = "agent_unknown",
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Execute a function with a strict timeout limit."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, *args, **kwargs)
        try:
            res = future.result(timeout=timeout_seconds)
            return {"result": res, "timed_out": False, "success": True}
        except concurrent.futures.TimeoutError:
            logger.error("[TIMEOUT] Task=%s Agent=%s exceeded timeout of %.1fs", task_id, agent_id, timeout_seconds)
            return {
                "result": f"Execution timed out after {timeout_seconds} seconds.",
                "timed_out": True,
                "success": False,
                "error": f"TimeoutError ({timeout_seconds}s limit)",
            }
        except Exception as e:
            logger.error("[EXECUTION-ERROR] Task=%s Agent=%s failed: %s", task_id, agent_id, str(e))
            return {
                "result": f"Task execution failed: {str(e)}",
                "timed_out": False,
                "success": False,
                "error": str(e),
            }
