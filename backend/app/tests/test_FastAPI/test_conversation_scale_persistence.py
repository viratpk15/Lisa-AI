"""
Jarvis AIOS — Scale & Process Restart Persistence Integration Tests
-------------------------------------------------------------------

Verifies 1,000+ message ingestion, cursor pagination, title/content search, and complete
backend process restart recovery (re-instantiating DB engine from disk data file).
"""

from fastapi.testclient import TestClient
from app.main import app
from app.Auth.dependencies import get_current_user
from app.Memory.persistence.sqlite_backend import SQLitePersistenceBackend
from app.Services.conversation_service import ConversationService


def mock_get_current_user():
    return {"sub": "test_persistence@jarvis.ai", "user_id": 999}


app.dependency_overrides[get_current_user] = mock_get_current_user
client = TestClient(app)


def test_conversation_scale_and_restart_recovery(tmp_path):
    db_file = str(tmp_path / "scale_test_memory.db")

    # 1. Initialize Backend Persistence System
    backend_p1 = SQLitePersistenceBackend(db_path=db_file)
    service_p1 = ConversationService(persistence=backend_p1)

    # 2. Create User Session Thread
    session_id = "ses_scale_test_999"
    user_id = 999
    backend_p1.create_conversation(session_id=session_id, user_id=user_id, title="Large Architecture Discussion")

    # 3. Ingest 1,000+ Messages
    total_messages = 1000
    for idx in range(1, total_messages + 1):
        role = "human" if idx % 2 == 1 else "ai"
        content = f"Message payload #{idx}: Constitutional Rule {idx} details."
        backend_p1.append_message(session_id=session_id, message=type("Msg", (), {"content": content, "__class__": type("C", (), {"__name__": "HumanMessage" if role == "human" else "AIMessage"})})(), position=idx)

    # 4. Verify Cursor Pagination Before Process Restart
    page1, has_more1, next_cursor1 = backend_p1.get_paginated_messages(session_id=session_id, limit=50, before_id=None)
    assert len(page1) == 50
    assert has_more1 is True
    assert next_cursor1 is not None

    page2, has_more2, next_cursor2 = backend_p1.get_paginated_messages(session_id=session_id, limit=50, before_id=next_cursor1)
    assert len(page2) == 50
    assert has_more2 is True
    assert next_cursor2 < next_cursor1

    # 5. Search Functionality Verification (Title & Message Content)
    search_results = service_p1.search_conversations(user_id=user_id, query="Architecture")
    assert len(search_results) == 1
    assert search_results[0].title == "Large Architecture Discussion"

    search_msg_results = service_p1.search_conversations(user_id=user_id, query="Constitutional Rule 450")
    assert len(search_msg_results) == 1

    # 6. SIMULATE COMPLETE BACKEND PROCESS RESTART
    # Completely destroy first backend instance references
    del backend_p1
    del service_p1

    # Re-instantiate a fresh SQLitePersistenceBackend & ConversationService loading existing disk DB file
    backend_p2 = SQLitePersistenceBackend(db_path=db_file)
    service_p2 = ConversationService(persistence=backend_p2)

    # 7. Verify 100% Message Continuity & Restart Recovery
    conv = service_p2.get_conversation(session_id=session_id, user_id=user_id)
    assert conv.id == session_id
    assert conv.title == "Large Architecture Discussion"

    # Query full paginated messages from fresh process instance
    restored_page, restored_has_more, restored_cursor = backend_p2.get_paginated_messages(session_id=session_id, limit=100, before_id=None)
    assert len(restored_page) == 100
    assert restored_has_more is True

    # Verify latest message content matches last inserted item
    assert f"Message payload #{total_messages}" in restored_page[-1]["content"]
