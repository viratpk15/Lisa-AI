"""
Memory Persistence Layer

Provides provider-independent persistent storage for conversation history and summaries.
Supports both SQLite (local development) and PostgreSQL (production).
"""

from app.Memory.persistence.base import IPersistenceBackend
from app.Memory.persistence.provider import get_persistence_backend

__all__ = ["IPersistenceBackend", "get_persistence_backend"]
