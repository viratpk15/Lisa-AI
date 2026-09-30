"""
Jarvis AIOS — Email Action & Deadline Extractor Tests
------------------------------------------------------
Tests for email.extract_actions:
- deadline parsed from various expressions ("by Friday", "Dec 20", "2026-01-15")
- invalid URLs dropped and valid URLs preserved
- missing deadline stored as null
- tasks extracted as list of strings
- LLM failure raises structured error
- user isolation (user A cannot extract actions from user B's email)
"""

import json
from datetime import datetime, timezone
import pytest
from sqlalchemy import select

from app.Data.database import SessionLocal
from app.Tools.email.models import EmailAnalysisModel, EmailModel
from app.Tools.engine import engine
from app.tests.email.conftest import MockLLMClient


def _seed_test_email(user_id: int = 901, subject: str = "Upcoming Deadlines & Tasks", body: str = "Action required.") -> int:
    """Helper to seed an email and return its ID."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        email = EmailModel(
            user_id=user_id,
            gmail_message_id=f"msg_act_{datetime.now(timezone.utc).timestamp()}",
            gmail_thread_id="th_act_1",
            sender="manager@work.com",
            sender_domain="work.com",
            recipients="[\"alice.intel@jarvis.test\"]",
            subject=subject,
            body_text=body,
            received_at=now_iso,
            attachment_metadata="[]",
            gmail_metadata="{}",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(email)
        db.commit()
        db.refresh(email)
        return email.id
    finally:
        db.close()


def test_action_extractor_valid_payload_and_tasks():
    """Verify tasks extracted as list of strings and saved into email_analysis."""
    email_id = _seed_test_email(901, "Sprint Planning Action Items", "Please complete these items.")
    mock_llm = MockLLMClient(json.dumps({
        "deadline": "2026-01-15",
        "links": ["https://jira.corp.internal/browse/PROJ-101", "http://github.com/org/repo/pull/42"],
        "tasks": [
            "Review pull request 42 before noon",
            "Update sprint velocity chart",
            "Confirm availability for tomorrow's standup"
        ],
        "sender_action_required": True
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.extract_actions")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.extract_actions", caller_context={"user_id": 901}, email_id=email_id)

    assert res["email_id"] == email_id
    assert res["deadline"] == "2026-01-15"
    assert len(res["tasks"]) == 3
    assert "Review pull request" in res["tasks"][0]
    assert len(res["links"]) == 2
    assert res["sender_action_required"] is True

    # Verify DB persistence
    db = SessionLocal()
    try:
        analysis = db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one()
        assert analysis.deadline == "2026-01-15"
        assert analysis.extracted_at is not None
        payload = json.loads(analysis.action_items_json or "{}")
        assert len(payload["tasks"]) == 3
        assert len(payload["links"]) == 2
        assert payload["sender_action_required"] is True
    finally:
        db.close()


@pytest.mark.parametrize("deadline_input,expected_deadline", [
    ("by Friday (2026-10-02)", "by Friday (2026-10-02)"),
    ("Dec 20, 2026", "Dec 20, 2026"),
    ("2026-01-15", "2026-01-15"),
    ("2026-04-30T17:00:00Z", "2026-04-30T17:00:00Z"),
])
def test_action_extractor_deadline_variations(deadline_input: str, expected_deadline: str):
    """Verify various deadline expressions parsed and preserved."""
    email_id = _seed_test_email(901, f"Deadline {deadline_input}", f"Due {deadline_input}")
    mock_llm = MockLLMClient(json.dumps({
        "deadline": deadline_input,
        "links": [],
        "tasks": ["Submit assignment"],
        "sender_action_required": True
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.extract_actions")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.extract_actions", caller_context={"user_id": 901}, email_id=email_id)
    assert res["deadline"] == expected_deadline


def test_action_extractor_invalid_urls_dropped():
    """Verify malformed or invalid URLs are dropped while valid http/https URLs are preserved."""
    email_id = _seed_test_email(901, "Link Verification", "Check these links.")
    mock_llm = MockLLMClient(json.dumps({
        "deadline": None,
        "links": [
            "https://valid-domain.com/path?arg=1",
            "not_a_valid_url",
            "ftp://unsupported-scheme.org/file",
            "javascript:alert(1)",
            "http://localhost:8000/api",
            ""
        ],
        "tasks": ["Check links"],
        "sender_action_required": False
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.extract_actions")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.extract_actions", caller_context={"user_id": 901}, email_id=email_id)

    assert "https://valid-domain.com/path?arg=1" in res["links"]
    assert "http://localhost:8000/api" in res["links"]
    assert "not_a_valid_url" not in res["links"]
    assert "ftp://unsupported-scheme.org/file" not in res["links"]
    assert "javascript:alert(1)" not in res["links"]
    assert len(res["links"]) == 2


def test_action_extractor_missing_deadline_stores_null():
    """Verify when no deadline is present, null/None is returned and stored."""
    email_id = _seed_test_email(901, "No Deadline", "Just FYI.")
    mock_llm = MockLLMClient(json.dumps({
        "deadline": None,
        "links": [],
        "tasks": [],
        "sender_action_required": False
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.extract_actions")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.extract_actions", caller_context={"user_id": 901}, email_id=email_id)
    assert res["deadline"] is None

    db = SessionLocal()
    try:
        analysis = db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one()
        assert analysis.deadline is None
    finally:
        db.close()


def test_action_extractor_llm_failure_structured_error():
    """Verify LLM failure raises structured error and leaves DB clean."""
    email_id = _seed_test_email(901, "Crash Test", "Details.")
    mock_llm = MockLLMClient()
    mock_llm.set_error(ConnectionError("Service unavailable 503"))

    from app.Tools.registry import registry
    tool = registry.get("email.extract_actions")
    setattr(tool, "llm", mock_llm)

    with pytest.raises(ValueError, match="LLM action extraction failure"):
        engine.execute("email.extract_actions", caller_context={"user_id": 901}, email_id=email_id)

    db = SessionLocal()
    try:
        assert db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one_or_none() is None
    finally:
        db.close()


def test_action_extractor_user_isolation():
    """Verify user A cannot extract actions from user B's email."""
    email_id_bob = _seed_test_email(902, "Bob's Action Items", "Confidential.")
    from app.Tools.registry import registry
    tool = registry.get("email.extract_actions")
    setattr(tool, "llm", MockLLMClient("{}"))

    with pytest.raises(ValueError, match="Email not found or access denied"):
        engine.execute("email.extract_actions", caller_context={"user_id": 901}, email_id=email_id_bob)
