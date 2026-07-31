"""
Executor Node

Manages plan execution by coordinating between Agent and Tool nodes.
Executes plans one step at a time. Before every iteration the execution
guardrails validator is consulted to prevent infinite execution scenarios;
every termination is classified with a deterministic outcome. The planner
is only invoked for failures or when replanning is explicitly required -
never after successful execution, and never after a non-replan outcome
(LIMIT_REACHED, TIMEOUT, INVALID_PLAN, ABORTED).
"""

import logging
import time
from typing import Any, Literal

from langgraph.graph import END

from app.LangGraph.state import State
from app.Observability.trace import measure_time, calculate_duration
from app.Observability.manager import observability_manager
from app.LangGraph.guardrails.validator import (
    GuardrailContext,
    validate_execution,
    OUTCOME_SUCCESS,
    OUTCOME_ABORTED,
    ACTION_REPLAN,
    ACTION_TERMINATE,
    ACTION_MARK_FAILED,
)
from app.LangGraph.recovery.recovery import evaluate_recovery
from app.LangGraph.recovery.policy import RecoveryDecision

logger = logging.getLogger(__name__)

# Execution outcome states (legacy, retained for compatibility).
EXECUTION_SUCCESS = "success"
EXECUTION_FAILURE = "failure"
EXECUTION_REPLAN_REQUIRED = "replan_required"


def _get_current_step(plan: dict[str, Any]) -> dict[str, Any] | None:
    """Find the current pending step in a plan.

    Args:
        plan: Plan dictionary with steps list.

    Returns:
        The first pending step, or None if no pending steps exist.
    """
    steps = plan.get("steps", [])
    for step in steps:
        if step.get("status") == "pending":
            return step
    return None


def _mark_step_in_progress(plan: dict[str, Any], step_id: int) -> None:
    """Mark a step as in_progress.

    Args:
        plan: Plan dictionary with steps list (modified in-place).
        step_id: ID of the step to mark.
    """
    for step in plan.get("steps", []):
        if step.get("id") == step_id:
            step["status"] = "in_progress"
            break


def _mark_step_completed(plan: dict[str, Any], step_id: int) -> None:
    """Mark a step as completed.

    Args:
        plan: Plan dictionary with steps list (modified in-place).
        step_id: ID of the step to mark.
    """
    for step in plan.get("steps", []):
        if step.get("id") == step_id:
            step["status"] = "completed"
            break


def _mark_step_failed(plan: dict[str, Any], step_id: int) -> None:
    """Mark a step as failed.

    Args:
        plan: Plan dictionary with steps list (modified in-place).
        step_id: ID of the step to mark.
    """
    for step in plan.get("steps", []):
        if step.get("id") == step_id:
            step["status"] = "failed"
            break


def _has_pending_steps(plan: dict[str, Any]) -> bool:
    """Check if plan has any pending steps.

    Args:
        plan: Plan dictionary with steps list.

    Returns:
        True if at least one step is pending, False otherwise.
    """
    steps = plan.get("steps", [])
    return any(step.get("status") == "pending" for step in steps)


def _build_guardrail_context(state: State) -> GuardrailContext:
    """Build a GuardrailContext from the current LangGraph state.

    Args:
        state: The current LangGraph state.

    Returns:
        A GuardrailContext populated with the state's guardrail counters.
    """
    return GuardrailContext(
        execution_start_time=state.get("execution_start_time", time.perf_counter()),
        iteration_count=state.get("iteration_count", 0),
        replanning_count=state.get("replanning_count", 0),
        tool_retry_count=state.get("tool_retry_count", 0),
        consecutive_failures=state.get("consecutive_failures", 0),
        step_execution_history=list(state.get("step_execution_history", [])),
    )


def _terminate(
    state: State,
    plan: dict[str, Any],
    outcome: str,
    reason: str,
) -> dict[str, Any]:
    """Terminate execution with a classified deterministic outcome.

    Persists the final execution state, clears active execution, and never
    leaves orphan execution state. Records the termination in the trace.

    Args:
        state: The current LangGraph state.
        plan: The current plan dictionary.
        outcome: Deterministic termination outcome.
        reason: Human-readable termination reason.

    Returns:
        State update dict routing to END with the termination outcome.
    """
    session_id = state.get("session_id")
    logger.warning("Execution terminated: %s (%s)", outcome, reason)

    observability_manager.record_termination(
        reason=reason,
        outcome=outcome,
        iterations=state.get("iteration_count", 0),
        duration_ms=(time.perf_counter() - state.get("execution_start_time", time.perf_counter())) * 1000.0,
        retry_count=state.get("tool_retry_count", 0),
        failure_count=state.get("consecutive_failures", 0),
    )

    if session_id:
        from app.Memory.manager import memory_manager

        memory_manager.clear_execution_state(session_id)

    return {
        "plan": plan,
        "execution_outcome": outcome,
        "termination_reason": outcome,
        "_route_to": END,
    }


