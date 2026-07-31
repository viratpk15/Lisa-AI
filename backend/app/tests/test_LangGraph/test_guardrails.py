"""
Tests for the Execution Guardrails layer.

These tests verify the deterministic validator and the named limits without
requiring any external services (LLM, network, or database).
"""

import time

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
    validate_execution,
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


def _plan(step_statuses: list[str]) -> dict:
    """Build a minimal plan dict from a list of step statuses."""
    return {
        "goal": "test",
        "steps": [
            {"id": i + 1, "description": f"step {i + 1}", "tool": "", "status": s}
            for i, s in enumerate(step_statuses)
        ],
    }


def test_limits_are_named_constants() -> None:
    assert MAX_PLAN_STEPS == 20
    assert MAX_REPLANS == 3
    assert MAX_TOOL_RETRIES == 2
    assert MAX_CONSECUTIVE_FAILURES == 3
    assert MAX_EXECUTION_TIME_SECONDS == 120
    assert MAX_EXECUTOR_ITERATIONS == 50


def test_continue_when_all_valid() -> None:
    ctx = GuardrailContext(execution_start_time=time.perf_counter())
    result = validate_execution(ctx, _plan(["pending"]), time.perf_counter())
    assert result.action == ACTION_CONTINUE
    assert result.outcome is None


def test_timeout_termination() -> None:
    ctx = GuardrailContext(execution_start_time=0.0)
    now = float(MAX_EXECUTION_TIME_SECONDS + 1)
    result = validate_execution(ctx, _plan(["pending"]), now)
    assert result.action == ACTION_TERMINATE
    assert result.outcome == OUTCOME_TIMEOUT


def test_iteration_limit_termination() -> None:
    ctx = GuardrailContext(execution_start_time=time.perf_counter(), iteration_count=MAX_EXECUTOR_ITERATIONS)
    result = validate_execution(ctx, _plan(["pending"]), time.perf_counter())
    assert result.action == ACTION_TERMINATE
    assert result.outcome == OUTCOME_LIMIT_REACHED


def test_replan_limit_termination() -> None:
    ctx = GuardrailContext(execution_start_time=time.perf_counter(), replanning_count=MAX_REPLANS + 1)
    result = validate_execution(ctx, _plan(["pending"]), time.perf_counter())
    assert result.action == ACTION_TERMINATE
    assert result.outcome == OUTCOME_LIMIT_REACHED


def test_consecutive_failures_abort() -> None:
    ctx = GuardrailContext(
        execution_start_time=time.perf_counter(),
        consecutive_failures=MAX_CONSECUTIVE_FAILURES,
    )
    result = validate_execution(ctx, _plan(["pending"]), time.perf_counter())
    assert result.action == ACTION_TERMINATE
    assert result.outcome == OUTCOME_ABORTED


def test_circular_execution_detected() -> None:
    # Alternating 2-cycle A -> B -> A -> B
    ctx = GuardrailContext(
        execution_start_time=time.perf_counter(),
        step_execution_history=[1, 2, 1, 2],
    )
    result = validate_execution(ctx, _plan(["pending", "pending"]), time.perf_counter())
    assert result.action == ACTION_TERMINATE
    assert result.outcome == OUTCOME_LIMIT_REACHED


def test_repeated_step_circular_detected() -> None:
    ctx = GuardrailContext(
        execution_start_time=time.perf_counter(),
        step_execution_history=[3, 3, 3, 3],
    )
    result = validate_execution(ctx, _plan(["pending"]), time.perf_counter())
    assert result.action == ACTION_TERMINATE
    assert result.outcome == OUTCOME_LIMIT_REACHED


def test_plan_too_large_invalid() -> None:
    ctx = GuardrailContext(execution_start_time=time.perf_counter())
    big_plan = _plan(["pending"] * (MAX_PLAN_STEPS + 1))
    result = validate_execution(ctx, big_plan, time.perf_counter())
    assert result.action == ACTION_TERMINATE
    assert result.outcome == OUTCOME_INVALID_PLAN


def test_missing_current_step_triggers_replan() -> None:
    ctx = GuardrailContext(execution_start_time=time.perf_counter())
    # All steps completed -> no current step, but plan not empty.
    result = validate_execution(ctx, _plan(["completed", "completed"]), time.perf_counter())
    assert result.action == ACTION_REPLAN


def test_tool_retry_exceeded_marks_failed() -> None:
    ctx = GuardrailContext(
        execution_start_time=time.perf_counter(),
        tool_retry_count=MAX_TOOL_RETRIES + 1,
    )
    result = validate_execution(ctx, _plan(["in_progress"]), time.perf_counter())
    assert result.action == ACTION_MARK_FAILED


def test_non_replan_outcomes_exclude_failed() -> None:
    assert OUTCOME_FAILED not in NON_REPLAN_OUTCOMES
    assert OUTCOME_LIMIT_REACHED in NON_REPLAN_OUTCOMES
    assert OUTCOME_TIMEOUT in NON_REPLAN_OUTCOMES
    assert OUTCOME_INVALID_PLAN in NON_REPLAN_OUTCOMES
    assert OUTCOME_ABORTED in NON_REPLAN_OUTCOMES
