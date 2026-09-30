"""
Jarvis AIOS — Email Intelligence REST API Router
-------------------------------------------------
Mounts at: /api/v1/email
Exposes production endpoints for:
- POST /sync                 — Sync Gmail inbox messages (delegates to email.sync)
- GET  /list                 — Query emails with intelligence analysis and verification metadata
- GET  /{id}                 — Single email detail with full analysis and sender verification
- POST /{id}/classify        — Trigger email classification (delegates to email.classify)
- POST /{id}/summarize       — Trigger email summarization (delegates to email.summarize)
- POST /{id}/extract-actions — Trigger action extraction (delegates to email.extract_actions)
- GET  /digest               — Aggregated intelligence digest (delegates to email.digest)

Security & Governance:
- All endpoints are JWT-protected (current_user).
- Enforces strict user isolation: all tool calls pass caller_context with user_id.
- Zero credential leakage: tokens, secrets, or internal keys are never exposed.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.Auth.dependencies import get_current_user
from app.Auth.models import User
from app.Data.database import get_db
from app.Tools.email.models import (
    EmailAnalysisModel,
    EmailModel,
    EmailSenderVerificationModel,
)
from app.Tools.engine import engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/email", tags=["Email Intelligence"])


# ---------------------------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------------------------


class EmailSyncRequest(BaseModel):
    max_results: int = Field(20, ge=1, le=100, description="Maximum messages to fetch")
    query: str = Field("", description="Optional search query filter")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


def _resolve_user_id(current_user: Any) -> int:
    """Safely extract user ID whether current_user is a User instance or dict from dependency override."""
    if isinstance(current_user, dict):
        uid = current_user.get("user_id") or current_user.get("id")
        if uid is not None:
            return int(uid)
    uid = getattr(current_user, "id", None)
    if uid is not None:
        return int(uid)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": "unauthorized", "message": "Invalid authentication credentials."}},
    )


@router.post(
    "/sync",
    summary="Synchronize Gmail Inbox",
    description="Synchronizes recent emails from the authenticated user's connected Gmail account.",
)
def sync_emails(
    payload: Optional[EmailSyncRequest] = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Execute authenticated email synchronization through ToolEngine."""
    user_id = _resolve_user_id(current_user)
    max_results = payload.max_results if payload else 20
    query = payload.query if payload else ""

    caller_context = {
        "user_id": user_id,
        "role": getattr(current_user, "role", "USER") if not isinstance(current_user, dict) else current_user.get("role", "USER"),
    }

    try:
        raw_result = engine.execute(
            "email.sync",
            caller_context=caller_context,
            max_results=max_results,
            query=query,
        )
    except ValueError as exc:
        logger.warning("Email sync failed for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "email_sync_error", "message": str(exc)}},
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error in email sync: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "email_sync_internal_error", "message": str(exc)}},
        ) from exc

    # Sanitize output — never return tokens or raw credentials
    return {
        "status": "success",
        "synced_count": raw_result.get("synced_count", 0),
        "new_messages": raw_result.get("new_messages", 0),
        "failed_messages": raw_result.get("failed_messages", 0),
        "total_messages_scanned": raw_result.get("total_messages_scanned", 0),
        "latest_synced_at": raw_result.get("latest_synced_at"),
    }


@router.get(
    "/list",
    summary="List Emails with Analysis",
    description="Returns user-scoped emails with classification, priority, and verification metadata.",
)
def list_emails(
    category: Optional[str] = Query(None, description="Filter by classified category"),
    priority: Optional[int] = Query(None, description="Minimum priority score filter"),
    limit: int = Query(50, ge=1, le=200, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Query user-scoped emails joined with analysis and verification metadata."""
    user_id = _resolve_user_id(current_user)
    query = (
        select(EmailModel, EmailAnalysisModel, EmailSenderVerificationModel)
        .outerjoin(EmailAnalysisModel, EmailModel.id == EmailAnalysisModel.email_id)
        .outerjoin(EmailSenderVerificationModel, EmailModel.id == EmailSenderVerificationModel.email_id)
        .where(EmailModel.user_id == user_id)
    )

    if category:
        query = query.where(EmailAnalysisModel.category == category.upper())

    if priority is not None:
        query = query.where(EmailAnalysisModel.priority_score >= priority)

    query = query.order_by(desc(EmailModel.received_at)).offset(offset).limit(limit)
    rows = db.execute(query).all()

    items: List[Dict[str, Any]] = []
    for email_rec, analysis_rec, verif_rec in rows:
        one_line = ""
        if analysis_rec and analysis_rec.summary_text:
            one_line = analysis_rec.summary_text.split("\n\n")[0].strip()

        is_verified = (
            verif_rec.spf_status == "pass"
            and verif_rec.dkim_status == "pass"
            and verif_rec.dmarc_status == "pass"
        ) if verif_rec else False

        items.append({
            "id": email_rec.id,
            "sender": email_rec.sender,
            "sender_domain": email_rec.sender_domain,
            "recipients": email_rec.recipients,
            "subject": email_rec.subject,
            "snippet": email_rec.snippet or (email_rec.body_text[:160] if email_rec.body_text else ""),
            "received_at": email_rec.received_at,
            "category": analysis_rec.category if analysis_rec else None,
            "subcategory": analysis_rec.subcategory if analysis_rec else None,
            "priority_score": analysis_rec.priority_score if analysis_rec else None,
            "one_line_summary": one_line or None,
            "deadline": analysis_rec.deadline if analysis_rec else None,
            "is_verified": is_verified,
            "spf_status": verif_rec.spf_status if verif_rec else "unavailable",
            "dkim_status": verif_rec.dkim_status if verif_rec else "unavailable",
            "dmarc_status": verif_rec.dmarc_status if verif_rec else "unavailable",
        })

    return {
        "emails": items,
        "count": len(items),
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/digest",
    summary="Get Email Intelligence Digest",
    description="Returns aggregated intelligence summaries and action items for today or week.",
)
def get_email_digest(
    period: str = Query("today", pattern="^(today|week)$", description="Digest aggregation window"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Compile or retrieve cached digest through ToolEngine."""
    user_id = _resolve_user_id(current_user)
    caller_context = {
        "user_id": user_id,
        "role": getattr(current_user, "role", "USER") if not isinstance(current_user, dict) else current_user.get("role", "USER"),
    }

    try:
        result = engine.execute(
            "email.digest",
            caller_context=caller_context,
            period=period,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "digest_error", "message": str(exc)}},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "digest_internal_error", "message": str(exc)}},
        ) from exc