def executor(state: State) -> dict[str, Any]:
    """Execute plan steps one at a time with guardrail validation.

    Before every iteration the guardrails validator is consulted. Depending
    on the result the executor continues, requests replanning, marks a step
    failed permanently, or terminates with a classified outcome. Every
    termination persists final state and clears active execution.

    Args:
        state: The current LangGraph state.

    Returns:
        State update dict with updated plan, execution outcome, and routing.
    """
    start_time = measure_time()
    plan = state.get("plan", {})
    action = state.get("action", {})
    observation = state.get("observation", {})
    session_id = state.get("session_id")

    # --- Guardrail validation before this iteration ---
    context = _build_guardrail_context(state)
    result = validate_execution(context, plan, time.perf_counter())

    if result.action == ACTION_TERMINATE:
        observability_manager.record_duration("executor", calculate_duration(start_time))
        return _terminate(state, plan, result.outcome, result.reason)

    if result.action == ACTION_REPLAN:
        logger.info("Guardrail triggered replanning: %s", result.reason)
        return {
            "plan": plan,
            "execution_outcome": EXECUTION_REPLAN_REQUIRED,
            "_route_to": "planner",
        }

    if result.action == ACTION_MARK_FAILED:
        # Mark the current in_progress step failed permanently.
        current_step = None
        for step in plan.get("steps", []):
            if step.get("status") == "in_progress":
                current_step = step
                break
        if current_step:
            _mark_step_failed(plan, current_step.get("id"))
            observability_manager.record_executor_step("failed")
        return {
            "plan": plan,
            "execution_outcome": EXECUTION_FAILURE,
            "_route_to": "planner",
        }

    # If no plan exists, request planning
    if not plan or not plan.get("steps"):
        logger.info("No plan exists, requesting planning")
        observability_manager.record_executor_step("skipped")
        return {
            "plan": plan,
            "execution_outcome": EXECUTION_REPLAN_REQUIRED,
            "_route_to": "planner",
        }

    # If this is the first execution (no action yet), initialize first step
    if not action:
        current_step = _get_current_step(plan)
        if current_step:
            step_id = current_step.get("id")
            _mark_step_in_progress(plan, step_id)
            history = list(state.get("step_execution_history", []))
            history.append(step_id)
            logger.info(
                "Starting execution of step %d/%d",
                step_id,
                len(plan.get("steps", [])),
            )

            if session_id:
                _persist_execution_state(session_id, plan, EXECUTION_SUCCESS)

            return {
                "plan": plan,
                "step_execution_history": history,
                "_route_to": "agent",
            }

    # If there's an observation from tool execution, process the result
    if observation:
        current_step = None
        for step in plan.get("steps", []):
            if step.get("status") == "in_progress":
                current_step = step
                break

        if current_step:
            step_id = current_step.get("id")

            # Classify execution outcome using deterministic rules
            outcome = _classify_execution_outcome(action, observation, plan)

            if outcome == EXECUTION_FAILURE:
                # --- Recovery evaluation BEFORE replanning ---
                error = observation.get("error")
                retry_count = state.get("tool_retry_count", 0)
                recovery = evaluate_recovery(error, retry_count)

                observability_manager.record_recovery(
                    error=error or "unknown",
                    decision=recovery.decision.value,
                    retry_count=recovery.retry_count,
                )

                if recovery.decision == RecoveryDecision.RETRY:
                    # Increment retry count and retry the same tool.
                    logger.info(
                        "Recovery: retrying step %d (retry %d)",
                        step_id,
                        retry_count + 1,
                    )
                    return {
                        "plan": plan,
                        "tool_retry_count": retry_count + 1,
                        "_route_to": "agent",
                    }

                if recovery.decision == RecoveryDecision.ABORT:
                    # Unrecoverable error - terminate.
                    observability_manager.record_duration(
                        "executor", calculate_duration(start_time)
                    )
                    return _terminate(
                        state, plan, OUTCOME_ABORTED, recovery.reason
                    )

                # REPLAN or RECOVER: mark step failed and go to planner.
                _mark_step_failed(plan, step_id)
                observability_manager.record_executor_step("failed")
                logger.warning(
                    "Step %d failed: %s",
                    step_id,
                    error or "unknown error",
                )
                if session_id:
                    _persist_execution_state(session_id, plan, EXECUTION_FAILURE)

                return {
                    "plan": plan,
                    "execution_outcome": EXECUTION_FAILURE,
                    "_route_to": "planner",
                }

            # Mark as completed (SUCCESS or REPLAN_REQUIRED)
            _mark_step_completed(plan, step_id)
            observability_manager.record_executor_step("completed")
            logger.info("Step %d completed successfully", step_id)

            if outcome == EXECUTION_REPLAN_REQUIRED:
                logger.info("Replanning required after step completion")
                if session_id:
                    _persist_execution_state(session_id, plan, EXECUTION_REPLAN_REQUIRED)

                return {
                    "plan": plan,
                    "execution_outcome": EXECUTION_REPLAN_REQUIRED,
                    "_route_to": "planner",
                }

            logger.info("Step succeeded, continuing to next step")

    # Check if there are more pending steps
    if _has_pending_steps(plan):
        next_step = _get_current_step(plan)
        if next_step:
            step_id = next_step.get("id")
            _mark_step_in_progress(plan, step_id)
            history = list(state.get("step_execution_history", []))
            history.append(step_id)
            logger.info(
                "Advancing to step %d/%d",
                step_id,
                len(plan.get("steps", [])),
            )

            if session_id:
                _persist_execution_state(session_id, plan, EXECUTION_SUCCESS)

            return {
                "plan": plan,
                "step_execution_history": history,
                "_route_to": "agent",
            }

    # No pending steps remaining - execution complete
    completed_count = sum(1 for s in plan.get("steps", []) if s.get("status") == "completed")
    total_count = len(plan.get("steps", []))
    logger.info(
        "Plan execution complete: %d/%d steps completed",
        completed_count,
        total_count,
    )

    observability_manager.record_duration("executor", calculate_duration(start_time))
    return _terminate(state, plan, OUTCOME_SUCCESS, "All steps completed")


