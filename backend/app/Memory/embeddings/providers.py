"""
Embedding Providers

Provides abstraction for embedding generation with pluggable backends.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for embedding providers.

    Defines the interface for generating text embeddings.
    """

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        ...


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers.

    Provides common functionality for embedding generation.
    """

    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        ...


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """Local embedding provider using sentence-transformers.

    Uses a local model for embedding generation, avoiding external API calls.
    This is the default provider for production deployments.

    Attributes:
        model_name: Name of the sentence-transformers model.
        dimension: Embedding vector dimension.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize local embedding provider.

        Args:
            model_name: Name of the sentence-transformers model.
                Defaults to "all-MiniLM-L6-v2" (384 dimensions, fast, good quality).
        """
        self.model_name = model_name
        self._model = None
        self._dimension = 384  # Default for all-MiniLM-L6-v2

    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                # Update dimension based on actual model
                self._dimension = self._model.get_sentence_embedding_dimension()
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for LocalEmbeddingProvider. "
                    "Install it with: pip install sentence-transformers"
                )

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        self._load_model()

        # Generate embedding
        embedding = self._model.encode(text, convert_to_numpy=False)

        # Convert to list of floats
        return embedding.tolist()

    @property
    def dimension(self) -> int:
        """Get embedding vector dimension.

        Returns:
            Dimension of embedding vectors.
        """
        self._load_model()
        return self._dimension
