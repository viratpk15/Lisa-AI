# backend/app/Agents/routers.py
"""FastAPI routers for Agent Studio.

All endpoints are protected by the existing JWT/RBAC dependency `get_current_user`.
Uses the repository and manager layers — no direct ORM usage here.
OpenAPI schemas are generated from the Pydantic models in `schemas.py`.
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..Auth.dependencies import get_current_user  # existing auth dependency
from ..Data.database import get_db               # existing DB session dependency
from . import manager, repository, schemas

router = APIRouter(
    prefix="/api/v1/agents",
    tags=["agents"],
    dependencies=[Depends(get_current_user)],
)

# Type alias for injected session — avoids repeating Annotated everywhere
DBSession = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------------
# Agent CRUD
# ---------------------------------------------------------------------------

@router.post("/", response_model=schemas.AgentRead, status_code=status.HTTP_201_CREATED)
def create_agent_endpoint(payload: schemas.AgentCreate, session: DBSession) -> schemas.AgentRead:
    agent = manager.create_new_agent(session, name=payload.name, description=payload.description)
    return agent  # type: ignore[return-value]


@router.get("/", response_model=List[schemas.AgentRead])
def list_agents_endpoint(
    session: DBSession,
    offset: int = 0,
    limit: int = 100,
) -> List[schemas.AgentRead]:
    return repository.list_agents(session, offset=offset, limit=limit)  # type: ignore[return-value]


@router.get("/{agent_id}", response_model=schemas.AgentRead)
def get_agent_endpoint(agent_id: int, session: DBSession) -> schemas.AgentRead:
    agent = repository.get_agent(session, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent  # type: ignore[return-value]


@router.patch("/{agent_id}", response_model=schemas.AgentRead)
def update_agent_endpoint(
    agent_id: int,
    payload: schemas.AgentUpdate,
    session: DBSession,
) -> schemas.AgentRead:
    agent = manager.update_existing_agent(
        session,
        agent_id,
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    return agent  # type: ignore[return-value]


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent_endpoint(agent_id: int, session: DBSession) -> None:
    manager.delete_existing_agent(session, agent_id)


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------

@router.post("/versions", response_model=schemas.AgentVersionRead, status_code=status.HTTP_201_CREATED)
def create_version_endpoint(
    payload: schemas.AgentVersionCreate,
    session: DBSession,
) -> schemas.AgentVersionRead:
    version = manager.create_agent_version(
        session,
        agent_id=payload.agent_id,
        version_number=payload.version_number,
        changelog=payload.changelog,
    )
    return version  # type: ignore[return-value]


@router.get("/{agent_id}/versions", response_model=List[schemas.AgentVersionRead])
def list_versions_endpoint(agent_id: int, session: DBSession) -> List[schemas.AgentVersionRead]:
    return repository.list_versions(session, agent_id)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------

@router.post("/teams", response_model=schemas.AgentTeamRead, status_code=status.HTTP_201_CREATED)
def create_team_endpoint(
    payload: schemas.AgentTeamCreate,
    session: DBSession,
) -> schemas.AgentTeamRead:
    nodes = [
        repository.TeamAgentNode(
            team_id=0,  # set by ORM relationship after persist
            agent_version_id=n.agent_version_id,
            position_x=n.position_x,
            position_y=n.position_y,
        )
        for n in payload.nodes
    ]
    edges = [
        repository.TeamEdge(
            team_id=0,
            source_node_id=e.source_node_id,
            target_node_id=e.target_node_id,
            condition_json=e.condition_json,
        )
        for e in payload.edges
    ]
    team = manager.create_agent_team(
        session, agent_id=payload.agent_id, name=payload.name, nodes=nodes, edges=edges
    )
    return team  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

@router.post("/executions", response_model=schemas.ExecutionRead, status_code=status.HTTP_202_ACCEPTED)
def execute_agent(
    payload: schemas.ExecutionCreate,
    session: DBSession,
) -> schemas.ExecutionRead:
    from .execution_engine import run_agent_execution  # local import to avoid circular

    execution = repository.create_execution(
        session,
        repository.AgentExecution(version_id=payload.version_id, status="running"),
    )
    # Fire-and-forget: delegates to LangGraph runtime
    run_agent_execution(execution.id)
    return execution  # type: ignore[return-value]
