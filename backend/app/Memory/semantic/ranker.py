"""
Memory Ranker

Ranks retrieved memories using a multi-factor scoring algorithm that combines
semantic similarity, importance, recency, and frequency. Implements lightweight
heuristics for importance detection without LLM calls.
"""

import math
import logging
from dataclasses import dataclass
from collections import Counter

from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


@dataclass
class RetrievedMemory:
    """Container for a retrieved memory with metadata for ranking.

    Attributes:
        message: The LangChain message object.
        similarity: Cosine similarity score (0-1).
        timestamp: ISO format timestamp of when the message was created.
        frequency: Number of times similar content appears in the session.
        importance: Importance score (0-1) based on content heuristics.
    """
    message: BaseMessage
    similarity: float
    timestamp: str
    frequency: int = 1
    importance: float = 0.0


# Ranking weight constants
SIMILARITY_WEIGHT: float = 0.55
IMPORTANCE_WEIGHT: float = 0.20
RECENCY_WEIGHT: float = 0.15
FREQUENCY_WEIGHT: float = 0.10


class MemoryRanker:
    """Ranks retrieved memories using multi-factor scoring.

    Combines semantic similarity, importance, recency, and frequency
    into a final score. Uses lightweight heuristics for importance
    detection without LLM calls.

    Attributes:
        similarity_weight: Weight for semantic similarity in final score.
        importance_weight: Weight for importance in final score.
        recency_weight: Weight for recency in final score.
        frequency_weight: Weight for frequency in final score.
    """

    def __init__(
        self,
        similarity_weight: float = SIMILARITY_WEIGHT,
        importance_weight: float = IMPORTANCE_WEIGHT,
        recency_weight: float = RECENCY_WEIGHT,
        frequency_weight: float = FREQUENCY_WEIGHT,
    ):
        """Initialize memory ranker with configurable weights.

        Args:
            similarity_weight: Weight for semantic similarity (default 0.55).
            importance_weight: Weight for importance (default 0.20).
            recency_weight: Weight for recency (default 0.15).
            frequency_weight: Weight for frequency (default 0.10).
        """
        self._similarity_weight = similarity_weight
        self._importance_weight = importance_weight
        self._recency_weight = recency_weight
        self._frequency_weight = frequency_weight

    def rank(
        self,
        query: str,
        candidates: list[RetrievedMemory],
        top_k: int = 5,
    ) -> list[RetrievedMemory]:
        """Rank candidate memories and return top-k.

        Computes final scores for all candidates using the weighted formula,
        removes duplicates, and returns the top-k memories sorted by
        final score (descending).

        Args:
            query: The user query (used for duplicate detection).
            candidates: List of RetrievedMemory objects to rank.
            top_k: Maximum number of memories to return. Defaults to 5.

        Returns:
            List of top-k RetrievedMemory objects ranked by final score.
            Returns empty list if no candidates provided.
        """
        if not candidates:
            return []

        # Remove duplicates based on message content
        unique_candidates = self._remove_duplicates(candidates)

        # Compute frequency scores
        self._compute_frequency_scores(unique_candidates)

        # Compute importance scores
        self._compute_importance_scores(unique_candidates)

        # Compute recency scores
        self._compute_recency_scores(unique_candidates)

        # Compute final scores
        for memory in unique_candidates:
            memory.final_score = self._compute_final_score(memory)

        # Sort by final score descending
        ranked = sorted(unique_candidates, key=lambda x: x.final_score, reverse=True)

        # Return top-k
        result = ranked[:top_k]

        logger.info(
            "Ranked %d memories, returning top %d (query='%s...')",
            len(unique_candidates),
            len(result),
            query[:50] if len(query) > 50 else query,
        )

        return result

    def _remove_duplicates(self, candidates: list[RetrievedMemory]) -> list[RetrievedMemory]:
        """Remove duplicate memories based on content.

        Messages with identical content are deduplicated, keeping the
        first occurrence.

        Args:
            candidates: List of RetrievedMemory objects.

        Returns:
            List of RetrievedMemory objects with duplicates removed.
        """
        seen_content: set[str] = set()
        unique: list[RetrievedMemory] = []

        for memory in candidates:
            content = memory.message.content.strip()
            if content not in seen_content:
                seen_content.add(content)
                unique.append(memory)

        return unique

    def _compute_frequency_scores(self, candidates: list[RetrievedMemory]) -> None:
        """Compute frequency scores for all candidates.

        Frequency is based on how many times similar content appears
        in the candidate set. Higher frequency = higher score.

        Args:
            candidates: List of RetrievedMemory objects (modified in-place).
        """
        # Count content occurrences
        content_counts: Counter = Counter()
        for memory in candidates:
            content = memory.message.content.strip().lower()
            content_counts[content] += 1

        # Normalize frequency scores (0-1)
        if content_counts:
            max_count = max(content_counts.values())
            for memory in candidates:
                content = memory.message.content.strip().lower()
                count = content_counts[content]
                memory.frequency = count / max_count if max_count > 0 else 0.0

    def _compute_importance_scores(self, candidates: list[RetrievedMemory]) -> None:
        """Compute importance scores using lightweight heuristics.

        Importance is increased if the message contains keywords related to:
        - preferences
        - goals
        - plans
        - project decisions
        - user identity

        Uses simple keyword matching - no LLM calls.

        Args:
            candidates: List of RetrievedMemory objects (modified in-place).
        """
        # Define importance keywords by category
        importance_keywords = {
            # Preferences
            "prefer", "preference", "like", "dislike", "favorite", "favourite",
            "rather", "instead", "would rather", "don't like", "dont like",
            "hate", "love", "enjoy", "want", "don't want", "dont want",
            # Goals
            "goal", "objective", "target", "aim", "aspiration", "plan to",
            "intend to", "plan on", "going to", "will be", "want to achieve",
            # Plans
            "plan", "strategy", "roadmap", "timeline", "schedule", "milestone",
            "deadline", "phase", "step", "next steps", "action plan",
            # Project decisions
            "decided", "decision", "chosen", "selected", "agreed", "consensus",
            "approved", "rejected", "alternative", "option", "trade-off",
            "tradeoff", "compromise", "architecture", "design choice",
            # User identity
            "my name is", "i am", "i'm", "i work as", "i live in", "i'm from",
            "i am from", "my role", "my position", "i'm a", "i am a",
            "my background", "my experience", "i have been", "i've been",
        }

        for memory in candidates:
            content_lower = memory.message.content.strip().lower()

            # Count keyword matches
            keyword_count = sum(1 for keyword in importance_keywords if keyword in content_lower)

            # Normalize to 0-1 scale (cap at 3 matches for max score)
            importance_score = min(keyword_count / 3.0, 1.0)

            # Boost importance for messages with multiple keyword categories
            categories_matched = 0
            category_keywords = [
                ["prefer", "preference", "like", "dislike", "favorite"],  # preferences
                ["goal", "objective", "target", "aim"],  # goals
                ["plan", "strategy", "roadmap", "timeline"],  # plans
                ["decided", "decision", "chosen", "agreed"],  # decisions
                ["my name", "i am", "i'm", "i work"],  # identity
            ]

            for category in category_keywords:
                if any(keyword in content_lower for keyword in category):
                    categories_matched += 1

            # Bonus for multi-category messages
            if categories_matched >= 2:
                importance_score = min(importance_score + 0.2, 1.0)

            memory.importance = importance_score

    def _compute_recency_scores(self, candidates: list[RetrievedMemory]) -> None:
        """Compute recency scores for all candidates.

        More recent messages receive higher scores. Uses exponential
        decay based on timestamp.

        Args:
            candidates: List of RetrievedMemory objects (modified in-place).
        """
        if not candidates:
            return

        from datetime import datetime

        # Parse timestamps and find the most recent
        parsed_timestamps = []
        for memory in candidates:
            try:
                dt = datetime.fromisoformat(memory.timestamp.replace('Z', '+00:00'))
                parsed_timestamps.append((dt, memory))
            except (ValueError, AttributeError):
                # If timestamp parsing fails, assign default score
                memory.recency = 0.5

        if not parsed_timestamps:
            return

        # Find the most recent timestamp
        most_recent = max(dt for dt, _ in parsed_timestamps)

        # Compute recency scores using exponential decay
        # More recent = higher score (closer to 1.0)
        for dt, memory in parsed_timestamps:
            time_diff_seconds = (most_recent - dt).total_seconds()

            # Exponential decay with half-life of 1 day (86400 seconds)
            # score = e^(-lambda * t) where lambda = ln(2) / half_life
            half_life = 86400.0  # 1 day in seconds
            lambda_decay = math.log(2) / half_life
            recency_score = math.exp(-lambda_decay * time_diff_seconds)

            memory.recency = recency_score

    def _compute_final_score(self, memory: RetrievedMemory) -> float:
        """Compute final weighted score for a memory.

        Combines all factors using the configured weights:
        final_score = 0.55 * similarity + 0.20 * importance + 0.15 * recency + 0.10 * frequency

        Args:
            memory: RetrievedMemory object with all scores computed.

        Returns:
            Final weighted score (0-1 range).
        """
        final_score = (
            self._similarity_weight * memory.similarity +
            self._importance_weight * memory.importance +
            self._recency_weight * getattr(memory, 'recency', 0.0) +
            self._frequency_weight * memory.frequency
        )

        return final_score
