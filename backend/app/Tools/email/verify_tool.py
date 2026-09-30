"""
Jarvis AIOS — Email Sender Verification Tool
--------------------------------------------
Tool identifier: "email.verify_sender"
Parses actual Gmail Authentication-Results headers for SPF, DKIM, and DMARC verification:
1. Resolves caller authenticated user context.
2. Extracts Authentication-Results from stored message metadata or direct parameter.
3. Parses SPF, DKIM, and DMARC results into explicit normalized states:
   - "pass"
   - "fail"
   - "unavailable"
   - "unknown"
4. Persists verification records in email_sender_verifications table.
5. Returns structured verification evidence.
Strictly disclaims that authentication checks alone do not prove trustworthiness.
"""

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Data.database import SessionLocal
from app.Tools.email.models import EmailModel, EmailSenderVerificationModel
from app.Tools.metadata import PermissionLevel, ToolMetadata
from app.Tools.tool import Tool

logger = logging.getLogger(__name__)

DISCLAIMER_NOTE = (
    "Sender verification reflects SPF, DKIM, and DMARC headers parsed from provider authentication evidence only. "
    "A passing result indicates protocol compliance and does not guarantee that the sender or message content is trustworthy."
)


def parse_spf(raw_header: str) -> Tuple[str, Optional[str]]:
    """Parse SPF status and details from Authentication-Results header.

    Returns:
        (status, details) where status is in {"pass", "fail", "unavailable", "unknown"}
    """
    if not raw_header:
        return "unavailable", "No Authentication-Results header present."

    match = re.search(r"\bspf=([a-zA-Z]+)(?:\s*\(([^)]+)\))?", raw_header, re.IGNORECASE)
    if not match:
        return "unavailable", "No SPF result found in Authentication-Results header."

    val = match.group(1).lower()
    details = match.group(2) or match.group(0)

    if val == "pass":
        return "pass", details
    if val in ("fail", "softfail", "permerror", "temperror"):
        return "fail", f"SPF {val}: {details}"
    if val in ("none", "neutral"):
        return "unavailable", f"SPF result: {val}"
    return "unknown", f"Unrecognized SPF result: {val}"


def parse_dkim(raw_header: str) -> Tuple[str, Optional[str]]:
    """Parse DKIM status and details from Authentication-Results header.

    Returns:
        (status, details) where status is in {"pass", "fail", "unavailable", "unknown"}
    """
    if not raw_header:
        return "unavailable", "No Authentication-Results header present."

    match = re.search(r"\bdkim=([a-zA-Z]+)(?:\s*\(([^)]+)\))?", raw_header, re.IGNORECASE)
    if not match:
        return "unavailable", "No DKIM result found in Authentication-Results header."

    val = match.group(1).lower()
    details = match.group(2) or match.group(0)

    if val == "pass":
        return "pass", details
    if val in ("fail", "permerror", "temperror"):
        return "fail", f"DKIM {val}: {details}"
    if val in ("none", "neutral"):
        return "unavailable", f"DKIM result: {val}"
    return "unknown", f"Unrecognized DKIM result: {val}"


def parse_dmarc(raw_header: str) -> Tuple[str, Optional[str]]:
    """Parse DMARC status and details from Authentication-Results header.

    Returns:
        (status, details) where status is in {"pass", "fail", "unavailable", "unknown"}
    """
    if not raw_header:
        return "unavailable", "No Authentication-Results header present."

    match = re.search(r"\bdmarc=([a-zA-Z]+)(?:\s*\(([^)]+)\))?", raw_header, re.IGNORECASE)
    if not match:
        return "unavailable", "No DMARC result found in Authentication-Results header."

    val = match.group(1).lower()
    details = match.group(2) or match.group(0)

    if val == "pass":
        return "pass", details
    if val in ("fail", "temperror", "permerror"):
        return "fail", f"DMARC {val}: {details}"
    if val == "none":
        return "unavailable", "DMARC policy evaluation none."
    return "unknown", f"Unrecognized DMARC result: {val}"


def calculate_overall_status(spf_status: str, dkim_status: str, dmarc_status: str) -> str:
    """Calculate normalized summary verification status."""
    if spf_status == "fail" or dkim_status == "fail" or dmarc_status == "fail":
        return "fail"
    if dmarc_status == "pass" or (spf_status == "pass" and dkim_status == "pass"):
        return "pass"
    if spf_status == "pass" or dkim_status == "pass":
        return "partial"
    return "unverified"


