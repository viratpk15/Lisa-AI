"""
Jarvis AIOS
--------------------
Modular Tool Execution Pipeline

Implements a stage-based execution pipeline for tool invocations:
Request -> Permission Stage -> Validation Stage -> Execution Stage -> Normalization -> Observability -> Return ToolResult.
"""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional, AsyncGenerator

from app.Tools.metadata import ToolResult, ExecutionStatus
from app.Tools.permissions import (
    permission_validator,
    ToolPermissionError,
    ToolDisabledError,
)
from app.Tools.registry import registry
from app.Observability.trace import measure_time, calculate_duration
from app.Observability.manager import observability_manager


def _validate_tool_name(tool_name: str) -> None:
    """Validate tool name formatting and safety."""
    if not isinstance(tool_name, str):
        raise ValueError(f"Tool name must be a string. Received {type(tool_name).__name__}.")
    if not tool_name.strip():
        raise ValueError("Tool name must not be empty.")
    if len(tool_name) > 64:
        raise ValueError("Tool name too long. Maximum length is 64 characters.")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    for char in tool_name:
        if char not in allowed:
            raise ValueError(f"Tool name contains unsafe character: '{char}'.")


def _validate_arguments(kwargs: Dict[str, Any]) -> None:
    """Validate tool arguments for dict type and size limit."""
    if not isinstance(kwargs, dict):
        raise ValueError(f"Tool arguments must be a dictionary. Received {type(kwargs).__name__}.")
    total_chars = sum(len(str(k)) + len(str(v)) for k, v in kwargs.items())
    if total_chars > 100_000:
        raise ValueError("Tool arguments too large. Exceeds size limit of 100,000 characters.")


class ExecutionPipeline:
    """
    Modular Execution Pipeline for Tool Engine.
    Executes each invocation stage sequentially and normalizes every output
    into a provider-independent ToolResult object.
    """

    async def run_async(
        self,
        tool_name: str,
        kwargs: Dict[str, Any],
        caller_context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Run tool invocation through the pipeline asynchronously."""
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        started_at = datetime.now(timezone.utc)
        start_time = measure_time()

        # 1. Validation Stage
        try:
            _validate_tool_name(tool_name)
            _validate_arguments(kwargs)
            tool = registry.get(tool_name)
        except (ValueError, KeyError) as e:
            completed_at = datetime.now(timezone.utc)
            duration_ms = calculate_duration(start_time)
            err_msg = str(e)
            observability_manager.record_tool_call(
                tool_name=tool_name,
                duration_ms=duration_ms,
                success=False,
                error=err_msg,
            )
            return ToolResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status=ExecutionStatus.ERROR,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                error=err_msg,
                metadata={"execution_id": execution_id},
            )

        # 2. Permission Stage
        try:
            permission_validator.validate(tool.metadata, caller_context)
        except (ToolPermissionError, ToolDisabledError) as e:
            completed_at = datetime.now(timezone.utc)
            duration_ms = calculate_duration(start_time)
            err_msg = str(e)
            observability_manager.record_tool_call(
                tool_name=tool_name,
                duration_ms=duration_ms,
                success=False,
                error=err_msg,
            )
            return ToolResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status=ExecutionStatus.PERMISSION_DENIED if isinstance(e, ToolPermissionError) else ExecutionStatus.ERROR,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                error=err_msg,
                metadata={"permission_level": tool.metadata.permission_level.value},
            )

        # 3. Human-in-the-Loop Approval Check Stage
        if permission_validator.is_approval_required(tool.metadata, caller_context):
            completed_at = datetime.now(timezone.utc)
            duration_ms = calculate_duration(start_time)
            return ToolResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status=ExecutionStatus.PENDING_APPROVAL,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                metadata={"requires_approval": True},
            )

        # 4. Execution & Observability Stage
        try:
            if tool.metadata.timeout_seconds > 0:
                raw_output = await asyncio.wait_for(
                    tool.execute_async(**kwargs),
                    timeout=tool.metadata.timeout_seconds,
                )
            else:
                raw_output = await tool.execute_async(**kwargs)

            completed_at = datetime.now(timezone.utc)
            duration_ms = calculate_duration(start_time)

            observability_manager.record_tool_call(
                tool_name=tool_name,
                duration_ms=duration_ms,
                success=True,
            )

            # Normalization Stage
            structured = raw_output if isinstance(raw_output, dict) else {"result": raw_output}
            return ToolResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status=ExecutionStatus.SUCCESS,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                output=raw_output,
                structured_output=structured,
                metadata={
                    "permission_level": tool.metadata.permission_level.value,
                    "execution_id": execution_id,
                },
            )

        except asyncio.TimeoutError:
            completed_at = datetime.now(timezone.utc)
            duration_ms = calculate_duration(start_time)
            err_msg = f"Tool execution timed out after {tool.metadata.timeout_seconds} seconds."
            observability_manager.record_tool_call(
                tool_name=tool_name,
                duration_ms=duration_ms,
                success=False,
                error=err_msg,
            )
            return ToolResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status=ExecutionStatus.TIMEOUT,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                error=err_msg,
            )
        except Exception as e:
            completed_at = datetime.now(timezone.utc)
            duration_ms = calculate_duration(start_time)
            err_msg = str(e) or f"An error occurred while executing tool '{tool_name}'."
            observability_manager.record_tool_call(
                tool_name=tool_name,
                duration_ms=duration_ms,
                success=False,
                error=err_msg,
            )
            return ToolResult(
                tool_name=tool_name,
                execution_id=execution_id,
                status=ExecutionStatus.ERROR,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                error=err_msg,
            )

    async def run_stream(
        self,
        tool_name: str,
        kwargs: Dict[str, Any],
        caller_context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Any, None]:
        """Stream tool output chunks using the same pipeline validation."""
        _validate_tool_name(tool_name)
        _validate_arguments(kwargs)
        tool = registry.get(tool_name)
        permission_validator.validate(tool.metadata, caller_context)

        async for chunk in tool.execute_stream(**kwargs):
            yield chunk


pipeline = ExecutionPipeline()
