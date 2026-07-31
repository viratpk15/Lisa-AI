"""
Tests for the Observability Layer.

These tests verify the manager, models, and trace context manager without
requiring any external services (LLM, network, or database).
"""

import time

from app.Observability.manager import observability_manager
from app.Observability.trace import trace_context, measure_time, calculate_duration
from app.Observability.models import ExecutionTrace


def _reset_manager() -> None:
    """Reset the global manager to a clean state for test isolation."""
    observability_manager._traces.clear()
    observability_manager._active.clear()
    from app.Observability import manager as manager_module

    manager_module._active_trace_id.set(None)


def test_start_and_finish_trace_produces_report() -> None:
    _reset_manager()
    with trace_context("sess-1", "hello world"):
        observability_manager.record_duration("router", 0.4)
        observability_manager.record_tool_call("calculator", 3.0, success=True)
        observability_manager.record_llm_usage(
            model_name="llama-3.3-70b-versatile",
            input_tokens=512,
            output_tokens=48,
            latency_ms=701.0,
        )
        observability_manager.record_memory_info(
            conversation_messages=10,
            summary_used=True,
            semantic_memories=3,
        )
        observability_manager.record_planner_call(is_replan=False)
        observability_manager.record_executor_step("completed")

    traces = observability_manager.get_recent_traces()
    assert len(traces) == 1
    trace = traces[0]
    assert trace.session_id == "sess-1"
    assert trace.request == "hello world"
    assert trace.status == "success"
    assert trace.router_duration_ms == 0.4
    assert trace.total_token_input == 512
    assert trace.total_token_output == 48
    assert trace.llm_model_name == "llama-3.3-70b-versatile"
    assert trace.memory_hits == 10
    assert trace.summary_used is True
    assert trace.semantic_hits == 3
    assert trace.planner_calls == 1
    assert trace.executor_steps_completed == 1
    assert len(trace.tool_calls) == 1
    assert trace.tool_calls[0].tool_name == "calculator"
    assert trace.tool_calls[0].success is True
    assert trace.total_duration_ms >= 0.0

    report = trace.to_report()
    assert "TRACE" in report
    assert "SUCCESS" in report
    assert "calculator" in report


def test_failed_tool_call_is_recorded() -> None:
    _reset_manager()
    with trace_context("sess-2", "do thing"):
        observability_manager.record_tool_call(
            "python", 12.5, success=False, error="SyntaxError"
        )

    trace = observability_manager.get_recent_traces()[0]
    assert trace.tool_calls[0].success is False
    assert trace.tool_calls[0].error == "SyntaxError"
    assert trace.tool_duration_ms == 12.5


def test_error_status_on_exception() -> None:
    _reset_manager()
    try:
        with trace_context("sess-3", "boom"):
            raise ValueError("kaboom")
    except ValueError:
        pass

    trace = observability_manager.get_recent_traces()[0]
    assert trace.status == "error"
    assert any("kaboom" in err for err in trace.errors)


def test_only_last_100_traces_are_kept() -> None:
    _reset_manager()
    for i in range(120):
        with trace_context(f"sess-{i}", f"req-{i}"):
            observability_manager.record_duration("router", 0.1)

    traces = observability_manager.get_recent_traces(count=200)
    assert len(traces) == 100
    # Oldest (sess-0) should have been evicted; newest (sess-119) retained.
    assert traces[0].session_id == "sess-20"
    assert traces[-1].session_id == "sess-119"


def test_no_active_trace_makes_records_noop() -> None:
    _reset_manager()
    # With no active trace, record calls must not raise and do nothing.
    observability_manager.record_duration("router", 1.0)
    observability_manager.record_tool_call("calculator", 1.0)
    observability_manager.record_error("nothing")
    assert observability_manager.get_current_trace_id() is None


def test_perf_counter_helpers_measure_elapsed() -> None:
    start = measure_time()
    time.sleep(0.01)
    elapsed = calculate_duration(start)
    # Allow a small margin for the sleep granularity.
    assert elapsed >= 5.0


def test_execution_trace_model_defaults() -> None:
    trace = ExecutionTrace(
        trace_id="t1",
        session_id="s1",
        request="r",
        request_start_time=0.0,
        request_end_time=1.0,
    )
    trace.finish()
    assert trace.total_duration_ms == 1000.0
    assert isinstance(trace.tool_calls, list)
    assert trace.status == "pending"
