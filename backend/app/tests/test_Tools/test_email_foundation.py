"""
Jarvis AIOS — Email Foundation Test Suite
-----------------------------------------
Automated unit & integration tests for:
1. Google OAuth URL generation, scopes, and CSRF state signing
2. State mismatch, tampering, and expiration validation
3. Token exchange and failure handling
4. Multi-tenant credential isolation per user
5. Gmail message payload, header, and attachment parsing
6. Successful email synchronization through ToolEngine
7. Message deduplication
8. Empty inbox handling
9. Provider failure resilience (does NOT become an empty inbox)
10. Automatic access token refresh
11. SPF, DKIM, and DMARC authentication header parsing
12. Missing authentication headers handling (unavailable state)
13. Credential leakage prevention across outputs and logs
"""

import base64
import json
import time
from datetime import datetime, timezone

import httpx
import pytest
from sqlalchemy import select

from app.Data.database import SessionLocal
from app.Data.models import UserModel
from app.Deployments.vault import decrypt_secret, encrypt_secret
from app.Tools.email.gmail_oauth import (
    GMAIL_READONLY_SCOPE,
    disconnect_gmail,
    exchange_code_for_tokens,
    generate_auth_state,
    get_authorization_url,
    get_connection_status,
    get_valid_access_token,
    validate_auth_state,
)
from app.Tools.email.models import EmailModel, EmailSenderVerificationModel, GmailConnectionModel
from app.Tools.email.sync_tool import _extract_domain, _extract_email_address, _parse_message_payload
from app.Tools.email.verify_tool import parse_dkim, parse_dmarc, parse_spf
from app.Tools.engine import engine


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Ensure test users and clean email tables exist."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "mock-google-client-id-12345.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "mock-google-client-secret-xyz987")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-state-signing-2026")

    db = SessionLocal()
    try:
        # Create test users if they don't exist
        for u_id, email in [(901, "alice@jarvis.test"), (902, "bob@jarvis.test")]:
            existing = db.execute(select(UserModel).where(UserModel.id == u_id)).scalar_one_or_none()
            if not existing:
                db.add(UserModel(id=u_id, email=email, password_hash="hashed_pw", created_at="2026-09-27T00:00:00Z"))

        # Clean existing test email records for test users
        db.query(EmailSenderVerificationModel).filter(EmailSenderVerificationModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.query(EmailModel).filter(EmailModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.query(GmailConnectionModel).filter(GmailConnectionModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        db.query(EmailSenderVerificationModel).filter(EmailSenderVerificationModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.query(EmailModel).filter(EmailModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.query(GmailConnectionModel).filter(GmailConnectionModel.user_id.in_([901, 902])).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 1. OAuth URL and State Tests
# ---------------------------------------------------------------------------

def test_oauth_url_and_state():
    """Verify authorization URL generation, read-only scope, and CSRF state token."""
    res = get_authorization_url(user_id=901)
    url = res["authorization_url"]
    state = res["state"]

    assert "accounts.google.com/o/oauth2/v2/auth" in url
    assert "mock-google-client-id-12345" in url
    assert "scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly" in url
    assert "access_type=offline" in url
    assert "prompt=consent" in url
    assert state in url

    # State validation should resolve user_id
    extracted_user = validate_auth_state(state, expected_user_id=901)
    assert extracted_user == 901


def test_state_mismatch_and_tampering():
    """Verify anti-CSRF state token rejects tampering, expiration, and user mismatch."""
    valid_state = generate_auth_state(901)

    # 1. Tampered signature
    tampered = valid_state[:-4] + "ABCD"
    with pytest.raises(ValueError, match="signature mismatch|Invalid OAuth state"):
        validate_auth_state(tampered, expected_user_id=901)

    # 2. User mismatch
    with pytest.raises(ValueError, match="mismatch with current user"):
        validate_auth_state(valid_state, expected_user_id=902)

    # 3. Expired state (simulate old timestamp)
    old_payload = f"901:{int(time.time()) - 1000}"
    import hashlib
    import hmac
    from app.Tools.email.gmail_oauth import _get_signing_key
    sig = hmac.new(_get_signing_key(), old_payload.encode(), hashlib.sha256).hexdigest()
    expired_token = base64.urlsafe_b64encode(f"{old_payload}:{sig}".encode()).decode()

    with pytest.raises(ValueError, match="has expired"):
        validate_auth_state(expired_token, expected_user_id=901)


# ---------------------------------------------------------------------------
# 2. Token Exchange & Refresh Failure Tests
# ---------------------------------------------------------------------------

def test_token_exchange_success_and_storage():
    """Verify exchange of code for tokens encrypts credentials and never leaks secrets."""
    state = generate_auth_state(901)

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if "oauth2.googleapis.com/token" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "access_token": "mock-access-token-sec-1",
                    "refresh_token": "mock-refresh-token-sec-1",
                    "expires_in": 3600,
                    "scope": GMAIL_READONLY_SCOPE,
                    "token_type": "Bearer",
                },
            )
        if "gmail/v1/users/me/profile" in str(request.url):
            return httpx.Response(200, json={"emailAddress": "alice.workspace@gmail.com"})
        return httpx.Response(404)

    mock_client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    db = SessionLocal()
    try:
        result = exchange_code_for_tokens(
            code="mock-auth-code-xyz",
            state=state,
            db=db,
            expected_user_id=901,
            http_client=mock_client,
        )

        assert result["status"] == "connected"
        assert result["email_address"] == "alice.workspace@gmail.com"
        assert result["user_id"] == 901
        # Crucial: verify raw credentials are NOT in return dict
        assert "access_token" not in result
        assert "refresh_token" not in result

        # Verify DB entry has encrypted credentials
        conn = db.execute(select(GmailConnectionModel).where(GmailConnectionModel.user_id == 901)).scalar_one()
        assert conn.email_address == "alice.workspace@gmail.com"
        assert conn.status == "connected"
        # Must not be plaintext
        assert "mock-access-token-sec-1" not in conn.encrypted_credentials
        # Decrypting should yield proper payload
        decrypted = json.loads(decrypt_secret(conn.encrypted_credentials))
        assert decrypted["access_token"] == "mock-access-token-sec-1"
        assert decrypted["refresh_token"] == "mock-refresh-token-sec-1"
    finally:
        db.close()


def test_token_exchange_provider_failure():
    """Verify provider 400/500 during code exchange raises clean error without leaking."""
    state = generate_auth_state(901)

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "invalid_grant", "error_description": "Bad Request"})

    mock_client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    db = SessionLocal()
    try:
        with pytest.raises(ValueError, match="Token exchange failed: HTTP 400"):
            exchange_code_for_tokens("invalid-code", state, db, expected_user_id=901, http_client=mock_client)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 3. Credential Isolation Tests
# ---------------------------------------------------------------------------

def test_credential_isolation_between_users():
    """Verify User 901 and User 902 have strictly isolated credentials and data."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        # Seed connection for User 901
        creds_901 = json.dumps({"access_token": "token-901", "refresh_token": "ref-901", "expires_at": int(time.time()) + 3600})
        conn_901 = GmailConnectionModel(
            user_id=901,
            email_address="alice@gmail.com",
            encrypted_credentials=encrypt_secret(creds_901),
            status="connected",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(conn_901)

        # Seed connection for User 902
        creds_902 = json.dumps({"access_token": "token-902", "refresh_token": "ref-902", "expires_at": int(time.time()) + 3600})
        conn_902 = GmailConnectionModel(
            user_id=902,
            email_address="bob@gmail.com",
            encrypted_credentials=encrypt_secret(creds_902),
            status="connected",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(conn_902)
        db.commit()

        # Token for 901 must be token-901
        token_a = get_valid_access_token(user_id=901, db=db)
        token_b = get_valid_access_token(user_id=902, db=db)

        assert token_a == "token-901"
        assert token_b == "token-902"
        assert token_a != token_b

        # Connection status for 901 must not leak 902 info
        status_a = get_connection_status(user_id=901, db=db)
        assert status_a["email_address"] == "alice@gmail.com"
        assert "token" not in str(status_a)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 4. Message Parsing Tests
# ---------------------------------------------------------------------------

def test_message_parsing_functions():
    """Verify header extraction, domain parsing, and multipart body traversal."""
    # 1. Header and domain extraction
    assert _extract_email_address("GitHub <notifications@github.com>") == "notifications@github.com"
    assert _extract_domain("notifications@github.com") == "github.com"
    assert _extract_email_address("plain@example.org") == "plain@example.org"
    assert _extract_domain("plain@example.org") == "example.org"

    # 2. Multipart payload traversal
    text_content = "Hello, this is a plain text notification."
    html_content = "<p>Hello, this is an <b>HTML</b> notification.</p>"
    b64_text = base64.urlsafe_b64encode(text_content.encode()).decode()
    b64_html = base64.urlsafe_b64encode(html_content.encode()).decode()

    payload = {
        "mimeType": "multipart/mixed",
        "parts": [
            {
                "mimeType": "multipart/alternative",
                "parts": [
                    {"mimeType": "text/plain", "body": {"data": b64_text}},
                    {"mimeType": "text/html", "body": {"data": b64_html}},
                ],
            },
            {
                "mimeType": "application/pdf",
                "filename": "invoice_2026.pdf",
                "body": {"size": 10240, "attachmentId": "att-id-pdf-1"},
            },
        ],
    }

    body_text, body_html, attachments = _parse_message_payload(payload)
    assert text_content in body_text
    assert html_content in (body_html or "")
    assert len(attachments) == 1
    assert attachments[0]["filename"] == "invoice_2026.pdf"
    assert attachments[0]["size_bytes"] == 10240
    assert attachments[0]["attachment_id"] == "att-id-pdf-1"


# ---------------------------------------------------------------------------
# 5. Email Sync & Deduplication Tests
# ---------------------------------------------------------------------------

def test_email_sync_and_deduplication():
    """Verify email.sync through ToolEngine stores emails, parses headers, and deduplicates."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        creds = json.dumps({"access_token": "valid-token-sync", "refresh_token": "ref-sync", "expires_at": int(time.time()) + 3600})
        conn = GmailConnectionModel(
            user_id=901,
            email_address="alice.test@gmail.com",
            encrypted_credentials=encrypt_secret(creds),
            status="connected",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(conn)
        db.commit()

        # Setup mock responses for Gmail API
        msg_1_payload = {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": "Stripe <receipts@stripe.com>"},
                {"name": "To", "value": "alice.test@gmail.com"},
                {"name": "Subject", "value": "Your Receipt for Order #1001"},
                {"name": "Date", "value": "Sun, 27 Sep 2026 10:00:00 +0000"},
                {"name": "Message-ID", "value": "<msg-stripe-1001@stripe.com>"},
                {"name": "Authentication-Results", "value": "mx.google.com; spf=pass; dkim=pass; dmarc=pass"},
            ],
            "body": {"data": base64.urlsafe_b64encode(b"Thank you for your payment of $49.00.").decode()},
        }

        msg_2_payload = {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": "GitHub Support <support@github.com>"},
                {"name": "To", "value": "alice.test@gmail.com, team@jarvis.test"},
                {"name": "Subject", "value": "Security Advisory Notice"},
                {"name": "Date", "value": "Sun, 27 Sep 2026 11:30:00 +0000"},
                {"name": "Message-ID", "value": "<msg-gh-2002@github.com>"},
                {"name": "Authentication-Results", "value": "mx.google.com; spf=pass; dkim=pass; dmarc=pass"},
            ],
            "body": {"data": base64.urlsafe_b64encode(b"Please review the advisory for your repository.").decode()},
        }

        def mock_gmail_handler(request: httpx.Request) -> httpx.Response:
            url_str = str(request.url)
            # List messages
            if "gmail/v1/users/me/messages?" in url_str:
                return httpx.Response(
                    200,
                    json={
                        "messages": [
                            {"id": "gmail_msg_001", "threadId": "th_001"},
                            {"id": "gmail_msg_002", "threadId": "th_002"},
                        ],
                        "resultSizeEstimate": 2,
                    },
                )
            # Detail message 1
            if "gmail_msg_001" in url_str:
                return httpx.Response(
                    200,
                    json={
                        "id": "gmail_msg_001",
                        "threadId": "th_001",
                        "snippet": "Thank you for your payment...",
                        "payload": msg_1_payload,
                    },
                )
            # Detail message 2
            if "gmail_msg_002" in url_str:
                return httpx.Response(
                    200,
                    json={
                        "id": "gmail_msg_002",
                        "threadId": "th_002",
                        "snippet": "Please review the advisory...",
                        "payload": msg_2_payload,
                    },
                )
            return httpx.Response(404)

        mock_http = httpx.Client(transport=httpx.MockTransport(mock_gmail_handler))

        # Register custom client in tool
        from app.Tools.registry import registry
        sync_tool = registry.get("email.sync")
        setattr(sync_tool, "http_client", mock_http)

        # 1. First sync run — should insert 2 new messages
        res1 = engine.execute("email.sync", caller_context={"user_id": 901})
        assert res1["status"] == "success"
        assert res1["synced_count"] == 2
        assert res1["duplicate_count"] == 0
        assert res1["total_fetched"] == 2

        # Verify DB records
        saved_emails = db.execute(select(EmailModel).where(EmailModel.user_id == 901)).scalars().all()
        assert len(saved_emails) == 2
        subjects = [e.subject for e in saved_emails]
        assert "Your Receipt for Order #1001" in subjects
        assert "Security Advisory Notice" in subjects

        # Verify sender domain
        stripe_email = next(e for e in saved_emails if "stripe" in e.sender)
        assert stripe_email.sender_domain == "stripe.com"
        assert "receipts@stripe.com" in stripe_email.sender

        # 2. Second sync run with same messages — should deduplicate
        res2 = engine.execute("email.sync", caller_context={"user_id": 901})
        assert res2["status"] == "success"
        assert res2["synced_count"] == 0
        assert res2["duplicate_count"] == 2
        assert res2["total_fetched"] == 2

        # Still only 2 emails in DB
        assert len(db.execute(select(EmailModel).where(EmailModel.user_id == 901)).scalars().all()) == 2
    finally:
        db.close()


