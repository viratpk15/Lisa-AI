# backend/app/FastAPI/routes_workflows.py
"""
Jarvis AIOS — FastAPI REST Router for Workflow Studio Subsystem (Sprint 6.7B).

Mount Path: /api/v1/workflows

Endpoints:
- GET    /api/v1/workflows
- POST   /api/v1/workflows
- GET    /api/v1/workflows/templates
- GET    /api/v1/workflows/{workflow_id}
- PUT    /api/v1/workflows/{workflow_id}
- DELETE /api/v1/workflows/{workflow_id}
- POST   /api/v1/workflows/{workflow_id}/compile
- POST   /api/v1/workflows/{workflow_id}/execute
- POST   /api/v1/workflows/executions/{execution_id}/resume
- GET    /api/v1/workflows/{workflow_id}/analytics
- POST   /api/v1/workflows/export
- POST   /api/v1/workflows/import
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.Auth.dependencies import get_current_user
from app.Data.database import get_db
from app.Workflows import schemas
from app.Workflows.manager import workflow_manager, WorkflowManager

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflow Studio"])


def get_workflow_manager() -> WorkflowManager:
    return workflow_manager


# ---------------------------------------------------------------------------
# Workflow Registry & Preset Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=List[schemas.WorkflowDefinitionResponse])
def list_workflows(
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """List all workflow definitions."""
    return manager.list_workflows(db)


@router.post("", response_model=schemas.WorkflowDefinitionResponse)
def create_workflow(
    payload: schemas.WorkflowCreatePayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Create a new visual workflow graph definition."""
    node_dicts = [n.model_dump() for n in payload.nodes]
    edge_dicts = [e.model_dump() for e in payload.edges]
    return manager.create_workflow(
        db=db,
        workflow_id=payload.workflow_id,
        name=payload.name,
        description=payload.description,
        nodes=node_dicts,
        edges=edge_dicts,
        variables=payload.variables,
    )


@router.get("/templates", response_model=List[schemas.TemplateItemResponse])
def list_templates(
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """List workflow preset templates."""
    return manager.list_templates()


# ---------------------------------------------------------------------------
# Compile, Execute & Resume Endpoints
# ---------------------------------------------------------------------------

@router.post("/{workflow_id}/compile", response_model=schemas.WorkflowCompileResponse)
def compile_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Validate & compile workflow definition AST to LangGraph Runnable."""
    return manager.compile_workflow(db, workflow_id)


@router.post("/{workflow_id}/execute", response_model=schemas.ExecutionResponse)
def execute_workflow(
    workflow_id: str,
    payload: schemas.ExecutionTriggerPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Trigger compiled LangGraph StateGraph execution."""
    try:
        res = manager.execute_workflow(
            db=db,
            workflow_id=workflow_id,
            inputs=payload.inputs,
            breakpoints=payload.breakpoints,
        )
        return schemas.ExecutionResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/executions/{execution_id}/resume", response_model=Dict[str, Any])
def resume_execution(
    execution_id: str,
    payload: schemas.ResumeExecutionPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Resume paused execution at Human Approval or Breakpoint step."""
    try:
        return manager.resume_execution(
            db=db,
            execution_id=execution_id,
            action=payload.action,
            inputs=payload.inputs,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------------------------------------------------------------------------
# Analytics, Export & Import Endpoints
# ---------------------------------------------------------------------------

@router.get("/{workflow_id}/analytics", response_model=schemas.WorkflowAnalyticsResponse)
def get_workflow_analytics(
    workflow_id: str,
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Fetch workflow execution analytics (total cost, tokens, latency)."""
    return manager.get_analytics(db, workflow_id)


@router.post("/export", response_model=Dict[str, Any])
def export_workflow(
    workflow_id: str = "wf_agent_tool_pipeline",
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Export workflow definition to JSON format."""
    try:
        return manager.export_workflow(db, workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/import", response_model=Dict[str, Any])
def import_workflow(
    payload: Dict[str, Any] = {},
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Import workflow definition payload."""
    return manager.import_workflow(db, payload)


# ---------------------------------------------------------------------------
# Parameterized Detail & Delete Endpoints (Placed at bottom of router)
# ---------------------------------------------------------------------------

@router.get("/{workflow_id}", response_model=schemas.WorkflowDefinitionResponse)
def get_workflow_detail(
    workflow_id: str,
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Fetch workflow graph details and nodes by ID."""
    wf = manager.get_workflow(db, workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return schemas.WorkflowDefinitionResponse(**wf)


@router.delete("/{workflow_id}", response_model=Dict[str, str])
def delete_workflow(
    workflow_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    manager: WorkflowManager = Depends(get_workflow_manager),
):
    """Delete a workflow definition by ID."""
    success = manager.delete_workflow(db, workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return {"message": f"Deleted workflow '{workflow_id}'"}
