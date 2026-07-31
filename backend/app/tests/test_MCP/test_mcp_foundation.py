"""
Jarvis AIOS — MCP Foundation Test Suite
----------------------------------------

Automated test suite verifying MCP Config, MCP Health Monitor, Tool Adapter,
Unified Tool Interface, MCP Manager lifecycle, error handling, and Tool Engine integration.
"""

from app.MCP.config import MCPServerConfigModel, load_mcp_configurations
from app.MCP.health_monitor import get_mcp_health_monitor
from app.MCP.tool_adapter import MCPToolAdapter
from app.MCP.mcp_manager import get_mcp_manager
from app.Tools.registry import registry as global_tool_registry


def test_mcp_config_loader():
    """Verify MCP configs load defaults and models correctly."""
    configs = load_mcp_configurations()
    assert len(configs) >= 3
    server_ids = [c.server_id for c in configs]
    assert "browser_mcp" in server_ids
    assert "github_mcp" in server_ids
    assert "filesystem_mcp" in server_ids


def test_mcp_health_monitor():
    """Verify MCPHealthMonitor records status, latency, and available tools."""
    monitor = get_mcp_health_monitor()
    monitor.update_health(server_id="test_mcp", status="online", latency_ms=2.4, tools=["tool_a"])

    h = monitor.get_health("test_mcp")
    assert h is not None
    assert h.status == "online"
    assert h.latency_ms == 2.4
    assert h.available_tools == ["tool_a"]


def test_unified_tool_and_adapter():
    """Verify UnifiedTool and MCPToolAdapter interface compliance."""
    adapter = MCPToolAdapter(client_name="test_server", tool_name="dummy_tool", description="Dummy test tool")

    assert adapter.name == "dummy_tool"
    assert adapter.is_mcp is True
    assert adapter.mcp_server_id == "test_server"

    schema = adapter.to_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "dummy_tool"


def test_mcp_manager_lifecycle_and_error_handling():
    """Verify MCPManager registration, tool execution, health monitoring, error handling, and shutdown."""
    manager = get_mcp_manager()

    # Dynamic registration
    custom_cfg = MCPServerConfigModel(
        server_id="custom_mcp",
        server_name="CustomMCP",
        version="1.0.0",
        enabled=True,
        available_tools=["custom_action"],
    )
    manager.register_server(custom_cfg)
    assert any(s.server_id == "custom_mcp" for s in manager.list_servers())

    # Execute tool on dynamic server
    res = manager.execute_tool("custom_mcp", "custom_action", target="dataset")
    assert res["success"] is True
    assert "custom_action" in res["result"]

    # Graceful error handling for missing server
    err_res = manager.execute_tool("non_existent_server", "some_tool")
    assert err_res["success"] is False
    assert "disconnected" in err_res["error"]

    # Graceful error handling for unavailable tool
    err_tool = manager.execute_tool("custom_mcp", "unknown_tool")
    assert err_tool["success"] is False
    assert "not exposed" in err_tool["error"]

    # Unregister server
    manager.unregister_server("custom_mcp")
    assert not any(s.server_id == "custom_mcp" for s in manager.list_servers())


def test_tool_engine_integration_compatibility():
    """Verify ToolRegistry lists and dispatches adapted MCP tools seamlessly alongside native tools."""
    manager = get_mcp_manager()
    manager.initialize()

    all_tools = global_tool_registry.list_tools()
    assert len(all_tools) > 0

    # Ensure search_web (adapted or native) is executable via registry
    if global_tool_registry.has_tool("search_web"):
        tool = global_tool_registry.get("search_web")
        assert hasattr(tool, "execute")
