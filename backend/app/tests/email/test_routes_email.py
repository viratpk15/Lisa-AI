"""
Jarvis AIOS — Email Router REST API Integration Tests
------------------------------------------------------
Tests for FastAPI router at /api/v1/email:
- Auth failure (no JWT) returns 401
- User isolation (User A cannot list or get User B's emails)
- Success paths for /sync, /list, /{id}, /{id}/classify, /{id}/summarize, /{id}/extract-actions, /digest
- Error passthrough on /sync when Gmail account is disconnected
- Security credential leakage assertion across all endpoint responses
"""

import json
from datetime import datetime, timezone
from typing import Any
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.Auth.security import create_access_token
from app.Data.database import SessionLocal
from app.Data.models import UserModel
from app.Tools.email.models import (
    EmailAnalysisModel,
    EmailModel,
    EmailSenderVerificationModel,
)
import pytest
from app.main import app
from app.tests.email.conftest import MockLLMClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_app_overrides():
    prev = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(prev)

FORBIDDEN_SECRET_KEYS = {
    "token",
    "refresh_token",
    "access_token",
    "client_secret",
    "code",
    "api_key",
}


def _assert_no_secret_leakage(data: Any, path: str = "root") -> None:
    if isinstance(data, dict):
        for k, v in data.items():
            key_clean = str(k).lower().strip()
            for forbidden in FORBIDDEN_SECRET_KEYS:
                assert forbidden != key_clean, f"Forbidden secret key '{forbidden}' leaked in response at {path}.{k}"
            _assert_no_secret_leakage(v, f"{path}.{k}")
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            _assert_no_secret_leakage(item, f"{path}[{idx}]")


def _auth_headers(user_id: int = 901, email: str = "alice.intel@jarvis.test") -> dict[str, str]:
    db = SessionLocal()
    try:
        user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
        if not user:
            db.add(UserModel(id=user_id, email=email, password_hash="hash", created_at="2026-09-27T00:00:00Z"))
            db.commit()
    finally:
        db.close()
    token = create_access_token(user_id=user_id, email=email)
    return {"Authorization": f"Bearer {token}"}


