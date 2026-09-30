"""
Jarvis AIOS — Email Intelligence Triage LangGraph Workflow
-----------------------------------------------------------
Compiled sequential graph for processing incoming emails:
  fetch_new → verify_sender → classify → summarize → extract_actions → emit_result

Design & Architecture:
- Adheres to LangGraph StateGraph orchestration layer (no business logic in graph nodes).
- Delegates all execution exclusively to ToolEngine.
- Fault-tolerant per node: if any node raises an exception, the error is recorded,
  the subsequent node receives null for that step, and the workflow returns
  partial results with status="partial".
- Node state is strictly JSON-serializable.
- Registers with Workflow Studio preset templates for visual canvas discovery.
"""

import logging
from typing import Any, Dict, List, Optional, TypedDict, cast

from langgraph.graph import END, START, StateGraph
from sqlalchemy import desc, select

from app.Data.database import SessionLocal
from app.Tools.email.models import EmailModel
from app.Tools.engine import engine
from app.Workflows.manager import PRESET_TEMPLATES

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State Definition
# ---------------------------------------------------------------------------


class EmailTriageState(TypedDict, total=False):
    """JSON-serializable execution state for the email triage pipeline."""
    user_id: int
    email_id: Optional[int]
    query: Optional[str]
    status: str  # "completed" | "partial" | "failed"
    errors: List[str]
    sync_result: Optional[Dict[str, Any]]
    verification_result: Optional[Dict[str, Any]]
    classification_result: Optional[Dict[str, Any]]
    summary_result: Optional[Dict[str, Any]]
    actions_result: Optional[Dict[str, Any]]
    emitted_result: Optional[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Graph Nodes
# ---------------------------------------------------------------------------


def fetch_new_node(state: EmailTriageState) -> Dict[str, Any]:
    """Fetch new emails or resolve existing target email for triage."""
    user_id = state.get("user_id")
    email_id = state.get("email_id")
    errors = list(state.get("errors") or [])

    if not user_id:
        return {
            "status": "failed",
            "errors": errors + ["Missing required 'user_id' in triage state."],
            "email_id": None,
            "sync_result": None,
        }

    # If specific email_id provided, verify existence
    if email_id:
        db = SessionLocal()
        try:
            exists = db.execute(
                select(EmailModel.id).where(EmailModel.id == email_id, EmailModel.user_id == user_id)
            ).scalar_one_or_none()
            if exists:
                return {"email_id": email_id, "sync_result": {"status": "targeted", "email_id": email_id}}
        finally:
            db.close()

    # Otherwise trigger email.sync to ingest latest messages
    try:
        caller_ctx = {"user_id": user_id}
        sync_res = engine.execute(
            "email.sync",
            caller_context=caller_ctx,
            max_results=5,
            query=state.get("query") or "",
        )
        # Find latest email id
        db = SessionLocal()
        try:
            latest = db.execute(
                select(EmailModel.id)
                .where(EmailModel.user_id == user_id)
                .order_by(desc(EmailModel.received_at))
                .limit(1)
            ).scalar_one_or_none()
        finally:
            db.close()

        return {
            "email_id": latest,
            "sync_result": sync_res,
        }
    except Exception as exc:
        logger.warning("fetch_new_node encountered an error: %s", exc)
        return {
            "status": "partial",
            "errors": errors + [f"fetch_new error: {exc}"],
            "email_id": None,
            "sync_result": None,
        }


def verify_sender_node(state: EmailTriageState) -> Dict[str, Any]:
    """Execute cryptographic sender verification (SPF, DKIM, DMARC)."""
    user_id = state.get("user_id")
    email_id = state.get("email_id")
    errors = list(state.get("errors") or [])

    if not email_id or not user_id:
        return {"verification_result": None}

    try:
        verif_res = engine.execute(
            "email.verify_sender",
            caller_context={"user_id": user_id},
            email_id=email_id,
        )
        return {"verification_result": verif_res}
    except Exception as exc:
        logger.warning("verify_sender_node error on email %s: %s", email_id, exc)
        return {
            "status": "partial",
            "errors": errors + [f"verify_sender error: {exc}"],
            "verification_result": None,
        }


def classify_node(state: EmailTriageState) -> Dict[str, Any]:
    """Execute AI classification and priority scoring."""
    user_id = state.get("user_id")
    email_id = state.get("email_id")
    errors = list(state.get("errors") or [])

    if not email_id or not user_id:
        return {"classification_result": None}

    try:
        classify_res = engine.execute(
            "email.classify",
            caller_context={"user_id": user_id},
            email_id=email_id,
        )
        return {"classification_result": classify_res}
    except Exception as exc:
        logger.warning("classify_node error on email %s: %s", email_id, exc)
        return {
            "status": "partial",
            "errors": errors + [f"classify error: {exc}"],
            "classification_result": None,
        }


def summarize_node(state: EmailTriageState) -> Dict[str, Any]:
    """Execute email summarization."""
    user_id = state.get("user_id")
    email_id = state.get("email_id")
    errors = list(state.get("errors") or [])

    if not email_id or not user_id:
        return {"summary_result": None}

    try:
        sum_res = engine.execute(
            "email.summarize",
            caller_context={"user_id": user_id},
            email_id=email_id,
        )
        return {"summary_result": sum_res}
    except Exception as exc:
        logger.warning("summarize_node error on email %s: %s", email_id, exc)
        return {
            "status": "partial",
            "errors": errors + [f"summarize error: {exc}"],
            "summary_result": None,
        }


def extract_actions_node(state: EmailTriageState) -> Dict[str, Any]:
    """Execute deadline, link, and action item extraction."""
    user_id = state.get("user_id")
    email_id = state.get("email_id")
    errors = list(state.get("errors") or [])

    if not email_id or not user_id:
        return {"actions_result": None}

    try:
        act_res = engine.execute(
            "email.extract_actions",
            caller_context={"user_id": user_id},
            email_id=email_id,
        )
        return {"actions_result": act_res}
    except Exception as exc:
        logger.warning("extract_actions_node error on email %s: %s", email_id, exc)
        return {
            "status": "partial",
            "errors": errors + [f"extract_actions error: {exc}"],
            "actions_result": None,
        }


def emit_result_node(state: EmailTriageState) -> Dict[str, Any]:
    """Consolidate pipeline outputs into a unified emitted result."""
    current_status = state.get("status")
    if not current_status:
        current_status = "partial" if state.get("errors") else "completed"

    emitted = {
        "status": current_status,
        "user_id": state.get("user_id"),
        "email_id": state.get("email_id"),
        "sync": state.get("sync_result"),
        "verification": state.get("verification_result"),
        "classification": state.get("classification_result"),
        "summary": state.get("summary_result"),
        "actions": state.get("actions_result"),
        "errors": state.get("errors") or [],
    }

    return {
        "status": current_status,
        "emitted_result": emitted,
    }


# ---------------------------------------------------------------------------
# StateGraph Construction & Compilation
# ---------------------------------------------------------------------------

builder: Any = cast(Any, StateGraph)(EmailTriageState)

builder.add_node("fetch_new", fetch_new_node)
builder.add_node("verify_sender", verify_sender_node)
builder.add_node("classify", classify_node)
builder.add_node("summarize", summarize_node)
builder.add_node("extract_actions", extract_actions_node)
builder.add_node("emit_result", emit_result_node)

builder.add_edge(START, "fetch_new")
builder.add_edge("fetch_new", "verify_sender")
builder.add_edge("verify_sender", "classify")
builder.add_edge("classify", "summarize")
builder.add_edge("summarize", "extract_actions")
builder.add_edge("extract_actions", "emit_result")
builder.add_edge("emit_result", END)

email_triage_graph = builder.compile()


# ---------------------------------------------------------------------------
# Workflow Studio Registration (Preset Templates Discovery)
# ---------------------------------------------------------------------------

EMAIL_TRIAGE_TEMPLATE = {
    "template_id": "tpl_email_triage",
    "name": "Email Intelligence & Triage Pipeline",
    "description": "Autonomous inbox sync, cryptographic sender verification, NLP classification, summarization, and action item extraction.",
    "category": "Personal Agents",
    "node_count": 6,
}

if not any(t.get("template_id") == "tpl_email_triage" for t in PRESET_TEMPLATES):
    PRESET_TEMPLATES.append(EMAIL_TRIAGE_TEMPLATE)
