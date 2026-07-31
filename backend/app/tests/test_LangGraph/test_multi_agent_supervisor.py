"""
Jarvis AIOS — Multi-Agent Supervisor Foundation Test Suite
-----------------------------------------------------------

Automated test suite verifying Agent Registry discovery, State extension fields,
Supervisor node delegation, Worker Agent dispatching via registry, and Team Scratchpad log.
"""

from app.Agents.agent import Agent
from app.Agents.registry import get_agent_registry
from app.Models.agent_config import AgentConfig
from app.LangGraph.nodes.router import router
from app.LangGraph.nodes.supervisor import supervisor
from app.LangGraph.nodes.worker_agent import worker_agent
from app.LangGraph.graph import route_from_router, route_from_supervisor


class MockResearcherAgent(Agent):
    config = AgentConfig(
        id="researcher",
        name="ResearchAgent",
        description="Deep research agent",
        capabilities=["web_search", "document_analysis"],
        allowed_tools=["web_search"],
    )

    def can_handle(self, request: str) -> bool:
        return "research" in str(request).lower()

    def execute(self, request: str) -> dict:
        return {"result": f"ResearchAgent results for query: '{request}'"}


class MockCoderAgent(Agent):
    config = AgentConfig(
        id="coder",
        name="CodingAgent",
        description="Code generation agent",
        capabilities=["python_execution", "git_ops"],
        allowed_tools=["execute_code"],
    )

    def can_handle(self, request: str) -> bool:
        return "code" in str(request).lower() or "python" in str(request).lower()

    def execute(self, request: str) -> dict:
        return {"result": f"CodingAgent code patch for query: '{request}'"}


def test_agent_registry_metadata_and_discovery():
    """Verify AgentRegistry registers, discovers metadata, and resolves by ID or name."""
    registry = get_agent_registry()
    registry.clear()

    res_agent = MockResearcherAgent()
    code_agent = MockCoderAgent()

    registry.register(res_agent)
    registry.register(code_agent)

    assert registry.has_agent("ResearchAgent") is True
    assert registry.get("researcher").name == "ResearchAgent"
    assert registry.get("coder").config.allowed_tools == ["execute_code"]
    assert len(registry.list_agents()) == 2


def test_router_classifies_multi_agent_intent():
    """Verify router classifies multi-agent keywords to request_type='multi_agent'."""
    state = {
        "session_id": "sess_ma_101",
        "message": "delegate to team for deep research and code analysis",
    }
    res = router(state)
    assert res["request_type"] == "multi_agent"


def test_supervisor_node_delegation_loop():
    """Verify Supervisor inspects scratchpad, delegates to team agents, and terminates with FINISH."""
    registry = get_agent_registry()
    registry.clear()
    registry.register(MockResearcherAgent())
    registry.register(MockCoderAgent())

    state = {
        "session_id": "sess_ma_202",
        "message": "delegate to team to write a report",
        "request_type": "multi_agent",
        "agent_team": ["researcher", "coder"],
        "team_scratchpad": [],
        "iteration_count": 0,
    }

    # Turn 1: Supervisor selects first available worker ("researcher")
    s1 = supervisor(state)
    assert s1["next_step_assignee"] == "researcher"
    assert len(s1["team_scratchpad"]) == 1
    assert s1["team_scratchpad"][0]["sender"] == "Supervisor"

    # Worker 1 executes and posts to scratchpad
    state.update(s1)
    w1 = worker_agent(state)
    assert w1["observation"]["agent"] == "researcher"
    assert len(w1["team_scratchpad"]) == 2

    # Turn 2: Supervisor selects next available worker ("coder")
    state["team_scratchpad"] = w1["team_scratchpad"]
    s2 = supervisor(state)
    assert s2["next_step_assignee"] == "coder"

    # Worker 2 executes
    state.update(s2)
    w2 = worker_agent(state)
    assert w2["observation"]["agent"] == "coder"

    # Turn 3: Supervisor sees all team members completed -> response_agent
    state["team_scratchpad"] = w2["team_scratchpad"]
    s3 = supervisor(state)
    assert s3["next_step_assignee"] == "response_agent"
    assert route_from_supervisor(s3) == "response_agent"


def test_state_backwards_compatibility():
    """Verify single-agent request types continue routing to agent or planner with zero regressions."""
    state_conv = {"session_id": "sess_bc_1", "message": "Hello Jarvis", "request_type": "conversation"}
    assert route_from_router(state_conv) == "agent"

    state_ms = {"session_id": "sess_bc_2", "message": "Read file then calculate total", "request_type": "multi_step"}
    assert route_from_router(state_ms) == "planner"
