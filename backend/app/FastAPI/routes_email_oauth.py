"""
Jarvis AIOS — Google OAuth & Gmail Connection Router
----------------------------------------------------
Provides secure OAuth 2.0 endpoints for Google/Gmail connection management:
- GET  /api/v1/auth/google/url        — Generate CSRF-protected authorization URL
- GET  /api/v1/auth/google/callback   — Exchange code for credentials & persist
- GET  /api/v1/auth/google/status     — Check connection status for authenticated user
- POST /api/v1/auth/google/disconnect — Revoke and disconnect account

Enforces user isolation and never leaks tokens or client secrets.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.Auth.dependencies import get_current_user
from app.Auth.models import User
from app.Data.database import get_db
from app.Tools.email.gmail_oauth import (
    disconnect_gmail,
    exchange_code_for_tokens,
    get_authorization_url,
    get_connection_status,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth/google", tags=["Google OAuth"])


@router.get("/url", response_model=Dict[str, str])
def get_google_auth_url(
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """Generate a Google OAuth 2.0 authorization URL for the authenticated user."""
    try:
        data = get_authorization_url(user_id=current_user.id)
        auth_url = data.get("authorization_url") or data.get("url", "")
        return {
            "authorization_url": auth_url,
            "url": auth_url,
            "state": data.get("state", ""),
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "oauth_config_error", "message": str(exc)}},
        ) from exc


@router.get("/callback")
def google_auth_callback(
    code: str = Query(..., description="Google authorization code"),
    state: str = Query(..., description="Anti-CSRF state token"),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """OAuth 2.0 callback endpoint handling authorization code exchange."""
    try:
        result = exchange_code_for_tokens(code=code, state=state, db=db)
        email_addr = result.get("email_address", "")
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Gmail Connected - Jarvis AIOS</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #f3f4f6; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
        .card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 32px; max-width: 420px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }}
        h2 {{ color: #10b981; margin-top: 0; }}
        p {{ color: #9ca3af; line-height: 1.5; }}
        .badge {{ background: rgba(16,185,129,0.15); color: #34d399; padding: 4px 10px; border-radius: 6px; font-family: monospace; font-size: 13px; display: inline-block; margin-top: 8px; }}
        .btn {{ display: inline-block; margin-top: 20px; background: #2563eb; color: #fff; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 13px; }}
        .btn:hover {{ background: #1d4ed8; }}
    </style>
    <script>
        setTimeout(function() {{
            var target = (window.location.port === "8000") ? "http://localhost:5174/email" : "/email";
            window.location.href = target;
        }}, 1500);
    </script>
</head>
<body>
    <div class="card">
        <h2>✓ Gmail Connected Successfully</h2>
        <p>Your Gmail account has been securely linked to Jarvis AIOS.</p>
        <div class="badge">{email_addr}</div>
        <p style="margin-top: 20px; font-size: 13px;">Redirecting back to your Mail page in a moment...</p>
        <a class="btn" href="http://localhost:5174/email">Return to Mail</a>
    </div>
</body>
</html>"""
        return HTMLResponse(content=html_content, status_code=200)
    except ValueError as exc:
        logger.warning("Google OAuth exchange failed: %s", exc)
        err_msg = str(exc)
        html_error = f"""<!DOCTYPE html>
<html>
<head>
    <title>Connection Failed - Jarvis AIOS</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #f3f4f6; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
        .card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 32px; max-width: 420px; text-align: center; }}
        h2 {{ color: #ef4444; margin-top: 0; }}
        p {{ color: #9ca3af; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>✕ Connection Failed</h2>
        <p>{err_msg}</p>
        <p style="margin-top: 20px; font-size: 13px;">Please return to Jarvis and try again.</p>
    </div>
</body>
</html>"""
        return HTMLResponse(content=html_error, status_code=400)


@router.get("/status", response_model=Dict[str, Any])
def get_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve current user's Gmail connection status."""
    return get_connection_status(user_id=current_user.id, db=db)


@router.post("/disconnect", response_model=Dict[str, Any])
def disconnect_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Disconnect and revoke Gmail connection for the authenticated user."""
    return disconnect_gmail(user_id=current_user.id, db=db)
