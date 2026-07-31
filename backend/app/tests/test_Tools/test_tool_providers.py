"""
Jarvis AIOS
--------------------
Unit Tests for Built-in Tool Providers (Sprint 6.1B)

Tests FilesystemTool, TerminalTool, GitTool, WebSearchTool, and BrowserTool.
Verifies sandbox path safety, command allowlists, read-only vs write actions,
and unconfigured provider graceful fallbacks.
"""

import pytest
import tempfile
from pathlib import Path

from app.Tools.filesystem_tool import FilesystemTool
from app.Tools.terminal_tool import TerminalTool
from app.Tools.git_tool import GitTool
from app.Tools.web_search_tool import WebSearchTool
from app.Tools.browser_tool import BrowserTool


def test_filesystem_tool_sandbox_and_operations():
    """Test FilesystemTool sandboxing, write, read, list, mkdir, delete, and path traversal prevention."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir).resolve()
        tool = FilesystemTool(workspace_root=sandbox)

        # Write file
        res = tool.execute(action="write", path="test.txt", content="Hello Jarvis")
        assert res["status"] == "success"
        assert res["bytes_written"] == 12

        # Read file
        read_res = tool.execute(action="read", path="test.txt")
        assert read_res["content"] == "Hello Jarvis"

        # Exists
        exists_res = tool.execute(action="exists", path="test.txt")
        assert exists_res["exists"] is True

        # Mkdir & List
        tool.execute(action="mkdir", path="subdir")
        list_res = tool.execute(action="list", path="")
        assert len(list_res["items"]) == 2

        # Path Traversal Security Check
        with pytest.raises(ValueError, match="outside sandbox"):
            tool.execute(action="read", path="../outside.txt")

        # Delete
        del_res = tool.execute(action="delete", path="test.txt")
        assert del_res["status"] == "success"
        assert not (sandbox / "test.txt").exists()


def test_terminal_tool_allowlist_and_execution():
    """Test TerminalTool command allowlist and execution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir).resolve()
        tool = TerminalTool(workspace_root=sandbox)

        # Safe command execution
        res = tool.execute(command="echo Hello Terminal")
        assert res["status"] == "success"
        assert "Hello Terminal" in res["stdout"]

        # Disallowed binary rejection
        with pytest.raises(ValueError, match="not in the allowed command list"):
            tool.execute(command="netstat -an")

        # Forbidden token rejection
        with pytest.raises(ValueError, match="forbidden token"):
            tool.execute(command="sudo ls")


def test_git_tool_read_and_write_actions():
    """Test GitTool status and read-only action verification."""
    tool = GitTool()
    res = tool.execute(action="status")
    assert res["action"] == "status"
    assert res["is_read_only"] is True

    diff_res = tool.execute(action="diff")
    assert diff_res["action"] == "diff"


def test_unconfigured_providers_graceful_fallbacks():
    """Test WebSearchTool and BrowserTool graceful unconfigured return objects."""
    search_tool = WebSearchTool(api_key=None)
    search_res = search_tool.execute(query="FastAPI tutorial")
    assert search_res["configured"] is False
    assert search_res["status"] == "not_configured"
    assert "not configured" in search_res["message"].lower()

    browser_tool = BrowserTool(browser_enabled=False)
    browser_res = browser_tool.execute(action="fetch_page", url="https://example.com")
    assert browser_res["configured"] is False
    assert browser_res["status"] == "not_configured"
    assert "not configured" in browser_res["message"].lower()
