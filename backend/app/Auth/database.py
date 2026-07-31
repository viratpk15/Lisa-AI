"""
Jarvis AIOS
-----------
Authentication User Repository Adapter

User repository layer delegating user storage operations to IPersistenceBackend.
Supports both SQLite and PostgreSQL persistence backends seamlessly.
Contains zero direct database driver dependencies.
"""

import logging
from typing import Any

from app.Memory.persistence import IPersistenceBackend, get_persistence_backend

logger = logging.getLogger(__name__)


class UserDatabase:
    """User database repository adapter.

    Delegates user persistence operations to active IPersistenceBackend.
    Exposes provider-agnostic user repository interface.
    """

    def __init__(
        self,
        db_path: str | None = None,
        persistence: IPersistenceBackend | None = None,
    ):
        """Initialize UserDatabase adapter.

        Args:
            db_path: Optional SQLite database file path (for backwards compatibility with test fixtures).
            persistence: Optional custom IPersistenceBackend instance.
        """
        if persistence is not None:
            self._persistence = persistence
        elif db_path is not None:
            from app.Memory.persistence.sqlite_backend import SQLitePersistenceBackend
            self._persistence = SQLitePersistenceBackend(db_path=db_path)
        else:
            self._persistence = None

    @property
    def persistence(self) -> IPersistenceBackend:
        """Lazily obtain active persistence backend."""
        if self._persistence is None:
            self._persistence = get_persistence_backend()
        return self._persistence

    def create_user(self, email: str, password_hash: str) -> int:
        """Create a new user account.

        Args:
            email: The user's email address.
            password_hash: The bcrypt-hashed password.

        Returns:
            The new user's integer database ID.

        Raises:
            ValueError: If email is already registered.
        """
        user_dict = self.persistence.create_user(email, password_hash)
        user_id = user_dict["id"]
        logger.info("Created user id=%s email=%s", user_id, email)
        return user_id

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Get user dictionary by email.

        Args:
            email: The user's email address.

        Returns:
            User dict with id, email, password_hash, or None if not found.
        """
        return self.persistence.get_user_by_email(email)

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Get user dictionary by database ID.

        Args:
            user_id: The user's integer database ID.

        Returns:
            User dict with id and email, or None if not found.
        """
        return self.persistence.get_user_by_id(user_id)


# Global database instance
user_db = UserDatabase()
