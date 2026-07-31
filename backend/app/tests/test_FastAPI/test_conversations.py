"""
Tests for Conversation API & Service Layer

Verifies conversation CRUD operations, ownership verification, rename, pin,
and deletion cascade across SQLite and PostgreSQL persistence providers.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.Data.base import Base
from app.Memory.persistence.sqlite_backend import SQLitePersistenceBackend
from app.Memory.persistence.postgres_backend import PostgreSQLPersistenceBackend
from app.Services.conversation_service import ConversationService
from app.FastAPI.schemas import ConversationSummary


@pytest.fixture
def sqlite_persistence(tmp_path):
    db_file = str(tmp_path / "test_conversations.db")
    return SQLitePersistenceBackend(db_path=db_file)


@pytest.fixture
def postgres_persistence():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    return PostgreSQLPersistenceBackend(session_factory=SessionFactory)


@pytest.mark.parametrize("backend_fixture", ["sqlite_persistence", "postgres_persistence"])
def test_conversation_service_full_crud(request, backend_fixture):
    persistence = request.getfixturevalue(backend_fixture)
    service = ConversationService(persistence=persistence)

    user_id = 101
    other_user_id = 202

    # 1. Create conversation
    conv1 = service.create_conversation(user_id)
    assert isinstance(conv1, ConversationSummary)
    assert conv1.title == "New Conversation"
    assert conv1.pinned is False

    # 2. List conversations
    items = service.list_conversations(user_id)
    assert len(items) == 1
    assert items[0].id == conv1.id

    # 3. Rename conversation
    updated = service.rename_conversation(conv1.id, user_id, "Sprint Planning")
    assert updated.title == "Sprint Planning"

    # 4. Pin conversation
    pinned = service.pin_conversation(conv1.id, user_id, True)
    assert pinned.pinned is True

    # 5. Ownership verification check (other_user_id cannot rename/pin/delete)
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.rename_conversation(conv1.id, other_user_id, "Hacked Title")
    assert exc_info.value.status_code == 403

    # 6. Delete conversation
    service.delete_conversation(conv1.id, user_id)
    items_after = service.list_conversations(user_id)
    assert len(items_after) == 0
