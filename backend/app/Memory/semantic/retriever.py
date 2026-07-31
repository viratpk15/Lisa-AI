"""
Semantic Retriever

Retrieves relevant memories using cosine similarity between query embedding
and stored message embeddings. Implements pure Python cosine similarity
without external dependencies. Uses MemoryRanker for multi-factor ranking.
"""

import math
import logging

from langchain_core.messages import BaseMessage

from app.Memory.embeddings.manager import EmbeddingManager
from app.Memory.persistence.base import IPersistenceBackend
from app.Memory.semantic.ranker import MemoryRanker, RetrievedMemory
from app.Observability.manager import observability_manager

logger = logging.getLogger(__name__)


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Cosine similarity measures the cosine of the angle between two vectors,
    providing a normalized similarity score between -1 and 1. For embeddings,
    values typically range from 0 to 1, where 1 indicates identical direction.

    The formula is: cos(θ) = (A · B) / (||A|| * ||B||)

    Args:
        vec1: First vector as list of floats.
        vec2: Second vector as list of floats.

    Returns:
        Cosine similarity score between -1 and 1.
        Returns 0.0 if either vector has zero magnitude.
    """
    if len(vec1) != len(vec2):
        # Vectors must have same dimension
        return 0.0

    # Compute dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    # Compute magnitudes (L2 norms)
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    # Avoid division by zero
    if magnitude1 == 0.0 or magnitude2 == 0.0:
        return 0.0

    # Return cosine similarity
    return dot_product / (magnitude1 * magnitude2)


class SemanticRetriever:
    """Retrieves relevant memories using semantic similarity.

    Uses cosine similarity to find messages whose embeddings are most
    similar to the query embedding. Messages without embeddings are
    automatically excluded from results.

    Attributes:
        embedding_manager: EmbeddingManager for generating query embeddings.
        persistence: IPersistenceBackend for loading stored embeddings.
        similarity_threshold: Minimum similarity score for inclusion.
    """

    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        persistence: IPersistenceBackend,
        similarity_threshold: float = 0.5,
    ):
        """Initialize semantic retriever.

        Args:
            embedding_manager: EmbeddingManager for generating embeddings.
            persistence: SQLitePersistenceBackend for loading stored embeddings.
            similarity_threshold: Minimum cosine similarity score (0-1).
                Messages below this threshold are not returned.
                Defaults to 0.5.
        """
        self._embedding_manager = embedding_manager
        self._persistence = persistence
        self._similarity_threshold = similarity_threshold
        self._ranker = MemoryRanker()

    def retrieve(
        self,
        session_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[BaseMessage]:
        """Retrieve top-k most relevant messages for a query.

        Generates an embedding for the query, loads all stored embeddings
        for the session, computes cosine similarity between the query and
        each message embedding, and returns the top-k messages above the
        similarity threshold.

        Messages without embeddings are automatically excluded.

        Args:
            session_id: Unique session identifier.
            query: User query to find relevant memories for.
            top_k: Maximum number of messages to return. Defaults to 5.

        Returns:
            List of BaseMessage objects ranked by similarity (highest first).
            Returns empty list if no messages meet the threshold or if
            embeddings are not enabled.
        """
        if not self._embedding_manager._enabled:
            logger.debug("Embeddings not enabled, skipping semantic retrieval")
            return []

        # Generate embedding for the query
        try:
            query_embedding = self._embedding_manager._provider.generate_embedding(query)
        except Exception as e:
            logger.debug("Failed to generate query embedding: %s", str(e))
            return []

        if not query_embedding:
            return []

        # Load all embeddings for the session
        stored_embeddings = self._persistence.load_session_embeddings(session_id)

        if not stored_embeddings:
            logger.debug("No stored embeddings found for session %s", session_id)
            return []

        # Compute similarity scores and create RetrievedMemory objects
        candidates: list[RetrievedMemory] = []

        for position, message, embedding in stored_embeddings:
            if not embedding:
                # Skip messages without embeddings
                continue

            similarity = _cosine_similarity(query_embedding, embedding)

            # Only include messages above threshold
            if similarity >= self._similarity_threshold:
                # Extract timestamp from message metadata if available
                timestamp = getattr(message, 'timestamp', '2024-01-01T00:00:00')
                if hasattr(message, 'additional_kwargs') and 'timestamp' in message.additional_kwargs:
                    timestamp = message.additional_kwargs['timestamp']

                candidates.append(RetrievedMemory(
                    message=message,
                    similarity=similarity,
                    timestamp=timestamp,
                ))

        # Use MemoryRanker to rank candidates
        ranked_memories = self._ranker.rank(
            query=query,
            candidates=candidates,
            top_k=top_k,
        )

        # Extract messages from ranked memories
        top_messages = [memory.message for memory in ranked_memories]

        # Record semantic memory hits for the active trace.
        observability_manager.record_semantic_hit(len(top_messages))

        logger.info(
            "Retrieved and ranked %d relevant memories for session %s (threshold=%.2f, top_k=%d)",
            len(top_messages),
            session_id,
            self._similarity_threshold,
            top_k,
        )

        return top_messages