@router.get(
    "/{id}",
    summary="Get Single Email Detail",
    description="Returns full email content, intelligence analysis, and cryptographic sender verification.",
)
def get_email_detail(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Fetch single email with user ownership check."""
    user_id = _resolve_user_id(current_user)
    email_rec = db.execute(
        select(EmailModel).where(
            EmailModel.id == id,
            EmailModel.user_id == user_id,
        )
    ).scalar_one_or_none()

    if not email_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "email_not_found", "message": f"Email with ID {id} not found."}},
        )

    analysis_rec = db.execute(
        select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == id)
    ).scalar_one_or_none()

    verif_rec = db.execute(
        select(EmailSenderVerificationModel).where(EmailSenderVerificationModel.email_id == id)
    ).scalar_one_or_none()

    action_payload = None
    if analysis_rec and analysis_rec.action_items_json:
        try:
            action_payload = json.loads(analysis_rec.action_items_json)
        except Exception:
            action_payload = None

    return {
        "id": email_rec.id,
        "sender": email_rec.sender,
        "sender_domain": email_rec.sender_domain,
        "recipients": email_rec.recipients,
        "subject": email_rec.subject,
        "body_text": email_rec.body_text,
        "body_html": email_rec.body_html,
        "snippet": email_rec.snippet,
        "received_at": email_rec.received_at,
        "analysis": {
            "category": analysis_rec.category,
            "subcategory": analysis_rec.subcategory,
            "priority_score": analysis_rec.priority_score,
            "summary_text": analysis_rec.summary_text,
            "action_items": action_payload,
            "deadline": analysis_rec.deadline,
            "classified_at": analysis_rec.classified_at,
            "summarized_at": analysis_rec.summarized_at,
            "extracted_at": analysis_rec.extracted_at,
        } if analysis_rec else None,
        "verification": {
            "is_verified": (
                verif_rec.spf_status == "pass"
                and verif_rec.dkim_status == "pass"
                and verif_rec.dmarc_status == "pass"
            ),
            "spf_status": verif_rec.spf_status,
            "dkim_status": verif_rec.dkim_status,
            "dmarc_status": verif_rec.dmarc_status,
            "spf_details": verif_rec.spf_details,
            "dkim_details": verif_rec.dkim_details,
            "dmarc_details": verif_rec.dmarc_details,
        } if verif_rec else None,
    }


@router.post(
    "/{id}/classify",
    summary="Classify Email",
    description="Triggers AI category classification and priority scoring for an email.",
)
def classify_email(
    id: int,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Execute email.classify tool through ToolEngine."""
    user_id = _resolve_user_id(current_user)
    caller_context = {
        "user_id": user_id,
        "role": getattr(current_user, "role", "USER") if not isinstance(current_user, dict) else current_user.get("role", "USER"),
    }

    try:
        return engine.execute(
            "email.classify",
            caller_context=caller_context,
            email_id=id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "classification_error", "message": str(exc)}},
        ) from exc


@router.post(
    "/{id}/summarize",
    summary="Summarize Email",
    description="Generates a factual one-line summary and key bullet points for an email.",
)
def summarize_email(
    id: int,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Execute email.summarize tool through ToolEngine."""
    user_id = _resolve_user_id(current_user)
    caller_context = {
        "user_id": user_id,
        "role": getattr(current_user, "role", "USER") if not isinstance(current_user, dict) else current_user.get("role", "USER"),
    }

    try:
        return engine.execute(
            "email.summarize",
            caller_context=caller_context,
            email_id=id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "summarization_error", "message": str(exc)}},
        ) from exc


@router.post(
    "/{id}/extract-actions",
    summary="Extract Email Action Items",
    description="Extracts structured deadlines, links, and action tasks for an email.",
)
def extract_email_actions(
    id: int,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Execute email.extract_actions tool through ToolEngine."""
    user_id = _resolve_user_id(current_user)
    caller_context = {
        "user_id": user_id,
        "role": getattr(current_user, "role", "USER") if not isinstance(current_user, dict) else current_user.get("role", "USER"),
    }

    try:
        return engine.execute(
            "email.extract_actions",
            caller_context=caller_context,
            email_id=id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "action_extraction_error", "message": str(exc)}},
        ) from exc
