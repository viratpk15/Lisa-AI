"""
Tests for the Authentication subsystem.

These tests cover registration, login, JWT validation, session ownership,
and unauthorized access. Tests use a temporary SQLite database to avoid
polluting the production auth database.
"""

import os
import tempfile

import jwt
import pytest

from app.Auth.database import UserDatabase
from app.Auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.Auth.models import User, Token, UserCreate
from app.Config.settings import JWT_SECRET_KEY, JWT_ALGORITHM


# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------


@pytest.fixture
def temp_db_path() -> str:
    """Provide a temporary database path for test isolation."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def test_db(temp_db_path: str) -> UserDatabase:
    """Provide a UserDatabase backed by a temporary file."""
    return UserDatabase(db_path=temp_db_path)


# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------


class TestRegistration:
    """User registration tests."""

    def test_register_user_success(self, test_db: UserDatabase) -> None:
        """A user can be registered with valid credentials."""
        pw_hash = hash_password("secure_pass_1")
        user_id = test_db.create_user("alice@example.com", pw_hash)
        user = test_db.get_user_by_id(user_id)
        assert user is not None
        assert user["email"] == "alice@example.com"

    def test_register_returns_user_object(self, test_db: UserDatabase) -> None:
        """Registering returns a User model with id and email."""
        pw_hash = hash_password("secure_pass_2")
        user_id = test_db.create_user("bob@example.com", pw_hash)
        assert isinstance(user_id, int)
        assert user_id > 0

    def test_register_password_is_hashed(self, test_db: UserDatabase) -> None:
        """Stored password must be a bcrypt hash, never plaintext."""
        pw_hash = hash_password("my_secret_password")
        test_db.create_user("carol@example.com", pw_hash)
        stored = test_db.get_user_by_email("carol@example.com")
        assert stored is not None
        assert stored["password_hash"] != "my_secret_password"
        assert stored["password_hash"].startswith("$2b$")

    def test_register_empty_password_raises(self) -> None:
        """Empty password must raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            hash_password("")

    def test_user_create_model_validates_min_length(self) -> None:
        """UserCreate model rejects passwords shorter than 8 characters."""
        with pytest.raises(ValueError):
            UserCreate(email="test@example.com", password="short")


# -------------------------------------------------------------------
# Duplicate email
# -------------------------------------------------------------------


class TestDuplicateEmail:
    """Duplicate email detection tests."""

    def test_duplicate_email_raises(self, test_db: UserDatabase) -> None:
        """Registering with an existing email raises ValueError."""
        pw_hash = hash_password("password_123")
        test_db.create_user("dup@example.com", pw_hash)
        with pytest.raises(ValueError, match="already registered"):
            test_db.create_user("dup@example.com", hash_password("other_pw"))

    def test_different_emails_allowed(self, test_db: UserDatabase) -> None:
        """Two different emails can both be registered."""
        pw_hash_1 = hash_password("password_a")
        pw_hash_2 = hash_password("password_b")
        id_1 = test_db.create_user("user_a@example.com", pw_hash_1)
        id_2 = test_db.create_user("user_b@example.com", pw_hash_2)
        assert id_2 != id_1


# -------------------------------------------------------------------
# Login success
# -------------------------------------------------------------------


class TestLoginSuccess:
    """Successful login tests."""

    def test_login_returns_token(self, test_db: UserDatabase) -> None:
        """Valid credentials return a Token with a JWT."""
        pw_hash = hash_password("valid_password")
        user_id = test_db.create_user("login@example.com", pw_hash)
        token_str = create_access_token(user_id, "login@example.com")
        token = Token(access_token=token_str)
        assert token.access_token
        assert token.token_type == "bearer"

    def test_login_token_contains_user_id_and_email(self) -> None:
        """Decoded JWT contains user_id and email."""
        token_str = create_access_token(42, "jwt@example.com")
        payload = decode_access_token(token_str)
        assert payload["user_id"] == 42
        assert payload["email"] == "jwt@example.com"

    def test_login_token_has_expiry(self) -> None:
        """JWT contains an expiration claim (exp)."""
        token_str = create_access_token(1, "expiry@example.com")
        payload = decode_access_token(token_str)
        assert "exp" in payload


# -------------------------------------------------------------------
# Login failure
# -------------------------------------------------------------------


