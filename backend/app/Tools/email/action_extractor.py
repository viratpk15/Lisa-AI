"""
Jarvis AIOS — Email Action & Deadline Extractor Tool
----------------------------------------------------
Tool identifier: "email.extract_actions"
Extracts action items, valid web links, deadlines, and recipient response requirements using LLM Engine.
"""

import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

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


URL_REGEX = re.compile(
    r'(?i)\b(?:https?://|www\d{0,3}[.])[^\s<>"\'{}|\\^`]+'
)
HTML_HREF_REGEX = re.compile(r'''(?i)href=["'](https?://[^"'>\s]+)["']''')


def _is_valid_url(url: str) -> bool:
    """Validate that a URL string has http/https scheme and netloc domain."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def extract_links_from_text(text: Optional[str]) -> List[str]:
    """Deterministically extract and sanitize 100% of URLs from plain text or HTML."""
    if not text or not isinstance(text, str):
        return []

    found: List[str] = []

    # 1. HTML href tags
    for match in HTML_HREF_REGEX.finditer(text):
        raw = match.group(1).strip()
        url = re.sub(r'[\.,;:!?)]+$', '', raw)
        if _is_valid_url(url) and url not in found:
            found.append(url)

    # 2. Plain text URLs
    for match in URL_REGEX.finditer(text):
        raw = match.group(0).strip()
        if raw.lower().startswith("www."):
            raw = f"https://{raw}"
        url = re.sub(r'[\.,;:!?)]+$', '', raw)
        if _is_valid_url(url) and url not in found:
            found.append(url)

    return found


class EmailActionExtractorTool(Tool):
    """Tool for extracting action items, deadlines, links, and requirements from an email."""

    def __init__(self, custom_llm: Optional[LLMClient] = None) -> None:
        self.llm = custom_llm or llm_client
        metadata = ToolMetadata(
            name="email.extract_actions",
            display_name="Email Action Extractor",
            description=(
                "Extracts structured action items, deadlines, validated URLs, and reply requirements from an email by ID."
            ),
            category="Email",
            permission_level=PermissionLevel.USER,
            parameter_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "integer",
                        "description": "Internal database email ID to extract actions from.",
                    }
                },
                "required": ["email_id"],
            },
            tags=["email", "actions", "deadlines", "tasks", "nlp"],
        )
        super().__init__(metadata=metadata)

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute email action extraction."""
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
            raise ValueError("Parameter 'email_id' is required for action extraction.")

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
                "extract_actions_v1",
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
                logger.error("LLM inference failed during action extraction: %s", exc)
                raise ValueError(f"LLM action extraction failure: {exc}") from exc

            latency_ms = round((time.time() - start_time) * 1000, 2)
            log_llm_telemetry(model_name="llm_action_extractor", latency_ms=latency_ms)

            # 6. Parse and validate strict JSON
            data = extract_json_from_llm(raw_text)

            deadline_raw = data.get("deadline")
            deadline: Optional[str] = None
            if deadline_raw and isinstance(deadline_raw, str) and deadline_raw.strip().lower() not in ("null", "none"):
                deadline = deadline_raw.strip()

            raw_links = data.get("links", [])
            valid_links: List[str] = []
            if isinstance(raw_links, list):
                for link in raw_links:
                    if isinstance(link, str) and _is_valid_url(link):
                        valid_links.append(link.strip())

            # Merge deterministic URL extractions with LLM results for 100% link extraction
            body_links = extract_links_from_text(email_record.body_text)
            html_links = extract_links_from_text(email_record.body_html)
            snippet_links = extract_links_from_text(email_record.snippet)

            all_extracted_links: List[str] = []
            for candidate in (valid_links + body_links + html_links + snippet_links):
                if candidate not in all_extracted_links and _is_valid_url(candidate):
                    all_extracted_links.append(candidate)

            raw_tasks = data.get("tasks", [])
            tasks: List[str] = []
            if isinstance(raw_tasks, list):
                for t in raw_tasks:
                    if str(t).strip():
                        tasks.append(str(t).strip())

            sender_action = bool(data.get("sender_action_required", False))

            # 7. Upsert into email_analysis
            now_iso = datetime.now(timezone.utc).isoformat()
            action_items_payload = json.dumps({
                "links": all_extracted_links,
                "tasks": tasks,
                "sender_action_required": sender_action,
            })

            analysis = db.execute(
                select(EmailAnalysisModel).where(EmailAnalysisModel.email_id == email_id)
            ).scalar_one_or_none()

            if analysis:
                analysis.deadline = deadline
                analysis.action_items_json = action_items_payload
                analysis.extracted_at = now_iso
                analysis.updated_at = now_iso
            else:
                analysis = EmailAnalysisModel(
                    email_id=email_id,
                    deadline=deadline,
                    action_items_json=action_items_payload,
                    extracted_at=now_iso,
                    created_at=now_iso,
                    updated_at=now_iso,
                )
                db.add(analysis)

            db.commit()

            return {
                "email_id": email_id,
                "deadline": deadline,
                "links": all_extracted_links,
                "tasks": tasks,
                "sender_action_required": sender_action,
            }
        finally:
            db.close()