def _classify_execution_outcome(
    action: dict[str, Any],
    observation: dict[str, Any],
    plan: dict[str, Any],
) -> Literal["success", "failure", "replan_required"]:
    """Classify the execution outcome after tool execution.

    Uses deterministic rules to classify the outcome:
    - SUCCESS: Tool executed successfully, continue to next step
    - FAILURE: Tool execution failed, needs replanning
    - REPLAN_REQUIRED: Tool succeeded but plan needs adjustment

    Args:
        action: The action dict from agent.
        observation: The observation dict from tool execution.
        plan: Current plan dictionary.

    Returns:
        Execution outcome: "success", "failure", or "replan_required".
    """
    if observation.get("error"):
        logger.info("Execution outcome: FAILURE (tool execution error)")
        return EXECUTION_FAILURE

    if not plan or not plan.get("steps"):
        logger.info("Execution outcome: REPLAN_REQUIRED (invalid plan)")
        return EXECUTION_REPLAN_REQUIRED

    current_step = _get_current_step(plan)
    if current_step and current_step.get("status") not in [
        "in_progress",
        "completed",
        "failed",
    ]:
        logger.info("Execution outcome: REPLAN_REQUIRED (step not properly marked)")
        return EXECUTION_REPLAN_REQUIRED

    result = observation.get("result", {})
    if isinstance(result, dict) and result.get("requires_replan"):
        logger.info("Execution outcome: REPLAN_REQUIRED (tool requested replanning)")
        return EXECUTION_REPLAN_REQUIRED

    if isinstance(result, dict) and result.get("partial_success"):
        logger.info("Execution outcome: REPLAN_REQUIRED (partial success)")
        return EXECUTION_REPLAN_REQUIRED

    logger.info("Execution outcome: SUCCESS")
    return EXECUTION_SUCCESS


def _persist_execution_state(session_id: str, plan: dict[str, Any], outcome: str) -> None:
    """Persist execution state to SQLite.

    Args:
        session_id: Session identifier.
        plan: Current plan dictionary.
        outcome: Current execution outcome.
    """
    try:
        from app.Memory.manager import memory_manager

        completed_steps = [
            s.get("id") for s in plan.get("steps", []) if s.get("status") == "completed"
        ]
        pending_steps = [
            s.get("id") for s in plan.get("steps", []) if s.get("status") == "pending"
        ]

        current_step = None
        for step in plan.get("steps", []):
            if step.get("status") == "in_progress":
                current_step = step.get("id")
                break

        if outcome == EXECUTION_FAILURE:
            execution_status = "failed"
        elif pending_steps:
            execution_status = "executing"
        else:
            execution_status = "completed"

        execution_state = {
            "current_plan": plan,
            "current_step": current_step,
            "completed_steps": completed_steps,
            "pending_steps": pending_steps,
            "execution_status": execution_status,
        }

        memory_manager.save_execution_state(session_id, execution_state)
        logger.debug("Persisted execution state for session %s", session_id)

    except Exception as e:
        logger.warning("Failed to persist execution state: %s", str(e))
        # Don't fail execution if persistence fails
