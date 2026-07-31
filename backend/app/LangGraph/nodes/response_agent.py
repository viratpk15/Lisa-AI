"""
Jarvis AIOS — Response Agent Node
---------------------------------

LangGraph node for ResponseAgent execution. Reads completed team_scratchpad log,
synthesizes final answer, organizes findings, preserves citations, and sets the final response.
"""

import logging
from typing import Any, Dict
from app.Agents.registry import get_agent_registry
from app.LangGraph.state import State
from app.Observability.trace import measure_time, calculate_duration
from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)


def response_agent_node(state: State) -> Dict[str, Any]:
    """Response Agent node function."""
    start_time = measure_time()
    registry = get_agent_registry()
    session_id = state.get("session_id", "default_session")
    scratchpad = state.get("team_scratchpad") or []

    logger.info("[RESPONSE-AGENT-NODE] Synthesizing final multi-agent response for session=%s", session_id)

    try:
        agent_obj = registry.get("response_agent")
        res = agent_obj.execute(scratchpad)
        final_response_str = res.get("response") if isinstance(res, dict) else str(res)
    except Exception as e:
        logger.error("[RESPONSE-AGENT-NODE] Execution error: %s", str(e))
        final_response_str = f"Multi-Agent execution completed for session {session_id}."

    duration = calculate_duration(start_time)
    observability_manager.record_duration("agent", duration)

    return {
        "response": final_response_str,
        "active_agent": "response_agent",
        "next_step_assignee": "FINISH",
    }
