"""
Jarvis AIOS — LangGraph Multi-Agent Supervisor Node
--------------------------------------------------

Orchestrates multi-agent team execution. Inspects task progress and team_scratchpad,
selects the next worker agent from AgentRegistry, and updates execution state.

Rules:
  - Never executes tools directly.
  - Never answers users directly.
  - Communicates strictly via team_scratchpad.
"""

import logging
from typing import Any, Dict, List
from app.Agents.registry import get_agent_registry
from app.LangGraph.state import State
from app.Observability.trace import measure_time, calculate_duration
from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)

MAX_SUPERVISOR_TURNS = 10


from app.Agents.task_model import AgentTask, TaskStatus
from app.Agents.task_queue import TaskQueue


def supervisor(state: State) -> Dict[str, Any]:
    """Multi-Agent Supervisor node function."""
    start_time = measure_time()
    registry = get_agent_registry()

    session_id = state.get("session_id", "default_session")
    user_msg = state.get("message", "")
    scratchpad: List[Dict[str, Any]] = list(state.get("team_scratchpad") or [])
    iteration = state.get("iteration_count", 0)

    # 1. Discover available worker agents from registry or state
    available_team = state.get("agent_team")
    if not available_team:
        registered_agents = registry.list_agents()
        available_team = [
            ag.config.id or ag.name
            for ag in registered_agents
            if (ag.config.id or ag.name) not in ["response_agent", "supervisor"]
        ]
        if not available_team:
            available_team = ["researcher", "coder", "document_agent"]

    logger.info(
        "[SUPERVISOR] Evaluating session=%s iteration=%d available_team=%s",
        session_id, iteration, available_team
    )

    # 2. Populate TaskQueue with pending team tasks
    task_queue = TaskQueue()
    completed_agents = {entry.get("agent") for entry in scratchpad if entry.get("agent")}

    for idx, worker_id in enumerate(available_team, start=1):
        if worker_id not in completed_agents and worker_id != "response_agent":
            task_queue.enqueue(
                AgentTask(
                    task_id=f"task_{len(scratchpad) + idx}",
                    objective=f"Process sub-task for {worker_id}: {user_msg[:60]}",
                    assigned_agent=worker_id,
                    status=TaskStatus.PENDING,
                )
            )

    # 3. Dequeue next pending task or assign response_agent
    next_task = task_queue.dequeue() if not task_queue.is_empty() else None
    next_assignee = next_task.assigned_agent if next_task else "response_agent"
    task_id_str = next_task.task_id if next_task else f"task_{len(scratchpad) + 1}"

    if iteration >= MAX_SUPERVISOR_TURNS:
        logger.warning("[SUPERVISOR] Reached MAX_SUPERVISOR_TURNS (%d). Routing to response_agent.", MAX_SUPERVISOR_TURNS)
        next_assignee = "response_agent"

    supervisor_entry = {
        "sender": "Supervisor",
        "action": "DELEGATE" if next_assignee != "response_agent" else "FINISH_AND_SYNTHESIZE",
        "task_id": task_id_str,
        "assigned_worker": next_assignee,
        "scratchpad_turn": len(scratchpad) + 1,
    }
    scratchpad.append(supervisor_entry)

    duration = calculate_duration(start_time)
    observability_manager.record_duration("router", duration)

    logger.info("[SUPERVISOR] Session=%s -> Task '%s' Assigned To '%s'", session_id, task_id_str, next_assignee)

    return {
        "active_agent": next_assignee if next_assignee != "response_agent" else "response_agent",
        "next_step_assignee": next_assignee,
        "team_scratchpad": scratchpad,
        "iteration_count": iteration + 1,
    }
