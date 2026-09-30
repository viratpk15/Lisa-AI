"""
Jarvis AIOS — Gmail OAuth 2.0 Client & Connection Manager
---------------------------------------------------------
Implements Google OAuth 2.0 authorization-code flow with Gmail read-only scope ONLY.
Enforces:
- Scope: https://www.googleapis.com/auth/gmail.readonly ONLY
- User-isolated credentials encrypted via existing Secret Vault
- Secure HMAC-signed state generation and validation (anti-CSRF)
- Code exchange, token storage, and automatic access-token refresh
- Strict masking: never logs or returns credentials, secrets, or tokens
"""

import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
import os
from sqlalchemy.orm import Session

from app.Config import settings
from app.Deployments.vault import decrypt_secret, encrypt_secret
from app.Tools.email.models import GmailConnectionModel

logger = logging.getLogger(__name__)

# Enforce read-only scope strictly as mandated by Engineering Constitution
GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
GMAIL_PROFILE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

STATE_EXPIRY_SECONDS = 900  # 15 minutes


def _get_client_id() -> Optional[str]:
    return os.getenv("GOOGLE_CLIENT_ID") or settings.GOOGLE_CLIENT_ID


def _get_client_secret() -> Optional[str]:
    return os.getenv("GOOGLE_CLIENT_SECRET") or settings.GOOGLE_CLIENT_SECRET


def _get_redirect_uri() -> str:
    return os.getenv("GOOGLE_REDIRECT_URI") or settings.GOOGLE_REDIRECT_URI


def _get_signing_key() -> bytes:
    """Derive secret key for signing state tokens."""
    key = os.getenv("JWT_SECRET_KEY") or settings.JWT_SECRET_KEY or "JARVIS_EMAIL_OAUTH_SIGNING_KEY_2026"
    return key.encode("utf-8")


