"""
Jarvis AIOS — Email Sync Tool
-----------------------------
Tool identifier: "email.sync"
Performs authenticated synchronization of user emails from Gmail:
1. Resolves caller authenticated user context.
2. Retrieves user's Gmail connection and ensures fresh access token.
3. Queries Gmail REST API messages.
4. Parses From, To, Subject, Date, Message-ID, Authentication-Results, body text/HTML, and attachment metadata.
5. Deduplicates against existing messages in DB.
6. Persists new messages and updates connection sync metadata.
7. Returns structured sync telemetry counts.
"""

import base64
import email.utils
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Data.database import SessionLocal
from app.Tools.email.gmail_oauth import get_valid_access_token
from app.Tools.email.models import EmailModel, GmailConnectionModel
from app.Tools.metadata import PermissionLevel, ToolMetadata
from app.Tools.tool import Tool

logger = logging.getLogger(__name__)

GMAIL_MESSAGES_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"


def _extract_email_address(raw_header: str) -> str:
    """Extract clean email address from a header like 'John Doe <john@example.com>'."""
    if not raw_header:
        return ""
    _, addr = email.utils.parseaddr(raw_header)
    if addr:
        return addr.lower().strip()
    # Fallback to regex if parseaddr failed
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_header)
    return match.group(0).lower().strip() if match else raw_header.strip()


def _extract_domain(email_addr: str) -> str:
    """Extract domain from an email address."""
    clean = _extract_email_address(email_addr)
    if "@" in clean:
        return clean.split("@", 1)[1].lower().strip()
    return "unknown"


def _decode_base64url(data: str) -> str:
    """Safely decode base64url encoded string from Gmail payload."""
    if not data:
        return ""
    try:
        # Add padding if missing
        padded = data + "=" * (-len(data) % 4)
        raw_bytes = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return raw_bytes.decode("utf-8", errors="replace")
    except Exception as exc:
        logger.debug("Failed to decode base64url payload: %s", exc)
        return ""


def _parse_message_payload(payload: Dict[str, Any]) -> Tuple[str, Optional[str], List[Dict[str, Any]]]:
    """Recursively traverse message payload to extract body_text, body_html, and attachments.

    Returns:
        (body_text, body_html, list_of_attachments)
    """
    body_text_parts: List[str] = []
    body_html_parts: List[str] = []
    attachments: List[Dict[str, Any]] = []

    def _walk(part: Dict[str, Any]):
        mime_type = part.get("mimeType", "")
        filename = part.get("filename", "")
        body = part.get("body", {})
        data = body.get("data", "")
        attachment_id = body.get("attachmentId")

        # Check for attachment
        if filename or attachment_id:
            attachments.append({
                "filename": filename or "attachment",
                "mimeType": mime_type,
                "size_bytes": body.get("size", 0),
                "attachment_id": attachment_id,
            })

        # Check for text or HTML content
        if data:
            decoded = _decode_base64url(data)
            if mime_type == "text/plain":
                body_text_parts.append(decoded)
            elif mime_type == "text/html":
                body_html_parts.append(decoded)

        # Recurse into sub-parts
        for sub_part in part.get("parts", []):
            _walk(sub_part)

    _walk(payload)

    body_text = "\n".join(body_text_parts).strip()
    body_html = "\n".join(body_html_parts).strip() if body_html_parts else None

    return body_text, body_html, attachments


