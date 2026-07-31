"""
Observability Models

Pydantic models for execution tracing and monitoring.

All durations are measured with ``time.perf_counter()`` (monotonic clock)
and stored as milliseconds. No ``datetime`` is used for timing so that
measurements remain accurate and unaffected by wall-clock adjustments.
"""

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Record of a single tool execution.

    Attributes:
        tool_name: Name of the tool that was executed.
        duration_ms: Execution duration in milliseconds (perf_counter based).
        success: Whether the tool executed successfully.
        error: Error message if execution failed, otherwise None.
    """

    tool_name: str
    duration_ms: float
    success: bool = True
    error: str | None = None


class LLMUsage(BaseModel):
    """Record of a single LLM invocation.

    Attributes:
        model_name: Name of the LLM model used.
        input_tokens: Number of input tokens (if available).
        output_tokens: Number of output tokens (if available).
        latency_ms: LLM call latency in milliseconds (perf_counter based).
    """

    model_name: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: float = 0.0


class MemoryInfo(BaseModel):
    """Record of memory operations for a single request.

    Attributes:
        conversation_messages_loaded: Number of conversation messages loaded.
        summary_used: Whether a conversation summary was used.
        semantic_memories_retrieved: Number of semantic memories retrieved.
        retrieval_latency_ms: Memory/semantic retrieval latency in ms.
    """

    conversation_messages_loaded: int = 0
    summary_used: bool = False
    semantic_memories_retrieved: int = 0
    retrieval_latency_ms: float = 0.0


class ExecutionTrace(BaseModel):
    """Complete execution trace for a single request.

    Every duration field is measured with ``time.perf_counter()`` and
    expressed in milliseconds. The trace is intentionally optional:
    business logic never depends on it, and tracing failures must never
    affect normal execution.

    Attributes:
        trace_id: Unique trace identifier (UUID4 string).
        session_id: Session identifier the request belongs to.
        request: The user request message.
        request_start_time: ``time.perf_counter()`` value at request start.
        request_end_time: ``time.perf_counter()`` value at request end.
        total_duration_ms: Total request duration in milliseconds.
        router_duration_ms: Router node processing duration.
        planner_duration_ms: Planner node processing duration.
        executor_duration_ms: Executor node processing duration.
        agent_duration_ms: Agent node processing duration.
        memory_duration_ms: Memory operations duration.
        semantic_retrieval_duration_ms: Semantic retrieval duration.
        tool_duration_ms: Aggregate tool execution duration.
        llm_duration_ms: Aggregate LLM call duration.
        total_token_input: Total input tokens consumed across LLM calls.
        total_token_output: Total output tokens produced across LLM calls.
        tool_calls: Ordered list of tool calls made during the request.
        memory_hits: Number of conversation messages loaded (memory hits).
        semantic_hits: Number of semantic memories retrieved.
        planner_calls: Number of plans generated (initial + replans).
        replanning_count: Number of replanning events.
        planner_completed_steps: Number of plan steps completed.
        executor_steps_completed: Number of executor steps completed.
        executor_steps_failed: Number of executor steps that failed.
        executor_steps_skipped: Number of executor steps skipped.
        llm_model_name: Name of the LLM model used (last/primary).
        summary_used: Whether a conversation summary was used.
        memory_retrieval_latency_ms: Memory retrieval latency in ms.
        errors: List of error messages encountered during the request.
        status: Final execution status (success / error / etc.).
    """

    trace_id: str
    session_id: str
    request: str
    request_start_time: float
    request_end_time: float | None = None
    total_duration_ms: float = 0.0

    router_duration_ms: float = 0.0
    planner_duration_ms: float = 0.0
    executor_duration_ms: float = 0.0
    agent_duration_ms: float = 0.0
    memory_duration_ms: float = 0.0
    semantic_retrieval_duration_ms: float = 0.0
    tool_duration_ms: float = 0.0
    llm_duration_ms: float = 0.0

    total_token_input: int = 0
    total_token_output: int = 0

    tool_calls: list[ToolCall] = Field(default_factory=list)

    memory_hits: int = 0
    semantic_hits: int = 0

    planner_calls: int = 0
    replanning_count: int = 0
    planner_completed_steps: int = 0

    # Plan Validation Engine details (populated by the validation layer).
    plan_validation_count: int = 0
    plan_validation_failures: int = 0
    plan_validation_duration_ms: float = 0.0
    plan_validation_warnings: int = 0
    plan_validation_failure_reasons: list[str] = Field(default_factory=list)

    executor_steps_completed: int = 0
    executor_steps_failed: int = 0
    executor_steps_skipped: int = 0

    llm_model_name: str = ""
    summary_used: bool = False
    memory_retrieval_latency_ms: float = 0.0

    errors: list[str] = Field(default_factory=list)
    status: str = "pending"

    # Guardrail termination details (populated by the execution guardrails).
    termination_reason: str = ""
    termination_outcome: str = ""
    termination_iterations: int = 0
    termination_duration_ms: float = 0.0
    termination_retry_count: int = 0
    termination_failure_count: int = 0

    # Recovery details (populated by the tool recovery layer).
    recovery_attempts: int = 0
    recovery_retries: int = 0
    recovery_replans: int = 0
    recovery_aborts: int = 0

    def finish(self) -> None:
        """Mark the trace as finished and compute total duration.

        Uses the stored ``time.perf_counter()`` start/end values so the
        result is independent of wall-clock time.
        """
        if self.request_end_time is not None:
            self.total_duration_ms = (self.request_end_time - self.request_start_time) * 1000.0

    def to_report(self) -> str:
        """Generate a developer-friendly, human-readable trace report.

        The report is designed for debugging and profiling: it shows the
        per-component duration breakdown, tool calls, LLM usage, memory
        activity, planner/executor statistics, and final status.

        Returns:
            Formatted multi-line trace report string.
        """
        border = "=" * 50
        lines: list[str] = [
            border,
            "TRACE",
            "",
            "Session:",
            self.session_id,
            "",
            "Duration:",
            f"{self.total_duration_ms:.0f} ms",
            "",
            "Router",
            f"{self.router_duration_ms:.1f} ms",
            "",
            "Planner",
            f"{self.planner_duration_ms:.1f} ms",
            "",
            "Agent",
            f"{self.agent_duration_ms:.1f} ms",
            "",
            "Memory",
            f"{self.memory_duration_ms:.1f} ms",
            "",
            "Semantic Retrieval",
            f"{self.semantic_retrieval_duration_ms:.1f} ms",
            "",
            "Tool",
        ]

        # Per-tool breakdown
        if self.tool_calls:
            for call in self.tool_calls:
                lines.append(call.tool_name)
                lines.append(f"{call.duration_ms:.1f} ms")
        else:
            lines.append("0.0 ms")

        lines.extend(["", "LLM", ""])

        # LLM usage
        if self.llm_model_name:
            lines.append("Model:")
            lines.append(self.llm_model_name)
            lines.append("")
        lines.append("Input Tokens:")
        lines.append(str(self.total_token_input))
        lines.append("")
        lines.append("Output Tokens:")
        lines.append(str(self.total_token_output))
        lines.append("")

        # Tool calls summary
        lines.append("Tool Calls")
        lines.append("")
        if self.tool_calls:
            for call in self.tool_calls:
                mark = "✓" if call.success else "✗"
                lines.append(f"{call.tool_name} {mark}")
        else:
            lines.append("None")
        lines.append("")

        # Memory summary
        lines.append("Memory")
        lines.append("")
        lines.append("Conversation messages:")
        lines.append(str(self.memory_hits))
        lines.append("")
        lines.append("Summary:")
        lines.append("YES" if self.summary_used else "NO")
        lines.append("")
        lines.append("Semantic memories:")
        lines.append(str(self.semantic_hits))
        lines.append("")

        # Planner summary
        lines.append("Planner")
        lines.append("")
        lines.append("Plans:")
        lines.append(str(self.planner_calls))
        lines.append("")
        lines.append("Replans:")
        lines.append(str(self.replanning_count))
        lines.append("")

        # Executor summary
        lines.append("Executor")
        lines.append("")
        lines.append("Completed:")
        lines.append(str(self.executor_steps_completed))
        lines.append("")
        lines.append("Failed:")
        lines.append(str(self.executor_steps_failed))
        lines.append("")

        # Status
        lines.append("Status")
        lines.append("")
        lines.append(self.status.upper())
        lines.append("")

        if self.errors:
            lines.append("Errors:")
            for error in self.errors:
                lines.append(f"  - {error}")
            lines.append("")

        lines.append(border)
        return "\n".join(lines)
