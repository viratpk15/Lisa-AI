"""
Jarvis AIOS — Runtime Hardening Test Suite
------------------------------------------

Automated test suite for TaskQueue, TaskStatus Enum, ToolExecutionRecord schema,
RetryPolicy exponential backoff, execute_with_timeout, Failure Recovery, Structured Logger,
and Execution Metrics.
"""

import time
from app.Agents.task_model import AgentTask, TaskStatus
from app.Agents.task_queue import TaskQueue
from app.Agents.retry_policy import RetryPolicy
from app.Agents.timeout_handler import execute_with_timeout
from app.Agents.failure_recovery import handle_worker_failure
from app.Models.tool_result_schema import ToolExecutionRecord
from app.Observability.structured_logger import log_task_execution
from app.Observability.execution_metrics import get_execution_metrics


def test_task_queue_fifo_ordering():
    """Verify TaskQueue enqueues, dequeues in FIFO order, and updates TaskStatus."""
    tq = TaskQueue()
    assert tq.is_empty() is True

    task1 = AgentTask(task_id="t1", objective="Research data", assigned_agent="researcher")
    task2 = AgentTask(task_id="t2", objective="Code patch", assigned_agent="coder")

    tq.enqueue(task1)
    tq.enqueue(task2)
    assert tq.size() == 2
    assert tq.peek().task_id == "t1"

    out1 = tq.dequeue()
    assert out1.task_id == "t1"
    assert out1.status == TaskStatus.RUNNING
    assert tq.size() == 1

    out2 = tq.dequeue()
    assert out2.task_id == "t2"
    assert tq.is_empty() is True


def test_task_status_enum_lifecycle():
    """Verify TaskStatus enum values and state updates."""
    task = AgentTask(task_id="t100", objective="Run unit test", assigned_agent="tester")
    assert task.status == TaskStatus.PENDING

    task.status = TaskStatus.RUNNING
    assert task.status == TaskStatus.RUNNING

    task.status = TaskStatus.COMPLETED
    assert task.status == TaskStatus.COMPLETED

    task.status = TaskStatus.FAILED
    assert task.status == TaskStatus.FAILED


def test_standard_tool_result_schema():
    """Verify ToolExecutionRecord standard output schema."""
    rec = ToolExecutionRecord(
        task_id="task_202",
        agent="researcher",
        tool="search_web",
        input={"query": "FastAPI"},
        output="FastAPI documentation summary",
        duration_ms=125.4,
        success=True,
    )
    dump = rec.model_dump()
    assert dump["task_id"] == "task_202"
    assert dump["agent"] == "researcher"
    assert dump["duration_ms"] == 125.4
    assert dump["success"] is True


def test_retry_policy_exponential_backoff():
    """Verify RetryPolicy retries transient failures and eventually succeeds."""
    policy = RetryPolicy(max_retries=2, initial_delay=0.01)

    counter = {"attempts": 0}

    def flaky_function():
        counter["attempts"] += 1
        if counter["attempts"] < 2:
            raise ValueError("Transient network glitch")
        return "Success on attempt 2"

    res = policy.execute_with_retry(flaky_function, task_id="t_flaky", agent_id="flaky_worker")
    assert res["success"] is True
    assert res["retries"] == 1
    assert res["result"] == "Success on attempt 2"


def test_timeout_handler_graceful_cancellation():
    """Verify execute_with_timeout gracefully catches TimeoutError."""
    def slow_function():
        time.sleep(0.5)
        return "Finished slow task"

    res = execute_with_timeout(slow_function, timeout_seconds=0.05, task_id="t_slow", agent_id="slow_agent")
    assert res["success"] is False
    assert res["timed_out"] is True
    assert "Execution timed out" in res["result"]


def test_failure_recovery_safe_continuation():
    """Verify handle_worker_failure captures exceptions without crashing runtime."""
    err = RuntimeError("Unexpected API denial")
    failure_res = handle_worker_failure("task_999", "worker_test", err, duration_ms=50.0)

    assert failure_res["status"] == TaskStatus.FAILED
    assert failure_res["error"] == "Unexpected API denial"
    assert failure_res["record"]["success"] is False


def test_structured_logger_and_execution_metrics():
    """Verify log_task_execution and ExecutionMetricsTracker metrics calculation."""
    metrics = get_execution_metrics()
    metrics.reset()

    log_task_execution("t_log1", "researcher", duration_ms=100.0, retries=0, success=True)
    metrics.record_task(success=True, duration_ms=100.0, retries=0)

    log_task_execution("t_log2", "coder", duration_ms=200.0, retries=1, success=False)
    metrics.record_task(success=False, duration_ms=200.0, retries=1)

    summary = metrics.get_summary()
    assert summary["total_tasks"] == 2
    assert summary["completed_tasks"] == 1
    assert summary["failed_tasks"] == 1
    assert summary["average_duration_ms"] == 150.0
    assert summary["retry_count"] == 1
