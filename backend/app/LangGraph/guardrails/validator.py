"""
Execution Guardrail Validator

Deterministic, side-effect-free validation that runs before every executor
iteration. The validator contains NO business logic and makes NO LLM calls.
It inspects an execution context and the current plan, then returns a
``ValidationResult`` telling the executor whether to continue, replan,
mark a step failed permanently, or terminate with a deterministic outcome.

Termination outcomes (every execution must end in exactly one of these):
    SUCCESS        - all steps completed.
    FAILED         - a step failed; replanning is permitted.
    ABORTED        - consecutive failures exceeded the limit.
    LIMIT_REACHED  - iteration / replan / circular limit exceeded.
    TIMEOUT        - wall-clock execution time exceeded.
    INVALID_PLAN   - plan violates structural invariants.
"""

from dataclasses import dataclass, field
from typing import Any

from app.LangGraph.guardrails.limits import (
    MAX_PLAN_STEPS,
    MAX_REPLANS,
    MAX_TOOL_RETRIES,
    MAX_CONSECUTIVE_FAILURES,
    MAX_EXECUTION_TIME_SECONDS,
    MAX_EXECUTOR_ITERATIONS,
)

# Deterministic termination outcomes.
OUTCOME_SUCCESS: str = "SUCCESS"
OUTCOME_FAILED: str = "FAILED"
OUTCOME_ABORTED: str = "ABORTED"
OUTCOME_LIMIT_REACHED: str = "LIMIT_REACHED"
OUTCOME_TIMEOUT: str = "TIMEOUT"
OUTCOME_INVALID_PLAN: str = "INVALID_PLAN"

# Outcomes after which the planner must NOT regenerate a plan.
# Only OUTCOME_FAILED permits replanning.
NON_REPLAN_OUTCOMES: tuple[str, ...] = (
    OUTCOME_ABORTED,
    OUTCOME_LIMIT_REACHED,
    OUTCOME_TIMEOUT,
    OUTCOME_INVALID_PLAN,
)

# Validator actions returned to the executor.
ACTION_CONTINUE: str = "continue"
ACTION_REPLAN: str = "replan"
ACTION_TERMINATE: str = "terminate"
ACTION_MARK_FAILED: str = "mark_failed"


