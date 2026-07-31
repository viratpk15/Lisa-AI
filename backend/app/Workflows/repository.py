# backend/app/Workflows/repository.py
"""
Jarvis AIOS — Repository Data Access Layer for Workflow Studio.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.Workflows.models import (
    WorkflowDefinitionModel,
    WorkflowVersionModel,
    WorkflowExecutionModel,
    WorkflowNodeLogModel,
)

DEFAULT_WORKFLOW_JSON = json.dumps({
    "nodes": [
        {"id": "node_start", "type": "custom", "position": {"x": 100, "y": 150}, "data": {"label": "Start Trigger", "node_type": "http", "config": {"method": "GET"}}},
        {"id": "node_agent", "type": "custom", "position": {"x": 350, "y": 150}, "data": {"label": "Coding Agent", "node_type": "agent", "config": {"agent_id": "code_assistant"}}},
        {"id": "node_tool", "type": "custom", "position": {"x": 600, "y": 150}, "data": {"label": "Execute Code", "node_type": "tool", "config": {"tool_name": "python_interpreter"}}},
        {"id": "node_approval", "type": "custom", "position": {"x": 850, "y": 150}, "data": {"label": "Human Approval", "node_type": "approval", "config": {"approver_role": "admin"}}},
    ],
    "edges": [
        {"id": "e1-2", "source": "node_start", "target": "node_agent"},
        {"id": "e2-3", "source": "node_agent", "target": "node_tool"},
        {"id": "e3-4", "source": "node_tool", "target": "node_approval"},
    ],
    "variables": {"env": "production", "max_retries": 3},
})


def seed_default_workflows(db: Session) -> None:
    """Populate default preset workflow graph if table is empty."""
    existing = db.execute(select(WorkflowDefinitionModel)).scalars().all()
    if existing:
        return

    wf = WorkflowDefinitionModel(
        workflow_id="wf_agent_tool_pipeline",
        name="Autonomous Agent & Tool Execution Pipeline",
        description="Preset workflow routing user query to Agent, running Python Code execution, and pausing for Human Approval.",
        is_active=True,
        definition_json=DEFAULT_WORKFLOW_JSON,
        definition_yaml="name: Autonomous Agent & Tool Execution Pipeline\nnodes:\n  - id: node_start\n    type: http",
    )
    db.add(wf)
    db.flush()

    # Add version 1
    ver = WorkflowVersionModel(
        workflow_id=wf.id,
        version_number=1,
        definition_json=DEFAULT_WORKFLOW_JSON,
    )
    db.add(ver)
    db.commit()


# ---------------------------------------------------------------------------
# Workflow Definition CRUD
# ---------------------------------------------------------------------------

def list_workflows(db: Session) -> List[WorkflowDefinitionModel]:
    seed_default_workflows(db)
    return db.execute(select(WorkflowDefinitionModel).order_by(WorkflowDefinitionModel.id.desc())).scalars().all()


def get_workflow_by_id(db: Session, workflow_id: str) -> Optional[WorkflowDefinitionModel]:
    return db.execute(
        select(WorkflowDefinitionModel).where(WorkflowDefinitionModel.workflow_id == workflow_id)
    ).scalar_one_or_none()


def create_workflow(
    db: Session,
    workflow_id: str,
    name: str,
    description: Optional[str] = None,
    definition_json: str = "{}",
    definition_yaml: Optional[str] = None,
) -> WorkflowDefinitionModel:
    wf = WorkflowDefinitionModel(
        workflow_id=workflow_id,
        name=name,
        description=description,
        is_active=True,
        definition_json=definition_json,
        definition_yaml=definition_yaml,
    )
    db.add(wf)
    db.flush()

    ver = WorkflowVersionModel(
        workflow_id=wf.id,
        version_number=1,
        definition_json=definition_json,
    )
    db.add(ver)
    db.commit()
    db.refresh(wf)
    return wf


def update_workflow(
    db: Session,
    workflow_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    definition_json: Optional[str] = None,
) -> Optional[WorkflowDefinitionModel]:
    wf = get_workflow_by_id(db, workflow_id)
    if not wf:
        return None

    if name:
        wf.name = name
    if description:
        wf.description = description
    if definition_json:
        wf.definition_json = definition_json
        # Append new version
        latest_ver = db.execute(
            select(WorkflowVersionModel)
            .where(WorkflowVersionModel.workflow_id == wf.id)
            .order_by(WorkflowVersionModel.version_number.desc())
        ).scalars().first()
        next_ver = (latest_ver.version_number + 1) if latest_ver else 1
        ver = WorkflowVersionModel(workflow_id=wf.id, version_number=next_ver, definition_json=definition_json)
        db.add(ver)

    db.commit()
    db.refresh(wf)
    return wf


def delete_workflow(db: Session, workflow_id: str) -> bool:
    wf = get_workflow_by_id(db, workflow_id)
    if not wf:
        return False
    db.delete(wf)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Executions & Logs CRUD
# ---------------------------------------------------------------------------

def create_execution(
    db: Session,
    workflow_db_id: int,
    execution_id: str,
    status: str = "running",
) -> WorkflowExecutionModel:
    exec_rec = WorkflowExecutionModel(
        execution_id=execution_id,
        workflow_id=workflow_db_id,
        status=status,
        total_latency_ms=0.0,
        total_tokens=0,
        total_cost=0.0,
    )
    db.add(exec_rec)
    db.commit()
    db.refresh(exec_rec)
    return exec_rec


def update_execution_status(
    db: Session,
    execution_id: str,
    status: str,
    latency_ms: float = 0.0,
    tokens: int = 0,
    cost: float = 0.0,
) -> Optional[WorkflowExecutionModel]:
    exec_rec = db.execute(
        select(WorkflowExecutionModel).where(WorkflowExecutionModel.execution_id == execution_id)
    ).scalar_one_or_none()
    if not exec_rec:
        return None

    exec_rec.status = status
    exec_rec.total_latency_ms += latency_ms
    exec_rec.total_tokens += tokens
    exec_rec.total_cost += cost
    if status in ("completed", "failed", "cancelled"):
        exec_rec.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(exec_rec)
    return exec_rec


def record_node_log(
    db: Session,
    execution_db_id: int,
    node_id: str,
    node_type: str,
    status: str,
    latency_ms: float,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
) -> WorkflowNodeLogModel:
    log_entry = WorkflowNodeLogModel(
        execution_id=execution_db_id,
        node_id=node_id,
        node_type=node_type,
        status=status,
        latency_ms=latency_ms,
        input_json=json.dumps(input_data),
        output_json=json.dumps(output_data),
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_execution_detail(db: Session, execution_id: str) -> Optional[WorkflowExecutionModel]:
    return db.execute(
        select(WorkflowExecutionModel).where(WorkflowExecutionModel.execution_id == execution_id)
    ).scalar_one_or_none()
