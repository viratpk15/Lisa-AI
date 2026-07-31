"""
Embedding Manager

Manages embedding generation for messages and summaries.
Coordinates between the embedding provider and persistence layer.
"""

import logging
from typing import TYPE_CHECKING

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

if TYPE_CHECKING:
    from app.Memory.embeddings.providers import EmbeddingProvider
    from app.Memory.persistence.base import IPersistenceBackend

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embedding generation for semantic memory.

    Coordinates embedding generation for messages and summaries,
    and persists embeddings to storage for future retrieval.

    Attributes:
        provider: EmbeddingProvider instance for generating embeddings.
        persistence: IPersistenceBackend for storing embeddings.
        enabled: Whether embedding generation is enabled.
    """

    def __init__(
        self,
        provider: "EmbeddingProvider",
        persistence: "IPersistenceBackend | None" = None,
        enabled: bool = True,
    ):
        """Initialize embedding manager.

        Args:
            provider: EmbeddingProvider instance for generating embeddings.
            persistence: Optional SQLitePersistenceBackend for storing embeddings.
            enabled: Whether embedding generation is enabled.
        """
        self._provider = provider
        self._persistence = persistence
        self._enabled = enabled

    def generate_and_store_message_embedding(
        self, session_id: str, message: BaseMessage, position: int
    ) -> None:
        """Generate and store embedding for a message.

        Args:
            session_id: Session identifier.
            message: Message to embed.
            position: Message position in session.
        """
        if not self._enabled or not self._persistence:
            return

        # Generate embedding
        text = self._extract_text(message)
        if not text:
            return

        try:
            embedding = self._provider.generate_embedding(text)
            self._persistence.save_embedding(session_id, position, embedding)
        except Exception as e:
            # Log at DEBUG level - never interrupts conversation flow
            logger.debug(
                "Embedding generation failed for session %s, position %d: %s",
                session_id,
                position,
                str(e),
            )

    def generate_and_store_summary_embedding(
        self, session_id: str, summary: str
    ) -> None:
        """Generate and store embedding for a summary.

        Args:
            session_id: Session identifier.
            summary: Summary text to embed.
        """
        if not self._enabled or not self._persistence or not summary:
            return

        try:
            embedding = self._provider.generate_embedding(summary)
            self._persistence.save_summary_embedding(session_id, embedding)
        except Exception as e:
            # Log at DEBUG level - never interrupts conversation flow
            logger.debug(
                "Summary embedding generation failed for session %s: %s",
                session_id,
                str(e),
            )

    def _extract_text(self, message: BaseMessage) -> str:
        """Extract text content from a message.

        Args:
            message: LangChain message object.

        Returns:
            Text content string.
        """
        if isinstance(message, (HumanMessage, AIMessage)):
            return message.content
        elif isinstance(message, SystemMessage):
            return message.content
        return ""