@dataclass
class GuardrailContext:
    """Mutable execution counters tracked across executor iterations.

    The executor populates this from the LangGraph state at the start of
    each iteration and writes any updates back to the state afterwards.

    Attributes:
        execution_start_time: ``time.perf_counter()`` reading when execution began.
        iteration_count: Number of executor iterations performed.
        replanning_count: Number of replanning events performed.
        tool_retry_count: Number of tool retries for the current step.
        consecutive_failures: Number of consecutive step failures.
        step_execution_history: Ordered list of executed step IDs (for
            circular-execution detection).
    """

    execution_start_time: float
    iteration_count: int = 0
    replanning_count: int = 0
    tool_retry_count: int = 0
    consecutive_failures: int = 0
    step_execution_history: list[int] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of a guardrail validation pass.

    Attributes:
        action: One of continue / replan / terminate / mark_failed.
        outcome: Termination outcome when action is terminate, else None.
        reason: Human-readable reason string (always present).
    """

    action: str
    outcome: str | None = None
    reason: str = ""


def _count_steps(plan: dict[str, Any], status: str) -> int:
    """Count plan steps with a given status.

    Args:
        plan: Plan dictionary with a 'steps' list.
        status: Status value to count.

    Returns:
        Number of steps matching the status.
    """
    return sum(1 for s in plan.get("steps", []) if s.get("status") == status)


def _detect_circular_execution(history: list[int]) -> bool:
    """Detect a repeating execution cycle in the step history.

    Detects patterns such as A -> B -> A -> B (a 2-cycle) or the same step
    executed repeatedly. This prevents infinite loops where the executor
    keeps re-executing the same step(s) without progress.

    Args:
        history: Ordered list of executed step IDs.

    Returns:
        True if a circular execution pattern is detected.
    """
    # Same step executed repeatedly (e.g. [3, 3, 3, 3]).
    if len(history) >= MAX_CONSECUTIVE_FAILURES + 1:
        tail = history[-(MAX_CONSECUTIVE_FAILURES + 1):]
        if all(step == tail[0] for step in tail):
            return True

    # Alternating 2-cycle (e.g. [A, B, A, B]).
    if len(history) >= 4:
        last_four = history[-4:]
        if (
            last_four[0] == last_four[2]
            and last_four[1] == last_four[3]
            and last_four[0] != last_four[1]
        ):
            return True

    return False


def validate_execution(
    context: GuardrailContext,
    plan: dict[str, Any],
    now: float,
) -> ValidationResult:
    """Validate execution bounds before a single executor iteration.

    Runs ten deterministic checks in priority order. The first terminating
    or redirecting condition wins. Contains no business logic and performs
    no LLM calls.

    Args:
        context: Current guardrail counters for this execution.
        plan: The current plan dictionary.
        now: Current ``time.perf_counter()`` reading.

    Returns:
        A ValidationResult instructing the executor how to proceed.
    """
    plan_steps = plan.get("steps", [])
    plan_length = len(plan_steps)

    # 1. Execution time exceeded -> TIMEOUT.
    elapsed_seconds = now - context.execution_start_time
    if elapsed_seconds > MAX_EXECUTION_TIME_SECONDS:
        return ValidationResult(
            action=ACTION_TERMINATE,
            outcome=OUTCOME_TIMEOUT,
            reason="Execution time exceeded limit",
        )

    # 2. Iteration count exceeded -> LIMIT_REACHED.
    if context.iteration_count >= MAX_EXECUTOR_ITERATIONS:
        return ValidationResult(
            action=ACTION_TERMINATE,
            outcome=OUTCOME_LIMIT_REACHED,
            reason="Executor iteration limit reached",
        )

    # 7. Replanning count exceeded -> LIMIT_REACHED.
    if context.replanning_count > MAX_REPLANS:
        return ValidationResult(
            action=ACTION_TERMINATE,
            outcome=OUTCOME_LIMIT_REACHED,
            reason="Replanning limit reached",
        )

    # 9. Consecutive failures exceeded -> ABORTED.
    if context.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
        return ValidationResult(
            action=ACTION_TERMINATE,
            outcome=OUTCOME_ABORTED,
            reason="Consecutive failure limit reached",
        )

    # 10. Circular execution detected -> LIMIT_REACHED.
    if _detect_circular_execution(context.step_execution_history):
        return ValidationResult(
            action=ACTION_TERMINATE,
            outcome=OUTCOME_LIMIT_REACHED,
            reason="Circular execution detected",
        )

    # 6. Plan size exceeds maximum -> INVALID_PLAN.
    if plan_length > MAX_PLAN_STEPS:
        return ValidationResult(
            action=ACTION_TERMINATE,
            outcome=OUTCOME_INVALID_PLAN,
            reason="Plan exceeds maximum step count",
        )

    # 3. Completed step count cannot exceed plan length -> INVALID_PLAN.
    completed = _count_steps(plan, "completed")
    if completed > plan_length:
        return ValidationResult(
            action=ACTION_TERMINATE,
            outcome=OUTCOME_INVALID_PLAN,
            reason="Completed step count exceeds plan length",
        )

    # 4. Pending step count cannot exceed plan length -> INVALID_PLAN.
    pending = _count_steps(plan, "pending")
    if pending > plan_length:
        return ValidationResult(
            action=ACTION_TERMINATE,
            outcome=OUTCOME_INVALID_PLAN,
            reason="Pending step count exceeds plan length",
        )

    # 5. Current step must exist; if missing, trigger replanning.
    has_current = any(
        s.get("status") in ("in_progress", "pending") for s in plan_steps
    )
    if not has_current and plan_length > 0:
        return ValidationResult(
            action=ACTION_REPLAN,
            reason="No current step found, replanning required",
        )

    # 8. Tool retry count exceeded -> mark step failed permanently.
    if context.tool_retry_count > MAX_TOOL_RETRIES:
        return ValidationResult(
            action=ACTION_MARK_FAILED,
            reason="Tool retry limit exceeded, marking step failed",
        )

    # All checks passed -> continue normal execution.
    return ValidationResult(action=ACTION_CONTINUE, reason="All guardrails satisfied")
