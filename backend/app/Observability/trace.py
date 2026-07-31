"""
Trace Utilities

Helper functions and context managers for creating and managing execution
traces. All timing uses ``time.perf_counter()`` (monotonic clock).

The context manager ``trace_context`` is the primary entry point: it starts
a trace, yields it, and finishes it on exit. Tracing is completely optional -
if tracing fails, the underlying request continues normally and no exception
is propagated from the tracing layer.
"""

import logging
import time
from contextlib import contextmanager
from typing import Iterator

from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)


@contextmanager
def trace_context(session_id: str, request: str) -> Iterator[None]:
    """Context manager that wraps a request with an execution trace.

    Starts a trace on entry and finishes it on exit (success or error).
    If an exception propagates through the block, it is recorded as a trace
    error and the trace is finished with an "error" status, but the exception
    is re-raised so normal execution flow is preserved.

    Args:
        session_id: Session identifier for the request.
        request: The user request message.

    Yields:
        None. The active trace is available via the observability manager.
    """
    observability_manager.start_trace(session_id, request)
    try:
        yield
    except Exception as e:
        try:
            observability_manager.record_error(str(e))
            observability_manager.finish_trace(status="error")
        except Exception as inner:  # pragma: no cover - defensive
            logger.debug("Failed to finalize errored trace: %s", str(inner))
        raise
    else:
        try:
            observability_manager.finish_trace(status="success")
        except Exception as inner:  # pragma: no cover - defensive
            logger.debug("Failed to finalize trace: %s", str(inner))


def measure_time() -> float:
    """Return the current high-resolution monotonic time.

    Returns:
        A ``time.perf_counter()`` reading in seconds. Subtract a previous
        reading and multiply by 1000 to obtain milliseconds.
    """
    return time.perf_counter()


def calculate_duration(start_time: float) -> float:
    """Calculate elapsed milliseconds from a ``measure_time`` start value.

    Args:
        start_time: A previous ``time.perf_counter()`` reading.

    Returns:
        Elapsed time in milliseconds.
    """
    return (time.perf_counter() - start_time) * 1000.0
