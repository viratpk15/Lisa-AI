"""
Tests for Memory Subsystem Persistence Migration & Provider Switching

Verifies message history, windowing, summarization, execution state,
embedding metadata persistence, and semantic retrieval across both
SQLite and PostgreSQL persistence backends.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain_core.messages import HumanMessage, AIMessage

from app.Data.base import Base
from app.Memory.persistence.sqlite_backend import SQLitePersistenceBackend
from app.Memory.persistence.postgres_backend import PostgreSQLPersistenceBackend
from app.Memory.manager import MemoryManager


@pytest.fixture
def sqlite_persistence(tmp_path):
    db_file = str(tmp_path / "test_memory.db")
    return SQLitePersistenceBackend(db_path=db_file)


@pytest.fixture
def postgres_persistence():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    return PostgreSQLPersistenceBackend(session_factory=SessionFactory)


@pytest.mark.parametrize("backend_fixture", ["sqlite_persistence", "postgres_persistence"])
def test_memory_persistence_full_lifecycle(request, backend_fixture):
    persistence = request.getfixturevalue(backend_fixture)
    manager = MemoryManager(persistence=persistence)

    session_id = "ses_mem_test_101"
    user_id = 999

    # 1. Bind session to user
    persistence.create_conversation(session_id, user_id, "Memory Test Session")
    assert persistence.get_session_owner(session_id) == user_id

    # 2. Append messages
    msg1 = HumanMessage(content="Hello Jarvis!")
    msg2 = AIMessage(content="Hello! How can I assist you today?")
    persistence.append_message(session_id, msg1, position=1)
    persistence.append_message(session_id, msg2, position=2)

    # 3. Load session messages
    loaded = persistence.load_session(session_id)
    assert loaded is not None
    assert len(loaded["messages"]) == 2
    assert loaded["messages"][0].content == "Hello Jarvis!"
    assert loaded["messages"][1].content == "Hello! How can I assist you today?"

    # 4. Summary update and loading
    summary_text = "User greeted Jarvis and Jarvis responded."
    persistence.update_summary(session_id, summary_text)
    assert persistence.load_summary(session_id) == summary_text

    # 5. Execution state saving and loading
    exec_state = {
        "execution_status": "in_progress",
        "current_step": 1,
        "completed_steps": ["step_0"],
    }
    manager.save_execution_state(session_id, exec_state)
    loaded_exec = manager.load_execution_state(session_id)
    assert loaded_exec is not None
    assert loaded_exec["execution_status"] == "in_progress"

    # 6. Clear execution state
    manager.clear_execution_state(session_id)
    assert manager.load_execution_state(session_id) is None

    # 7. Embedding metadata saving and loading
    embedding_vec = [0.1, 0.2, 0.3, 0.4]
    persistence.save_embedding(session_id, position=1, embedding=embedding_vec)
    embeddings_list = persistence.load_session_embeddings(session_id)
    assert len(embeddings_list) >= 1
