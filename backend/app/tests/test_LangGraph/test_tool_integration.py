"""
Jarvis AIOS
--------------------
LangGraph Tool Integration Tests (Sprint 6.1C)

Tests dynamic planner tool discovery, tool_node execution, ToolResult normalization,
graph state tracking (executed_tools, tool_results, pending_approvals), and recovery policies.
"""

from app.LangGraph.nodes.planner import _build_planner_prompt
from app.LangGraph.nodes.tool_node import tool_node
from app.LangGraph.state import State


def test_planner_dynamic_tool_discovery():
    """Verify Planner prompt dynamically includes all registered tools from ToolRegistry."""
    prompt = _build_planner_prompt()
    assert "filesystem" in prompt
    assert "terminal" in prompt
    assert "git" in prompt
    assert "calculator" in prompt
    assert "python" in prompt
    assert "Available tools:" in prompt


def test_tool_node_successful_execution():
    """Verify tool_node executes tool via ToolEngine and updates state keys cleanly."""
    initial_state: State = {
        "session_id": "test_session_1",
        "message": "Calculate 15 * 4",
        "action": {
            "tool": "calculator",
            "arguments": {"expression": "15 * 4"},
        },
        "observation": {},
        "response": "",
        "iteration_count": 0,
        "plan": {
            "goal": "Math calculation",
            "steps": [
                {"id": 1, "description": "Calculate math", "tool": "calculator", "status": "in_progress"}
            ],
        },
        "request_type": "single_tool",
        "execution_outcome": None,
        "execution_start_time": 0.0,
        "replanning_count": 0,
        "tool_retry_count": 0,
        "consecutive_failures": 0,
        "step_execution_history": [1],
        "termination_reason": None,
        "executed_tools": [],
        "tool_results": [],
        "pending_approvals": [],
        "execution_history": [],
        "active_tool": None,
        "tool_call_depth": 0,
        "tool_execution_count": 0,
    }

    update = tool_node(initial_state)

    assert update["iteration_count"] == 1
    assert update["tool_execution_count"] == 1
    assert update["observation"]["result"] == 60.0
    assert "calculator" in update["executed_tools"]
    assert len(update["tool_results"]) == 1
    assert update["tool_results"][0]["status"] == "SUCCESS"
    assert update["plan"]["steps"][0]["status"] == "completed"


def test_tool_node_permission_denial_and_error():
    """Verify tool_node handles permission denial cleanly."""
    initial_state: State = {
        "session_id": "test_session_2",
        "message": "Run admin command",
        "action": {
            "tool": "terminal",
            "arguments": {"command": "sudo rm -rf /"},
            "caller_context": {"role": "USER"},
        },
        "observation": {},
        "response": "",
        "iteration_count": 0,
        "plan": {
            "goal": "Admin action",
            "steps": [
                {"id": 1, "description": "Run admin command", "tool": "terminal", "status": "in_progress"}
            ],
        },
        "request_type": "single_tool",
        "execution_outcome": None,
        "execution_start_time": 0.0,
        "replanning_count": 0,
        "tool_retry_count": 0,
        "consecutive_failures": 0,
        "step_execution_history": [1],
        "termination_reason": None,
        "executed_tools": [],
        "tool_results": [],
        "pending_approvals": [],
        "execution_history": [],
        "active_tool": None,
        "tool_call_depth": 0,
        "tool_execution_count": 0,
    }

    update = tool_node(initial_state)

    assert update["iteration_count"] == 1
    assert "error" in update["observation"]
    assert "forbidden token" in update["observation"]["error"].lower()
    assert update["plan"]["steps"][0]["status"] == "failed"
    assert len(update["execution_history"]) == 1
