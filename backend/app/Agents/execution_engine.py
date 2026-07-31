# backend/app/Agents/execution_engine.py
"""Thin adapter that delegates Agent execution to the existing LangGraph runtime.

It fires off the execution asynchronously and updates DB state on completion.
All orchestration is done by the existing LangGraph graph — no new runtime is introduced.
"""

import asyncio
import logging
from datetime import datetime, timezone
from uuid import uuid4

from ..Data.database import SessionLocal          # reuse existing session factory
from ..LangGraph.graph import graph as langgraph_graph   # compiled LangGraph entry point
from . import repository

logger = logging.getLogger(__name__)


async def _run_execution(execution_id: int) -> None:
    """Async task: runs one agent execution via LangGraph and writes results to DB."""
    # --- Phase 1: mark as running ---
    session = SessionLocal()
    try:
        execution = repository.get_execution(session, execution_id)
        if not execution:
            logger.warning("Execution %s not found, aborting.", execution_id)
            return
        execution.status = "running"
        execution.started_at = datetime.now(timezone.utc)
        repository.update_execution(session, execution)
    finally:
        session.close()

    # --- Phase 2: run LangGraph orchestration ---
    try:
        await langgraph_graph.astream({"execution_id": execution_id})
        final_status = "completed"
    except Exception as exc:
        logger.error("Execution %s failed: %s", execution_id, exc)
        final_status = "failed"

    # --- Phase 3: persist final state ---
    session = SessionLocal()
    try:
        execution = repository.get_execution(session, execution_id)
        if execution:
            execution.status = final_status
            execution.finished_at = datetime.now(timezone.utc)
            execution.run_id = str(uuid4())
            repository.update_execution(session, execution)
    finally:
        session.close()


def run_agent_execution(execution_id: int) -> None:
    """Public entry point called by the FastAPI router.

    Schedules the async execution without blocking the request thread.
    Uses asyncio.create_task so it runs within the existing event loop.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_run_execution(execution_id))
    except RuntimeError:
        # No running loop — fallback for tests / CLI usage
        asyncio.run(_run_execution(execution_id))
