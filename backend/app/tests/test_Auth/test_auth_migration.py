"""
Tests for Authentication Migration & Repository Decoupling

Verifies user registration, login, duplicate registration, invalid credentials,
JWT verification, and provider switching across SQLite and PostgreSQL backends.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.Data.base import Base
from app.Memory.persistence.sqlite_backend import SQLitePersistenceBackend
from app.Memory.persistence.postgres_backend import PostgreSQLPersistenceBackend
from app.Auth.database import UserDatabase
from app.Auth.service import AuthService
from app.Auth.models import User, Token
from app.Auth.security import decode_access_token


@pytest.fixture
def sqlite_persistence(tmp_path):
    db_file = str(tmp_path / "test_auth.db")
    return SQLitePersistenceBackend(db_path=db_file)


@pytest.fixture
def postgres_persistence():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    return PostgreSQLPersistenceBackend(session_factory=SessionFactory)


@pytest.mark.parametrize("backend_fixture", ["sqlite_persistence", "postgres_persistence"])
def test_auth_service_full_workflow(request, backend_fixture):
    persistence = request.getfixturevalue(backend_fixture)
    user_db = UserDatabase(persistence=persistence)
    service = AuthService(db=user_db)

    email = "testuser@example.com"
    password = "SecurePassword123!"

    # 1. Register User
    registered_user = service.register(email, password)
    assert isinstance(registered_user, User)
    assert registered_user.email == email
    assert registered_user.id > 0

    # 2. Duplicate Registration Check
    with pytest.raises(ValueError, match="already registered"):
        service.register(email, "AnotherPassword")

    # 3. Login with Correct Credentials
    token_obj = service.login(email, password)
    assert isinstance(token_obj, Token)
    assert token_obj.access_token

    # 4. Decode & Validate JWT Token
    payload = decode_access_token(token_obj.access_token)
    assert payload.get("user_id") == registered_user.id
    assert payload.get("email") == email

    # 5. Invalid Password Login Check
    with pytest.raises(ValueError, match="Invalid email or password"):
        service.login(email, "WrongPassword")

    # 6. Non-existent User Login Check
    with pytest.raises(ValueError, match="Invalid email or password"):
        service.login("nonexistent@example.com", password)

    # 7. Get User by ID
    retrieved_user = service.get_user(registered_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == registered_user.id
    assert retrieved_user.email == email
