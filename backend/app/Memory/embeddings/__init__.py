"""
Embedding Infrastructure

Provides embedding generation and management for semantic memory.
Embeddings are generated for messages and summaries to enable future
semantic search and retrieval capabilities.
"""

from app.Memory.embeddings.manager import EmbeddingManager
from app.Memory.embeddings.providers import EmbeddingProvider, LocalEmbeddingProvider

__all__ = ["EmbeddingManager", "EmbeddingProvider", "LocalEmbeddingProvider"]
