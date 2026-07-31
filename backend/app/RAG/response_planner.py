"""
Jarvis AIOS — Dedicated Response Planner
---------------------------------------

Decides the structural layout formatting (headings, bullet points, tables, timeline,
executive summaries) based on DocumentIntent and document category (resume, paper, slides, report).
"""

from dataclasses import dataclass
import logging
from typing import List
from app.RAG.intent_classifier import DocumentIntent

logger = logging.getLogger(__name__)


@dataclass
class ResponsePlan:
    layout_name: str
    headings: List[str]
    formatting_directives: str


class ResponsePlanner:
    """Generates structural response plan tailored to document type and intent."""

    @classmethod
    def create_response_plan(
        self,
        intent: DocumentIntent,
        document_type: str = "notes",
        primary_filename: str = "Document",
    ) -> ResponsePlan:

        if intent == DocumentIntent.PRESENTATION or document_type == "slides":
            return ResponsePlan(
                layout_name="PRESENTATION_LAYOUT",
                headings=["Executive Presentation Summary", "Slide-by-Slide Breakdown", "Key Takeaways"],
                formatting_directives=(
                    "STRUCTURED PRESENTATION LAYOUT DIRECTIVES:\n"
                    "1. Provide a high-level summary of the presentation.\n"
                    "2. List the slides sequentially in markdown headers (`# Slide N: Title`).\n"
                    "3. Highlight key takeaways at the end."
                ),
            )

        if intent == DocumentIntent.COMPARISON:
            return ResponsePlan(
                layout_name="COMPARISON_LAYOUT",
                headings=["Executive Comparison Summary", "Side-by-Side Analysis Table", "Key Differences", "Conclusion"],
                formatting_directives=(
                    "STRUCTURED COMPARISON LAYOUT DIRECTIVES:\n"
                    "1. Present an Executive Comparison Summary comparing all target files.\n"
                    "2. Include a Markdown comparison table comparing key metrics/features.\n"
                    "3. Highlight major differences and key conclusions."
                ),
            )

        if document_type == "resume":
            return ResponsePlan(
                layout_name="RESUME_LAYOUT",
                headings=["Executive Overview", "Work Experience & Projects", "Technical Skills", "Education & Qualifications", "Key Strengths"],
                formatting_directives=(
                    "STRUCTURED RESUME LAYOUT DIRECTIVES:\n"
                    "Format response cleanly into:\n"
                    "# Executive Overview\n"
                    "# Work Experience & Projects\n"
                    "# Technical Skills\n"
                    "# Education & Qualifications\n"
                    "# Key Strengths & Achievements"
                ),
            )

        if document_type == "paper":
            return ResponsePlan(
                layout_name="RESEARCH_PAPER_LAYOUT",
                headings=["Abstract & Core Problem", "Methodology & Architecture", "Experiments & Results", "Key Insights", "Conclusion"],
                formatting_directives=(
                    "STRUCTURED RESEARCH PAPER LAYOUT DIRECTIVES:\n"
                    "Format response cleanly into:\n"
                    "# Abstract & Problem Statement\n"
                    "# Methodology & Architecture\n"
                    "# Experiments & Evaluation Results\n"
                    "# Key Insights & Contributions\n"
                    "# Conclusion"
                ),
            )

        if intent == DocumentIntent.OVERVIEW:
            return ResponsePlan(
                layout_name="DOCUMENT_OVERVIEW_LAYOUT",
                headings=["Executive Overview", "Main Topics & Themes", "Detailed Section Breakdown", "Key Takeaways"],
                formatting_directives=(
                    "STRUCTURED DOCUMENT OVERVIEW LAYOUT DIRECTIVES:\n"
                    "Format response cleanly into:\n"
                    "# Executive Overview\n"
                    "# Main Topics & Themes\n"
                    "# Detailed Section Breakdown\n"
                    "# Important Concepts\n"
                    "# Key Takeaways"
                ),
            )

        if intent == DocumentIntent.SUMMARIZATION:
            return ResponsePlan(
                layout_name="EXECUTIVE_SUMMARY_LAYOUT",
                headings=["Executive Summary (TLDR)", "Key Highlights", "Critical Details"],
                formatting_directives=(
                    "STRUCTURED EXECUTIVE SUMMARY DIRECTIVES:\n"
                    "Format response into:\n"
                    "# Executive Summary (TLDR)\n"
                    "# Key Highlights & Metrics\n"
                    "# Critical Findings & Next Steps"
                ),
            )

        # Default Q&A Layout
        return ResponsePlan(
            layout_name="STANDARD_QA_LAYOUT",
            headings=["Direct Answer", "Supporting Evidence"],
            formatting_directives="Provide a direct, grounded answer with clear headings and factual source attributions.",
        )
