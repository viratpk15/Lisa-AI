"""
Jarvis AIOS — Core Multi-Agent Execution Test Suite
---------------------------------------------------

Automated test suite verifying Task Model lifecycle, ResearchAgent, CodingAgent,
DocumentAgent, ResponseAgent, Supervisor task assignment, Scratchpad communications,
and full end-to-end multi-agent pipeline.
"""

from app.Agents.task_model import AgentTask
from app.Agents.registry import get_agent_registry
from app.Agents.research import ResearchAgent
from app.Agents.coding import CodingAgent
from app.Agents.document_agent import DocumentAgent
from app.Agents.response_agent import ResponseAgent
from app.LangGraph.nodes.supervisor import supervisor
from app.LangGraph.nodes.worker_agent import worker_agent
from app.LangGraph.nodes.response_agent import response_agent_node
from app.LangGraph.graph import route_from_supervisor


def test_task_model_creation_and_lifecycle():
    """Verify AgentTask attributes and lifecycle status transitions."""
    task = AgentTask(
        task_id="task_101",
        objective="Gather web search data",
        assigned_agent="researcher",
        priority=2,
    )
    assert task.task_id == "task_101"
    assert task.status == "pending"
    assert task.priority == 2

    task.status = "completed"
    assert task.status == "completed"


def test_worker_agents_execution():
    """Verify ResearchAgent, CodingAgent, DocumentAgent, ResponseAgent execute cleanly."""
    registry = get_agent_registry()
    registry.clear()

    res_ag = ResearchAgent()
    code_ag = CodingAgent()
    doc_ag = DocumentAgent()
    resp_ag = ResponseAgent()

    registry.register(res_ag)
    registry.register(code_ag)
    registry.register(doc_ag)
    registry.register(resp_ag)

    r_out = res_ag.execute("FastAPI security features")
    assert r_out["status"] == "completed"

    c_out = code_ag.execute("Write python sorting function")
    assert c_out["status"] == "completed"

    d_out = doc_ag.execute("Summarize attached PDF")
    assert d_out["status"] == "completed"

    mock_scratchpad = [
        {"sender": "researcher", "content": "Found security best practices."},
        {"sender": "coder", "content": "Implemented Pydantic request models."},
    ]
    resp_out = resp_ag.execute({"team_scratchpad": mock_scratchpad})
    assert "# Multi-Agent Task Execution Report" in resp_out["response"]
    assert "Findings from researcher" in resp_out["response"]


def test_end_to_end_multi_agent_pipeline():
    """Verify end-to-end execution loop: Supervisor -> Workers -> ResponseAgent -> END."""
    registry = get_agent_registry()
    registry.clear()
    registry.register(ResearchAgent())
    registry.register(CodingAgent())
    registry.register(DocumentAgent())
    registry.register(ResponseAgent())

    state = {
        "session_id": "sess_e2e_999",
        "message": "delegate to team for deep research and code implementation",
        "request_type": "multi_agent",
        "agent_team": ["researcher", "coder", "document_agent"],
        "team_scratchpad": [],
        "iteration_count": 0,
    }

    # Step 1: Supervisor assigns task 1 to researcher
    s1 = supervisor(state)
    assert s1["next_step_assignee"] == "researcher"
    state.update(s1)

    # Step 2: Worker researcher executes task 1
    w1 = worker_agent(state)
    assert w1["observation"]["agent"] == "researcher"
    assert len(w1["team_scratchpad"]) == 2  # Supervisor delegate + Worker 1 record
    state["team_scratchpad"] = w1["team_scratchpad"]

    # Step 3: Supervisor assigns task 2 to coder
    s2 = supervisor(state)
    assert s2["next_step_assignee"] == "coder"
    state.update(s2)

    # Step 4: Worker coder executes task 2
    w2 = worker_agent(state)
    assert w2["observation"]["agent"] == "coder"
    state["team_scratchpad"] = w2["team_scratchpad"]

    # Step 5: Supervisor assigns task 3 to document_agent
    s3 = supervisor(state)
    assert s3["next_step_assignee"] == "document_agent"
    state.update(s3)

    # Step 6: Worker document_agent executes task 3
    w3 = worker_agent(state)
    assert w3["observation"]["agent"] == "document_agent"
    state["team_scratchpad"] = w3["team_scratchpad"]

    # Step 7: All worker agents completed -> Supervisor assigns response_agent
    s4 = supervisor(state)
    assert s4["next_step_assignee"] == "response_agent"
    assert route_from_supervisor(s4) == "response_agent"

    # Step 8: ResponseAgent node synthesizes final user output
    state.update(s4)
    resp_node_out = response_agent_node(state)
    assert resp_node_out["next_step_assignee"] == "FINISH"
    assert "# Multi-Agent Task Execution Report" in resp_node_out["response"]
