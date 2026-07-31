import logging

from langgraph.graph import StateGraph, START, END

from app.LangGraph.state import State

from app.LangGraph.nodes.router import router
from app.LangGraph.nodes.planner import planner
from app.LangGraph.nodes.executor import executor
from app.LangGraph.nodes.agent import agent
from app.LangGraph.nodes.tool_node import tool_node
from app.LangGraph.nodes.supervisor import supervisor
from app.LangGraph.nodes.worker_agent import worker_agent

from app.LangGraph.nodes.response_agent import response_agent_node

logger = logging.getLogger(__name__)

# Maximum number of tool-calling iterations before forcing a final response.
# Prevents infinite loops when the LLM repeatedly requests tool execution.
MAX_TOOL_ITERATIONS = 10

builder = StateGraph(State)

builder.add_node("router", router)
builder.add_node("planner", planner)
builder.add_node("executor", executor)
builder.add_node("agent", agent)
builder.add_node("tool", tool_node)
builder.add_node("supervisor", supervisor)
builder.add_node("worker_agent", worker_agent)
builder.add_node("response_agent", response_agent_node)


def route_from_router(state: State):
    """Route from router to appropriate execution path."""
    request_type = state.get("request_type", "conversation")

    if request_type == "multi_agent":
        return "supervisor"

    if request_type == "resume":
        plan = state.get("plan", {})
        if (
            plan
            and plan.get("steps")
            and any(step.get("status") == "pending" for step in plan.get("steps", []))
        ):
            logger.info("Resuming interrupted plan")
            return "executor"
        else:
            logger.info(
                "Resume requested but no unfinished plan, treating as conversation"
            )
            return "agent"

    if request_type == "multi_step":
        return "planner"

    return "agent"


def route_from_planner(state: State):
    """Route from planner to executor."""
    plan = state.get("plan", {})
    steps = plan.get("steps", [])

    if state.get("termination_reason") == "INVALID_PLAN":
        return END

    if steps and any(step.get("status") == "pending" for step in steps):
        return "executor"

    return END


def route_from_executor(state: State):
    """Route from executor to appropriate next node."""
    route_to = state.get("_route_to", "agent")
    if route_to == END:
        return END
    return route_to


def route_from_agent(state: State):
    """Route from agent to tool node or back to executor."""
    if state["action"].get("type") == "tool":
        iteration_count = state.get("iteration_count", 0)
        if iteration_count >= MAX_TOOL_ITERATIONS:
            return END
        return "tool"
    return "executor"


def route_from_supervisor(state: State):
    """Route from supervisor to worker_agent, response_agent, or END."""
    assignee = state.get("next_step_assignee", "FINISH")
    if assignee == "response_agent":
        return "response_agent"
    if assignee == "FINISH":
        return END
    return "worker_agent"


builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    route_from_router,
    {
        "agent": "agent",
        "planner": "planner",
        "supervisor": "supervisor",
        END: END,
    },
)

builder.add_conditional_edges(
    "planner",
    route_from_planner,
    {
        "executor": "executor",
        END: END,
    },
)

builder.add_conditional_edges(
    "executor",
    route_from_executor,
    {
        "agent": "agent",
        "planner": "planner",
        END: END,
    },
)

builder.add_conditional_edges(
    "agent",
    route_from_agent,
    {
        "tool": "tool",
        "executor": "executor",
        END: END,
    },
)

builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "worker_agent": "worker_agent",
        "response_agent": "response_agent",
        END: END,
    },
)

builder.add_edge("worker_agent", "supervisor")
builder.add_edge("response_agent", END)
builder.add_edge("tool", "executor")

graph = builder.compile()
