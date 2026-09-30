"""
Jarvis AIOS — Email Classification Tool
---------------------------------------
Tool identifier: "email.classify"
Classifies emails using LLM Engine into strictly defined categories:
URGENT | COLLEGE | PLACEMENT | INTERNSHIP | FINANCE | PERSONAL |
BOOKING | TRAVEL | ADS | NEWS | SPAM | SCAM
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Data.database import SessionLocal
from app.LLM.client import LLMClient, llm_client
from app.Prompts.email import render_email_prompt
from app.Tools.email.guards import (
    cap_email_body,
    check_and_record_rate_limit,
    extract_json_from_llm,
    log_llm_telemetry,
)
from app.Tools.email.models import EmailAnalysisModel, EmailModel
from app.Tools.metadata import PermissionLevel, ToolMetadata
from app.Tools.tool import Tool

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {
    "URGENT",
    "COLLEGE",
    "PLACEMENT",
    "INTERNSHIP",
    "FINANCE",
    "PERSONAL",
    "BOOKING",
    "TRAVEL",
    "ADS",
    "NEWS",
    "SPAM",
    "SCAM",
}


class EmailClassifierTool(Tool):
    """Tool for classifying user emails using prompt engineering and LLM Engine."""

    def __init__(self, custom_llm: Optional[LLMClient] = None) -> None:
        self.llm = custom_llm or llm_client
        metadata = ToolMetadata(
            name="email.classify",
            display_name="Email Classifier",
            description=(
                "Classifies an email by ID into categories: URGENT, COLLEGE, PLACEMENT, INTERNSHIP, "
                "FINANCE, PERSONAL, BOOKING, TRAVEL, ADS, NEWS, SPAM, SCAM with a priority score (0-100)."
            ),
            category="Email",
            permission_level=PermissionLevel.USER,
            parameter_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "integer",
                        "description": "Internal database email ID to classify.",
                    }
                },
                "required": ["email_id"],
            },
            tags=["email", "classify", "nlp", "llm"],
        )
        super().__init__(metadata=metadata)

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute email classification."""
        caller_context = kwargs.get("caller_context") or {}
        user_id = caller_context.get("user_id")
        if not user_id and "user" in caller_context:
            user_obj = caller_context["user"]
            user_id = getattr(user_obj, "id", None) or (user_obj.get("id") if isinstance(user_obj, dict) else None)
        if not user_id:
            user_id = kwargs.get("user_id")

        if not user_id:
            raise ValueError("Authentication required: no authenticated user_id provided in execution context.")

        email_id = kwargs.get("email_id")
        if not email_id:
            raise ValueError("Parameter 'email_id' is required for email classification.")

        # 1. Enforce per-user rate limit
        check_and_record_rate_limit(user_id)

        db: Session = SessionLocal()
        try:
            # 2. Verify ownership and load email
            email_record = db.execute(
                select(EmailModel).where(
                    EmailModel.id == email_id,
                    EmailModel.user_id == user_id,
                )
            ).scalar_one_or_none()

            if not email_record:
                raise ValueError("Email not found or access denied for this user.")

            # 3. Cap body text to 8000 chars
            capped_body = cap_email_body(email_record.body_text or email_record.snippet or "")

            # 4. Render prompt template
            prompt_content = render_email_prompt(
                "classify_v1",
                {
                    "sender": email_record.sender or "",
                    "subject": email_record.subject or "",
                    "body": capped_body,
                },
            )

            # 5. Invoke LLM Engine
            start_time = time.time()
            try:
                response = self.llm.invoke([HumanMessage(content=prompt_content)])
                raw_text = getattr(response, "content", "") if response else ""
            except Exception as exc:
                logger.error("LLM inference failed during email classification: %s", exc)
                raise ValueError(f"LLM classification failure: {exc}") from exc

            latency_ms = round((time.time() - start_time) * 1000, 2)
            log_llm_telemetry(model_name="llm_classifier", latency_ms=latency_ms)

            # 6. Parse and validate strict JSON
            data = extract_json_from_llm(raw_text)

            category = str(data.get("category", "")).strip().upper()
            if category not in VALID_CATEGORIES:
                raise ValueError(
                    f"Invalid category from LLM: '{category}'. Must be one of: {sorted(VALID_CATEGORIES)}"
                )

            subcategory = str(data.get("subcategory", "")).strip() or None
            try:
                priority_score = int(data.get("priority_score", 50))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid priority_score from LLM: {data.get('priority_score')}. Expected integer.") from exc

            if not (0 <= priority_score <= 100):
                raise ValueError(f"Priority score {priority_score} is out of bounds (0-100).")

            reason = str(data.get("reason", "")).strip()

            # 7. Upsert into email_analysis
            now_iso = datetime.now(timezone.utc).isoformat()
            analysis = db.execute(
                select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)
            ).scalar_one_or_none()

            if analysis:
                analysis.category = category
                analysis.subcategory = subcategory
                analysis.priority_score = priority_score
                analysis.classified_at = now_iso
                analysis.updated_at = now_iso
            else:
                analysis = EmailAnalysisModel(
                    email_id=email_id,
                    category=category,
                    subcategory=subcategory,
                    priority_score=priority_score,
                    classified_at=now_iso,
                    created_at=now_iso,
                    updated_at=now_iso,
                )
                db.add(analysis)

            db.commit()

            return {
                "email_id": email_id,
                "category": category,
                "subcategory": subcategory,
                "priority_score": priority_score,
                "reason": reason,
            }
        finally:
            db.close()
