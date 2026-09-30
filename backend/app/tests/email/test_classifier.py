"""
Jarvis AIOS — Email Classifier Tests
------------------------------------
Tests for email.classify:
- valid category stored correctly
- invalid category from LLM rejected with structured error
- priority_score boundaries (0, 100)
- priority_score out of range rejected
- LLM timeout / failure raises structured error with nothing stored
- LLM returns malformed JSON raises structured error
- user isolation (user A cannot classify user B's email)
"""

import json
from datetime import datetime, timezone
import pytest
from sqlalchemy import select

from app.Data.database import SessionLocal
from app.Tools.email.models import EmailAnalysisModel, EmailModel
from app.Tools.engine import engine
from app.tests.email.conftest import MockLLMClient


def _seed_test_email(user_id: int = 901, subject: str = "Test Subject", body: str = "Test body") -> int:
    """Helper to seed an email and return its ID."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        email = EmailModel(
            user_id=user_id,
            gmail_message_id=f"msg_test_{datetime.now(timezone.utc).timestamp()}",
            gmail_thread_id="th_test_1",
            sender="recruiter@google.com",
            sender_domain="google.com",
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


def test_classify_valid_category_stored_correctly():
    """Verify valid classification outputs and persistence in email_analysis."""
    email_id = _seed_test_email(901, "Interview for Software Engineer", "Congratulations! You have an interview scheduled.")
    mock_llm = MockLLMClient(json.dumps({
        "category": "PLACEMENT",
        "subcategory": "interview_invitation",
        "priority_score": 90,
        "reason": "Direct interview invitation for an engineering position."
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.classify")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)

    assert res["email_id"] == email_id
    assert res["category"] == "PLACEMENT"
    assert res["subcategory"] == "interview_invitation"
    assert res["priority_score"] == 90
    assert "interview" in res["reason"].lower()

    # Verify stored in DB
    db = SessionLocal()
    try:
        analysis = db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one()
        assert analysis.category == "PLACEMENT"
        assert analysis.subcategory == "interview_invitation"
        assert analysis.priority_score == 90
        assert analysis.classified_at is not None
    finally:
        db.close()


def test_classify_invalid_category_rejected():
    """Verify invalid category from LLM is rejected with structured error and not stored."""
    email_id = _seed_test_email(901, "Notice", "Important update.")
    mock_llm = MockLLMClient(json.dumps({
        "category": "INVALID_UNKNOWN_CAT",
        "subcategory": "general",
        "priority_score": 50,
        "reason": "Unknown"
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.classify")
    setattr(tool, "llm", mock_llm)

    with pytest.raises(ValueError, match="Invalid category from LLM: 'INVALID_UNKNOWN_CAT'"):
        engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)

    # Verify nothing stored
    db = SessionLocal()
    try:
        analysis = db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one_or_none()
        assert analysis is None
    finally:
        db.close()


def test_classify_priority_score_boundaries_and_out_of_range():
    """Verify priority_score bounds [0, 100] and rejection when out of range."""
    email_id = _seed_test_email(901, "Boundary Test", "Test content.")
    mock_llm = MockLLMClient()
    from app.Tools.registry import registry
    tool = registry.get("email.classify")
    setattr(tool, "llm", mock_llm)

    # 1. Boundary: 0
    mock_llm.set_response(json.dumps({
        "category": "NEWS",
        "subcategory": "weekly",
        "priority_score": 0,
        "reason": "Low priority"
    }))
    res_zero = engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)
    assert res_zero["priority_score"] == 0

    # 2. Boundary: 100
    mock_llm.set_response(json.dumps({
        "category": "URGENT",
        "subcategory": "critical",
        "priority_score": 100,
        "reason": "Top priority"
    }))
    res_hundred = engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)
    assert res_hundred["priority_score"] == 100

    # 3. Out of range: 105
    mock_llm.set_response(json.dumps({
        "category": "URGENT",
        "subcategory": "critical",
        "priority_score": 105,
        "reason": "Out of bounds"
    }))
    with pytest.raises(ValueError, match="Priority score 105 is out of bounds"):
        engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)

    # 4. Out of range: -5
    mock_llm.set_response(json.dumps({
        "category": "URGENT",
        "subcategory": "critical",
        "priority_score": -5,
        "reason": "Negative score"
    }))
    with pytest.raises(ValueError, match="Priority score -5 is out of bounds"):
        engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)


def test_classify_llm_failure_raises_structured_error():
    """Verify LLM timeout/error raises clean error and stores nothing."""
    email_id = _seed_test_email(901, "Error Test", "Content.")
    mock_llm = MockLLMClient()
    mock_llm.set_error(TimeoutError("LLM API request timed out after 30s"))

    from app.Tools.registry import registry
    tool = registry.get("email.classify")
    setattr(tool, "llm", mock_llm)

    with pytest.raises(ValueError, match="LLM classification failure"):
        engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)

    db = SessionLocal()
    try:
        assert db.execute(select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)).scalar_one_or_none() is None
    finally:
        db.close()


def test_classify_malformed_json_raises_structured_error():
    """Verify malformed JSON from LLM raises clean error."""
    email_id = _seed_test_email(901, "Malformed Test", "Content.")
    mock_llm = MockLLMClient("Here is your classification: {category: URGENT, bad_json")

    from app.Tools.registry import registry
    tool = registry.get("email.classify")
    setattr(tool, "llm", mock_llm)

    with pytest.raises(ValueError, match="Malformed LLM response"):
        engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)


def test_classify_user_isolation():
    """Verify user A cannot classify user B's email."""
    # Seed email for user 902 (Bob)
    email_id_bob = _seed_test_email(902, "Bob's Secret", "Confidential.")

    from app.Tools.registry import registry
    tool = registry.get("email.classify")
    setattr(tool, "llm", MockLLMClient("{}"))

    # User 901 (Alice) tries to classify Bob's email
    with pytest.raises(ValueError, match="Email not found or access denied"):
        engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id_bob)
