"""
Recovery Policy

Named constants and error classifications for deterministic tool recovery.
No magic numbers; all recoverable/permanent errors are explicitly listed.
"""

from enum import Enum

# Maximum number of retries for a recoverable tool error.
MAX_TOOL_RETRIES: int = 2

# Backoff time in seconds between retries (0 = immediate retry).
RETRY_BACKOFF_SECONDS: float = 0.0

# Error types that are considered recoverable (may be retried).
RECOVERABLE_ERRORS: tuple[str, ...] = (
    "FileNotFound",
    "Timeout",
    "TemporaryFailure",
    "RateLimit",
    "ConnectionError",
)

# Error types that are permanent (never retry).
PERMANENT_ERRORS: tuple[str, ...] = (
    "InvalidArguments",
    "PermissionDenied",
    "ToolNotFound",
    "UnsupportedOperation",
)


class RecoveryDecision(Enum):
    """Deterministic recovery decision for a failed tool execution.

    Values:
        RETRY: The tool should be retried with the same arguments.
        RECOVER: The tool may be recovered (state modified, no replan).
        REPLAN: The planner should be invoked to generate a new plan.
        ABORT: Execution should be terminated immediately.
    """

    RETRY = "retry"
    RECOVER = "recover"
    REPLAN = "replan"
    ABORT = "abort"