def test_empty_inbox():
    """Verify empty inbox returns zero counts gracefully without error."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        creds = json.dumps({"access_token": "token-empty", "refresh_token": "ref-empty", "expires_at": int(time.time()) + 3600})
        conn = GmailConnectionModel(
            user_id=901,
            email_address="alice.empty@gmail.com",
            encrypted_credentials=encrypt_secret(creds),
            status="connected",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(conn)
        db.commit()

        def mock_empty_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"messages": [], "resultSizeEstimate": 0})

        mock_http = httpx.Client(transport=httpx.MockTransport(mock_empty_handler))
        from app.Tools.registry import registry
        sync_tool = registry.get("email.sync")
        setattr(sync_tool, "http_client", mock_http)

        res = engine.execute("email.sync", caller_context={"user_id": 901})
        assert res["status"] == "success"
        assert res["synced_count"] == 0
        assert res["duplicate_count"] == 0
        assert res["total_fetched"] == 0
    finally:
        db.close()


def test_provider_failure_does_not_become_empty_inbox():
    """Verify provider 500 error raises an error and does NOT report empty inbox."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        creds = json.dumps({"access_token": "token-fail", "refresh_token": "ref-fail", "expires_at": int(time.time()) + 3600})
        conn = GmailConnectionModel(
            user_id=901,
            email_address="alice.fail@gmail.com",
            encrypted_credentials=encrypt_secret(creds),
            status="connected",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(conn)
        db.commit()

        def mock_error_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, json={"error": {"code": 500, "message": "Backend Error"}})

        mock_http = httpx.Client(transport=httpx.MockTransport(mock_error_handler))
        from app.Tools.registry import registry
        sync_tool = registry.get("email.sync")
        setattr(sync_tool, "http_client", mock_http)

        # Must raise ValueError, NOT return empty sync
        with pytest.raises(ValueError, match="Gmail provider error: HTTP 500"):
            engine.execute("email.sync", caller_context={"user_id": 901})
    finally:
        db.close()


