"""
Jarvis AIOS
--------------------
Unit Tests for Native Tool Calling Foundation (Sprint 6.1A)

Tests metadata validation, JSON schema export, registry discovery & search,
permission layer (RBAC & HITL), sync/async/streaming execution, timeout handling,
ToolResult normalization, and backward compatibility.
"""

import pytest
import asyncio
from typing import AsyncGenerator

from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, ToolResult, PermissionLevel, ExecutionStatus
from app.Tools.permissions import ToolPermissionValidator, ToolPermissionError
from app.Tools.registry import ToolRegistry
from app.Tools.engine import ToolEngine


# Mock Tools for Testing

class DummySyncTool(Tool):
    name = "dummy_sync_tool"
    description = "A dummy synchronous tool for testing."

    def execute(self, val: int = 10) -> int:
        if val < 0:
            raise ValueError("Value cannot be negative.")
        return val * 2


class DummyAsyncTool(Tool):
    def __init__(self) -> None:
        meta = ToolMetadata(
            name="dummy_async_tool",
            description="A dummy async tool.",
            category="testing",
            tags=["test", "async"],
            permission_level=PermissionLevel.USER,
            requires_approval=False,
            timeout_seconds=2.0,
            parameter_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        )
        super().__init__(metadata=meta)

    def execute(self, text: str) -> str:
        return text.upper()

    async def execute_async(self, text: str) -> str:
        await asyncio.sleep(0.01)
        return text.upper()


class DummyStreamTool(Tool):
    def __init__(self) -> None:
        meta = ToolMetadata(
            name="dummy_stream_tool",
            description="A streaming test tool.",
            supports_streaming=True,
        )
        super().__init__(metadata=meta)

    def execute(self, text: str) -> str:
        return text

    async def execute_stream(self, text: str) -> AsyncGenerator[str, None]:
        for char in text:
            yield char


class SlowTimeoutTool(Tool):
    def __init__(self) -> None:
        meta = ToolMetadata(
            name="slow_timeout_tool",
            description="Tool that sleeps longer than timeout.",
            timeout_seconds=0.1,
        )
        super().__init__(metadata=meta)

    def execute(self) -> str:
        import time
        time.sleep(0.5)
        return "done"

    async def execute_async(self) -> str:
        await asyncio.sleep(0.5)
        return "done"


class AdminOnlyTool(Tool):
    def __init__(self) -> None:
        meta = ToolMetadata(
            name="admin_only_tool",
            description="Tool restricted to admins.",
            permission_level=PermissionLevel.ADMIN,
        )
        super().__init__(metadata=meta)

    def execute() -> str:
        return "admin_secret"


class HITLApprovalTool(Tool):
    def __init__(self) -> None:
        meta = ToolMetadata(
            name="hitl_approval_tool",
            description="Tool requiring human approval.",
            requires_approval=True,
        )
        super().__init__(metadata=meta)

    def execute() -> str:
        return "approved_output"


class DisabledTool(Tool):
    def __init__(self) -> None:
        meta = ToolMetadata(
            name="disabled_tool",
            description="A disabled tool.",
            enabled=False,
        )
        super().__init__(metadata=meta)

    def execute() -> str:
        return "disabled"


# Tests

def test_tool_metadata_and_schema_export():
    """Verify ToolMetadata initialization and OpenAI JSON Schema export."""
    tool = DummyAsyncTool()
    assert tool.metadata.name == "dummy_async_tool"
    assert tool.metadata.category == "testing"
    assert "test" in tool.metadata.tags

    schema = tool.to_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "dummy_async_tool"
    assert schema["function"]["parameters"]["properties"]["text"]["type"] == "string"


def test_tool_registry_operations():
    """Verify ToolRegistry register, get, unregister, search, discover, schemas."""
    reg = ToolRegistry()
    sync_tool = DummySyncTool()
    async_tool = DummyAsyncTool()

    reg.register(sync_tool)
    reg.register(async_tool)

    assert reg.get("dummy_sync_tool") == sync_tool
    assert reg.get("dummy_async_tool") == async_tool

    # Discovery by tag
    discovered = reg.discover(tag="async")
    assert len(discovered) == 1
    assert discovered[0].name == "dummy_async_tool"

    # Search
    search_res = reg.search("dummy")
    assert len(search_res) == 2

    # Schemas export
    exported = reg.schemas(names=["dummy_sync_tool", "dummy_async_tool"])
    assert len(exported) == 2

    # Unregister
    reg.unregister("dummy_sync_tool")
    with pytest.raises(ValueError, match="not registered"):
        reg.get("dummy_sync_tool")