def generate_auth_state(user_id: int) -> str:
    """Generate tamper-proof, timestamped HMAC-signed state token containing user_id."""
    timestamp = int(time.time())
    payload = f"{user_id}:{timestamp}"
    signature = hmac.new(_get_signing_key(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    raw_token = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(raw_token.encode("utf-8")).decode("utf-8").rstrip("=")


def validate_auth_state(state: str, expected_user_id: Optional[int] = None) -> int:
    """Validate state token signature, expiration, and user_id.

    Returns:
        Validated user_id.

    Raises:
        ValueError: If state is invalid, tampered, expired, or user mismatch.
    """
    if not state:
        raise ValueError("OAuth state parameter is missing.")

    try:
        padded = state + "=" * (-len(state) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
        parts = decoded.split(":")
        if len(parts) != 3:
            raise ValueError("Malformed OAuth state format.")

        user_id_str, timestamp_str, sig = parts
        user_id = int(user_id_str)
        timestamp = int(timestamp_str)
    except Exception as exc:
        raise ValueError("Invalid OAuth state token structure.") from exc

    # Check expiration
    now = int(time.time())
    if now - timestamp > STATE_EXPIRY_SECONDS:
        raise ValueError("OAuth state token has expired.")
    if timestamp > now + 300:  # Clock skew tolerance
        raise ValueError("OAuth state timestamp is invalid.")

    # Check HMAC signature
    expected_payload = f"{user_id}:{timestamp}"
    expected_sig = hmac.new(_get_signing_key(), expected_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("OAuth state signature mismatch. Possible CSRF attempt.")

    # Match user if specified
    if expected_user_id is not None and user_id != expected_user_id:
        raise ValueError("OAuth state user_id mismatch with current user.")

    return user_id


def get_authorization_url(user_id: int) -> Dict[str, str]:
    """Generate Google OAuth 2.0 authorization URL with Gmail read-only scope.

    Args:
        user_id: Authenticated Jarvis user ID.

    Returns:
        Dict containing authorization_url and state token.
    """
    client_id = _get_client_id()
    if not client_id:
        raise ValueError("Google OAuth is not configured. Missing GOOGLE_CLIENT_ID in environment.")

    state = generate_auth_state(user_id)
    params = {
        "client_id": client_id,
        "redirect_uri": _get_redirect_uri(),
        "response_type": "code",
        "scope": GMAIL_READONLY_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return {"authorization_url": url, "url": url, "state": state}


def exchange_code_for_tokens(
    code: str,
    state: str,
    db: Session,
    expected_user_id: Optional[int] = None,
    http_client: Optional[httpx.Client] = None,
) -> Dict[str, Any]:
    """Exchange authorization code for access and refresh tokens.

    Stores tokens securely encrypted at rest. Never returns raw credentials.
    """
    client_id = _get_client_id()
    client_secret = _get_client_secret()
    if not client_id or not client_secret:
        raise ValueError("Google OAuth configuration is incomplete (client ID or secret missing).")

    user_id = validate_auth_state(state, expected_user_id)

    client = http_client or httpx.Client(timeout=15.0)
    try:
        # 1. Exchange code for tokens
        token_resp = client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": _get_redirect_uri(),
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            logger.error("Token exchange failed with status %s", token_resp.status_code)
            raise ValueError(f"Token exchange failed: HTTP {token_resp.status_code}")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)

        if not access_token:
            raise ValueError("Token response did not include an access_token.")

        # 2. Fetch associated Gmail user email
        profile_resp = client.get(
            GMAIL_PROFILE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        email_address = None
        if profile_resp.status_code == 200:
            email_address = profile_resp.json().get("emailAddress")
        else:
            # Fallback to UserInfo endpoint
            userinfo_resp = client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if userinfo_resp.status_code == 200:
                email_address = userinfo_resp.json().get("email")

        if not email_address:
            raise ValueError("Could not determine Gmail address for authenticated user.")

        now_ts = int(time.time())
        expires_at = now_ts + int(expires_in)

        # 3. Handle existing connection to preserve refresh token if Google didn't reissue one
        existing = db.execute(
            select(GmailConnectionModel).where(
                GmailConnectionModel.user_id == user_id,
                GmailConnectionModel.email_address == email_address,
            )
        ).scalar_one_or_none()

        if not refresh_token and existing:
            try:
                old_creds = json.loads(decrypt_secret(existing.encrypted_credentials))
                refresh_token = old_creds.get("refresh_token")
            except Exception:
                pass

        if not refresh_token:
            logger.warning("No refresh token received for user %s (%s)", user_id, email_address)

        # 4. Encrypt and persist credentials
        credentials_dict = {
            "access_token": access_token,
            "refresh_token": refresh_token or "",
            "expires_at": expires_at,
            "scope": token_data.get("scope", GMAIL_READONLY_SCOPE),
        }
        encrypted = encrypt_secret(json.dumps(credentials_dict))
        now_iso = datetime.now(timezone.utc).isoformat()

        if existing:
            existing.encrypted_credentials = encrypted
            existing.status = "connected"
            existing.updated_at = now_iso
            conn_record = existing
        else:
            conn_record = GmailConnectionModel(
                user_id=user_id,
                email_address=email_address,
                encrypted_credentials=encrypted,
                status="connected",
                created_at=now_iso,
                updated_at=now_iso,
            )
            db.add(conn_record)

        db.commit()
        db.refresh(conn_record)

        logger.info("Successfully connected Gmail for user %s (%s)", user_id, email_address)
        return {
            "status": "connected",
            "email_address": email_address,
            "user_id": user_id,
            "connected_at": now_iso,
        }
    finally:
        if not http_client:
            client.close()


def get_valid_access_token(
    user_id: int,
    db: Session,
    http_client: Optional[httpx.Client] = None,
) -> str:
    """Retrieve active access token for user, refreshing if expired.

    Raises:
        ValueError: If connection not found, revoked, or refresh fails.
    """
    connection = db.execute(
        select(GmailConnectionModel).where(
            GmailConnectionModel.user_id == user_id,
            GmailConnectionModel.status == "connected",
        )
    ).scalar_one_or_none()

    if not connection:
        raise ValueError("No active Gmail connection found for user. Please connect via OAuth.")

    try:
        raw_creds = json.loads(decrypt_secret(connection.encrypted_credentials))
    except Exception as exc:
        raise ValueError("Failed to decrypt stored Gmail credentials.") from exc

    access_token = raw_creds.get("access_token", "")
    refresh_token = raw_creds.get("refresh_token", "")
    expires_at = raw_creds.get("expires_at", 0)

    # Refresh if expired or expiring within 60 seconds
    now_ts = int(time.time())
    if now_ts >= expires_at - 60:
        if not refresh_token:
            connection.status = "expired"
            db.commit()
            raise ValueError("Gmail access token expired and no refresh token is stored. Re-authentication required.")

        client_id = _get_client_id()
        client_secret = _get_client_secret()
        if not client_id or not client_secret:
            raise ValueError("Google OAuth client credentials not configured for token refresh.")

        client = http_client or httpx.Client(timeout=15.0)
        try:
            refresh_resp = client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            if refresh_resp.status_code != 200:
                logger.error("Token refresh failed: HTTP %s", refresh_resp.status_code)
                connection.status = "expired"
                db.commit()
                raise ValueError(f"Failed to refresh Gmail token: HTTP {refresh_resp.status_code}")

            new_token_data = refresh_resp.json()
            access_token = new_token_data.get("access_token")
            new_expires_in = new_token_data.get("expires_in", 3600)
            raw_creds["access_token"] = access_token
            raw_creds["expires_at"] = now_ts + int(new_expires_in)

            # Some providers return a refreshed refresh_token
            if new_token_data.get("refresh_token"):
                raw_creds["refresh_token"] = new_token_data["refresh_token"]

            now_iso = datetime.now(timezone.utc).isoformat()
            connection.encrypted_credentials = encrypt_secret(json.dumps(raw_creds))
            connection.updated_at = now_iso
            db.commit()
            logger.info("Successfully refreshed Gmail access token for user %s", user_id)
        finally:
            if not http_client:
                client.close()

    return access_token


def get_connection_status(user_id: int, db: Session) -> Dict[str, Any]:
    """Retrieve connection status metadata without exposing any secrets or tokens."""
    connection = db.execute(
        select(GmailConnectionModel).where(GmailConnectionModel.user_id == user_id)
    ).scalar_one_or_none()

    if not connection:
        return {
            "connected": False,
            "status": "not_connected",
            "email_address": None,
            "last_sync_at": None,
        }

    return {
        "connected": connection.status == "connected",
        "status": connection.status,
        "email_address": connection.email_address,
        "created_at": connection.created_at,
        "last_sync_at": connection.last_sync_at,
    }


def disconnect_gmail(
    user_id: int,
    db: Session,
    http_client: Optional[httpx.Client] = None,
) -> Dict[str, Any]:
    """Revoke tokens and delete or mark connection as revoked."""
    connection = db.execute(
        select(GmailConnectionModel).where(GmailConnectionModel.user_id == user_id)
    ).scalar_one_or_none()

    if not connection:
        return {"status": "not_connected", "message": "No connection to disconnect."}

    # Attempt revocation at Google
    try:
        raw_creds = json.loads(decrypt_secret(connection.encrypted_credentials))
        token = raw_creds.get("refresh_token") or raw_creds.get("access_token")
        if token:
            client = http_client or httpx.Client(timeout=10.0)
            try:
                client.post(GOOGLE_REVOKE_URL, params={"token": token})
            finally:
                if not http_client:
                    client.close()
    except Exception as exc:
        logger.warning("Revocation request to Google endpoint failed: %s", exc)

    connection.status = "revoked"
    connection.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()

    return {"status": "revoked", "email_address": connection.email_address}
