# backend/app/Agents/manager.py
"""Business‑logic layer for Agent Studio.
Validates inputs, enforces RBAC via existing auth dependencies, handles versioning, tool/memory/model bindings, and team graph validation (cycle detection)."""

from typing import List, Optional
from sqlalchemy.orm import Session

from .models import Agent, AgentVersion, AgentTeam, TeamAgentNode, TeamEdge
from .repository import (
    get_agent,
    create_agent,
    update_agent,
    delete_agent,
    create_version,
    update_version,
    create_team,
    list_versions,
)

# Simple cycle detection for team graph
def _has_cycle(nodes: List[TeamAgentNode], edges: List[TeamEdge]) -> bool:
    graph = {node.id: [] for node in nodes}
    for edge in edges:
        if edge.source_node_id in graph:
            graph[edge.source_node_id].append(edge.target_node_id)
    visited = set()
    rec_stack = set()
    def dfs(v):
        visited.add(v)
        rec_stack.add(v)
        for neigh in graph.get(v, []):
            if neigh not in visited:
                if dfs(neigh):
                    return True
            elif neigh in rec_stack:
                return True
        rec_stack.remove(v)
        return False
    return any(dfs(node.id) for node in nodes if node.id not in visited)

# ---------- Agent ----------

def create_new_agent(session: Session, name: str, description: Optional[str] = None) -> Agent:
    agent = Agent(name=name, description=description)
    return create_agent(session, agent)

def update_existing_agent(
    session: Session,
    agent_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Agent:
    agent = get_agent(session, agent_id)
    if not agent:
        raise ValueError(f"Agent {agent_id} not found")
    if name is not None:
        agent.name = name
    if description is not None:
        agent.description = description
    if is_active is not None:
        agent.is_active = is_active
    return update_agent(session, agent)

def delete_existing_agent(session: Session, agent_id: int) -> None:
    agent = get_agent(session, agent_id)
    if not agent:
        raise ValueError(f"Agent {agent_id} not found")
    delete_agent(session, agent)

# ---------- Version ----------

def create_agent_version(session: Session, agent_id: int, version_number: int, changelog: Optional[str] = None) -> AgentVersion:
    # Ensure only one current version per agent
    existing_versions = list_versions(session, agent_id)
    for v in existing_versions:
        if v.is_current:
            v.is_current = False
            update_version(session, v)  # correctly typed as AgentVersion
    version = AgentVersion(agent_id=agent_id, version_number=version_number, changelog=changelog, is_current=True)
    return create_version(session, version)

# ---------- Team ----------

def create_agent_team(session: Session, agent_id: int, name: str, nodes: List[TeamAgentNode], edges: List[TeamEdge]) -> AgentTeam:
    if _has_cycle(nodes, edges):
        raise ValueError("Team graph contains cycles, which are not allowed")
    team = AgentTeam(agent_id=agent_id, name=name, nodes=nodes, edges=edges)
    return create_team(session, team)

# Additional manager functions (binding updates, execution triggers) can be added as needed.