class EmailVerifySenderTool(Tool):
    """Tool for verifying email sender authenticity (SPF, DKIM, DMARC)."""

    def __init__(self) -> None:
        metadata = ToolMetadata(
            name="email.verify_sender",
            display_name="Email Sender Verification",
            description=(
                "Verifies sender authentication by inspecting actual SPF, DKIM, and DMARC results "
                "from Gmail Authentication-Results headers. Returns explicit states: pass, fail, unavailable, unknown."
            ),
            category="Email",
            permission_level=PermissionLevel.USER,
            parameter_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "integer",
                        "description": "Internal database email ID to verify.",
                    },
                    "gmail_message_id": {
                        "type": "string",
                        "description": "Gmail message ID to verify.",
                    },
                    "raw_auth_results": {
                        "type": "string",
                        "description": "Direct raw Authentication-Results header string for ad-hoc evaluation.",
                    },
                },
                "required": [],
            },
            tags=["email", "verification", "spf", "dkim", "dmarc", "security"],
        )
        super().__init__(metadata=metadata)

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute sender verification."""
        caller_context = kwargs.get("caller_context") or {}
        user_id = caller_context.get("user_id")
        if not user_id and "user" in caller_context:
            user_obj = caller_context["user"]
            user_id = getattr(user_obj, "id", None) or (user_obj.get("id") if isinstance(user_obj, dict) else None)

        if not user_id:
            user_id = kwargs.get("user_id")

        email_id = kwargs.get("email_id")
        gmail_msg_id = kwargs.get("gmail_message_id")
        raw_header = kwargs.get("raw_auth_results")

        # 1. If raw_header provided directly (e.g. testing or ad-hoc check)
        if raw_header is not None:
            spf_status, spf_details = parse_spf(raw_header)
            dkim_status, dkim_details = parse_dkim(raw_header)
            dmarc_status, dmarc_details = parse_dmarc(raw_header)
            overall = calculate_overall_status(spf_status, dkim_status, dmarc_status)
            now_iso = datetime.now(timezone.utc).isoformat()

            return {
                "spf": {"status": spf_status, "details": spf_details},
                "dkim": {"status": dkim_status, "details": dkim_details},
                "dmarc": {"status": dmarc_status, "details": dmarc_details},
                "overall_status": overall,
                "raw_auth_results": raw_header,
                "verified_at": now_iso,
                "disclaimer": DISCLAIMER_NOTE,
            }

        # 2. Database email lookup
        if not user_id:
            raise ValueError("Authentication required: no authenticated user_id provided in execution context.")

        if not email_id and not gmail_msg_id:
            raise ValueError("Either email_id, gmail_message_id, or raw_auth_results must be provided.")

        db: Session = SessionLocal()
        try:
            # Query email with user isolation
            stmt = select(EmailModel).where(EmailModel.user_id == user_id)
            if email_id:
                stmt = stmt.where(EmailModel.id == email_id)
            elif gmail_msg_id:
                stmt = stmt.where(EmailModel.gmail_message_id == gmail_msg_id)

            email_record = db.execute(stmt).scalar_one_or_none()
            if not email_record:
                raise ValueError("Email not found for the authenticated user.")

            # Extract auth header from stored gmail_metadata
            auth_header = ""
            try:
                meta = json.loads(email_record.gmail_metadata)
                auth_header = meta.get("authentication_results") or ""
            except Exception:
                pass

            spf_status, spf_details = parse_spf(auth_header)
            dkim_status, dkim_details = parse_dkim(auth_header)
            dmarc_status, dmarc_details = parse_dmarc(auth_header)
            overall = calculate_overall_status(spf_status, dkim_status, dmarc_status)
            now_iso = datetime.now(timezone.utc).isoformat()

            # Persist or update verification record
            existing_ver = db.execute(
                select(EmailSenderVerificationModel).where(
                    EmailSenderVerificationModel.email_id == email_record.id,
                    EmailSenderVerificationModel.user_id == user_id,
                )
            ).scalar_one_or_none()

            if existing_ver:
                existing_ver.spf_status = spf_status
                existing_ver.spf_details = spf_details
                existing_ver.dkim_status = dkim_status
                existing_ver.dkim_details = dkim_details
                existing_ver.dmarc_status = dmarc_status
                existing_ver.dmarc_details = dmarc_details
                existing_ver.raw_auth_results = auth_header
                existing_ver.verification_status = overall
                existing_ver.verified_at = now_iso
            else:
                ver_record = EmailSenderVerificationModel(
                    user_id=user_id,
                    email_id=email_record.id,
                    spf_status=spf_status,
                    spf_details=spf_details,
                    dkim_status=dkim_status,
                    dkim_details=dkim_details,
                    dmarc_status=dmarc_status,
                    dmarc_details=dmarc_details,
                    raw_auth_results=auth_header,
                    verification_status=overall,
                    verified_at=now_iso,
                )
                db.add(ver_record)

            db.commit()

            return {
                "email_id": email_record.id,
                "gmail_message_id": email_record.gmail_message_id,
                "sender": email_record.sender,
                "sender_domain": email_record.sender_domain,
                "spf": {"status": spf_status, "details": spf_details},
                "dkim": {"status": dkim_status, "details": dkim_details},
                "dmarc": {"status": dmarc_status, "details": dmarc_details},
                "overall_status": overall,
                "raw_auth_results": auth_header,
                "verified_at": now_iso,
                "disclaimer": DISCLAIMER_NOTE,
            }
        finally:
            db.close()
