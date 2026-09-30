"""
Jarvis AIOS — Email Security & Secret Leakage Tests
---------------------------------------------------
A dedicated test scans every email tool return value for forbidden secret keys:
  - token
  - refresh_token
  - access_token
  - client_secret
  - code
  - api_key
Asserts none are present in any dictionary key or value.
"""

import json
from datetime import datetime, timezone
from typing import Any

from app.Data.database import SessionLocal
from app.Tools.email.models import EmailAnalysisModel, EmailModel
from app.Tools.engine import engine
from app.tests.email.conftest import MockLLMClient

FORBIDDEN_SECRET_KEYS = {
    "token",
    "refresh_token",
    "access_token",
    "client_secret",
    "code",
    "api_key",
}


def _assert_no_secret_keys_recursive(data: Any, path: str = "root") -> None:
    """Recursively scan dict/list structures to verify no forbidden keys exist."""
    if isinstance(data, dict):
        for k, v in data.items():
            key_clean = str(k).lower().strip()
            for forbidden in FORBIDDEN_SECRET_KEYS:
                assert forbidden != key_clean, f"Forbidden secret key '{forbidden}' leaked in response at {path}.{k}"
            _assert_no_secret_keys_recursive(v, f"{path}.{k}")
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            _assert_no_secret_keys_recursive(item, f"{path}[{idx}]")


def _seed_test_email(user_id: int = 901) -> int:
    """Seed test email for scanning."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        email = EmailModel(
            user_id=user_id,
            gmail_message_id=f"msg_sec_{datetime.now(timezone.utc).timestamp()}",
            gmail_thread_id="th_sec_1",
            sender="service@provider.com",
            sender_domain="provider.com",
            recipients="[\"alice.intel@jarvis.test\"]",
            subject="Security Audit Confirmation",
            body_text="Your account passed the security verification. Review terms at https://provider.com/terms.",
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


def test_no_secret_leakage_in_classify_tool():
    """Verify email.classify output contains zero sensitive credential keys."""
    email_id = _seed_test_email(901)
    mock_llm = MockLLMClient(json.dumps({
        "category": "FINANCE",
        "subcategory": "billing",
        "priority_score": 65,
        "reason": "Billing invoice statement"
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.classify")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.classify", caller_context={"user_id": 901}, email_id=email_id)
    _assert_no_secret_keys_recursive(res)


def test_no_secret_leakage_in_summarize_tool():
    """Verify email.summarize output contains zero sensitive credential keys."""
    email_id = _seed_test_email(901)
    mock_llm = MockLLMClient(json.dumps({
        "one_line_summary": "Security audit verified and complete.",
        "key_points": [
            "All compliance checks completed",
            "No high severity vulnerabilities discovered",
            "Annual recertification scheduled for next year"
        ]
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.summarize")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.summarize", caller_context={"user_id": 901}, email_id=email_id)
    _assert_no_secret_keys_recursive(res)


def test_no_secret_leakage_in_extract_actions_tool():
    """Verify email.extract_actions output contains zero sensitive credential keys."""
    email_id = _seed_test_email(901)
    mock_llm = MockLLMClient(json.dumps({
        "deadline": "2026-12-31",
        "links": ["https://provider.com/terms"],
        "tasks": ["Review terms and conditions"],
        "sender_action_required": True
    }))

    from app.Tools.registry import registry
    tool = registry.get("email.extract_actions")
    setattr(tool, "llm", mock_llm)

    res = engine.execute("email.extract_actions", caller_context={"user_id": 901}, email_id=email_id)
    _assert_no_secret_keys_recursive(res)


def test_no_secret_leakage_in_digest_tool():
    """Verify email.digest output contains zero sensitive credential keys."""
    email_id = _seed_test_email(901)

    # Classify and summarize to populate analysis
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        analysis = EmailAnalysisModel(
            email_id=email_id,
            category="FINANCE",
            subcategory="billing",
            priority_score=75,
            summary_text="Invoice paid in full.",
            action_items_json=json.dumps({"tasks": ["File invoice"], "links": []}),
            deadline="2026-11-01",
            classified_at=now_iso,
            summarized_at=now_iso,
            extracted_at=now_iso,
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(analysis)
        db.commit()
    finally:
        db.close()

    res = engine.execute("email.digest", caller_context={"user_id": 901}, period="today")
    _assert_no_secret_keys_recursive(res)
