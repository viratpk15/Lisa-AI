# backend/app/tests/test_Workflows/test_workflow_studio.py
"""
Jarvis AIOS — Unit Tests for Workflow Studio & LangGraph Compiler (Sprint 6.7B).
"""

import pytest
from app.Data.base import Base
from app.Data.database import engine, SessionLocal
from app.Workflows.manager import workflow_manager
from app.Workflows.compiler import workflow_compiler


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_workflow_compiler_validation():
    valid_json = '{"nodes": [{"id": "n1", "data": {"node_type": "agent"}}], "edges": []}'
    is_valid, errors, warnings, ast = workflow_compiler.parse_and_validate(valid_json)
    assert is_valid is True
    assert len(errors) == 0
    assert ast["node_count"] == 1

    invalid_json = '{"nodes": [], "edges": []}'
    is_valid, errors, warnings, ast = workflow_compiler.parse_and_validate(invalid_json)
    assert is_valid is False
    assert len(errors) >= 1


def test_workflow_creation_and_listing():
    db = SessionLocal()
    import uuid
    wf_id = f"wf_test_pipeline_{uuid.uuid4().hex[:6]}"
    try:
        wf = workflow_manager.create_workflow(
            db=db,
            workflow_id=wf_id,
            name="Test Pipeline",
            description="Testing creation",
            nodes=[{"id": "n1", "type": "custom", "position": {"x": 0, "y": 0}, "data": {"label": "Start", "node_type": "http"}}],
            edges=[],
        )
        assert wf["workflow_id"] == wf_id

        all_wfs = workflow_manager.list_workflows(db)
        assert any(w["workflow_id"] == wf_id for w in all_wfs)
    finally:
        db.close()


def test_workflow_execution():
    db = SessionLocal()
    try:
        res = workflow_manager.execute_workflow(
            db=db,
            workflow_id="wf_agent_tool_pipeline",
            inputs={"query": "Hello test"},
            breakpoints=[],
        )
        assert "execution_id" in res
        assert res["status"] in ("completed", "paused")
    finally:
        db.close()


def test_workflow_analytics():
    db = SessionLocal()
    try:
        analytics = workflow_manager.get_analytics(db, workflow_id="wf_agent_tool_pipeline")
        assert analytics["workflow_id"] == "wf_agent_tool_pipeline"
        assert "avg_latency_ms" in analytics
    finally:
        db.close()
