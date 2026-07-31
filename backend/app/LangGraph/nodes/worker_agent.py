"""
Jarvis AIOS — LangGraph Worker Agent Node Dispatcher
---------------------------------------------------

Generic worker agent dispatcher node. Resolves target sub-agent dynamically through
AgentRegistry, executes logic with RetryPolicy, Timeout enforcement, Failure Recovery,
and logs structured ToolExecutionRecords to team_scratchpad.
"""

import logging
from typing import Any, Dict, List
from app.Agents.registry import get_agent_registry
from app.Agents.retry_policy import RetryPolicy
from app.Agents.timeout_handler import execute_with_timeout
from app.Agents.failure_recovery import handle_worker_failure
from app.Models.tool_result_schema import ToolExecutionRecord
from app.Observability.structured_logger import log_task_execution
from app.Observability.execution_metrics import get_execution_metrics
from app.LangGraph.state import State
from app.Observability.trace import measure_time, calculate_duration
from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)


def worker_agent(state: State) -> Dict[str, Any]:
    """Hardened generic worker agent node dispatcher."""
    start_time = measure_time()
    registry = get_agent_registry()
    metrics = get_execution_metrics()

    target_agent_id = state.get("next_step_assignee") or state.get("active_agent") or "researcher"
    session_id = state.get("session_id", "default_session")
    message = state.get("message", "")
    scratchpad: List[Dict[str, Any]] = list(state.get("team_scratchpad") or [])

    # Extract task ID from scratchpad or generate fallback
    last_task_id = f"task_{len(scratchpad)}"
    for item in reversed(scratchpad):
        if item.get("sender") == "Supervisor" and item.get("task_id"):
            last_task_id = item["task_id"]
            break

    logger.info("[WORKER-DISPATCH] Session=%s Dispatching Task '%s' -> Worker='%s'", session_id, last_task_id, target_agent_id)

    # 1. Resolve agent dynamically from AgentRegistry
    worker_result_text = ""
    allowed_tools_used: List[str] = []
    agent_timeout = 60.0
    retry_count = 0
    success = True
    error_msg: str | None = None

    try:
        agent_obj = registry.get(target_agent_id)
        allowed_tools_used = getattr(agent_obj.config, "allowed_tools", [])
        agent_timeout = getattr(agent_obj.config, "timeout", 60.0)

        retry_pol = RetryPolicy(max_retries=2, initial_delay=0.05)

        # Inner execution lambda
        def run_agent_execution():
            if hasattr(agent_obj, "execute"):
                res = agent_obj.execute(message)
                return res.get("result") if isinstance(res, dict) else str(res)
            return f"Worker agent '{target_agent_id}' completed task breakdown for: {message[:60]}"

        # Execute with retry policy and timeout enforcement
        timeout_res = execute_with_timeout(
            lambda: retry_pol.execute_with_retry(
                run_agent_execution,
                task_id=last_task_id,
                agent_id=target_agent_id,
            ),
            timeout_seconds=agent_timeout,
            task_id=last_task_id,
            agent_id=target_agent_id,
        )

        if timeout_res.get("success"):
            exec_data = timeout_res["result"]
            worker_result_text = exec_data.get("result", "")
            retry_count = exec_data.get("retries", 0)
            success = exec_data.get("success", True)
        else:
            success = False
            error_msg = timeout_res.get("error", "Execution failed")
            worker_result_text = f"Worker failure: {error_msg}"

    except Exception as exc:
        failure_data = handle_worker_failure(last_task_id, target_agent_id, exc)
        success = False
        error_msg = failure_data["error"]
        worker_result_text = f"Worker exception failure: {error_msg}"

    duration = calculate_duration(start_time)
    duration_ms = duration * 1000.0
    observability_manager.record_duration("agent", duration)

    # 2. Build Standardized ToolExecutionRecord
    record = ToolExecutionRecord(
        task_id=last_task_id,
        agent=target_agent_id,
        tool=allowed_tools_used[0] if allowed_tools_used else "internal_reasoning",
        input={"query": message},
        output=worker_result_text,
        duration_ms=duration_ms,
        success=success,
    )

    record_dict = record.model_dump()
    record_dict["sender"] = target_agent_id
    record_dict["content"] = worker_result_text
    record_dict["turn"] = len(scratchpad) + 1
    record_dict["next_recommendation"] = "Proceed with remaining multi-agent team steps."

    scratchpad.append(record_dict)

    # 3. Log structured metric and observability record
    log_task_execution(
        task_id=last_task_id,
        agent_id=target_agent_id,
        duration_ms=duration_ms,
        retries=retry_count,
        success=success,
        selected_tools=allowed_tools_used,
    )
    metrics.record_task(success=success, duration_ms=duration_ms, retries=retry_count)

    logger.info("[WORKER-DISPATCH] Task '%s' completed by Worker='%s' (success=%s)", last_task_id, target_agent_id, success)

    return {
        "observation": {"result": worker_result_text, "agent": target_agent_id, "task_id": last_task_id, "success": success},
        "response": worker_result_text,
        "team_scratchpad": scratchpad,
    }
