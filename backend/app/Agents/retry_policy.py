"""
Jarvis AIOS — Multi-Agent Retry Policy
-------------------------------------

Exponential backoff retry policy for worker agent tool and task executions.
"""

import logging
import time
from typing import Any, Callable, Dict
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RetryPolicy(BaseModel):
    """Configuration and helper for exponential backoff retries."""

    max_retries: int = Field(default=3, description="Maximum retry attempts.")
    initial_delay: float = Field(default=0.1, description="Initial backoff delay in seconds.")
    backoff_factor: float = Field(default=2.0, description="Backoff multiplier.")

    def execute_with_retry(
        self,
        fn: Callable[..., Any],
        *args: Any,
        task_id: str = "task_unknown",
        agent_id: str = "agent_unknown",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a function with exponential backoff retries on failure."""
        attempts = 0
        current_delay = self.initial_delay
        last_exception: Exception | None = None

        while attempts <= self.max_retries:
            attempts += 1
            try:
                res = fn(*args, **kwargs)
                if attempts > 1:
                    logger.info("[RETRY-SUCCESS] Task=%s Agent=%s succeeded on attempt %d", task_id, agent_id, attempts)
                return {"result": res, "retries": attempts - 1, "success": True}
            except Exception as e:
                last_exception = e
                logger.warning(
                    "[RETRY-FAILURE] Task=%s Agent=%s attempt %d/%d failed with error: %s",
                    task_id, agent_id, attempts, self.max_retries + 1, str(e)
                )
                if attempts <= self.max_retries:
                    time.sleep(current_delay)
                    current_delay *= self.backoff_factor

        return {
            "result": f"Execution failed after {attempts} attempts: {str(last_exception)}",
            "retries": attempts - 1,
            "success": False,
            "error": str(last_exception),
        }
