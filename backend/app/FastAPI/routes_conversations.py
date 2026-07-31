"""
Jarvis AIOS
-----------
Conversation FastAPI Routes

HTTP endpoints for conversation thread management.
All endpoints require authentication and delegate to ConversationService.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from app.Auth.dependencies import get_current_user
from app.Auth.models import User
from app.FastAPI.schemas import (
    ConversationSummary,
    ConversationDetail,
    PaginatedMessagesResponse,
)
from app.Services.conversation_service import conversation_service

router = APIRouter()


class RenameRequest(BaseModel):
    title: str = Field(..., description="New conversation title")


class PinRequest(BaseModel):
    pinned: bool = Field(..., description="Pinned status")


@router.get(
    "/conversations",
    response_model=List[ConversationSummary],
    tags=["conversations"],
    summary="List conversations",
)
async def list_conversations(current_user: User = Depends(get_current_user)):
    """List all conversation threads belonging to the authenticated user."""
    return conversation_service.list_conversations(current_user.id)


@router.get(
    "/conversations/search",
    response_model=List[ConversationSummary],
    tags=["conversations"],
    summary="Search conversations",
)
async def search_conversations(
    q: str = Query(..., description="Query string matching title or message content"),
    current_user: User = Depends(get_current_user),
):
    """Search conversation threads by title or message content."""
    return conversation_service.search_conversations(current_user.id, q)


@router.get(
    "/conversations/{session_id}",
    response_model=ConversationDetail,
    tags=["conversations"],
    summary="Get conversation details",
)
async def get_conversation_details(
    session_id: str, current_user: User = Depends(get_current_user)
):
    """Get details and latest page of messages for a single conversation session thread."""
    return conversation_service.get_conversation(session_id, current_user.id)


@router.get(
    "/conversations/{session_id}/messages",
    response_model=PaginatedMessagesResponse,
    tags=["conversations"],
    summary="Get paginated conversation messages",
)
async def get_conversation_messages(
    session_id: str,
    cursor: int | None = Query(None, description="Cursor message ID for loading older messages page"),
    limit: int = Query(100, ge=1, le=500, description="Page size limit"),
    current_user: User = Depends(get_current_user),
):
    """Fetch a page of messages for a single conversation session using cursor-based pagination."""
    return conversation_service.get_conversation_messages(
        session_id=session_id,
        user_id=current_user.id,
        limit=limit,
        cursor=cursor,
    )


@router.post(
    "/conversations",
    response_model=ConversationSummary,
    status_code=status.HTTP_201_CREATED,
    tags=["conversations"],
    summary="Create a new conversation",
)
async def create_conversation(current_user: User = Depends(get_current_user)):
    """Create a new conversation thread for the authenticated user."""
    return conversation_service.create_conversation(current_user.id)


@router.delete(
    "/conversations/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["conversations"],
    summary="Delete a conversation",
)
async def delete_conversation(
    session_id: str, current_user: User = Depends(get_current_user)
):
    """Delete a conversation thread if owned by the authenticated user."""
    conversation_service.delete_conversation(session_id, current_user.id)
    return None


@router.patch(
    "/conversations/{session_id}/rename",
    response_model=ConversationSummary,
    tags=["conversations"],
    summary="Rename a conversation",
)
async def rename_conversation(
    session_id: str,
    req: RenameRequest,
    current_user: User = Depends(get_current_user),
):
    """Rename a conversation thread if owned by the authenticated user."""
    return conversation_service.rename_conversation(
        session_id=session_id,
        user_id=current_user.id,
        title=req.title,
    )


@router.post(
    "/conversations/{session_id}/pin",
    response_model=ConversationSummary,
    tags=["conversations"],
    summary="Toggle pin status",
)
async def pin_conversation(
    session_id: str,
    req: PinRequest,
    current_user: User = Depends(get_current_user),
):
    """Toggle the pinned status of a conversation thread if owned by the authenticated user."""
    return conversation_service.pin_conversation(
        session_id=session_id,
        user_id=current_user.id,
        pinned=req.pinned,
    )
