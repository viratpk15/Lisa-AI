"""
Jarvis AIOS
-----------
FastAPI Request Models

Pydantic models for all API request bodies.
Each model includes field descriptions for OpenAPI documentation.

Validation notes:
- session_id: stripped, non-empty, max 128 chars
- message: stripped, non-empty, max 10 000 chars
"""

from pydantic import BaseModel, Field
from pydantic import StringConstraints
from typing import Annotated

# Reusable validated string for chat session IDs
SessionIdField = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=128,
    ),
]

# Reusable validated string for chat messages
MessageField = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=10_000,
    ),
]


class ChatRequest(BaseModel):
    """Request model for the chat endpoint.

    Sends a user message to an existing (or new) chat session.
    """

    session_id: SessionIdField = Field(
        ...,
        description="Unique identifier for the chat session. "
        "A new session is created automatically if it doesn't exist. "
        "Must be non-empty and at most 128 characters.",
        examples=["session-123"],
    )
    message: MessageField = Field(
        ...,
        description="The user's message to the AI assistant. "
        "Leading/trailing whitespace is trimmed. "
        "Must be non-empty and at most 10 000 characters.",
        examples=["What is the weather today?"],
    )
    attachment_ids: list[str] = Field(
        default_factory=list,
        description="Optional list of attachment identifiers bound to this message.",
    )
    active_document_id: str | None = Field(
        default=None,
        description="Optional document ID explicitly targeted for scoped retrieval.",
    )
    active_filename: str | None = Field(
        default=None,
        description="Optional filename explicitly targeted for scoped retrieval.",
    )


class ConversationCreateRequest(BaseModel):
    """Request model for creating a new conversation.

    Optional title; if omitted, backend may generate a default title.
    """
    title: str = Field(
        "Untitled Conversation",
        description="Title of the new conversation.",
        max_length=255,
    )

class ConversationRenameRequest(BaseModel):
    """Request model for renaming an existing conversation."""
    title: str = Field(
        ...,
        description="New title for the conversation.",
        max_length=255,
    )

class ConversationPinRequest(BaseModel):
    """Request model for pinning or unpinning a conversation."""
    pinned: bool = Field(
        ...,
        description="Pin status to set for the conversation.",
    )
