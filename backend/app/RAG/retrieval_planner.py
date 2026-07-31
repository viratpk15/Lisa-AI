"""
Jarvis AIOS — Adaptive Retrieval Planner
----------------------------------------

Dynamically builds a RetrievalPlan based on DocumentIntent, document metadata,
and query scope. Replaces fixed top_k with hierarchical section-aware plans.
"""

from dataclasses import dataclass, field
import logging
from typing import List, Optional
from app.RAG.intent_classifier import DocumentIntent

logger = logging.getLogger(__name__)


@dataclass
class RetrievalPlan:
    intent: DocumentIntent
    strategy: str
    top_k: int = 5
    include_all_sections: bool = False
    neighbor_window: int = 0
    target_sections: List[str] = field(default_factory=list)
    requested_slide: Optional[int] = None
    is_hierarchical: bool = False


class AdaptiveRetrievalPlanner:
    """Plans retrieval strategy dynamically based on intent and document type."""

    @classmethod
    def create_plan(
        self,
        intent: DocumentIntent,
        query: str,
        document_type: str = "notes",
        doc_type: Optional[str] = None,
        total_chunks_in_doc: int = 10,
    ) -> RetrievalPlan:
        ql = query.lower()

        if intent == DocumentIntent.OVERVIEW:
            # Scalable Hierarchical Outline Retrieval
            return RetrievalPlan(
                intent=intent,
                strategy="HIERARCHICAL_OUTLINE",
                top_k=min(25, max(10, total_chunks_in_doc)),
                include_all_sections=True,
                neighbor_window=1,
                is_hierarchical=total_chunks_in_doc > 15,
            )

        if intent == DocumentIntent.SUMMARIZATION:
            return RetrievalPlan(
                intent=intent,
                strategy="HIERARCHICAL_SUMMARY",
                top_k=min(20, max(8, total_chunks_in_doc)),
                include_all_sections=True,
                neighbor_window=1,
                is_hierarchical=total_chunks_in_doc > 15,
            )

        if intent == DocumentIntent.COMPARISON:
            return RetrievalPlan(
                intent=intent,
                strategy="MULTI_DOC_COMPARISON",
                top_k=10,
                neighbor_window=0,
                is_hierarchical=False,
            )

        if intent == DocumentIntent.PRESENTATION:
            return RetrievalPlan(
                intent=intent,
                strategy="SLIDE_SEQUENCE",
                top_k=min(30, max(10, total_chunks_in_doc)),
                include_all_sections=True,
                neighbor_window=0,
                is_hierarchical=False,
            )

        if intent == DocumentIntent.SECTION:
            # Extract section name from query
            section_keywords = [
                "education", "skills", "experience", "projects", "certifications",
                "methodology", "experiments", "financials", "budget", "compliance"
            ]
            found = [sk for sk in section_keywords if sk in ql]
            return RetrievalPlan(
                intent=intent,
                strategy="SECTION_FILTER",
                top_k=8,
                neighbor_window=1,
                target_sections=found,
                is_hierarchical=False,
            )

        # Default Q_AND_A: Lightweight fast top-k retrieval
        return RetrievalPlan(
            intent=DocumentIntent.Q_AND_A,
            strategy="TOP_K",
            top_k=5,
            neighbor_window=0,
            is_hierarchical=False,
        )