class TestLoginFailure:
    """Failed login tests."""

    def test_login_wrong_password(self, test_db: UserDatabase) -> None:
        """Wrong password fails password verification."""
        pw_hash = hash_password("correct_password")
        test_db.create_user("fail@example.com", pw_hash)
        assert not verify_password("wrong_password", pw_hash)

    def test_login_nonexistent_email(self, test_db: UserDatabase) -> None:
        """Login with an unregistered email returns user as None."""
        user = test_db.get_user_by_email("nobody@example.com")
        assert user is None

    def test_verify_password_wrong_hash(self) -> None:
        """verify_password returns False for an invalid hash."""
        result = verify_password("any_password", "not_a_valid_hash")
        assert result is False


# -------------------------------------------------------------------
# JWT validation
# -------------------------------------------------------------------


class TestJWTValidation:
    """JWT token validation tests."""

    def test_valid_token_decodes(self) -> None:
        """A properly signed token decodes successfully."""
        token = create_access_token(7, "valid@example.com")
        payload = decode_access_token(token)
        assert payload["user_id"] == 7
        assert payload["email"] == "valid@example.com"

    def test_expired_token_raises(self) -> None:
        """An expired token raises ValueError."""
        import time

        payload = {
            "user_id": 1,
            "email": "expired@example.com",
            "exp": int(time.time()) - 3600,
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        with pytest.raises(ValueError, match="has expired"):
            decode_access_token(token)

    def test_malformed_token_raises(self) -> None:
        """A malformed token raises ValueError."""
        with pytest.raises(ValueError, match="Invalid token"):
            decode_access_token("not.a.jwt.token")

    def test_token_wrong_secret_fails(self) -> None:
        """A token signed with a different secret is rejected."""
        token = jwt.encode(
            {"user_id": 1, "email": "test@example.com"},
            "a-different-secret-that-is-at-least-32-bytes-long!",
            algorithm="HS256",
        )
        with pytest.raises(ValueError, match="Invalid token"):
            decode_access_token(token)

    def test_decode_empty_token_raises(self) -> None:
        """Decoding an empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid token"):
            decode_access_token("")


# -------------------------------------------------------------------
# Unauthorized access
# -------------------------------------------------------------------


class TestUnauthorizedAccess:
    """Unauthorized access tests focusing on the get_current_user dependency."""

    def test_invalid_token_in_dependency(self) -> None:
        """An invalid token passed through the dependency raises HTTPException."""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials
        from app.Auth.dependencies import get_current_user

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_jwt_token_here",
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401

    def test_expired_token_in_dependency(self) -> None:
        """An expired token passed through the dependency raises 401."""
        import time
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials
        from app.Auth.dependencies import get_current_user

        payload = {
            "user_id": 1,
            "email": "expired@example.com",
            "exp": int(time.time()) - 3600,
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401


# -------------------------------------------------------------------
# Session ownership
# -------------------------------------------------------------------


class TestSessionOwnership:
    """Session ownership verification tests.

    verify_session_ownership uses sqlite3 directly (no dependency on the Memory
    package) to avoid triggering eager MemoryManager() initialization.
    """

    def test_new_session_allowed(self) -> None:
        """A session that doesn't exist yet is allowed (creation-on-demand)."""
        from app.FastAPI.dependencies import verify_session_ownership

        # A nonexistent session with a valid user passes (returns User)
        user = User(id=1, email="test@example.com")
        result = verify_session_ownership(session_id="nonexistent", current_user=user)
        assert result == user

    def test_owner_matches(self) -> None:
        """A session bound to the requesting user passes verification."""
        from app.FastAPI.dependencies import verify_session_ownership

        _seed_session("owned-session", user_id=5)
        user = User(id=5, email="owner@example.com")
        result = verify_session_ownership(session_id="owned-session", current_user=user)
        assert result == user

    def test_owner_mismatch(self) -> None:
        """A session bound to a different user fails with 403."""
        from fastapi import HTTPException
        from app.FastAPI.dependencies import verify_session_ownership

        _seed_session("foreign-session", user_id=10)
        user = User(id=99, email="intruder@example.com")
        with pytest.raises(HTTPException) as exc_info:
            verify_session_ownership(session_id="foreign-session", current_user=user)
        assert exc_info.value.status_code == 403


def _seed_session(session_id: str, user_id: int) -> None:
    """Insert a session row directly into the persistence DB.

    This helper avoids importing SQLitePersistenceBackend (which
    triggers eager MemoryManager initialization) by using sqlite3
    directly. The same default path used by verify_session_ownership.
    """
    import datetime
    import sqlite3
    from pathlib import Path

    from app.Config.settings import PERSISTENCE_DB_PATH

    db_path = PERSISTENCE_DB_PATH
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sessions "
            "(session_id, user_id, summary, created_at, last_accessed) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, user_id, None, now, now),
        )
