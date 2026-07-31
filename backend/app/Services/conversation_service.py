"""
Jarvis AIOS
-----------
Conversation Service

Business layer for managing conversation threads and session lifecycles.
Decouples FastAPI routes from database persistence through IPersistenceBackend.
"""

import uuid
import logging
from typing import Any
from fastapi import HTTPException, status

from app.FastAPI.schemas import (
    ConversationSummary,
    ConversationDetail,
    MessageSchema,
    PaginatedMessagesResponse,
)
from app.Memory.persistence import IPersistenceBackend, get_persistence_backend

logger = logging.getLogger(__name__)


class ConversationService:
    """Business service for conversation operations."""

    def __init__(self, persistence: IPersistenceBackend | None = None):
        """Initialize ConversationService.

        Args:
            persistence: Optional custom IPersistenceBackend provider.
        """
        self._persistence = persistence

    @property
    def persistence(self) -> IPersistenceBackend:
        """Lazily obtain active persistence backend."""
        if self._persistence is None:
            self._persistence = get_persistence_backend()
        return self._persistence

    def list_conversations(self, user_id: int) -> list[ConversationSummary]:
        """List all conversations for an authenticated user."""
        raw_items = self.persistence.list_conversations_for_user(user_id)
        return [self._to_summary(item) for item in raw_items]

    def search_conversations(self, user_id: int, query: str) -> list[ConversationSummary]:
        """Search conversations by title or message content for an authenticated user."""
        raw_items = self.persistence.search_conversations(user_id, query)
        return [self._to_summary(item) for item in raw_items]

    def get_conversation(self, session_id: str, user_id: int) -> ConversationDetail:
        """Get details and latest page of messages for a single conversation session."""
        self._verify_ownership_or_raise(session_id, user_id)
        item = self.persistence.get_conversation(session_id)
        paginated_res = self.get_conversation_messages(session_id, user_id, limit=100, cursor=None)

        summary = self._to_summary(item)
        return ConversationDetail(
            **summary.model_dump(),
            messages=paginated_res.messages,
        )

    def get_conversation_messages(
        self, session_id: str, user_id: int, limit: int = 100, cursor: int | None = None
    ) -> PaginatedMessagesResponse:
        """Fetch a page of messages for a conversation session using cursor-based pagination."""
        self._verify_ownership_or_raise(session_id, user_id)
        raw_msgs, has_more, next_cursor = self.persistence.get_paginated_messages(
            session_id, limit=limit, before_id=cursor
        )

        messages: list[MessageSchema] = []
        for m in raw_msgs:
            raw_type = m.get("message_type") or "human"
            content = m.get("content") or ""
            msg_id = m.get("id")
            timestamp = m.get("timestamp") or ""

            str_type = str(raw_type).lower()
            role = "user" if str_type in ["human", "user"] else ("assistant" if str_type in ["ai", "assistant"] else "system")

            messages.append(
                MessageSchema(
                    id=f"msg_{msg_id}_{session_id}",
                    role=role,
                    content=content,
                    timestamp=timestamp,
                )
            )

        print(f"[STAGE 1 - BACKEND] GET /conversations/{session_id}/messages | cursor received={cursor}, limit={limit}")
        print(f"[STAGE 1 - BACKEND] messages returned count={len(messages)}, has_more={has_more}, next_cursor={next_cursor}")
        if messages:
            print(f"[STAGE 1 - BACKEND] first message id={messages[0].id}, last message id={messages[-1].id}")

        return PaginatedMessagesResponse(
            messages=messages,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    def create_conversation(self, user_id: int) -> ConversationSummary:
        """Create a new conversation session for an authenticated user."""
        session_id = f"ses_{uuid.uuid4().hex[:12]}"
        item = self.persistence.create_conversation(
            session_id=session_id,
            user_id=user_id,
            title="New Conversation",
        )
        return self._to_summary(item, is_new=True)

    def rename_conversation(
        self, session_id: str, user_id: int, title: str
    ) -> ConversationSummary:
        """Rename a conversation session if owned by the user."""
        item = self.persistence.rename_conversation(session_id, user_id, title)
        if not item:
            self._verify_ownership_or_raise(session_id, user_id)
        return self._to_summary(item)

    def pin_conversation(
        self, session_id: str, user_id: int, pinned: bool
    ) -> ConversationSummary:
        """Update pinned status for a conversation session if owned by the user."""
        item = self.persistence.pin_conversation(session_id, user_id, pinned)
        if not item:
            self._verify_ownership_or_raise(session_id, user_id)
        return self._to_summary(item)

    def delete_conversation(self, session_id: str, user_id: int) -> None:
        """Delete a conversation session and all related records if owned by the user."""
        success = self.persistence.delete_conversation(session_id, user_id)
        if not success:
            self._verify_ownership_or_raise(session_id, user_id)

    def _verify_ownership_or_raise(self, session_id: str, user_id: int) -> None:
        """Helper to verify session existence and user ownership."""
        conv = self.persistence.get_conversation(session_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "not_found", "message": "Conversation not found"}},
            )
        if conv.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "session_forbidden",
                        "message": "Session does not belong to the authenticated user",
                    }
                },
            )

    def _to_summary(
        self, item: dict[str, Any] | None, is_new: bool = False
    ) -> ConversationSummary:
        """Convert a persistence dictionary to a ConversationSummary response schema."""
        if not item:
            raise ValueError("Item cannot be None")
        return ConversationSummary(
            id=item["session_id"],
            title=item.get("title") or "Conversation",
            preview="",
            time="Just now" if is_new else "",
            pinned=bool(item.get("pinned", False)),
            model="Gemini 2.5 Pro",
            unread=False,
            group="Today",
        )


# Global service instance
conversation_service = ConversationService()
