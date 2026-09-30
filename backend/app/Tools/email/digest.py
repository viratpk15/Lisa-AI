"""
Jarvis AIOS — Email Intelligence Digest Tool
--------------------------------------------
Tool identifier: "email.digest"
Aggregates and caches intelligence summaries across user emails for 'today' or 'week':
- Counts per category
- Top 5 urgent emails with summaries
- Aggregated action items and links
- Upcoming deadlines sorted ascending
- Multi-tier caching with TTL (15 min for 'today', 1 hour for 'week')
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Data.database import SessionLocal
from app.Tools.email.models import EmailAnalysisModel, EmailDigestCacheModel, EmailModel
from app.Tools.metadata import PermissionLevel, ToolMetadata
from app.Tools.tool import Tool

logger = logging.getLogger(__name__)

CACHE_TTL_TODAY_SECONDS = 900.0   # 15 minutes
CACHE_TTL_WEEK_SECONDS = 3600.0   # 1 hour


def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO8601 or RFC2822 date string into aware datetime."""
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return None


class EmailDigestTool(Tool):
    """Tool for compiling and caching periodic email intelligence digests."""

    def __init__(self) -> None:
        metadata = ToolMetadata(
            name="email.digest",
            display_name="Email Digest",
            description=(
                "Generates an aggregated intelligence digest over user emails for 'today' or 'week', "
                "including category breakdown, top urgent items, action items, and upcoming deadlines with TTL caching."
            ),
            category="Email",
            permission_level=PermissionLevel.USER,
            parameter_schema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "enum": ["today", "week"],
                        "description": "Aggregation window: 'today' (last 24 hours) or 'week' (last 7 days).",
                        "default": "today",
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "If true, bypasses cache and regenerates digest.",
                        "default": False,
                    },
                },
                "required": [],
            },
            tags=["email", "digest", "analytics", "summary"],
        )
        super().__init__(metadata=metadata)

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute email digest generation."""
        caller_context = kwargs.get("caller_context") or {}
        user_id = caller_context.get("user_id")
        if not user_id and "user" in caller_context:
            user_obj = caller_context["user"]
            user_id = getattr(user_obj, "id", None) or (user_obj.get("id") if isinstance(user_obj, dict) else None)
        if not user_id:
            user_id = kwargs.get("user_id")

        if not user_id:
            raise ValueError("Authentication required: no authenticated user_id provided in execution context.")

        period = str(kwargs.get("period", "today")).strip().lower()
        if period not in ("today", "week"):
            raise ValueError(f"Invalid period: '{period}'. Expected 'today' or 'week'.")

        force_refresh = bool(kwargs.get("force_refresh", False))
        ttl_seconds = CACHE_TTL_TODAY_SECONDS if period == "today" else CACHE_TTL_WEEK_SECONDS

        db: Session = SessionLocal()
        try:
            # 1. Check cache if not force_refresh
            now = datetime.now(timezone.utc)
            if not force_refresh:
                cached = db.execute(
                    select(EmailDigestCacheModel).where(
                        EmailDigestCacheModel.user_id == user_id,
                        EmailDigestCacheModel.period == period,
                    )
                ).scalar_one_or_none()

                if cached:
                    gen_dt = _parse_datetime(cached.generated_at)
                    if gen_dt and (now - gen_dt).total_seconds() < ttl_seconds:
                        try:
                            cached_payload = json.loads(cached.payload_json)
                            cached_payload["cached"] = True
                            return cached_payload
                        except Exception:
                            pass

            # 2. Compute time boundary
            cutoff = now - timedelta(hours=24 if period == "today" else 168)

            # 3. Query all emails and analyses for this user
            records = db.execute(
                select(EmailModel, EmailAnalysisModel)
                .outerjoin(EmailAnalysisModel, EmailModel.id == EmailAnalysisModel.email_id)
                .where(EmailModel.user_id == user_id)
            ).all()

            counts_by_category: Dict[str, int] = defaultdict(int)
            urgent_candidates: List[Dict[str, Any]] = []
            action_items: List[Dict[str, Any]] = []
            upcoming_deadlines: List[Dict[str, Any]] = []

            for email_rec, analysis_rec in records:
                # Check date boundary
                rec_dt = _parse_datetime(email_rec.received_at) or _parse_datetime(email_rec.created_at)
                if rec_dt and rec_dt < cutoff:
                    continue

                category = analysis_rec.category if analysis_rec and analysis_rec.category else "UNCATEGORIZED"
                counts_by_category[category] += 1

                # Extract summary text
                summary = ""
                if analysis_rec and analysis_rec.summary_text:
                    summary = analysis_rec.summary_text.split("\n\n")[0].strip()

                priority = analysis_rec.priority_score if analysis_rec and analysis_rec.priority_score is not None else 0

                urgent_candidates.append({
                    "email_id": email_rec.id,
                    "subject": email_rec.subject,
                    "sender": email_rec.sender,
                    "category": category,
                    "priority_score": priority,
                    "one_line_summary": summary,
                    "received_at": email_rec.received_at,
                })

                # Action items
                if analysis_rec and analysis_rec.action_items_json:
                    try:
                        actions = json.loads(analysis_rec.action_items_json)
                        if actions.get("tasks") or actions.get("links") or actions.get("sender_action_required"):
                            action_items.append({
                                "email_id": email_rec.id,
                                "subject": email_rec.subject,
                                "sender": email_rec.sender,
                                "tasks": actions.get("tasks", []),
                                "links": actions.get("links", []),
                                "sender_action_required": actions.get("sender_action_required", False),
                                "deadline": analysis_rec.deadline,
                            })
                    except Exception:
                        pass

                # Deadlines
                if analysis_rec and analysis_rec.deadline:
                    upcoming_deadlines.append({
                        "email_id": email_rec.id,
                        "subject": email_rec.subject,
                        "sender": email_rec.sender,
                        "deadline": analysis_rec.deadline,
                        "category": category,
                    })

            # Sort top 5 urgent by priority_score desc
            urgent_candidates.sort(key=lambda x: x["priority_score"], reverse=True)
            top_urgent = urgent_candidates[:5]

            # Sort upcoming deadlines by deadline string asc
            upcoming_deadlines.sort(key=lambda x: str(x["deadline"]))

            payload = {
                "period": period,
                "generated_at": now.isoformat(),
                "counts_by_category": dict(counts_by_category),
                "top_urgent": top_urgent,
                "action_items": action_items,
                "upcoming_deadlines": upcoming_deadlines,
                "cached": False,
            }

            # 4. Save to cache
            payload_str = json.dumps(payload)
            existing_cache = db.execute(
                select(EmailDigestCacheModel).where(
                    EmailDigestCacheModel.user_id == user_id,
                    EmailDigestCacheModel.period == period,
                )
            ).scalar_one_or_none()

            if existing_cache:
                existing_cache.payload_json = payload_str
                existing_cache.generated_at = now.isoformat()
            else:
                db.add(
                    EmailDigestCacheModel(
                        user_id=user_id,
                        period=period,
                        payload_json=payload_str,
                        generated_at=now.isoformat(),
                    )
                )

            db.commit()
            return payload
        finally:
            db.close()
