"""
Jarvis AIOS
--------------------
Tools REST API Router

Exposes production endpoints for tool discovery, category search, schema retrieval,
and tool execution (sync/async & SSE streaming). Always delegates to ToolEngine.
"""

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import StreamingResponse

from app.Tools.engine import engine
from app.Tools.registry import registry
from app.Tools.metadata import ToolMetadata, ToolResult
from app.Auth.dependencies import get_current_user
from app.Auth.models import User

router = APIRouter(prefix="/tools", tags=["Tools Engine"])


@router.get(
    "",
    response_model=List[ToolMetadata],
    summary="Discover Tools",
    description="Discover registered tools with optional filtering by category, tag, or search query.",
)
def list_tools(
    category: Optional[str] = Query(None, description="Filter tools by category."),
    tag: Optional[str] = Query(None, description="Filter tools by tag."),
    query: Optional[str] = Query(None, description="Search query string."),
    current_user: User = Depends(get_current_user),
) -> List[ToolMetadata]:
    if query:
        return registry.search(query)
    return registry.discover(category=category, tag=tag)


@router.get(
    "/categories",
    response_model=List[str],
    summary="List Tool Categories",
    description="Returns a sorted list of unique tool categories.",
)
def list_categories(
    current_user: User = Depends(get_current_user),
) -> List[str]:
    return registry.categories()


@router.get(
    "/{tool_name}",
    response_model=Dict[str, Any],
    summary="Get Tool Details & Schema",
    description="Returns tool metadata and OpenAPI JSON Schema for LLM binding.",
)
def get_tool(
    tool_name: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        tool = registry.get(tool_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found.",
        ) from e

    return {
        "metadata": tool.metadata.model_dump(mode="json"),
        "schema": tool.to_schema(),
    }


@router.post(
    "/{tool_name}/execute",
    response_model=ToolResult,
    summary="Execute Tool",
    description="Executes a registered tool via ToolEngine pipeline and returns ToolResult.",
)
async def execute_tool(
    tool_name: str,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
) -> ToolResult:
    tool_args = payload.get("arguments", payload)
    caller_ctx = payload.get("caller_context", {})

    # Inject current user ID and role into context
    caller_ctx.setdefault("user_id", current_user.id)
    caller_ctx.setdefault("role", getattr(current_user, "role", "USER"))

    try:
        result = await engine.execute_async(
            tool_name=tool_name,
            caller_context=caller_ctx,
            **tool_args,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal tool execution error: {str(e)}",
        ) from e


@router.post(
    "/{tool_name}/execute/stream",
    summary="Stream Tool Execution",
    description="Executes a tool in streaming mode returning Server-Sent Events (SSE).",
)
async def stream_tool_execution(
    tool_name: str,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    tool_args = payload.get("arguments", payload)
    caller_ctx = payload.get("caller_context", {})
    caller_ctx.setdefault("user_id", current_user.id)
    caller_ctx.setdefault("role", getattr(current_user, "role", "USER"))

    async def event_generator():
        try:
            async for chunk in engine.execute_stream(
                tool_name=tool_name,
                caller_context=caller_ctx,
                **tool_args,
            ):
                data_str = json.dumps({"chunk": chunk}, default=str)
                yield f"data: {data_str}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            err_str = json.dumps({"error": str(e)})
            yield f"data: {err_str}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
