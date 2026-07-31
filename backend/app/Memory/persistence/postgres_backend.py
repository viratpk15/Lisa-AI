"""
PostgreSQL Persistence Backend

Provides PostgreSQL (Supabase) persistent storage for conversation history, summaries,
message embeddings, and execution state using SQLAlchemy 2.x ORM models.
Implements the exact interface contract as SQLitePersistenceBackend.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.Data.base import Base
from app.Data.database import SessionLocal, engine
from app.Data.models import (
    ExecutionStateModel,
    MessageEmbeddingModel,
    MessageModel,
    SessionModel,
    SummaryEmbeddingModel,
    UserModel,
)

from app.Memory.persistence.base import IPersistenceBackend

logger = logging.getLogger(__name__)


class PostgreSQLPersistenceBackend(IPersistenceBackend):
    """PostgreSQL-backed persistent storage for memory.

    Stores conversation history, summaries, session metadata, and embeddings in PostgreSQL (Supabase).
    Implements the exact repository interface as SQLitePersistenceBackend.
    """

    def __init__(self, session_factory: sessionmaker | None = None):
        """Initialize PostgreSQL persistence backend.

        Args:
            session_factory: Optional custom SQLAlchemy sessionmaker instance.
        """
        self.SessionLocal = session_factory or SessionLocal
        self._ensure_tables_exist()

    def _ensure_tables_exist(self) -> None:
        """Create database tables using SQLAlchemy Base metadata if missing."""
        try:
            Base.metadata.create_all(bind=engine)
            logger.debug("Ensured PostgreSQL database tables exist")
        except Exception as exc:
            logger.warning("Could not auto-create PostgreSQL tables: %s", exc)

    def _get_session(self) -> Session:
        """Helper to create a new DB session context."""
        return self.SessionLocal()

    def load_session(self, session_id: str) -> dict[str, Any] | None:
        """Load session data from PostgreSQL.

        Args:
            session_id: Unique session identifier.

        Returns:
            Dict containing 'summary' and 'messages', or None if session not found.
        """
        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()

            if not session_obj:
                return None

            summary = session_obj.summary

            # Load messages sorted by order_in_session
            message_objs = db.execute(
                select(MessageModel)
                .where(MessageModel.session_id == session_id)
                .order_by(MessageModel.order_in_session.asc())
            ).scalars().all()

            messages: list[BaseMessage] = []
            for msg in message_objs:
                if msg.message_type == "human":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.message_type == "ai":
                    messages.append(AIMessage(content=msg.content))
                elif msg.message_type == "system":
                    messages.append(SystemMessage(content=msg.content))

            return {
                "summary": summary,
                "messages": messages,
            }

    def load_summary(self, session_id: str) -> str | None:
        """Load only the summary for a session.

        Args:
            session_id: Unique session identifier.

        Returns:
            Summary text, or None if not found.
        """
        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel.summary).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()
            return session_obj

    def append_message(self, session_id: str, message: BaseMessage, position: int) -> None:
        """Append a single new message to PostgreSQL.

        Args:
            session_id: Unique session identifier.
            message: Message to append.
            position: Message position in session (0-indexed).
        """
        now = datetime.now(timezone.utc).isoformat()
        msg_type = self._get_message_type(message)

        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()

            if not session_obj:
                session_obj = SessionModel(
                    session_id=session_id,
                    summary=None,
                    created_at=now,
                    last_accessed=now,
                )
                db.add(session_obj)
            else:
                session_obj.last_accessed = now

            new_msg = MessageModel(
                session_id=session_id,
                message_type=msg_type,
                content=message.content,
                timestamp=now,
                order_in_session=position,
            )
            db.add(new_msg)
            db.commit()

    def update_summary(self, session_id: str, summary: str) -> None:
        """Update only the summary for a session.

        Args:
            session_id: Unique session identifier.
            summary: New summary text.
        """
        now = datetime.now(timezone.utc).isoformat()

        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()

            if not session_obj:
                session_obj = SessionModel(
                    session_id=session_id,
                    summary=summary,
                    created_at=now,
                    last_accessed=now,
                )
                db.add(session_obj)
            else:
                session_obj.summary = summary
                session_obj.last_accessed = now

            db.commit()

    def get_paginated_messages(
        self, session_id: str, limit: int = 100, before_id: int | None = None
    ) -> tuple[list[dict[str, Any]], bool, int | None]:
        """Fetch a page of messages for a session using cursor-based pagination.

        Args:
            session_id: Unique session identifier.
            limit: Page size (default: 100).
            before_id: Cursor pointing to earliest message ID from previous page.

        Returns:
            Tuple of (messages_list, has_more_boolean, next_cursor_int_or_none).
        """
        with self._get_session() as db:
            stmt = select(MessageModel).where(MessageModel.session_id == session_id)
            if before_id is not None:
                stmt = stmt.where(MessageModel.id < before_id)
            stmt = stmt.order_by(MessageModel.id.desc()).limit(limit)

            rows = list(db.scalars(stmt).all())
            if not rows:
                return ([], False, None)

            rows_asc = list(reversed(rows))
            min_id = rows_asc[0].id

            has_more_stmt = (
                select(MessageModel.id)
                .where(MessageModel.session_id == session_id, MessageModel.id < min_id)
                .limit(1)
            )
            has_more = db.scalar(has_more_stmt) is not None

            msgs = [
                {
                    "id": m.id,
                    "message_type": m.message_type,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "order_in_session": m.order_in_session,
                }
                for m in rows_asc
            ]
            return (msgs, has_more, min_id if has_more else None)

    def replace_message_window(self, session_id: str, messages: list[BaseMessage]) -> None:
        """Replace all messages for a session with a new window.

        Args:
            session_id: Unique session identifier.
            messages: New message window to persist.
        """
        now = datetime.now(timezone.utc).isoformat()

        with self._get_session() as db:
            # Delete existing messages
            db.execute(delete(MessageModel).where(MessageModel.session_id == session_id))

            # Insert new message window
            for idx, msg in enumerate(messages):
                msg_type = self._get_message_type(msg)
                db.add(
                    MessageModel(
                        session_id=session_id,
                        message_type=msg_type,
                        content=msg.content,
                        timestamp=now,
                        order_in_session=idx,
                    )
                )

            # Update session last_accessed
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()
            if session_obj:
                session_obj.last_accessed = now

            db.commit()

    def delete_session(self, session_id: str) -> None:
        """Delete session and all related records from PostgreSQL.

        Args:
            session_id: Unique session identifier.
        """
        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()

            if session_obj:
                db.delete(session_obj)
                db.commit()

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists in PostgreSQL.

        Args:
            session_id: Unique session identifier.

        Returns:
            True if session exists, False otherwise.
        """
        with self._get_session() as db:
            count = db.scalar(
                select(SessionModel.session_id).where(SessionModel.session_id == session_id)
            )
            return count is not None

    def get_session_owner(self, session_id: str) -> int | None:
        """Get the user_id that owns a session.

        Args:
            session_id: Unique session identifier.

        Returns:
            The owner's user_id, or None if not set.
        """
        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()
            return session_obj.user_id if session_obj else None

    def bind_session_to_user(self, session_id: str, user_id: int) -> None:
        """Bind a session to a user.

        Args:
            session_id: Unique session identifier.
            user_id: The user's database ID.
        """
        now = datetime.now(timezone.utc).isoformat()

        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()

            if not session_obj:
                session_obj = SessionModel(
                    session_id=session_id,
                    user_id=user_id,
                    summary=None,
                    created_at=now,
                    last_accessed=now,
                )
                db.add(session_obj)
            else:
                session_obj.user_id = user_id
                session_obj.last_accessed = now

            db.commit()

    def save_embedding(self, session_id: str, position: int, embedding: list[float]) -> None:
        """Save embedding for a message.

        Args:
            session_id: Unique session identifier.
            position: Message position in session.
            embedding: Embedding vector as list of floats.
        """
        now = datetime.now(timezone.utc).isoformat()
        embedding_blob = json.dumps(embedding).encode("utf-8")

        with self._get_session() as db:
            db.add(
                MessageEmbeddingModel(
                    session_id=session_id,
                    position=position,
                    embedding=embedding_blob,
                    created_at=now,
                )
            )
            db.commit()

    def save_summary_embedding(self, session_id: str, embedding: list[float]) -> None:
        """Save embedding for a summary.

        Args:
            session_id: Unique session identifier.
            embedding: Embedding vector as list of floats.
        """
        now = datetime.now(timezone.utc).isoformat()
        embedding_blob = json.dumps(embedding).encode("utf-8")

        with self._get_session() as db:
            summary_emb = db.execute(
                select(SummaryEmbeddingModel).where(SummaryEmbeddingModel.session_id == session_id)
            ).scalar_one_or_none()

            if not summary_emb:
                summary_emb = SummaryEmbeddingModel(
                    session_id=session_id,
                    embedding=embedding_blob,
                    created_at=now,
                )
                db.add(summary_emb)
            else:
                summary_emb.embedding = embedding_blob
                summary_emb.created_at = now

            db.commit()

    def load_session_embeddings(
        self, session_id: str
    ) -> list[tuple[int, BaseMessage, list[float] | None]]:
        """Load all messages with their embeddings for a session.

        Args:
            session_id: Unique session identifier.

        Returns:
            List of tuples (position, message, embedding) for each message.
        """
        with self._get_session() as db:
            message_objs = db.execute(
                select(MessageModel)
                .where(MessageModel.session_id == session_id)
                .order_by(MessageModel.order_in_session.asc())
            ).scalars().all()

            embedding_objs = db.execute(
                select(MessageEmbeddingModel).where(MessageEmbeddingModel.session_id == session_id)
            ).scalars().all()

            embedding_map: dict[int, list[float]] = {}
            for emb in embedding_objs:
                try:
                    embedding_map[emb.position] = json.loads(emb.embedding.decode("utf-8"))
                except Exception:
                    continue

            result: list[tuple[int, BaseMessage, list[float] | None]] = []
            for msg in message_objs:
                if msg.message_type == "human":
                    message = HumanMessage(
                        content=msg.content, additional_kwargs={"timestamp": msg.timestamp}
                    )
                elif msg.message_type == "ai":
                    message = AIMessage(
                        content=msg.content, additional_kwargs={"timestamp": msg.timestamp}
                    )
                elif msg.message_type == "system":
                    message = SystemMessage(
                        content=msg.content, additional_kwargs={"timestamp": msg.timestamp}
                    )
                else:
                    continue

                emb_val = embedding_map.get(msg.order_in_session)
                result.append((msg.order_in_session, message, emb_val))

            return result

    def save_execution_state(self, session_id: str, execution_state: dict[str, Any]) -> None:
        """Save execution state for a session.

        Args:
            session_id: Unique session identifier.
            execution_state: Execution state dictionary.
        """
        now = datetime.now(timezone.utc).isoformat()
        current_plan = json.dumps(execution_state.get("current_plan"))
        completed_steps = json.dumps(execution_state.get("completed_steps", []))
        pending_steps = json.dumps(execution_state.get("pending_steps", []))
        current_step = execution_state.get("current_step")
        execution_status = execution_state.get("execution_status", "idle")

        with self._get_session() as db:
            state_obj = db.execute(
                select(ExecutionStateModel).where(ExecutionStateModel.session_id == session_id)
            ).scalar_one_or_none()

            if not state_obj:
                state_obj = ExecutionStateModel(
                    session_id=session_id,
                    current_plan=current_plan,
                    current_step=current_step,
                    completed_steps=completed_steps,
                    pending_steps=pending_steps,
                    execution_status=execution_status,
                    updated_at=now,
                )
                db.add(state_obj)
            else:
                state_obj.current_plan = current_plan
                state_obj.current_step = current_step
                state_obj.completed_steps = completed_steps
                state_obj.pending_steps = pending_steps
                state_obj.execution_status = execution_status
                state_obj.updated_at = now

            db.commit()

    def load_execution_state(self, session_id: str) -> dict[str, Any] | None:
        """Load execution state for a session.

        Args:
            session_id: Unique session identifier.

        Returns:
            Execution state dictionary, or None if not found.
        """
        with self._get_session() as db:
            state_obj = db.execute(
                select(ExecutionStateModel).where(ExecutionStateModel.session_id == session_id)
            ).scalar_one_or_none()

            if not state_obj:
                return None

            return {
                "current_plan": json.loads(state_obj.current_plan) if state_obj.current_plan else None,
                "current_step": state_obj.current_step,
                "completed_steps": json.loads(state_obj.completed_steps) if state_obj.completed_steps else [],
                "pending_steps": json.loads(state_obj.pending_steps) if state_obj.pending_steps else [],
                "execution_status": state_obj.execution_status,
            }

    def clear_execution_state(self, session_id: str) -> None:
        """Clear execution state for a session.

        Args:
            session_id: Unique session identifier.
        """
        with self._get_session() as db:
            db.execute(delete(ExecutionStateModel).where(ExecutionStateModel.session_id == session_id))
            db.commit()

    def _get_message_type(self, message: BaseMessage) -> str:
        """Get string type for LangChain message."""
        if isinstance(message, HumanMessage):
            return "human"
        elif isinstance(message, AIMessage):
            return "ai"
        elif isinstance(message, SystemMessage):
            return "system"
        return "unknown"

    # ---------------------------------------------------------------------------
    # Conversation CRUD Operations
    # ---------------------------------------------------------------------------

    def create_conversation(
        self, session_id: str, user_id: int, title: str = "New Conversation"
    ) -> dict[str, Any]:
        """Create a new conversation session for a user."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_session() as db:
            session_obj = SessionModel(
                session_id=session_id,
                user_id=user_id,
                title=title,
                pinned=0,
                summary=None,
                created_at=now,
                last_accessed=now,
            )
            db.add(session_obj)
            db.commit()

        return {
            "session_id": session_id,
            "user_id": user_id,
            "title": title,
            "pinned": 0,
            "created_at": now,
            "last_accessed": now,
        }

    def list_conversations_for_user(self, user_id: int) -> list[dict[str, Any]]:
        """List all conversation sessions belonging to a user."""
        with self._get_session() as db:
            rows = db.execute(
                select(SessionModel)
                .where(SessionModel.user_id == user_id)
                .order_by(SessionModel.pinned.desc(), SessionModel.last_accessed.desc())
            ).scalars().all()

            return [
                {
                    "session_id": r.session_id,
                    "title": r.title if r.title else "Conversation",
                    "pinned": bool(r.pinned),
                    "created_at": r.created_at,
                    "last_accessed": r.last_accessed,
                }
                for r in rows
            ]

    def search_conversations(self, user_id: int, query: str) -> list[dict[str, Any]]:
        """Search conversations by title or message content matching query string."""
        with self._get_session() as db:
            pattern = f"%{query}%"
            stmt = (
                select(SessionModel)
                .outerjoin(MessageModel, SessionModel.session_id == MessageModel.session_id)
                .where(
                    SessionModel.user_id == user_id,
                    (SessionModel.title.ilike(pattern)) | (MessageModel.content.ilike(pattern)),
                )
                .distinct()
                .order_by(SessionModel.last_accessed.desc())
            )
            rows = db.scalars(stmt).all()
            return [
                {
                    "session_id": r.session_id,
                    "user_id": r.user_id,
                    "title": r.title,
                    "pinned": r.pinned,
                    "summary": r.summary,
                    "created_at": r.created_at,
                    "last_accessed": r.last_accessed,
                }
                for r in rows
            ]

    def get_conversation(self, session_id: str) -> dict[str, Any] | None:
        """Get a conversation session metadata dict by session_id."""
        with self._get_session() as db:
            r = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()
            if not r:
                return None
            return {
                "session_id": r.session_id,
                "user_id": r.user_id,
                "title": r.title if r.title else "Conversation",
                "pinned": bool(r.pinned),
                "created_at": r.created_at,
                "last_accessed": r.last_accessed,
            }

    def rename_conversation(
        self, session_id: str, user_id: int, title: str
    ) -> dict[str, Any] | None:
        """Rename a conversation session if owned by user_id."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()

            if not session_obj or session_obj.user_id != user_id:
                return None

            session_obj.title = title
            session_obj.last_accessed = now
            db.commit()

        return self.get_conversation(session_id)

    def pin_conversation(
        self, session_id: str, user_id: int, pinned: bool
    ) -> dict[str, Any] | None:
        """Update pinned status for a conversation session if owned by user_id."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()

            if not session_obj or session_obj.user_id != user_id:
                return None

            session_obj.pinned = 1 if pinned else 0
            session_obj.last_accessed = now
            db.commit()

        return self.get_conversation(session_id)

    def delete_conversation(self, session_id: str, user_id: int) -> bool:
        """Delete a conversation session and all its messages if owned by user_id."""
        with self._get_session() as db:
            session_obj = db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            ).scalar_one_or_none()

            if not session_obj or session_obj.user_id != user_id:
                return False

            db.delete(session_obj)
            db.commit()
            return True

    # ---------------------------------------------------------------------------
    # User / Auth Persistence Operations
    # ---------------------------------------------------------------------------

    def create_user(self, email: str, password_hash: str) -> dict[str, Any]:
        """Create a new user account.

        Args:
            email: User's email address.
            password_hash: Hashed password.

        Returns:
            Dict containing user id, email, password_hash, and created_at.

        Raises:
            ValueError: If email is already registered.
        """
        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._get_session() as db:
                user_obj = UserModel(
                    email=email,
                    password_hash=password_hash,
                    created_at=now,
                )
                db.add(user_obj)
                db.commit()
                db.refresh(user_obj)
                user_id = user_obj.id
        except IntegrityError:
            raise ValueError(f"Email '{email}' is already registered")

        return {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "created_at": now,
        }

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Get a user by email address."""
        with self._get_session() as db:
            user_obj = db.execute(
                select(UserModel).where(UserModel.email == email)
            ).scalar_one_or_none()
            if not user_obj:
                return None
            return {
                "id": user_obj.id,
                "email": user_obj.email,
                "password_hash": user_obj.password_hash,
                "created_at": user_obj.created_at,
            }

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Get a user by database ID."""
        with self._get_session() as db:
            user_obj = db.execute(
                select(UserModel).where(UserModel.id == user_id)
            ).scalar_one_or_none()
            if not user_obj:
                return None
            return {
                "id": user_obj.id,
                "email": user_obj.email,
                "password_hash": user_obj.password_hash,
                "created_at": user_obj.created_at,
            }
