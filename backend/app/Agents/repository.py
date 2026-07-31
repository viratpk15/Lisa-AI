# backend/app/Agents/repository.py
"""Repository layer for Agent Studio domain objects.

Provides thin CRUD wrappers using the existing SQLAlchemy Session from
`app.Data.database` — the same session used throughout the rest of the project.
SQLModel models work fine with a plain SQLAlchemy Session.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Agent,
    AgentExecution,
    AgentTeam,
    AgentVersion,
    ExecutionStep,
    TeamAgentNode,  # re-exported so routers can import from repository
    TeamEdge,       # re-exported so routers can import from repository
)

__all__ = [
    "get_agent", "list_agents", "create_agent", "update_agent", "delete_agent",
    "get_version", "list_versions", "create_version", "update_version",
    "get_team", "create_team",
    "create_execution", "get_execution", "update_execution", "add_execution_step",
    "TeamAgentNode", "TeamEdge", "AgentExecution",
]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

def get_agent(session: Session, agent_id: int) -> Optional[Agent]:
    return session.get(Agent, agent_id)


def list_agents(session: Session, *, offset: int = 0, limit: int = 100) -> List[Agent]:
    stmt = select(Agent).offset(offset).limit(limit)
    return list(session.execute(stmt).scalars().all())


def create_agent(session: Session, agent: Agent) -> Agent:
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def update_agent(session: Session, agent: Agent) -> Agent:
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def delete_agent(session: Session, agent: Agent) -> None:
    session.delete(agent)
    session.commit()


# ---------------------------------------------------------------------------
# AgentVersion
# ---------------------------------------------------------------------------

def get_version(session: Session, version_id: int) -> Optional[AgentVersion]:
    return session.get(AgentVersion, version_id)


def list_versions(session: Session, agent_id: int) -> List[AgentVersion]:
    stmt = select(AgentVersion).where(AgentVersion.agent_id == agent_id)
    return list(session.execute(stmt).scalars().all())


def create_version(session: Session, version: AgentVersion) -> AgentVersion:
    session.add(version)
    session.commit()
    session.refresh(version)
    return version


def update_version(session: Session, version: AgentVersion) -> AgentVersion:
    """Persist changes to an existing AgentVersion row."""
    session.add(version)
    session.commit()
    session.refresh(version)
    return version


# ---------------------------------------------------------------------------
# AgentTeam
# ---------------------------------------------------------------------------

def get_team(session: Session, team_id: int) -> Optional[AgentTeam]:
    return session.get(AgentTeam, team_id)


def create_team(session: Session, team: AgentTeam) -> AgentTeam:
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def create_execution(session: Session, execution: AgentExecution) -> AgentExecution:
    session.add(execution)
    session.commit()
    session.refresh(execution)
    return execution


def get_execution(session: Session, execution_id: int) -> Optional[AgentExecution]:
    return session.get(AgentExecution, execution_id)


def update_execution(session: Session, execution: AgentExecution) -> AgentExecution:
    session.add(execution)
    session.commit()
    session.refresh(execution)
    return execution


def add_execution_step(session: Session, step: ExecutionStep) -> ExecutionStep:
    session.add(step)
    session.commit()
    session.refresh(step)
    return step
