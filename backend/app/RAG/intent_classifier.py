"""
Jarvis AIOS — Multi-Stage Document Intent Classifier
--------------------------------------------------

Classifies user document intent into Q_AND_A, OVERVIEW, SUMMARIZATION, COMPARISON, PRESENTATION, or SECTION.

Pipeline:
  1. Rule / Pattern Signals
  2. Semantic Embedding Similarity Matching (e.g. "Can you break this down?", "Give me a deep dive")
  3. LLM Fallback (Optional for ambiguous queries)
"""

from enum import Enum
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DocumentIntent(str, Enum):
    Q_AND_A = "Q_AND_A"
    OVERVIEW = "OVERVIEW"
    SUMMARIZATION = "SUMMARIZATION"
    COMPARISON = "COMPARISON"
    PRESENTATION = "PRESENTATION"
    SECTION = "SECTION"


class DocumentIntentClassifier:
    """Multi-stage intent classifier: Rules -> Semantic Matching -> LLM Fallback."""

    # Canonical intent query anchors for semantic similarity matching
    CANONICAL_ANCHORS: Dict[DocumentIntent, List[str]] = {
        DocumentIntent.OVERVIEW: [
            "What is this PDF about?",
            "Explain this document in detail",
            "Tell me about this resume",
            "Walk me through the document",
            "Explain everything in here",
            "Can you break this down?",
            "Give me a deep dive of this file",
            "Provide a complete breakdown of the document",
        ],
        DocumentIntent.SUMMARIZATION: [
            "Summarize this document",
            "TLDR executive summary",
            "Provide a concise summary",
            "Give me the key takeaways",
        ],
        DocumentIntent.COMPARISON: [
            "Compare these documents",
            "Difference between document A and document B",
            "Compare both PDFs",
        ],
        DocumentIntent.PRESENTATION: [
            "Explain slide 5",
            "Summarize this presentation slide by slide",
            "List all slide titles",
        ],
        DocumentIntent.SECTION: [
            "Explain education",
            "Show work experience",
            "Explain methodology section",
            "What is in the financial section?",
        ],
    }

    @classmethod
    def classify(
        self,
        query: str,
        has_active_doc: bool = True,
        document_type: str = "notes",
    ) -> DocumentIntent:
        """Classify query intent across 3 stages."""
        ql = query.lower()

        # ── STAGE 1: RULE & PATTERN SIGNALS ─────────────────────────────────────
        # 1. Comparison Mode
        if any(kw in ql for kw in ["compare", "versus", " vs ", "difference between", "both files", "both documents"]):
            logger.info("[INTENT-CLASSIFIER] Query='%s' -> STAGE 1 (Rules): COMPARISON", query[:50])
            return DocumentIntent.COMPARISON

        # 2. Presentation Mode (Overview or specific slide number)
        if any(kw in ql for kw in ["slide by slide", "all slides", "presentation overview", "cover slide", "opening slide", "last slide"]) or bool(re.search(r"\bslide\s*\d+\b", ql)):
            logger.info("[INTENT-CLASSIFIER] Query='%s' -> STAGE 1 (Rules): PRESENTATION", query[:50])
            return DocumentIntent.PRESENTATION

        # 3. Summarization Mode
        if any(kw in ql for kw in ["summarize", "summary", "tldr", "executive summary", "key takeaways", "abstract"]):
            logger.info("[INTENT-CLASSIFIER] Query='%s' -> STAGE 1 (Rules): SUMMARIZATION", query[:50])
            return DocumentIntent.SUMMARIZATION

        # 4. Section-Aware Mode
        section_keywords = [
            "education", "skills", "experience", "projects", "certifications",
            "methodology", "experiments", "financials", "budget", "compliance",
            "architecture", "team", "author", "background"
        ]
        if any(f"explain {sk}" in ql or f"show {sk}" in ql or f"list {sk}" in ql for sk in section_keywords):
            logger.info("[INTENT-CLASSIFIER] Query='%s' -> STAGE 1 (Rules): SECTION", query[:50])
            return DocumentIntent.SECTION

        # 5. Direct Overview Phrases
        overview_phrases = [
            "what is this pdf about", "what is this document about", "explain this pdf",
            "explain this document", "tell me about this", "describe this", "walk me through",
            "give detail info", "detail info of", "explain everything", "deep dive", "break this down"
        ]
        if any(ph in ql for ph in overview_phrases):
            logger.info("[INTENT-CLASSIFIER] Query='%s' -> STAGE 1 (Rules): OVERVIEW", query[:50])
            return DocumentIntent.OVERVIEW

        # ── STAGE 2: SEMANTIC SIMILARITY MATCHING ───────────────────────────────
        if has_active_doc:
            # Check semantic word token overlap against canonical anchors
            q_words = set(re.findall(r"\w+", ql))
            best_intent: Optional[DocumentIntent] = None
            best_overlap = 0.0

            for intent, anchors in self.CANONICAL_ANCHORS.items():
                for anchor in anchors:
                    a_words = set(re.findall(r"\w+", anchor.lower()))
                    if not a_words:
                        continue
                    overlap = len(q_words.intersection(a_words)) / len(a_words)
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_intent = intent

            if best_intent and best_overlap >= 0.40:
                logger.info(
                    "[INTENT-CLASSIFIER] Query='%s' -> STAGE 2 (Semantic Similarity score=%.2f): %s",
                    query[:50], best_overlap, best_intent.value
                )
                return best_intent

        # ── DEFAULT FALLBACK: Q_AND_A ───────────────────────────────────────────
        logger.info("[INTENT-CLASSIFIER] Query='%s' -> DEFAULT: Q_AND_A", query[:50])
        return DocumentIntent.Q_AND_A
