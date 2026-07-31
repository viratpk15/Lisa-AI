"""
Jarvis AIOS
--------------------
LangGraph Tool Node

The single LangGraph entry point for tool execution.
Delegates execution strictly to ToolEngine, normalizes provider-independent ToolResult objects,
and updates state (executed_tools, tool_results, pending_approvals, execution_history).
"""

from typing import Any, Dict
from app.LangGraph.state import State
from app.Tools.engine import engine
from app.Tools.metadata import ToolResult, ExecutionStatus


def tool_node(state: State) -> Dict[str, Any]:
    """
    Execute the tool specified in state['action'] through ToolEngine.

    Normalizes ToolResult into graph state updates, handling SUCCESS,
    PENDING_APPROVAL, TIMEOUT, PERMISSION_DENIED, and ERROR outcomes.
    """
    action = state["action"]
    tool_name = action["tool"]
    tool_args = action.get("arguments", {})
    caller_ctx = action.get("caller_context", {})

    iteration_count = state.get("iteration_count", 0) + 1
    tool_execution_count = state.get("tool_execution_count", 0) + 1

    executed_tools = list(state.get("executed_tools", []))
    tool_results = list(state.get("tool_results", []))
    pending_approvals = list(state.get("pending_approvals", []))
    execution_history = list(state.get("execution_history", []))

    # Execute tool synchronously via ToolEngine with return_result_object=True
    try:
        tool_result: ToolResult = engine.execute(
            tool_name=tool_name,
            caller_context=caller_ctx,
            return_result_object=True,
            **tool_args,
        )
    except Exception as e:
        # Wrap unexpected exceptions as error result
        err_msg = str(e)
        updated_plan = state.get("plan", {})
        if updated_plan:
            for step in updated_plan.get("steps", []):
                if step.get("status") == "in_progress":
                    step["status"] = "failed"
                    break

        return {
            "iteration_count": iteration_count,
            "tool_execution_count": tool_execution_count,
            "observation": {"error": err_msg},
            "plan": updated_plan,
        }

    res_dict = tool_result.to_dict()
    execution_history.append(res_dict)

    # 1. PENDING APPROVAL STAGE
    if tool_result.status == ExecutionStatus.PENDING_APPROVAL:
        pending_item = {
            "tool_name": tool_name,
            "arguments": tool_args,
            "execution_id": tool_result.execution_id,
            "requires_approval": True,
        }
        pending_approvals.append(pending_item)

        return {
            "iteration_count": iteration_count,
            "tool_execution_count": tool_execution_count,
            "active_tool": tool_name,
            "pending_approvals": pending_approvals,
            "execution_history": execution_history,
            "observation": {
                "pending_approval": True,
                "tool": tool_name,
                "message": f"Tool '{tool_name}' requires Human-in-the-Loop approval.",
            },
        }

    # 2. SUCCESS STAGE
    if tool_result.status == ExecutionStatus.SUCCESS:
        executed_tools.append(tool_name)
        tool_results.append(res_dict)

        updated_plan = state.get("plan", {})
        if updated_plan:
            for step in updated_plan.get("steps", []):
                if step.get("status") == "in_progress":
                    step["status"] = "completed"
                    break

        return {
            "iteration_count": iteration_count,
            "tool_execution_count": tool_execution_count,
            "active_tool": None,
            "executed_tools": executed_tools,
            "tool_results": tool_results,
            "execution_history": execution_history,
            "observation": {
                "result": tool_result.output,
                "tool_result": res_dict,
            },
            "plan": updated_plan,
        }

    # 3. ERROR / TIMEOUT / PERMISSION DENIED STAGE
    updated_plan = state.get("plan", {})
    if updated_plan:
        for step in updated_plan.get("steps", []):
            if step.get("status") == "in_progress":
                step["status"] = "failed"
                break

    return {
        "iteration_count": iteration_count,
        "tool_execution_count": tool_execution_count,
        "active_tool": None,
        "execution_history": execution_history,
        "observation": {
            "error": tool_result.error or f"Tool '{tool_name}' execution failed ({tool_result.status.value}).",
        },
        "plan": updated_plan,
    }