def _seed_test_email(user_id: int, subject: str, category: str = "URGENT", priority: int = 90) -> int:
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        email = EmailModel(
            user_id=user_id,
            gmail_message_id=f"msg_route_{datetime.now(timezone.utc).timestamp()}_{user_id}",
            gmail_thread_id="th_route_1",
            sender=f"sender_{user_id}@test.org",
            sender_domain="test.org",
            recipients="[\"recipient@test.org\"]",
            subject=subject,
            body_text=f"Body content for {subject}",
            received_at=now_iso,
            attachment_metadata="[]",
            gmail_metadata="{}",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(email)
        db.commit()
        db.refresh(email)

        analysis = EmailAnalysisModel(
            email_id=email.id,
            category=category,
            subcategory="general",
            priority_score=priority,
            summary_text=f"Summary for {subject}\n\n- Key point 1\n- Key point 2\n- Key point 3",
            action_items_json=json.dumps({"tasks": ["Review doc"], "links": ["https://test.org/doc"], "sender_action_required": True}),
            deadline="2026-10-30",
            classified_at=now_iso,
            summarized_at=now_iso,
            extracted_at=now_iso,
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(analysis)

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


def test_routes_auth_failure_without_jwt():
    """Verify missing JWT returns 401 Unauthorized across endpoints."""
    assert client.get("/api/v1/email/list").status_code == 401
    assert client.get("/api/v1/email/1").status_code == 401
    assert client.post("/api/v1/email/sync").status_code == 401
    assert client.post("/api/v1/email/1/classify").status_code == 401
    assert client.post("/api/v1/email/1/summarize").status_code == 401
    assert client.post("/api/v1/email/1/extract-actions").status_code == 401
    assert client.get("/api/v1/email/digest").status_code == 401


def test_routes_sync_passthrough_error_when_disconnected():
    """Verify /sync returns structured 400 when user has not connected Gmail."""
    headers = _auth_headers(901)
    res = client.post("/api/v1/email/sync", headers=headers, json={"max_results": 10})
    assert res.status_code == 400
    data = res.json()
    assert "error" in data
    assert "not connected" in data["error"]["message"].lower()


def test_routes_list_and_user_isolation():
    """Verify /list returns user-scoped emails and prevents cross-user access."""
    email_alice = _seed_test_email(901, "Alice Confidential", "FINANCE", 80)
    email_bob = _seed_test_email(902, "Bob Secret", "PERSONAL", 50)

    headers_alice = _auth_headers(901)
    res_alice = client.get("/api/v1/email/list", headers=headers_alice)
    assert res_alice.status_code == 200
    emails_alice = res_alice.json()["emails"]
    ids_alice = [e["id"] for e in emails_alice]

    assert email_alice in ids_alice
    assert email_bob not in ids_alice

    # Filter by category
    res_filtered = client.get("/api/v1/email/list?category=FINANCE", headers=headers_alice)
    assert res_filtered.status_code == 200
    filtered_items = res_filtered.json()["emails"]
    assert all(e["category"] == "FINANCE" for e in filtered_items)


def test_routes_get_email_detail_and_isolation():
    """Verify /{id} returns complete email detail and blocks other users with 404."""
    email_alice = _seed_test_email(901, "Alice Interview Notice", "PLACEMENT", 95)
    email_bob = _seed_test_email(902, "Bob Tax Form", "FINANCE", 70)

    headers_alice = _auth_headers(901)

    # Alice fetches her email
    res_ok = client.get(f"/api/v1/email/{email_alice}", headers=headers_alice)
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["id"] == email_alice
    assert data["analysis"]["category"] == "PLACEMENT"
    assert data["verification"]["is_verified"] is True
    assert data["verification"]["spf_status"] == "pass"

    # Alice attempts to fetch Bob's email
    res_forbidden = client.get(f"/api/v1/email/{email_bob}", headers=headers_alice)
    assert res_forbidden.status_code == 404


def test_routes_classify_summarize_extract_actions():
    """Verify /{id}/classify, /{id}/summarize, and /{id}/extract-actions endpoints."""
    email_id = _seed_test_email(901, "Job Offer Letter", "PLACEMENT", 90)
    headers = _auth_headers(901)

    # 1. Classify
    from app.Tools.registry import registry
    tool_cls = registry.get("email.classify")
    setattr(tool_cls, "llm", MockLLMClient(json.dumps({
        "category": "PLACEMENT",
        "subcategory": "offer",
        "priority_score": 98,
        "reason": "Direct offer letter."
    })))
    res_cls = client.post(f"/api/v1/email/{email_id}/classify", headers=headers)
    assert res_cls.status_code == 200
    assert res_cls.json()["category"] == "PLACEMENT"
    assert res_cls.json()["priority_score"] == 98

    # 2. Summarize
    tool_sum = registry.get("email.summarize")
    setattr(tool_sum, "llm", MockLLMClient(json.dumps({
        "one_line_summary": "Official full-time offer letter from tech company.",
        "key_points": ["Competitive compensation package", "Start date on November 1st", "Response requested by Friday"]
    })))
    res_sum = client.post(f"/api/v1/email/{email_id}/summarize", headers=headers)
    assert res_sum.status_code == 200
    assert len(res_sum.json()["key_points"]) == 3

    # 3. Extract Actions
    tool_act = registry.get("email.extract_actions")
    setattr(tool_act, "llm", MockLLMClient(json.dumps({
        "deadline": "2026-11-01",
        "links": ["https://portal.company.com/sign"],
        "tasks": ["Sign offer letter", "Upload tax ID"],
        "sender_action_required": True
    })))
    res_act = client.post(f"/api/v1/email/{email_id}/extract-actions", headers=headers)
    assert res_act.status_code == 200
    assert res_act.json()["deadline"] == "2026-11-01"
    assert len(res_act.json()["tasks"]) == 2


def test_routes_digest():
    """Verify /digest endpoint returns aggregated analytics."""
    _seed_test_email(901, "Urgent Server Problem", "URGENT", 92)
    headers = _auth_headers(901)

    res = client.get("/api/v1/email/digest?period=today", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["period"] == "today"
    assert "counts_by_category" in data
    assert "top_urgent" in data


def test_routes_no_credential_leakage():
    """Verify no tokens, credentials, or client secrets leak in router responses."""
    email_id = _seed_test_email(901, "Security Audit Check", "FINANCE", 80)
    headers = _auth_headers(901)

    for path in [
        "/api/v1/email/list",
        f"/api/v1/email/{email_id}",
        "/api/v1/email/digest?period=today",
    ]:
        res = client.get(path, headers=headers)
        if res.status_code == 200:
            _assert_no_secret_leakage(res.json(), path=path)
