"""
Observability Manager

Manages execution traces and provides instrumentation for Jarvis AIOS.

The manager is completely optional: every method is defensive and never
raises. Tracing failures must never affect business logic. The active
trace is tracked via a ``ContextVar`` so that instrumented components can
record metrics without changing their public signatures.

Only the last 100 traces are retained in memory. Traces are never
persisted to disk.
"""

import logging
import time
import uuid
from collections import deque
from contextvars import ContextVar

from app.Observability.models import ExecutionTrace, ToolCall

logger = logging.getLogger(__name__)

# Maximum number of traces retained in memory (no persistence).
MAX_TRACES: int = 100

# ContextVar holding the trace_id of the currently active request.
# This lets instrumented components record metrics without threading the
# trace_id through every function signature (which would change public APIs).
_active_trace_id: ContextVar[str | None] = ContextVar("active_trace_id", default=None)


class ObservabilityManager:
    """Manages execution traces for monitoring and debugging.

    Stores only the last 100 traces in memory (no persistence). Tracing is
    completely optional and never affects business logic. Every public
    method is wrapped so that tracing failures are logged but never raised.

    Attributes:
        traces: Deque of recently completed traces (max 100).
    """

    def __init__(self) -> None:
        """Initialize the observability manager with empty trace storage."""
        self._traces: deque[ExecutionTrace] = deque(maxlen=MAX_TRACES)
        self._active: dict[str, ExecutionTrace] = {}

    def start_trace(self, session_id: str, request: str) -> str:
        """Start a new execution trace and mark it active.

        Args:
            session_id: Session identifier the request belongs to.
            request: The user request message.

        Returns:
            The new trace identifier. An empty string is returned if
            tracing fails so callers can safely ignore it.
        """
        try:
            trace_id = str(uuid.uuid4())
            trace = ExecutionTrace(
                trace_id=trace_id,
                session_id=session_id,
                request=request,
                request_start_time=time.perf_counter(),
            )
            self._active[trace_id] = trace
            _active_trace_id.set(trace_id)
            logger.debug("Started trace %s for session %s", trace_id, session_id)
            return trace_id
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to start trace: %s", str(e))
            return ""

    def finish_trace(self, status: str = "success") -> ExecutionTrace | None:
        """Finish the active trace, finalize it, and emit a report.

        Args:
            status: Final execution status (e.g. "success" or "error").

        Returns:
            The completed ExecutionTrace, or None if no active trace exists
            or tracing failed.
        """
        trace_id = _active_trace_id.get()
        if not trace_id:
            return None
        try:
            trace = self._active.get(trace_id)
            if not trace:
                return None

            trace.status = status
            trace.request_end_time = time.perf_counter()
            trace.finish()

            # Move to the bounded deque (old traces auto-discarded).
            self._traces.append(trace)
            del self._active[trace_id]
            _active_trace_id.set(None)

            # Emit the developer-friendly report.
            logger.info("Trace %s completed:\n%s", trace_id, trace.to_report())
            return trace
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to finish trace %s: %s", trace_id, str(e))
            try:
                _active_trace_id.set(None)
            except Exception:  # pragma: no cover - defensive
                pass
            return None

    def get_current_trace_id(self) -> str | None:
        """Return the trace_id of the currently active trace, if any.

        Returns:
            The active trace identifier, or None if no trace is active.
        """
        return _active_trace_id.get()

    def _get_active_trace(self) -> ExecutionTrace | None:
        """Resolve the currently active trace from the context variable.

        Returns:
            The active ExecutionTrace, or None if absent.
        """
        trace_id = _active_trace_id.get()
        if not trace_id:
            return None
        return self._active.get(trace_id)

    def record_duration(self, component: str, duration_ms: float) -> None:
        """Record a component's processing duration in milliseconds.

        Args:
            component: Component name (router, planner, executor, agent,
                memory, semantic, tool, llm).
            duration_ms: Duration in milliseconds (perf_counter based).
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            duration_map = {
                "router": "router_duration_ms",
                "planner": "planner_duration_ms",
                "executor": "executor_duration_ms",
                "agent": "agent_duration_ms",
                "memory": "memory_duration_ms",
                "semantic": "semantic_retrieval_duration_ms",
                "tool": "tool_duration_ms",
                "llm": "llm_duration_ms",
            }
            field_name = duration_map.get(component)
            if field_name:
                setattr(trace, field_name, duration_ms)
            else:
                logger.debug("Unknown component for duration: %s", component)
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record duration: %s", str(e))

    def record_tool_call(
        self,
        tool_name: str,
        duration_ms: float,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Record a single tool execution.

        Args:
            tool_name: Name of the tool that was executed.
            duration_ms: Execution duration in milliseconds.
            success: Whether the tool executed successfully.
            error: Error message if execution failed.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.tool_calls.append(
                ToolCall(
                    tool_name=tool_name,
                    duration_ms=duration_ms,
                    success=success,
                    error=error,
                )
            )
            trace.tool_duration_ms += duration_ms
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record tool call: %s", str(e))

    def record_llm_usage(
        self,
        model_name: str = "",
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: float = 0.0,
    ) -> None:
        """Record a single LLM invocation.

        Args:
            model_name: Name of the LLM model used.
            input_tokens: Number of input tokens (if available).
            output_tokens: Number of output tokens (if available).
            latency_ms: LLM call latency in milliseconds.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.llm_duration_ms += latency_ms
            if model_name:
                trace.llm_model_name = model_name
            if input_tokens:
                trace.total_token_input += input_tokens
            if output_tokens:
                trace.total_token_output += output_tokens
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record LLM usage: %s", str(e))

    def record_memory_hit(self, count: int = 1) -> None:
        """Record conversation memory messages loaded (memory hits).

        Args:
            count: Number of conversation messages loaded.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.memory_hits += count
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record memory hit: %s", str(e))

    def record_semantic_hit(self, count: int = 1) -> None:
        """Record semantic memories retrieved.

        Args:
            count: Number of semantic memories retrieved.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.semantic_hits += count
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record semantic hit: %s", str(e))

    def record_planner_call(self, is_replan: bool = False) -> None:
        """Record a planner invocation.

        Args:
            is_replan: Whether this invocation was a replanning event.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.planner_calls += 1
            if is_replan:
                trace.replanning_count += 1
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record planner call: %s", str(e))

    def record_plan_validation(
        self,
        duration_ms: float,
        success: bool,
        failure_reason: str = "",
        warning_count: int = 0,
    ) -> None:
        """Record a single plan-validation pass by the Plan Validation Engine.

        Args:
            duration_ms: Validation duration in milliseconds (perf_counter based).
            success: Whether the plan passed validation.
            failure_reason: Human-readable failure reason when success is False.
            warning_count: Number of non-fatal warnings produced.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.plan_validation_count += 1
            trace.plan_validation_duration_ms += duration_ms
            if not success:
                trace.plan_validation_failures += 1
                if failure_reason:
                    trace.plan_validation_failure_reasons.append(failure_reason)
            trace.plan_validation_warnings += warning_count
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record plan validation: %s", str(e))

    def record_planner_completed_steps(self, count: int = 1) -> None:
        """Record the number of plan steps completed.

        Args:
            count: Number of completed plan steps.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.planner_completed_steps += count
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record planner completed steps: %s", str(e))

    def record_executor_step(self, status: str) -> None:
        """Record an executor step outcome.

        Args:
            status: One of "completed", "failed", or "skipped".
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            if status == "completed":
                trace.executor_steps_completed += 1
            elif status == "failed":
                trace.executor_steps_failed += 1
            elif status == "skipped":
                trace.executor_steps_skipped += 1
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record executor step: %s", str(e))

    def record_memory_info(
        self,
        conversation_messages: int = 0,
        summary_used: bool = False,
        semantic_memories: int = 0,
        retrieval_latency_ms: float = 0.0,
    ) -> None:
        """Record detailed memory operation information.

        Args:
            conversation_messages: Number of conversation messages loaded.
            summary_used: Whether a conversation summary was used.
            semantic_memories: Number of semantic memories retrieved.
            retrieval_latency_ms: Memory/semantic retrieval latency in ms.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.memory_hits += conversation_messages
            trace.summary_used = summary_used
            trace.semantic_hits += semantic_memories
            trace.memory_retrieval_latency_ms += retrieval_latency_ms
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record memory info: %s", str(e))

    def record_error(self, error: str) -> None:
        """Record an error message encountered during the request.

        Args:
            error: Error message to record.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.errors.append(error)
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record error: %s", str(e))

    def record_termination(
        self,
        reason: str,
        outcome: str,
        iterations: int = 0,
        duration_ms: float = 0.0,
        retry_count: int = 0,
        failure_count: int = 0,
    ) -> None:
        """Record execution termination details for guardrails.

        Args:
            reason: Human-readable termination reason.
            outcome: Deterministic termination outcome (SUCCESS, FAILED,
                ABORTED, LIMIT_REACHED, TIMEOUT, INVALID_PLAN).
            iterations: Number of executor iterations performed.
            duration_ms: Total execution duration in milliseconds.
            retry_count: Number of tool retries performed.
            failure_count: Number of consecutive failures.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.termination_reason = reason
            trace.termination_outcome = outcome
            trace.termination_iterations = iterations
            trace.termination_duration_ms = duration_ms
            trace.termination_retry_count = retry_count
            trace.termination_failure_count = failure_count
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record termination: %s", str(e))

    def record_recovery(
        self,
        error: str,
        decision: str,
        retry_count: int = 0,
    ) -> None:
        """Record a recovery evaluation for a failed tool.

        Args:
            error: The error message that triggered recovery.
            decision: The recovery decision (retry, recover, replan, abort).
            retry_count: Number of retries attempted.
        """
        try:
            trace = self._get_active_trace()
            if not trace:
                return
            trace.recovery_attempts += 1
            if decision == "retry":
                trace.recovery_retries += 1
            elif decision == "replan":
                trace.recovery_replans += 1
            elif decision == "abort":
                trace.recovery_aborts += 1
        except Exception as e:  # pragma: no cover - defensive
            logger.debug("Failed to record recovery: %s", str(e))

    def get_trace(self, trace_id: str) -> ExecutionTrace | None:
        """Get a trace by its identifier.

        Args:
            trace_id: Trace identifier to look up.

        Returns:
            The ExecutionTrace if found, otherwise None.
        """
        if trace_id in self._active:
            return self._active[trace_id]
        for trace in self._traces:
            if trace.trace_id == trace_id:
                return trace
        return None

    def get_recent_traces(self, count: int = 10) -> list[ExecutionTrace]:
        """Get the most recent completed traces.

        Args:
            count: Maximum number of traces to return.

        Returns:
            List of recent ExecutionTrace instances (oldest first).
        """
        return list(self._traces)[-count:]

    def get_trace_report(self, trace_id: str) -> str | None:
        """Get the human-readable report for a trace.

        Args:
            trace_id: Trace identifier to look up.

        Returns:
            The formatted report string, or None if the trace is not found.
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return None
        return trace.to_report()


# Global observability manager instance (documented singleton).
observability_manager = ObservabilityManager()
