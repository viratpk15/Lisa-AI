"""
Jarvis AIOS — Context-Aware Reference Resolver
---------------------------------------------

Resolves user prompt references ("this PDF", "attached resume", "uploaded presentation",
"page 2", "slide 7", explicit filename references, multi-file comparisons) to specific
target document_ids and filenames for deterministic filter-first retrieval.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ReferenceResolver:
    @staticmethod
    def resolve_references(
        message: str,
        session_id: str = "",
        session_attachments: Optional[List[Dict[str, Any]]] = None,
        active_document_id: Optional[str] = None,
        active_filename: Optional[str] = None,
    ) -> Tuple[List[str], Optional[str], bool]:
        """
        Resolves prompt references against session attachment state.

        Returns:
            (target_document_ids, primary_filename, is_comparison)
        """
        attachments = session_attachments or []
        msg_lower = message.lower()
        target_doc_ids: List[str] = []
        primary_fn: Optional[str] = None
        is_comparison = any(
            kw in msg_lower for kw in ["compare", "versus", " vs ", "difference between", "both files", "both documents"]
        )

        # 1. Direct explicit active document override
        if active_document_id:
            target_doc_ids.append(active_document_id)
            primary_fn = active_filename

        # 2. Check for explicit filenames mentioned in text or [Attached File: filename]
        fn_matches = re.findall(r"[\w\-\.\s\+]+\.(?:pdf|docx|pptx|ppt|doc|md|txt|csv)", message, re.IGNORECASE)
        for fn in fn_matches:
            clean_fn = fn.strip().strip("[]()\"'")
            for att in attachments:
                if att["filename"].lower() == clean_fn.lower() or clean_fn.lower() in att["filename"].lower():
                    if att["document_id"] not in target_doc_ids:
                        target_doc_ids.append(att["document_id"])
                        if not primary_fn:
                            primary_fn = att["filename"]

        # 3. Extended Deictic Pronoun & Ordinal References ("this PDF", "it", "the resume", "inside pdf")
        _DEICTIC_SIGNALS = [
            "this pdf", "this file", "this document", "this presentation", "this report", "this cv",
            "attached file", "attached document", "attached resume", "attached pdf",
            "uploaded file", "uploaded document", "uploaded resume", "uploaded presentation",
            "above file", "above document", "that pdf", "that file", "that document", "explain this",
            "the pdf", "the file", "the document", "the resume", "the presentation", "the report",
            "inside pdf", "in pdf", "of pdf", "details inside", "what's inside", "list all projects",
            "list all skills", "summarize skills", "explain education", "explain certifications"
        ]

        has_deictic = any(sig in msg_lower for sig in _DEICTIC_SIGNALS)

        # Check ordinal references ("first document", "second file", "1st pdf")
        ordinal_map = {"first": 0, "1st": 0, "second": 1, "2nd": 1, "third": 2, "3rd": 2}
        for ord_kw, idx in ordinal_map.items():
            if f"{ord_kw} document" in msg_lower or f"{ord_kw} file" in msg_lower or f"{ord_kw} pdf" in msg_lower:
                if idx < len(attachments):
                    doc_id = attachments[idx]["document_id"]
                    if doc_id not in target_doc_ids:
                        target_doc_ids.append(doc_id)
                        if not primary_fn:
                            primary_fn = attachments[idx]["filename"]

        # If user requests comparison of multiple files in session
        if is_comparison and len(attachments) > 1:
            for att in attachments:
                if att["document_id"] not in target_doc_ids:
                    target_doc_ids.append(att["document_id"])
            primary_fn = ", ".join([att["filename"] for att in attachments])

        # Active Session Attachment Fallback: Default to latest active attachment for session
        if (has_deictic or not target_doc_ids) and attachments:
            if not target_doc_ids:
                latest_att = attachments[-1]
                target_doc_ids.append(latest_att["document_id"])
                primary_fn = latest_att["filename"]

        logger.info(
            "[REFERENCE-RESOLVER] Session='%s' Message='%s' ResolvedDocIDs=%s PrimaryFn='%s' IsComparison=%s",
            session_id, message[:50], target_doc_ids, primary_fn, is_comparison
        )

        return target_doc_ids, primary_fn, is_comparison
