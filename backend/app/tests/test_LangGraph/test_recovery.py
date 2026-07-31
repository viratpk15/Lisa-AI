"""
Tests for the Tool Recovery layer.

These tests verify the deterministic recovery engine and policy without
requiring any external services (LLM, network, or database).
"""


from app.LangGraph.recovery.policy import (
    MAX_TOOL_RETRIES,
    RETRY_BACKOFF_SECONDS,
    RECOVERABLE_ERRORS,
    PERMANENT_ERRORS,
    RecoveryDecision,
)
from app.LangGraph.recovery.recovery import (
    RecoveryResult,
    evaluate_recovery,
    should_retry,
    should_recover,
    should_replan,
    should_abort,
)


def test_policy_constants() -> None:
    assert MAX_TOOL_RETRIES == 2
    assert RETRY_BACKOFF_SECONDS == 0.0
    assert "FileNotFound" in RECOVERABLE_ERRORS
    assert "Timeout" in RECOVERABLE_ERRORS
    assert "InvalidArguments" in PERMANENT_ERRORS
    assert "PermissionDenied" in PERMANENT_ERRORS


def test_recovery_decision_enum() -> None:
    assert RecoveryDecision.RETRY.value == "retry"
    assert RecoveryDecision.RECOVER.value == "recover"
    assert RecoveryDecision.REPLAN.value == "replan"
    assert RecoveryDecision.ABORT.value == "abort"


def test_recoverable_error_triggers_retry() -> None:
    result = evaluate_recovery("FileNotFound: /path/to/file", 0)
    assert result.decision == RecoveryDecision.RETRY
    assert result.retry_count == 0


def test_recoverable_error_replans_after_retries_exhausted() -> None:
    result = evaluate_recovery("Timeout: connection timed out", MAX_TOOL_RETRIES)
    assert result.decision == RecoveryDecision.REPLAN


def test_permanent_error_triggers_replan() -> None:
    result = evaluate_recovery("InvalidArguments: missing required field", 0)
    assert result.decision == RecoveryDecision.REPLAN


def test_unclassified_error_triggers_abort() -> None:
    result = evaluate_recovery("SomeUnknownError: something went wrong", 0)
    assert result.decision == RecoveryDecision.ABORT


def test_no_error_triggers_retry() -> None:
    result = evaluate_recovery(None, 0)
    assert result.decision == RecoveryDecision.RETRY


def test_should_retry_true_for_recoverable() -> None:
    assert should_retry("Timeout: slow response", 0) is True
    assert should_retry("ConnectionError: network down", 1) is True


def test_should_retry_false_for_exhausted() -> None:
    assert should_retry("Timeout: slow response", MAX_TOOL_RETRIES) is False


def test_should_retry_false_for_permanent() -> None:
    assert should_retry("InvalidArguments: bad input", 0) is False


def test_should_recover_true_for_recoverable() -> None:
    assert should_recover("RateLimit: too many requests") is True
    assert should_recover("TemporaryFailure: try again") is True


def test_should_recover_false_for_permanent() -> None:
    assert should_recover("ToolNotFound: unknown tool") is False


def test_should_replan_true_for_permanent() -> None:
    assert should_replan("InvalidArguments: bad input", 0) is True


def test_should_replan_true_for_exhausted_recoverable() -> None:
    assert should_replan("Timeout: slow", MAX_TOOL_RETRIES) is True


def test_should_replan_false_for_recoverable_with_retries() -> None:
    assert should_replan("Timeout: slow", 0) is False


def test_should_abort_true_for_unclassified() -> None:
    assert should_abort("UnknownError: something") is True


def test_should_abort_false_for_recoverable() -> None:
    assert should_abort("FileNotFound: missing") is False


def test_recovery_result_dataclass() -> None:
    result = RecoveryResult(
        decision=RecoveryDecision.RETRY,
        reason="test",
        retry_count=1,
    )
    assert result.decision == RecoveryDecision.RETRY
    assert result.reason == "test"
    assert result.retry_count == 1
