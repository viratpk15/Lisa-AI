"""
Jarvis AIOS
-----------
Memory Persistence Interface

Defines the provider-independent abstract base interface (IPersistenceBackend)
that all memory persistence storage backends (SQLite, PostgreSQL, etc.) must implement.
"""

from abc import ABC, abstractmethod
from typing import Any
from langchain_core.messages import BaseMessage


class IPersistenceBackend(ABC):
    """Abstract interface for memory persistence backends in Jarvis AIOS."""

    @abstractmethod
    def load_session(self, session_id: str) -> dict[str, Any] | None:
        """Load session data from persistent storage."""
        pass

    @abstractmethod
    def get_paginated_messages(
        self, session_id: str, limit: int = 30, before_id: int | None = None
    ) -> tuple[list[dict[str, Any]], bool, int | None]:
        """Fetch a page of messages for a session using cursor-based pagination.

        Returns:
            Tuple of (messages_list, has_more_boolean, next_cursor_int_or_none).
        """
        pass

    @abstractmethod
    def load_summary(self, session_id: str) -> str | None:
        """Load session summary text."""
        pass

    @abstractmethod
    def append_message(self, session_id: str, message: BaseMessage, position: int) -> None:
        """Append a single message to persistent storage."""
        pass

    @abstractmethod
    def update_summary(self, session_id: str, summary: str) -> None:
        """Update session summary in persistent storage."""
        pass

    @abstractmethod
    def replace_message_window(self, session_id: str, messages: list[BaseMessage]) -> None:
        """Replace all session messages with a trimmed window."""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Delete session and all related records from storage."""
        pass

    @abstractmethod
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists in persistent storage."""
        pass

    @abstractmethod
    def get_session_owner(self, session_id: str) -> int | None:
        """Get user_id of the session owner."""
        pass

    @abstractmethod
    def bind_session_to_user(self, session_id: str, user_id: int) -> None:
        """Bind a session to a specific user_id."""
        pass

    @abstractmethod
    def save_embedding(self, session_id: str, position: int, embedding: list[float]) -> None:
        """Save vector embedding for a message position."""
        pass

    @abstractmethod
    def save_summary_embedding(self, session_id: str, embedding: list[float]) -> None:
        """Save vector embedding for session summary."""
        pass

    @abstractmethod
    def load_session_embeddings(
        self, session_id: str
    ) -> list[tuple[int, BaseMessage, list[float] | None]]:
        """Load all messages with vector embeddings for a session."""
        pass

    @abstractmethod
    def save_execution_state(self, session_id: str, execution_state: dict[str, Any]) -> None:
        """Save plan execution state for a session."""
        pass

    @abstractmethod
    def load_execution_state(self, session_id: str) -> dict[str, Any] | None:
        """Load plan execution state for a session."""
        pass

    @abstractmethod
    def clear_execution_state(self, session_id: str) -> None:
        """Clear plan execution state for a session."""
        pass

    # ---------------------------------------------------------------------------
    # Conversation CRUD Operations
    # ---------------------------------------------------------------------------

    @abstractmethod
    def create_conversation(
        self, session_id: str, user_id: int, title: str = "New Conversation"
    ) -> dict[str, Any]:
        """Create a new conversation session for a user."""
        pass

    @abstractmethod
    def list_conversations_for_user(self, user_id: int) -> list[dict[str, Any]]:
        """List all conversation sessions belonging to a user."""
        pass

    @abstractmethod
    def get_conversation(self, session_id: str) -> dict[str, Any] | None:
        """Get a conversation session metadata dict by session_id."""
        pass

    @abstractmethod
    def rename_conversation(
        self, session_id: str, user_id: int, title: str
    ) -> dict[str, Any] | None:
        """Rename a conversation session if owned by user_id."""
        pass

    @abstractmethod
    def pin_conversation(
        self, session_id: str, user_id: int, pinned: bool
    ) -> dict[str, Any] | None:
        """Update pinned status for a conversation session if owned by user_id."""
        pass

    @abstractmethod
    def delete_conversation(self, session_id: str, user_id: int) -> bool:
        """Delete a conversation session and all its messages if owned by user_id."""
        pass

    @abstractmethod
    def search_conversations(self, user_id: int, query: str) -> list[dict[str, Any]]:
        """Search conversations by title or message content matching query string."""
        pass

    # ---------------------------------------------------------------------------
    # User / Auth Persistence Operations
    # ---------------------------------------------------------------------------

    @abstractmethod
    def create_user(self, email: str, password_hash: str) -> dict[str, Any]:
        """Create a new user account.

        Raises:
            ValueError: If email is already registered.
        """
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Get a user dictionary by email address."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Get a user dictionary by user_id."""
        pass
