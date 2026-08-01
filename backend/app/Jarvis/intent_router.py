"""
Jarvis AIOS — Query Intent Router & Classifier
----------------------------------------------

Classifies incoming user queries into discrete knowledge intents BEFORE retrieval or execution:
- MEMORY: Identity, name, conversation recall, and project context.
- DOCUMENT_QA: Explicit requests regarding uploaded files, PDFs, or attached documents.
- GENERAL_KNOWLEDGE: Conceptual, technical, or factual questions (e.g. "Who is Elon Musk?").
- LIVE_SEARCH: Live / real-time data, stocks, crypto, weather, current news.
- TOOL: Direct tool invocation commands (filesystem, calculator, python, git, datetime).
- CHAT: Conversational greetings and small talk.
"""

from enum import Enum
import logging
import re
from typing import Optional  # noqa: F401 -- kept for future use


logger = logging.getLogger(__name__)


class QueryIntent(str, Enum):
    MEMORY = "MEMORY"
    DOCUMENT_QA = "DOCUMENT_QA"
    GENERAL_KNOWLEDGE = "GENERAL_KNOWLEDGE"
    LIVE_SEARCH = "LIVE_SEARCH"
    TOOL = "TOOL"
    CHAT = "CHAT"


class QueryIntentClassifier:
    """Classifies user queries to determine the correct knowledge subsystem."""

    @classmethod
    def classify(
        cls,
        message: str,
        has_active_doc: bool = False,
        has_attachment: bool = False,
    ) -> QueryIntent:
        msg_lower = message.lower().strip()

        # ── 1. MEMORY INTENT ──────────────────────────────────────────────────
        # Identity / self-referential queries
        memory_identity_patterns = [
            r"\bwho am i\b",
            r"\bwhat is my name\b",
            r"\bwhat's my name\b",
            r"\bdo you know my name\b",
            r"\bmy name is\b",
            r"\btell me my name\b",
        ]
        if any(re.search(p, msg_lower) for p in memory_identity_patterns):
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> MEMORY (Identity)", message[:50])
            return QueryIntent.MEMORY

        # Conversation memory recall
        memory_recall_keywords = [
            "what did i tell you",
            "what did i say",
            "remember when",
            "remember that",
            "what project are we building",
            "what are we building",
            "earlier you said",
            "earlier you mentioned",
            "what did we discuss",
            "continue previous conversation",
            "remember this",
            "what was the previous",
        ]
        if any(kw in msg_lower for kw in memory_recall_keywords):
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> MEMORY (Recall)", message[:50])
            return QueryIntent.MEMORY

        # ── 2. TOOL INTENT ───────────────────────────────────────────────────
        tool_keywords = [
            "read file",
            "list workspace",
            "list files",
            "directory contents",
            "create directory",
            "create folder",
            "run python",
            "run code",
            "execute code",
            "execute script",
            "git status",
            "git log",
            "git diff",
            "browse url",
            "open web page",
        ]
        if any(kw in msg_lower for kw in tool_keywords):
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> TOOL (System)", message[:50])
            return QueryIntent.TOOL

        # Date/time
        if any(kw in msg_lower for kw in ["what is the date", "what time is it", "clock", "today's date", "current time"]):
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> TOOL (DateTime)", message[:50])
            return QueryIntent.TOOL

        # Math
        if any(kw in msg_lower for kw in ["calculate", "evaluate expression", "square root of", "factorial of"]) or (
            any(op in message for op in ["+", "*", "/", "^"]) and any(c.isdigit() for c in message)
        ):
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> TOOL (Math)", message[:50])
            return QueryIntent.TOOL

        # ── 3. LIVE SEARCH INTENT ─────────────────────────────────────────────
        # Layer 1: Structured live data (stocks, crypto, commodities, weather, forex)
        from app.Tools.search_providers.classifier import SearchIntentClassifier

        live_class = SearchIntentClassifier.classify(message)
        if live_class.is_live_info:
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> LIVE_SEARCH (Structured Live Data: %s)", message[:50], live_class.domain)
            return QueryIntent.LIVE_SEARCH

        # Layer 2: Time-sensitive general queries (latest products, versions, news, events)
        # These require current information and must NOT be answered from stale LLM knowledge.
        #
        # Strategy: detect a strong RECENCY SIGNAL combined with a TIME-SENSITIVE SUBJECT.
        # We use a scoring approach — recency words are weighted, subject indicators multiply
        # the confidence. A combined score > threshold → LIVE_SEARCH.
        _RECENCY_SIGNALS: dict[str, int] = {
            "latest ":     5,
            "latest":      5,
            "newest ":     5,
            "newest":      5,
            "new ":        3,
            "current ":    4,
            "current":     4,
            "currently":   4,
            "recent ":     4,
            "recent":      4,
            "recently":    4,
            "today":       5,
            "today's":     5,
            "right now":   5,
            "as of now":   5,
            "this week":   4,
            "this month":  3,
            "this year":   3,
            "live ":       4,
            "live":        4,
            "breaking":    5,
            "just released": 5,
            "just launched": 5,
            "just announced": 5,
            "updated":     4,
            "released":    4,
            "launched":    4,
            "announced":   4,
            "version":     4,
            "release":     4,
        }

        # Subject categories indicating the answer is time-sensitive
        _TIME_SENSITIVE_SUBJECTS: dict[str, int] = {
            # Technology products
            "iphone":      5, "macbook":     5, "ipad":       5, "apple":      3,
            "galaxy":      5, "pixel":       5, "android":    4, "ios":        4,
            "windows":     4, "macos":       4,
            "gpu":         5, "cpu":         5, "chip":       4, "processor":  4,
            "laptop":      3, "phone":       3, "tablet":     3, "device":     2,
            # Software / programming
            "python":      5, "node":        4, "nodejs":     4, "react":      4,
            "nextjs":      4, "typescript":  4, "rust":       4, "go ":        3,
            "django":      4, "fastapi":     4, "llama":      5, "gpt":        5,
            "gemini":      5, "claude":      5, "openai":     5, "anthropic":  5,
            "langchain":   4, "langgraph":   4, "hugging face": 4,
            # AI / ML general
            "ai model":    5, "llm":         5, "model":      3, "ai news":    5,
            "ai research": 5, "foundation model": 5, "multimodal": 4,
            # Sports / events
            "ipl":         5, "score":       4, "match":      3, "tournament": 3,
            "champions league": 5, "world cup": 5, "standings": 4,
            # Finance (non-structured — supplements Layer 1)
            "interest rate": 5, "inflation":  4, "gdp":       4, "cpi":       4,
            "market":      3, "nasdaq":      4, "dow jones":  4, "s&p":        4,
            # News / people
            "news":        4, "headlines":   4, "ceo":        4, "president":  3,
            "prime minister": 4, "election": 4, "bill":       3, "law":        3,
        }

        recency_score = sum(w for kw, w in _RECENCY_SIGNALS.items() if kw in msg_lower)
        subject_score = sum(w for kw, w in _TIME_SENSITIVE_SUBJECTS.items() if kw in msg_lower)

        # Threshold: a strong recency word alone (score ≥ 5) OR a weaker recency word
        # combined with an identifiable time-sensitive subject (combined ≥ 7) routes to search.
        _LIVE_THRESHOLD = 7
        _RECENCY_ALONE_THRESHOLD = 5  # "latest" or "today" alone with any noun context

        is_time_sensitive = (
            recency_score >= _RECENCY_ALONE_THRESHOLD and subject_score >= 2
        ) or (
            recency_score + subject_score >= _LIVE_THRESHOLD and recency_score > 0
        )

        if is_time_sensitive:
            logger.info(
                "[KNOWLEDGE-ROUTER] Query='%s' -> LIVE_SEARCH (Time-Sensitive: recency=%d subject=%d total=%d)",
                message[:50], recency_score, subject_score, recency_score + subject_score
            )
            return QueryIntent.LIVE_SEARCH

        # Explicit live search phrases (catch-all for patterns not covered above)
        live_search_explicit = [
            "bitcoin price",
            "crypto price",
            "stock price",
            "current price of",
            "weather in",
            "ipl score",
            "breaking news",
            "today's headlines",
            "search online for",
            "search web for",
        ]
        if any(kw in msg_lower for kw in live_search_explicit):
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> LIVE_SEARCH (Explicit Phrase)", message[:50])
            return QueryIntent.LIVE_SEARCH

        # ── 4. DOCUMENT QA INTENT ─────────────────────────────────────────────
        # Triggered ONLY when explicit document indicators exist or files are attached.
        doc_explicit_keywords = [
            "summarize this pdf",
            "summarize the pdf",
            "summarize this document",
            "summarize the document",
            "summarize attached",
            "summarize the attached",
            "explain page",
            "what does the report say",
            "search my documents",
            "compare uploaded",
            "according to the file",
            "in the document",
            "from the uploaded file",
            "read the attached",
            "in this pdf",
            "in the pdf",
            "in page ",
            "in slide ",
            "what is in the file",
            "what does the document say",
            "uploaded papers",
            "uploaded files",
            "uploaded pdf",
            "uploaded doc",
            "attached report",
            "attached document",
            "attached pdf",
            "attached paper",
            "attached file",
            "the attached",
        ]
        doc_noun_indicators = [
            "pdf",
            "docx",
            "pptx",
            "uploaded file",
            "uploaded paper",
            "attached file",
            "the report",
            "knowledge base",
            "rag dataset",
        ]

        is_explicit_doc_query = any(ph in msg_lower for ph in doc_explicit_keywords) or (
            any(ind in msg_lower for ind in doc_noun_indicators)
            and any(verb in msg_lower for verb in ["read", "summarize", "search", "explain", "find", "show", "check", "parse", "extract", "content", "what is in", "what does"])
        )

        if has_attachment or has_active_doc or is_explicit_doc_query:
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> DOCUMENT_QA (Explicit Doc Request / Attachment)", message[:50])
            return QueryIntent.DOCUMENT_QA

        # ── 5. CHAT INTENT ────────────────────────────────────────────────────
        greetings = ["hello", "hi", "hey", "good morning", "good evening", "how are you", "what can you do", "who are you"]
        if msg_lower in greetings or any(msg_lower.startswith(g + " ") for g in greetings if len(g) > 2):
            logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> CHAT", message[:50])
            return QueryIntent.CHAT

        # ── 6. GENERAL KNOWLEDGE INTENT (Default) ─────────────────────────────
        # Questions like "Who is Elon Musk?", "Explain FastAPI", "What is LangGraph?"
        logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> GENERAL_KNOWLEDGE", message[:50])
        return QueryIntent.GENERAL_KNOWLEDGE
