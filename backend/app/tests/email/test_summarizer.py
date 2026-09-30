"""
Jarvis AIOS — Email Summarizer Tests
------------------------------------
Tests for email.summarize:
- correct output shape stored
- empty key_points rejected
- key_points out of range (< 3 or > 7) rejected
- missing one_line_summary rejected
- LLM failure raises structured error with nothing stored
- user isolation (user A cannot summarize user B's email)
"""

import json
from datetime import datetime, timezone
import pytest
from sqlalchemy import select

from app.Data.database import SessionLocal
from app.Tools.email.models import EmailAnalysisModel, EmailModel
from app.Tools.engine import engine
from app.tests.email.conftest import MockLLMClient


def _seed_test_email(user_id: int = 901, subject: str = "Quarterly Business Review", body: str = "Financials and roadmap.") -> int:
    """Helper to seed an email and return its ID."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        email = EmailModel(
            user_id=user_id,
            gmail_message_id=f"msg_sum_{datetime.now(timezone.utc).timestamp()}",
            gmail_thread_id="th_sum_1",
            sender="director@company.org",
            sender_domain="company.org",
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


def test_summarize_correct_output_shape_and_stored():
    """Verify standard summarization outputs and database persistence."""
    email_id = _seed_test_email(901, "Project Titan Status", "Titan milestone reached. 3 critical blockers resolved.")
    mock_llm = MockLLMClient(json.dumps({
        "one_line_summary": "Project Titan achieved key milestone with three blockers resolved.",
        "key_points": [
            "Milestone 2 reached on schedule",
            "Resolved 3 high-severity blockers in data pipeline",
            "Next sprint focuses on end-to-end integration testing",
            "Budget remains within the projected envelope"
        ]
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.summarize")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.summarize", caller_context={"user_id": 901}, email_id=email_id)

    assert res["email_id"] == email_id
    assert res["one_line_summary"] == "Project Titan achieved key milestone with three blockers resolved."
    assert len(res["key_points"]) == 4
    assert res["key_points"][0] == "Milestone 2 reached on schedule"

    # Verify DB persistence
    db = SessionLocal()
    try:
        analysis = db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one()
        assert analysis.summary_text is not None
        assert "Project Titan" in analysis.summary_text
        assert "- Milestone 2 reached on schedule" in analysis.summary_text
        assert analysis.summarized_at is not None
    finally:
        db.close()


def test_summarize_empty_key_points_rejected():
    """Verify empty key_points list from LLM is rejected and not stored."""
    email_id = _seed_test_email(901, "Empty Points Test", "Details.")
    mock_llm = MockLLMClient(json.dumps({
        "one_line_summary": "Summary without points.",
        "key_points": []
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.summarize")
    setattr(tool, "llm", mock_llm)

    with pytest.raises(ValueError, match="Invalid key_points"):
        engine.execute("email.summarize", caller_context={"user_id": 901}, email_id=email_id)

    db = SessionLocal()
    try:
        assert db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one_or_none() is None
    finally:
        db.close()


def test_summarize_key_points_count_boundaries():
    """Verify key_points count validation: between 3 and 7 items."""
    email_id = _seed_test_email(901, "Boundary Test", "Details.")
    mock_llm = MockLLMClient()
    from app.Tools.registry import registry
    tool = registry.get("email.summarize")
    setattr(tool, "llm", mock_llm)

    # Too few: 2 points
    mock_llm.set_response(json.dumps({
        "one_line_summary": "Too few points.",
        "key_points": ["Point 1", "Point 2"]
    }))
    with pytest.raises(ValueError, match="Invalid key_points count: 2"):
        engine.execute("email.summarize", caller_context={"user_id": 901}, email_id=email_id)

    # Too many: 8 points
    mock_llm.set_response(json.dumps({
        "one_line_summary": "Too many points.",
        "key_points": [f"Point {i}" for i in range(1, 9)]
    }))
    with pytest.raises(ValueError, match="Invalid key_points count: 8"):
        engine.execute("email.summarize", caller_context={"user_id": 901}, email_id=email_id)


def test_summarize_missing_summary_rejected():
    """Verify missing or empty one_line_summary is rejected."""
    email_id = _seed_test_email(901, "No Summary Test", "Details.")
    mock_llm = MockLLMClient(json.dumps({
        "one_line_summary": "",
        "key_points": ["Pt 1", "Pt 2", "Pt 3"]
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.summarize")
    setattr(tool, "llm", mock_llm)

    with pytest.raises(ValueError, match="missing non-empty 'one_line_summary'"):
        engine.execute("email.summarize", caller_context={"user_id": 901}, email_id=email_id)


def test_summarize_llm_failure_raises_structured_error():
    """Verify LLM failure raises structured error and leaves DB clean."""
    email_id = _seed_test_email(901, "Crash Test", "Details.")
    mock_llm = MockLLMClient()
    mock_llm.set_error(RuntimeError("Gemini API connection reset by peer"))

    from app.Tools.registry import registry
    tool = registry.get("email.summarize")
    setattr(tool, "llm", mock_llm)

    with pytest.raises(ValueError, match="LLM summarization failure"):
        engine.execute("email.summarize", caller_context={"user_id": 901}, email_id=email_id)

    db = SessionLocal()
    try:
        assert db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one_or_none() is None
    finally:
        db.close()


def test_summarize_user_isolation():
    """Verify user A cannot summarize user B's email."""
    email_id_bob = _seed_test_email(902, "Bob's Financial Plan", "Confidential.")
    from app.Tools.registry import registry
    tool = registry.get("email.summarize")
    setattr(tool, "llm", MockLLMClient("{}"))

    with pytest.raises(ValueError, match="Email not found or access denied"):
        engine.execute("email.summarize", caller_context={"user_id": 901}, email_id=email_id_bob)
