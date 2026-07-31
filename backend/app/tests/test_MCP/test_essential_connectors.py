"""
Jarvis AIOS — Essential MCP Connectors Test Suite
--------------------------------------------------

Automated test suite verifying GitHub MCP read-only enforcement, Filesystem MCP workspace security,
health monitoring metrics, and MCPManager transparent tool dispatching.
"""

import pytest
from app.MCP.servers.github import GitHubMCPClient
from app.MCP.servers.filesystem import FilesystemMCPClient, validate_workspace_path, get_workspace_root
from app.MCP.mcp_manager import get_mcp_manager
from app.MCP.health_monitor import get_mcp_health_monitor


def test_github_mcp_read_only_tools():
    """Verify GitHubMCPClient executes read-only capabilities cleanly."""
    gh = GitHubMCPClient()
    gh.initialize()

    repo = gh.execute_tool("get_repository", owner="jarvis-aios", repo="jarvis")
    assert repo["name"] == "jarvis"
    assert repo["read_only"] is True

    branches = gh.execute_tool("list_branches", owner="jarvis-aios", repo="jarvis")
    assert len(branches) >= 2
    assert branches[0]["name"] == "main"

    readme = gh.execute_tool("get_readme", owner="jarvis-aios", repo="jarvis")
    assert "# jarvis" in readme

    files = gh.execute_tool("browse_files", owner="jarvis-aios", repo="jarvis")
    assert len(files) >= 4

    commits = gh.execute_tool("list_commits", owner="jarvis-aios", repo="jarvis")
    assert len(commits) >= 1


def test_github_mcp_enforces_read_only_rejection():
    """Verify GitHubMCPClient strictly rejects write or mutation attempts."""
    gh = GitHubMCPClient()
    gh.initialize()

    with pytest.raises(PermissionError) as exc_info:
        gh.execute_tool("create_pull_request", owner="jarvis-aios", repo="jarvis")
    assert "strictly READ-ONLY" in str(exc_info.value)

    with pytest.raises(PermissionError):
        gh.execute_tool("write_file", owner="jarvis-aios", repo="jarvis")

    with pytest.raises(PermissionError):
        gh.execute_tool("delete_file", owner="jarvis-aios", repo="jarvis")


def test_filesystem_mcp_operations():
    """Verify FilesystemMCPClient executes write_file, read_file, list_directory, search_files."""
    fs = FilesystemMCPClient()
    fs.initialize()

    # 1. Write file
    w_res = fs.execute_tool("write_file", path="mcp_test/sample.txt", content="Hello MCP Filesystem!")
    assert w_res["status"] == "success"

    # 2. Read file
    content = fs.execute_tool("read_file", path="mcp_test/sample.txt")
    assert content == "Hello MCP Filesystem!"

    # 3. List directory
    entries = fs.execute_tool("list_directory", path="mcp_test")
    assert "sample.txt" in entries

    # 4. Search files
    matches = fs.execute_tool("search_files", query="sample")
    assert any("sample.txt" in m for m in matches)

    # 5. Metadata
    meta = fs.execute_tool("get_file_metadata", path="mcp_test/sample.txt")
    assert meta["name"] == "sample.txt"
    assert meta["size_bytes"] > 0


def test_filesystem_mcp_workspace_security_containment():
    """Verify validate_workspace_path rejects parent traversal, absolute outside paths, and home directory traversal."""
    root = get_workspace_root()

    # 1. Parent traversal rejection
    with pytest.raises(ValueError) as exc1:
        validate_workspace_path("../outside.txt", root)
    assert "directory traversal is forbidden" in str(exc1.value).lower()

    # 2. Home directory traversal rejection
    with pytest.raises(ValueError) as exc2:
        validate_workspace_path("~/secret.txt", root)
    assert "home directory traversal is forbidden" in str(exc2.value).lower()

    # 3. Absolute path outside workspace root rejection
    with pytest.raises(ValueError) as exc3:
        validate_workspace_path("/etc/passwd", root)
    assert "access denied" in str(exc3.value).lower() or "forbidden" in str(exc3.value).lower()


def test_mcp_manager_transparent_dispatch():
    """Verify MCPManager dispatches calls to github_mcp and filesystem_mcp transparently."""
    manager = get_mcp_manager()
    manager.initialize()

    # Dispatch to github_mcp
    repo_res = manager.execute_tool("github_mcp", "get_repository", owner="testowner", repo="testrepo")
    assert repo_res["name"] == "testrepo"

    # Dispatch to filesystem_mcp
    w_res = manager.execute_tool("filesystem_mcp", "write_file", path="transparent_test.txt", content="Transparent execution")
    assert w_res["status"] == "success"

    r_res = manager.execute_tool("filesystem_mcp", "read_file", path="transparent_test.txt")
    assert r_res == "Transparent execution"


def test_health_monitoring_extension():
    """Verify MCPHealthMonitor records connector-specific health metrics."""
    monitor = get_mcp_health_monitor()
    monitor.update_health("github_mcp", status="online", latency_ms=3.2)
    monitor.update_health("filesystem_mcp", status="online", latency_ms=0.5)

    all_h = monitor.get_all_health()
    assert "github_mcp" in all_h
    assert "filesystem_mcp" in all_h
    assert all_h["github_mcp"]["authenticated"] is True
    assert all_h["filesystem_mcp"]["workspace_valid"] is True
