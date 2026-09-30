"""
Jarvis AIOS — Email Triage LangGraph Workflow Tests
---------------------------------------------------
Tests for email_triage_graph:
- Full happy path with mocked tools produces status="completed"
- Partial failure path (e.g. classification or extraction fails) returns status="partial" with nulls
- Missing user_id returns status="failed"
"""

import json
from datetime import datetime, timezone

from app.Data.database import SessionLocal
from app.Tools.email.models import EmailModel, EmailSenderVerificationModel
from app.Tools.registry import registry
from app.Workflows.compiled.email_triage_graph import (
    EmailTriageState,
    email_triage_graph,
)
from app.tests.email.conftest import MockLLMClient


def _seed_test_email(user_id: int = 901, subject: str = "Quarterly Business Update") -> int:
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        email = EmailModel(
            user_id=user_id,
            gmail_message_id=f"msg_graph_{datetime.now(timezone.utc).timestamp()}",
            gmail_thread_id="th_graph_1",
            sender="director@company.org",
            sender_domain="company.org",
            recipients="[\"alice.intel@jarvis.test\"]",
            subject=subject,
            body_text=f"Body for {subject} with important actions.",
            received_at=now_iso,
            attachment_metadata="[]",
            gmail_metadata="{}",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(email)
        db.commit()
        db.refresh(email)

        # Seed initial verification
        verif = EmailSenderVerificationModel(
            user_id=user_id,
            email_id=email.id,
            spf_status="pass",
            dkim_status="pass",
            dmarc_status="pass",
            raw_auth_results="spf=pass dkim=pass dmarc=pass",
            verification_status="completed",
            verified_at=now_iso,
        )
        db.add(verif)
        db.commit()
        return email.id
    finally:
        db.close()


def test_email_triage_graph_happy_path():
    """Verify full end-to-end execution through the compiled LangGraph StateGraph."""
    email_id = _seed_test_email(901, "Sprint Demo Deliverables")

    # Mock LLM for classifier, summarizer, action extractor
    mock_classify = MockLLMClient(json.dumps({
        "category": "PLACEMENT",
        "subcategory": "project",
        "priority_score": 85,
        "reason": "Sprint deliverables."
    }))
    mock_summarize = MockLLMClient(json.dumps({
        "one_line_summary": "Deliverables for sprint demo are prepared.",
        "key_points": ["Completed backend routes", "Integrated LangGraph pipeline", "Verified test suite"]
    }))
    mock_extract = MockLLMClient(json.dumps({
        "deadline": "2026-10-15",
        "links": ["https://jira.org/demo"],
        "tasks": ["Prepare demo slides"],
        "sender_action_required": True
    }))

    setattr(registry.get("email.classify"), "llm", mock_classify)
    setattr(registry.get("email.summarize"), "llm", mock_summarize)
    setattr(registry.get("email.extract_actions"), "llm", mock_extract)

    initial_state: EmailTriageState = {
        "user_id": 901,
        "email_id": email_id,
    }

    final_state = email_triage_graph.invoke(initial_state)

    assert final_state["status"] == "completed"
    assert final_state["email_id"] == email_id

    # Verify node outputs
    assert final_state["verification_result"] is not None
    assert final_state["classification_result"]["category"] == "PLACEMENT"
    assert final_state["summary_result"]["one_line_summary"] == "Deliverables for sprint demo are prepared."
    assert final_state["actions_result"]["deadline"] == "2026-10-15"

    # Verify consolidated emitted_result
    emitted = final_state["emitted_result"]
    assert emitted["status"] == "completed"
    assert emitted["email_id"] == email_id
    assert emitted["classification"]["category"] == "PLACEMENT"


def test_email_triage_graph_partial_failure():
    """Verify when an intermediate node errors, the graph continues and returns status='partial' with nulls."""
    email_id = _seed_test_email(901, "Partial Failure Test")

    # Make classifier fail
    mock_fail = MockLLMClient()
    mock_fail.set_error(RuntimeError("LLM API rate limit exceeded"))
    setattr(registry.get("email.classify"), "llm", mock_fail)

    # Let summarizer succeed
    mock_summarize = MockLLMClient(json.dumps({
        "one_line_summary": "Email summary works despite classification error.",
        "key_points": ["Point A", "Point B", "Point C"]
    }))
    setattr(registry.get("email.summarize"), "llm", mock_summarize)

    # Let extract actions fail
    mock_act_fail = MockLLMClient()
    mock_act_fail.set_error(ValueError("Invalid JSON from LLM"))
    setattr(registry.get("email.extract_actions"), "llm", mock_act_fail)

    initial_state: EmailTriageState = {
        "user_id": 901,
        "email_id": email_id,
    }

    final_state = email_triage_graph.invoke(initial_state)

    assert final_state["status"] == "partial"
    assert len(final_state["errors"]) >= 2
    # Failed nodes must have None
    assert final_state["classification_result"] is None
    assert final_state["actions_result"] is None
    # Succeeded nodes must be preserved
    assert final_state["summary_result"] is not None
    assert final_state["verification_result"] is not None


def test_email_triage_graph_missing_user_id():
    """Verify graph returns failed status when user_id is missing."""
    empty_state: EmailTriageState = {}
    final_state = email_triage_graph.invoke(empty_state)
    assert final_state["status"] == "failed"
    assert any("user_id" in err for err in final_state["errors"])