def test_automatic_token_refresh():
    """Verify expired access token is refreshed automatically using refresh token."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        # Token expired 100 seconds ago
        creds = json.dumps({"access_token": "expired-access-token", "refresh_token": "valid-refresh-token", "expires_at": int(time.time()) - 100})
        conn = GmailConnectionModel(
            user_id=901,
            email_address="alice.refresh@gmail.com",
            encrypted_credentials=encrypt_secret(creds),
            status="connected",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(conn)
        db.commit()

        def mock_refresh_handler(request: httpx.Request) -> httpx.Response:
            if "oauth2.googleapis.com/token" in str(request.url):
                return httpx.Response(
                    200,
                    json={
                        "access_token": "freshly-refreshed-token-2026",
                        "expires_in": 3600,
                        "token_type": "Bearer",
                    },
                )
            return httpx.Response(404)

        mock_http = httpx.Client(transport=httpx.MockTransport(mock_refresh_handler))
        new_token = get_valid_access_token(user_id=901, db=db, http_client=mock_http)

        assert new_token == "freshly-refreshed-token-2026"

        # Verify DB connection has updated credentials
        db.refresh(conn)
        decrypted = json.loads(decrypt_secret(conn.encrypted_credentials))
        assert decrypted["access_token"] == "freshly-refreshed-token-2026"
        assert decrypted["expires_at"] > int(time.time())
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 6. SPF, DKIM, DMARC Sender Verification Tests
# ---------------------------------------------------------------------------

def test_spf_dkim_dmarc_parsing():
    """Verify parsing of real-world Authentication-Results header variations."""
    # 1. Full Pass (Standard Google/Gmail header format)
    header_pass = (
        "mx.google.com; "
        "dkim=pass header.i=@github.com header.s=s20150108 header.b=AbC1234; "
        "spf=pass (google.com: domain of support@github.com designates 192.30.252.206 as permitted sender) smtp.mailfrom=support@github.com; "
        "dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=github.com"
    )
    spf_st, _ = parse_spf(header_pass)
    dkim_st, _ = parse_dkim(header_pass)
    dmarc_st, _ = parse_dmarc(header_pass)

    assert spf_st == "pass"
    assert dkim_st == "pass"
    assert dmarc_st == "pass"

    # Test via ToolEngine
    res = engine.execute("email.verify_sender", raw_auth_results=header_pass)
    assert res["spf"]["status"] == "pass"
    assert res["dkim"]["status"] == "pass"
    assert res["dmarc"]["status"] == "pass"
    assert res["overall_status"] == "pass"
    assert "disclaimer" in res
    assert "does not guarantee" in res["disclaimer"]

    # 2. Spoofed / Failed Authentication
    header_fail = (
        "mx.google.com; "
        "dkim=fail (test key) header.i=@attacker.com; "
        "spf=fail (google.com: domain of bad@attacker.com does not designate 1.2.3.4 as permitted sender); "
        "dmarc=fail (p=REJECT) header.from=attacker.com"
    )
    spf_st2, _ = parse_spf(header_fail)
    dkim_st2, _ = parse_dkim(header_fail)
    dmarc_st2, _ = parse_dmarc(header_fail)

    assert spf_st2 == "fail"
    assert dkim_st2 == "fail"
    assert dmarc_st2 == "fail"

    res_fail = engine.execute("email.verify_sender", raw_auth_results=header_fail)
    assert res_fail["overall_status"] == "fail"

    # 3. Softfail / Neutral / None variations
    header_neutral = "mx.google.com; spf=softfail; dkim=none; dmarc=none"
    res_neut = engine.execute("email.verify_sender", raw_auth_results=header_neutral)
    assert res_neut["spf"]["status"] == "fail"  # softfail maps to fail
    assert res_neut["dkim"]["status"] == "unavailable"
    assert res_neut["dmarc"]["status"] == "unavailable"


def test_missing_authentication_headers():
    """Verify missing Authentication-Results header yields unavailable states without inventing results."""
    res = engine.execute("email.verify_sender", raw_auth_results="")
    assert res["spf"]["status"] == "unavailable"
    assert res["dkim"]["status"] == "unavailable"
    assert res["dmarc"]["status"] == "unavailable"
    assert res["overall_status"] == "unverified"


def test_verify_sender_persists_in_database():
    """Verify email.verify_sender records verification results in database with user isolation."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        auth_hdr = "mx.google.com; spf=pass; dkim=pass; dmarc=pass"
        email_record = EmailModel(
            user_id=901,
            gmail_message_id="gmail_msg_verify_test",
            gmail_thread_id="th_verify_test",
            sender="service@paypal.com",
            sender_domain="paypal.com",
            recipients=json.dumps(["alice@jarvis.test"]),
            subject="Account Update",
            body_text="Your account is active.",
            received_at=now_iso,
            attachment_metadata="[]",
            gmail_metadata=json.dumps({"authentication_results": auth_hdr}),
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(email_record)
        db.commit()
        db.refresh(email_record)

        # Run verification by email_id
        res = engine.execute(
            "email.verify_sender",
            caller_context={"user_id": 901},
            email_id=email_record.id,
        )
        assert res["email_id"] == email_record.id
        assert res["spf"]["status"] == "pass"
        assert res["overall_status"] == "pass"

        # Check DB record
        ver_record = db.execute(
            select(EmailSenderVerificationModel).where(
                EmailSenderVerificationModel.email_id == email_record.id,
                EmailSenderVerificationModel.user_id == 901,
            )
        ).scalar_one_or_none()
        assert ver_record is not None
        assert ver_record.spf_status == "pass"
        assert ver_record.dkim_status == "pass"
        assert ver_record.dmarc_status == "pass"

        # User 902 cannot verify User 901's email
        with pytest.raises(ValueError, match="Email not found"):
            engine.execute(
                "email.verify_sender",
                caller_context={"user_id": 902},
                email_id=email_record.id,
            )
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 7. Credential Leakage Prevention Tests
# ---------------------------------------------------------------------------

def test_credential_leakage_prevention():
    """Verify that credentials, tokens, and client secrets are never leaked."""
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        secret_access = "secret-access-token-12345"
        secret_refresh = "secret-refresh-token-67890"
        creds = json.dumps({"access_token": secret_access, "refresh_token": secret_refresh, "expires_at": int(time.time()) + 3600})
        conn = GmailConnectionModel(
            user_id=901,
            email_address="alice.secure@gmail.com",
            encrypted_credentials=encrypt_secret(creds),
            status="connected",
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(conn)
        db.commit()

        status_res = get_connection_status(user_id=901, db=db)
        status_str = json.dumps(status_res)
        assert secret_access not in status_str
        assert secret_refresh not in status_str
        assert "mock-google-client-secret" not in status_str

        # Disconnect output
        disconnect_res = disconnect_gmail(user_id=901, db=db)
        disc_str = json.dumps(disconnect_res)
        assert secret_access not in disc_str
        assert secret_refresh not in disc_str
    finally:
        db.close()