class EmailSyncTool(Tool):
    """Tool for synchronizing messages from connected Gmail accounts."""

    def __init__(self, http_client: Optional[httpx.Client] = None) -> None:
        self.http_client = http_client
        metadata = ToolMetadata(
            name="email.sync",
            display_name="Email Sync",
            description=(
                "Synchronizes emails from the authenticated user's connected Gmail account. "
                "Parses headers, text/html content, sender details, and attachment metadata."
            ),
            category="Email",
            permission_level=PermissionLevel.USER,
            parameter_schema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of messages to fetch in this batch (1-100, default: 20).",
                        "default": 20,
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional Gmail search query filter (e.g. 'is:unread', 'newer_than:7d').",
                        "default": "",
                    },
                },
                "required": [],
            },
            tags=["email", "gmail", "sync", "inbox"],
        )
        super().__init__(metadata=metadata)

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute synchronous email synchronization."""
        # 1. Resolve caller context / user isolation
        caller_context = kwargs.get("caller_context") or {}
        user_id = caller_context.get("user_id")
        if not user_id and "user" in caller_context:
            user_obj = caller_context["user"]
            user_id = getattr(user_obj, "id", None) or (user_obj.get("id") if isinstance(user_obj, dict) else None)

        # Also support direct argument for testing/direct calls
        if not user_id:
            user_id = kwargs.get("user_id")

        if not user_id:
            raise ValueError("Authentication required: no authenticated user_id provided in execution context.")

        max_results = min(max(int(kwargs.get("max_results", 20)), 1), 100)
        query = kwargs.get("query", "").strip()

        db: Session = SessionLocal()
        client = self.http_client or httpx.Client(timeout=25.0)

        try:
            # 2. Verify active connection and get fresh token
            connection = db.execute(
                select(GmailConnectionModel).where(
                    GmailConnectionModel.user_id == user_id,
                    GmailConnectionModel.status == "connected",
                )
            ).scalar_one_or_none()

            if not connection:
                raise ValueError("Gmail account is not connected for this user. Please connect via OAuth.")

            access_token = get_valid_access_token(user_id, db, http_client=client)

            # 3. Query list of messages from Gmail API
            params: Dict[str, Any] = {"maxResults": max_results}
            if query:
                params["q"] = query

            headers = {"Authorization": f"Bearer {access_token}"}
            resp = client.get(GMAIL_MESSAGES_URL, params=params, headers=headers)

            if resp.status_code != 200:
                logger.error("Gmail message list query failed: HTTP %s - %s", resp.status_code, resp.text[:200])
                raise ValueError(f"Gmail provider error: HTTP {resp.status_code}")

            data = resp.json()
            message_items = data.get("messages", [])

            total_fetched = len(message_items)
            synced_count = 0
            duplicate_count = 0

            # 4. Fetch details for each message and persist
            for item in message_items:
                msg_id = item.get("id")
                thread_id = item.get("threadId") or msg_id

                if not msg_id:
                    continue

                # Check deduplication
                existing = db.execute(
                    select(EmailModel.id).where(
                        EmailModel.user_id == user_id,
                        EmailModel.gmail_message_id == msg_id,
                    )
                ).scalar_one_or_none()

                if existing:
                    duplicate_count += 1
                    continue

                # Fetch full message
                detail_resp = client.get(
                    f"{GMAIL_MESSAGES_URL}/{msg_id}",
                    params={"format": "full"},
                    headers=headers,
                )
                if detail_resp.status_code != 200:
                    logger.warning("Failed to fetch detail for Gmail message %s: HTTP %s", msg_id, detail_resp.status_code)
                    continue

                msg_data = detail_resp.json()
                payload = msg_data.get("payload", {})
                headers_list = payload.get("headers", [])

                # Header dictionary lookup (case-insensitive)
                headers_dict: Dict[str, str] = {
                    h.get("name", "").lower(): h.get("value", "") for h in headers_list if h.get("name")
                }

                from_header = headers_dict.get("from", "")
                to_header = headers_dict.get("to", "")
                subject = headers_dict.get("subject", "")
                date_header = headers_dict.get("date", "")
                auth_results = headers_dict.get("authentication-results", "")

                sender = _extract_email_address(from_header)
                sender_domain = _extract_domain(sender)

                # Parse recipients list
                recipients: List[str] = []
                if to_header:
                    for addr_str in to_header.split(","):
                        parsed_addr = _extract_email_address(addr_str)
                        if parsed_addr:
                            recipients.append(parsed_addr)

                # Body & attachment extraction
                body_text, body_html, attachments = _parse_message_payload(payload)
                snippet = msg_data.get("snippet", "")

                # Normalize received_at timestamp
                received_at = date_header
                if not received_at and "internalDate" in msg_data:
                    try:
                        ms = int(msg_data["internalDate"])
                        received_at = datetime.fromtimestamp(ms / 1000.0, timezone.utc).isoformat()
                    except Exception:
                        received_at = datetime.now(timezone.utc).isoformat()

                now_iso = datetime.now(timezone.utc).isoformat()

                # Preserve useful Gmail metadata for verification and auditing
                gmail_metadata = {
                    "thread_id": thread_id,
                    "label_ids": msg_data.get("labelIds", []),
                    "history_id": msg_data.get("historyId"),
                    "internal_date": msg_data.get("internalDate"),
                    "authentication_results": auth_results,
                    "raw_headers": {
                        "from": from_header,
                        "to": to_header,
                        "subject": subject,
                        "date": date_header,
                        "message_id": headers_dict.get("message-id", ""),
                    },
                }

                email_record = EmailModel(
                    user_id=user_id,
                    gmail_message_id=msg_id,
                    gmail_thread_id=thread_id,
                    sender=sender or from_header,
                    sender_domain=sender_domain,
                    recipients=json.dumps(recipients),
                    subject=subject,
                    body_text=body_text,
                    body_html=body_html,
                    snippet=snippet,
                    received_at=received_at or now_iso,
                    attachment_metadata=json.dumps(attachments),
                    gmail_metadata=json.dumps(gmail_metadata),
                    created_at=now_iso,
                    updated_at=now_iso,
                )
                db.add(email_record)
                synced_count += 1

            # 5. Update connection sync timestamp
            now_iso = datetime.now(timezone.utc).isoformat()
            connection.last_sync_at = now_iso
            connection.updated_at = now_iso
            db.commit()

            logger.info(
                "Email sync completed for user %s: fetched=%s, new=%s, duplicates=%s",
                user_id,
                total_fetched,
                synced_count,
                duplicate_count,
            )

            return {
                "status": "success",
                "synced_count": synced_count,
                "duplicate_count": duplicate_count,
                "total_fetched": total_fetched,
                "last_sync_at": now_iso,
                "user_id": user_id,
            }
        finally:
            if not self.http_client:
                client.close()
            db.close()
