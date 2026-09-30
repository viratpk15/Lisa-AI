"""
Jarvis AIOS — Email Summarizer Tool
-----------------------------------
Tool identifier: "email.summarize"
Summarizes emails using LLM Engine into a concise one-line summary and 3-7 key points.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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


class EmailSummarizerTool(Tool):
    """Tool for summarizing user emails using prompt engineering and LLM Engine."""

    def __init__(self, custom_llm: Optional[LLMClient] = None) -> None:
        self.llm = custom_llm or llm_client
        metadata = ToolMetadata(
            name="email.summarize",
            display_name="Email Summarizer",
            description=(
                "Generates a factual one-line summary and 3 to 7 bullet key points for an email by ID."
            ),
            category="Email",
            permission_level=PermissionLevel.USER,
            parameter_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "integer",
                        "description": "Internal database email ID to summarize.",
                    }
                },
                "required": ["email_id"],
            },
            tags=["email", "summarize", "nlp", "llm"],
        )
        super().__init__(metadata=metadata)

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute email summarization."""
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
            raise ValueError("Parameter 'email_id' is required for email summarization.")

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
                "summarize_v1",
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
                logger.error("LLM inference failed during email summarization: %s", exc)
                raise ValueError(f"LLM summarization failure: {exc}") from exc

            latency_ms = round((time.time() - start_time) * 1000, 2)
            log_llm_telemetry(model_name="llm_summarizer", latency_ms=latency_ms)

            # 6. Parse and validate strict JSON
            data = extract_json_from_llm(raw_text)

            one_line_summary = str(data.get("one_line_summary", "")).strip()
            if not one_line_summary:
                raise ValueError("LLM response missing non-empty 'one_line_summary'.")

            key_points_raw = data.get("key_points")
            if not isinstance(key_points_raw, list) or len(key_points_raw) == 0:
                raise ValueError("Invalid key_points: expected a non-empty list of strings (3 to 7 items).")

            key_points: List[str] = [str(kp).strip() for kp in key_points_raw if str(kp).strip()]
            if not (3 <= len(key_points) <= 7):
                raise ValueError(f"Invalid key_points count: {len(key_points)}. Must contain between 3 and 7 bullet points.")

            # 7. Upsert into email_analysis
            now_iso = datetime.now(timezone.utc).isoformat()
            formatted_summary = f"{one_line_summary}\n\n" + "\n".join(f"- {kp}" for kp in key_points)

            analysis = db.execute(
                select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)
            ).scalar_one_or_none()

            if analysis:
                analysis.summary_text = formatted_summary
                analysis.summarized_at = now_iso
                analysis.updated_at = now_iso
            else:
                analysis = EmailAnalysisModel(
                    email_id=email_id,
                    summary_text=formatted_summary,
                    summarized_at=now_iso,
                    created_at=now_iso,
                    updated_at=now_iso,
                )
                db.add(analysis)

            db.commit()

            return {
                "email_id": email_id,
                "one_line_summary": one_line_summary,
                "key_points": key_points,
            }
        finally:
            db.close()
