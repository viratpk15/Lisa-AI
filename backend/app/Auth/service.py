"""
Jarvis AIOS
-----------
Authentication Service

Business logic for user registration and login.
Coordinates between user repository and security layers with dependency injection.
"""

import logging

from app.Auth.database import UserDatabase, user_db
from app.Auth.models import User, Token
from app.Auth.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management.

    Handles registration and login with secure password handling.
    Supports optional dependency injection of user repository.
    """

    def __init__(self, db: UserDatabase | None = None):
        """Initialize AuthService.

        Args:
            db: Optional UserDatabase instance.
        """
        self._db = db

    @property
    def db(self) -> UserDatabase:
        """Lazily obtain user database repository."""
        if self._db is None:
            self._db = user_db
        return self._db

    def register(self, email: str, password: str) -> User:
        """Register a new user.

        Args:
            email: The user's email address.
            password: The plain-text password.

        Returns:
            The created User model.

        Raises:
            ValueError: If the email is already registered or password is invalid.
        """
        password_hash = hash_password(password)
        user_id = self.db.create_user(email, password_hash)
        return User(id=user_id, email=email)

    def login(self, email: str, password: str) -> Token:
        """Authenticate a user and return a JWT token.

        Args:
            email: The user's email address.
            password: The plain-text password.

        Returns:
            A Token containing the access token.

        Raises:
            ValueError: If credentials are invalid.
        """
        user = self.db.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(user["id"], user["email"])
        logger.info("User logged in: id=%s email=%s", user["id"], email)
        return Token(access_token=access_token)

    def get_user(self, user_id: int) -> User | None:
        """Get a user by ID.

        Args:
            user_id: The user's database ID.

        Returns:
            The User model, or None if not found.
        """
        user = self.db.get_user_by_id(user_id)
        if user:
            return User(id=user["id"], email=user["email"])
        return None


# Global service instance
auth_service = AuthService()
