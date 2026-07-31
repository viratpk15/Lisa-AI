"""
Execution Guardrails

Deterministic safety layer that prevents infinite execution scenarios.
Every request must terminate safely with a classified outcome.
"""

from app.LangGraph.guardrails.limits import (
    MAX_PLAN_STEPS,
    MAX_REPLANS,
    MAX_TOOL_RETRIES,
    MAX_CONSECUTIVE_FAILURES,
    MAX_EXECUTION_TIME_SECONDS,
    MAX_EXECUTOR_ITERATIONS,
)
from app.LangGraph.guardrails.validator import (
    GuardrailContext,
    ValidationResult,
    validate_execution,
    OUTCOME_SUCCESS,
    OUTCOME_FAILED,
    OUTCOME_ABORTED,
    OUTCOME_LIMIT_REACHED,
    OUTCOME_TIMEOUT,
    OUTCOME_INVALID_PLAN,
    NON_REPLAN_OUTCOMES,
    ACTION_CONTINUE,
    ACTION_REPLAN,
    ACTION_TERMINATE,
    ACTION_MARK_FAILED,
)

__all__ = [
    "MAX_PLAN_STEPS",
    "MAX_REPLANS",
    "MAX_TOOL_RETRIES",
    "MAX_CONSECUTIVE_FAILURES",
    "MAX_EXECUTION_TIME_SECONDS",
    "MAX_EXECUTOR_ITERATIONS",
    "GuardrailContext",
    "ValidationResult",
    "validate_execution",
    "OUTCOME_SUCCESS",
    "OUTCOME_FAILED",
    "OUTCOME_ABORTED",
    "OUTCOME_LIMIT_REACHED",
    "OUTCOME_TIMEOUT",
    "OUTCOME_INVALID_PLAN",
    "NON_REPLAN_OUTCOMES",
    "ACTION_CONTINUE",
    "ACTION_REPLAN",
    "ACTION_TERMINATE",
    "ACTION_MARK_FAILED",
]
