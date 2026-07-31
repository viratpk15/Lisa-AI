"""
Recovery Engine

Deterministic tool recovery that runs before replanning. Classifies errors,
decides whether to retry, recover, replan, or abort. Contains no business
logic and makes no LLM calls.
"""

from dataclasses import dataclass

from app.LangGraph.recovery.policy import (
    MAX_TOOL_RETRIES,
    RECOVERABLE_ERRORS,
    PERMANENT_ERRORS,
    RecoveryDecision,
)


@dataclass
class RecoveryResult:
    """Result of a recovery evaluation.

    Attributes:
        decision: The recovery decision (RETRY, RECOVER, REPLAN, or ABORT).
        reason: Human-readable reason for the decision.
        retry_count: Number of retries attempted so far.
    """

    decision: RecoveryDecision
    reason: str
    retry_count: int = 0


def _classify_error(error: str | None) -> str | None:
    """Classify an error string into a known error type.

    Args:
        error: The error message from a tool execution.

    Returns:
        The error type string if recognized, otherwise None.
    """
    if not error:
        return None
    error_lower = error.lower()
    for err_type in RECOVERABLE_ERRORS:
        if err_type.lower() in error_lower:
            return err_type
    for err_type in PERMANENT_ERRORS:
        if err_type.lower() in error_lower:
            return err_type
    return None


def should_retry(error: str | None, retry_count: int) -> bool:
    """Determine if a tool should be retried.

    Args:
        error: The error message from the tool execution.
        retry_count: Number of retries already attempted.

    Returns:
        True if the tool should be retried, False otherwise.
    """
    if retry_count >= MAX_TOOL_RETRIES:
        return False
    error_type = _classify_error(error)
    return error_type in RECOVERABLE_ERRORS


def should_recover(error: str | None) -> bool:
    """Determine if a tool can be recovered (state modified).

    Recovery is possible for recoverable errors when retry is not
    appropriate. This is a placeholder for future recovery logic.

    Args:
        error: The error message from the tool execution.

    Returns:
        True if recovery is possible, False otherwise.
    """
    error_type = _classify_error(error)
    return error_type in RECOVERABLE_ERRORS


def should_replan(error: str | None, retry_count: int) -> bool:
    """Determine if the planner should be invoked.

    The planner is invoked when retries are exhausted for recoverable
    errors, or when a permanent error occurs.

    Args:
        error: The error message from the tool execution.
        retry_count: Number of retries already attempted.

    Returns:
        True if the planner should be invoked, False otherwise.
    """
    error_type = _classify_error(error)
    if error_type in PERMANENT_ERRORS:
        return True
    if error_type in RECOVERABLE_ERRORS and retry_count >= MAX_TOOL_RETRIES:
        return True
    return False


def should_abort(error: str | None) -> bool:
    """Determine if execution should be aborted.

    Execution is aborted for unclassified errors that cannot be recovered.

    Args:
        error: The error message from the tool execution.

    Returns:
        True if execution should abort, False otherwise.
    """
    error_type = _classify_error(error)
    return error_type is None and error is not None


def evaluate_recovery(
    error: str | None,
    retry_count: int,
) -> RecoveryResult:
    """Evaluate a tool failure and return a recovery decision.

    This is the main entry point for the recovery engine. It inspects
    the error and retry count, then returns a deterministic decision.

    Args:
        error: The error message from the tool execution.
        retry_count: Number of retries already attempted.

    Returns:
        A RecoveryResult with the decision and reason.
    """
    error_type = _classify_error(error)

    if error_type in PERMANENT_ERRORS:
        return RecoveryResult(
            decision=RecoveryDecision.REPLAN,
            reason=f"Permanent error: {error_type}",
            retry_count=retry_count,
        )

    if error_type in RECOVERABLE_ERRORS:
        if retry_count < MAX_TOOL_RETRIES:
            return RecoveryResult(
                decision=RecoveryDecision.RETRY,
                reason=f"Recoverable error: {error_type}, retrying",
                retry_count=retry_count,
            )
        return RecoveryResult(
            decision=RecoveryDecision.REPLAN,
            reason=f"Recoverable error: {error_type}, retries exhausted",
            retry_count=retry_count,
        )

    if error is not None:
        return RecoveryResult(
            decision=RecoveryDecision.ABORT,
            reason=f"Unclassified error: {error}",
            retry_count=retry_count,
        )

    return RecoveryResult(
        decision=RecoveryDecision.RETRY,
        reason="No error, continuing",
        retry_count=retry_count,
    )