def test_permission_validator():
    """Verify RBAC and approval checks in ToolPermissionValidator."""
    validator = ToolPermissionValidator()
    admin_meta = AdminOnlyTool().metadata

    # User level should fail
    with pytest.raises(ToolPermissionError, match="Permission denied"):
        validator.validate(admin_meta, caller_context={"permission_level": "USER"})

    # Admin level should pass
    validator.validate(admin_meta, caller_context={"permission_level": "ADMIN"})
    validator.validate(admin_meta, caller_context={"permission_level": PermissionLevel.ADMIN})

    # HITL Approval
    hitl_meta = HITLApprovalTool().metadata
    assert validator.is_approval_required(hitl_meta, caller_context={}) is True
    assert validator.is_approval_required(hitl_meta, caller_context={"is_approved": True}) is False


@pytest.mark.anyio
async def test_tool_engine_async_execution():
    """Verify ToolEngine execute_async returns standardized ToolResult."""
    reg = ToolRegistry()
    async_tool = DummyAsyncTool()
    reg.register(async_tool)

    test_engine = ToolEngine()
    # Patch registry lookup in pipeline
    from unittest.mock import patch
    with patch("app.Tools.pipeline.registry", reg):
        res: ToolResult = await test_engine.execute_async("dummy_async_tool", text="hello")
        assert isinstance(res, ToolResult)
        assert res.status == ExecutionStatus.SUCCESS
        assert res.output == "HELLO"
        assert res.duration_ms >= 0.0
        assert res.execution_id.startswith("exec_")


@pytest.mark.anyio
async def test_tool_engine_streaming():
    """Verify ToolEngine execute_stream chunk generator."""
    reg = ToolRegistry()
    stream_tool = DummyStreamTool()
    reg.register(stream_tool)

    test_engine = ToolEngine()
    from unittest.mock import patch
    with patch("app.Tools.pipeline.registry", reg):
        chunks = []
        async for chunk in test_engine.execute_stream("dummy_stream_tool", text="abc"):
            chunks.append(chunk)
        assert chunks == ["a", "b", "c"]


@pytest.mark.anyio
async def test_tool_engine_permission_denial_and_approval():
    """Verify ToolEngine handles permission denial and HITL approval states."""
    reg = ToolRegistry()
    admin_tool = AdminOnlyTool()
    hitl_tool = HITLApprovalTool()
    reg.register(admin_tool)
    reg.register(hitl_tool)

    test_engine = ToolEngine()
    from unittest.mock import patch
    with patch("app.Tools.pipeline.registry", reg):
        # Admin tool called by normal user
        res_denied = await test_engine.execute_async("admin_only_tool", caller_context={"role": "USER"})
        assert res_denied.status == ExecutionStatus.PERMISSION_DENIED
        assert "Permission denied" in res_denied.error

        # HITL tool called without approval
        res_hitl = await test_engine.execute_async("hitl_approval_tool", caller_context={})
        assert res_hitl.status == ExecutionStatus.PENDING_APPROVAL
        assert res_hitl.metadata.get("requires_approval") is True


@pytest.mark.anyio
async def test_tool_engine_timeout_handling():
    """Verify ToolEngine catches timeout and returns TIMEOUT status."""
    reg = ToolRegistry()
    slow_tool = SlowTimeoutTool()
    reg.register(slow_tool)

    test_engine = ToolEngine()
    from unittest.mock import patch
    with patch("app.Tools.pipeline.registry", reg):
        res = await test_engine.execute_async("slow_timeout_tool")
        assert res.status == ExecutionStatus.TIMEOUT
        assert "timed out" in res.error


def test_legacy_sync_execution_and_backward_compatibility():
    """Verify legacy `engine.execute(...)` calls remain 100% backward compatible."""
    from app.Tools.engine import engine

    # Test builtin tools through engine.execute
    calc_res = engine.execute("calculator", expression="2 + 3 * 4")
    assert calc_res == 14.0

    # Test returning full ToolResult object explicitly
    res_obj: ToolResult = engine.execute("calculator", expression="10 / 2", return_result_object=True)
    assert isinstance(res_obj, ToolResult)
    assert res_obj.status == ExecutionStatus.SUCCESS
    assert res_obj.output == 5.0

    # Test legacy error handling raises ValueError
    with pytest.raises(ValueError):
        engine.execute("calculator", expression="invalid_syntax ???")
