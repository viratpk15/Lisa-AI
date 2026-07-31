"""
Jarvis AIOS
-----------
MCP Verification Script

Verifies the MCP (Model Context Protocol) module is correctly configured
and all imports work as expected.
"""

import sys
from pathlib import Path
from typing import Any

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


# =============================================================================
# Helper Functions
# =============================================================================


def _create_test_file(workspace: Path, filename: str, content: str) -> Path:
    """Create a test file in the workspace directory."""
    test_file = workspace / filename
    test_file.write_text(content, encoding="utf-8")
    return test_file


def _verify_server(client_class: Any, client_getter: Any, name: str, expected_tools: list[str]) -> Any:
    """Verify MCP server client creation and tool registration.

    Args:
        client_class: The MCP client class to instantiate.
        client_getter: Function to get the client singleton (or None for new instance).
        name: Server name for output messages.
        expected_tools: List of expected tool names.

    Returns:
        The initialized client instance.
    """
    client = client_getter() if client_getter else client_class()
    print(f"✓ Created {name}MCPClient: {client.config.name}")
    client.initialize()
    tools = client.list_tools()
    for tool in expected_tools:
        assert tool in tools, f"{tool} tool missing"
    print(f"✓ Tools registered: {tools}")
    return client


def _verify_mock_metadata(result: dict[str, Any], expected_provider: str) -> bool:
    """Verify mock metadata in a result dict."""
    assert result.get("mock") is True, "Result should have mock=True"
    assert result.get("provider") == expected_provider, (
        f"Result should have provider={expected_provider}"
    )
    return True


# =============================================================================
# MCP Core Verification
# =============================================================================


def verify_mcp_imports() -> bool:
    """Verify all MCP module imports work correctly."""
    print("=" * 60)
    print("MCP Module Import Verification")
    print("=" * 60)

    errors = []

    imports_to_test = [
        ("MCPClient, MCPServerConfig", "app.MCP.client"),
        ("MCPRegistry", "app.MCP.registry"),
        ("MCPServerConfigModel, MCPConfigModel", "app.MCP.models"),
        ("FilesystemMCPClient, get_filesystem_server", "app.MCP"),
        ("BrowserMCPClient, get_browser_server", "app.MCP"),
        ("GitHubMCPClient, get_github_server", "app.MCP"),
        ("get_mcp_registry, MCPClient, MCPRegistry", "app.MCP"),
    ]

    for names, module in imports_to_test:
        try:
            exec(f"from {module} import {names}")
            print(f"✓ {names} imported successfully")
        except ImportError as e:
            errors.append(f"✗ Failed to import {names}: {e}")
            print(errors[-1])

    return len(errors) == 0


def verify_mcp_dataclass() -> bool:
    """Verify MCPServerConfig dataclass functionality."""
    print("\n" + "=" * 60)
    print("MCPServerConfig Dataclass Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP.client import MCPServerConfig

        config = MCPServerConfig(
            name="test_server",
            description="Test server for verification",
            enabled=True,
            capabilities=["tool1", "tool2"],
        )

        assert config.name == "test_server"
        assert config.description == "Test server for verification"
        assert config.enabled is True
        assert config.capabilities == ["tool1", "tool2"]
        print(f"✓ Created MCPServerConfig: {config.name}")

    except Exception as e:
        errors.append(f"✗ MCPServerConfig test failed: {e}")
        print(errors[-1])

    try:
        config = MCPServerConfig(name="default_server")
        assert config.capabilities == []
        print("✓ Default capabilities initialization works correctly")
    except Exception as e:
        errors.append(f"✗ Default capabilities test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_mcp_models() -> bool:
    """Verify Pydantic MCP configuration models."""
    print("\n" + "=" * 60)
    print("MCP Pydantic Models Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP.models import MCPServerConfigModel, MCPConfigModel

        server_config = MCPServerConfigModel(
            name="pydantic_server",
            description="Pydantic server config",
            enabled=True,
            timeout=60,
        )

        assert server_config.name == "pydantic_server"
        assert server_config.timeout == 60
        print(f"✓ Created MCPServerConfigModel: {server_config.name}")

        config = MCPConfigModel(servers=[server_config], auto_register=True)
        assert config.auto_register is True
        enabled_servers = config.get_enabled_servers()
        assert len(enabled_servers) == 1
        print(f"✓ MCPConfigModel created with {len(enabled_servers)} enabled server(s)")

    except Exception as e:
        errors.append(f"✗ MCP Pydantic models test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_mcp_registry() -> bool:
    """Verify MCPRegistry functionality."""
    print("\n" + "=" * 60)
    print("MCPRegistry Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP.registry import MCPRegistry

        registry = MCPRegistry()
        assert registry.list_clients() == []
        assert registry.has_client("nonexistent") is False
        print("✓ Empty registry state verified")

    except Exception as e:
        errors.append(f"✗ MCPRegistry basic test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_immutability() -> bool:
    """Verify Pydantic models are immutable (frozen=True)."""
    print("\n" + "=" * 60)
    print("Immutability Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP.models import MCPServerConfigModel

        server_config = MCPServerConfigModel(name="test")
        try:
            server_config.name = "modified"  # type: ignore
            errors.append("✗ MCPServerConfigModel should be immutable (frozen)")
        except Exception:
            print("✓ MCPServerConfigModel is properly frozen (immutable)")

    except Exception as e:
        errors.append(f"✗ Immutability test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


# =============================================================================
# Filesystem MCP Verification
# =============================================================================


def verify_filesystem_server() -> bool:
    """Verify Filesystem MCP Server implementation."""
    print("\n" + "=" * 60)
    print("Filesystem MCP Server Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP.servers.filesystem import FilesystemMCPClient
        from app.MCP import get_filesystem_server

        _verify_server(FilesystemMCPClient, get_filesystem_server, "Filesystem", ["list_directory", "read_file"])

    except Exception as e:
        errors.append(f"✗ FilesystemMCPClient test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_filesystem_registration() -> bool:
    """Verify Filesystem server registration with MCP registry."""
    print("\n" + "=" * 60)
    print("Filesystem Server Registration Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP import get_mcp_registry, get_filesystem_server

        registry = get_mcp_registry()
        client = get_filesystem_server()

        registry.register(client)
        print(f"✓ Registered Filesystem MCP server: {client.config.name}")

        assert registry.has_client("filesystem") is True
        print("✓ Registry has 'filesystem' client")

        all_tools = registry.list_all_tools()
        assert "list_directory" in all_tools
        assert "read_file" in all_tools
        print(f"✓ All tools available: {sorted(all_tools)}")

    except Exception as e:
        errors.append(f"✗ Registration test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_filesystem_tools() -> bool:
    """Verify Filesystem MCP tools functionality."""
    print("\n" + "=" * 60)
    print("Filesystem MCP Tools Verification")
    print("=" * 60)

    errors = []
    workspace = Path.cwd() / "workspace"

    try:
        workspace.mkdir(parents=True, exist_ok=True)
        test_file = _create_test_file(
            workspace, "test_verify_fs.txt", "Hello from Filesystem MCP!"
        )
        test_dir = workspace / "test_subdir_fs"
        test_dir.mkdir(parents=True, exist_ok=True)
        _create_test_file(test_dir, "nested_fs.txt", "nested content")

        from app.MCP import get_filesystem_server

        client = get_filesystem_server()
        client.initialize()

        entries = client._list_directory(path="")
        assert "test_verify_fs.txt" in entries
        print(f"✓ list_directory (root): found {len(entries)} entries")

        subdir_entries = client._list_directory(path="test_subdir_fs")
        assert "nested_fs.txt" in subdir_entries
        print(f"✓ list_directory (subdir): found {len(subdir_entries)} entries")

        content = client._read_file(path="test_verify_fs.txt")
        assert content == "Hello from Filesystem MCP!"
        print(f"✓ read_file: read {len(content)} characters")

        # Cleanup
        test_file.unlink()
        (test_dir / "nested_fs.txt").unlink()
        test_dir.rmdir()

    except Exception as e:
        errors.append(f"✗ Tool functionality test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


# =============================================================================
# Browser MCP Verification
# =============================================================================


def verify_browser_server() -> bool:
    """Verify Browser MCP Server implementation."""
    print("\n" + "=" * 60)
    print("Browser MCP Server Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP.servers.browser import BrowserMCPClient
        from app.MCP import get_browser_server

        _verify_server(BrowserMCPClient, get_browser_server, "Browser", ["search_web", "fetch_page"])

    except Exception as e:
        errors.append(f"✗ BrowserMCPClient test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_browser_registration() -> bool:
    """Verify Browser server registration with MCP registry."""
    print("\n" + "=" * 60)
    print("Browser Server Registration Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP import get_mcp_registry, get_browser_server

        registry = get_mcp_registry()
        client = get_browser_server()

        registry.register(client)
        print(f"✓ Registered Browser MCP server: {client.config.name}")

        assert registry.has_client("browser") is True
        print("✓ Registry has 'browser' client")

        all_tools = registry.list_all_tools()
        assert "search_web" in all_tools
        assert "fetch_page" in all_tools
        print(f"✓ All tools available: {sorted(all_tools)}")

    except Exception as e:
        errors.append(f"✗ Registration test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_browser_tools() -> bool:
    """Verify Browser MCP tools functionality with mock responses."""
    print("\n" + "=" * 60)
    print("Browser MCP Tools Verification (Mocked)")
    print("=" * 60)

    errors = []

    try:
        from app.MCP import get_browser_server

        client = get_browser_server()
        client.initialize()

        results = client._search_web(query="test query")
        assert isinstance(results, list) and len(results) == 2
        assert "url" in results[0] and "snippet" in results[0]
        _verify_mock_metadata(results[0], "browser-mcp")
        print(f"✓ search_web: returned {len(results)} mock results with metadata")

        content = client._fetch_page(url="https://example.com")
        assert "Mock page content" in content
        assert "mock': true" in content and "provider': 'browser-mcp'" in content
        print(f"✓ fetch_page: returned {len(content)} characters with metadata")

        try:
            client._fetch_page(url="invalid-url")
            errors.append("✗ fetch_page should reject invalid URLs")
        except ValueError:
            print("✓ fetch_page: correctly rejects invalid URLs")

    except Exception as e:
        errors.append(f"✗ Tool functionality test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


# =============================================================================
# GitHub MCP Verification
# =============================================================================


def verify_github_server() -> bool:
    """Verify GitHub MCP Server implementation."""
    print("\n" + "=" * 60)
    print("GitHub MCP Server Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP.servers.github import GitHubMCPClient
        from app.MCP import get_github_server

        _verify_server(GitHubMCPClient, get_github_server, "GitHub", ["get_repository", "list_repository_files"])

    except Exception as e:
        errors.append(f"✗ GitHubMCPClient test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_github_registration() -> bool:
    """Verify GitHub server registration with MCP registry."""
    print("\n" + "=" * 60)
    print("GitHub Server Registration Verification")
    print("=" * 60)

    errors = []

    try:
        from app.MCP import get_mcp_registry, get_github_server

        registry = get_mcp_registry()
        client = get_github_server()

        registry.register(client)
        print(f"✓ Registered GitHub MCP server: {client.config.name}")

        assert registry.has_client("github") is True
        print("✓ Registry has 'github' client")

        all_tools = registry.list_all_tools()
        assert "get_repository" in all_tools
        assert "list_repository_files" in all_tools
        print(f"✓ All tools available: {sorted(all_tools)}")

    except Exception as e:
        errors.append(f"✗ Registration test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


def verify_github_tools() -> bool:
    """Verify GitHub MCP tools functionality with mock responses."""
    print("\n" + "=" * 60)
    print("GitHub MCP Tools Verification (Mocked)")
    print("=" * 60)

    errors = []

    try:
        from app.MCP import get_github_server

        client = get_github_server()
        client.initialize()

        repo = client._get_repository(owner="testuser", repo="testrepo")
        assert isinstance(repo, dict)
        assert repo["full_name"] == "testuser/testrepo"
        _verify_mock_metadata(repo, "github-mcp")
        print(f"✓ get_repository: returned mock repo for {repo['full_name']}")

        files = client._list_repository_files(owner="testuser", repo="testrepo")
        assert isinstance(files, list) and len(files) == 6
        assert "testuser/testrepo/README.md" in files
        print(f"✓ list_repository_files: returned {len(files)} mock files")

    except Exception as e:
        errors.append(f"✗ Tool functionality test failed: {e}")
        print(errors[-1])

    return len(errors) == 0


# =============================================================================
# Main
# =============================================================================


def main() -> int:
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("MCP Module Verification Script")
    print("=" * 60 + "\n")

    all_passed = True

    # Core MCP Verification
    all_passed &= verify_mcp_imports()
    all_passed &= verify_mcp_dataclass()
    all_passed &= verify_mcp_models()
    all_passed &= verify_mcp_registry()
    all_passed &= verify_immutability()

    # MCP Server Verification
    all_passed &= verify_filesystem_server()
    all_passed &= verify_filesystem_registration()
    all_passed &= verify_filesystem_tools()
    all_passed &= verify_browser_server()
    all_passed &= verify_browser_registration()
    all_passed &= verify_browser_tools()
    all_passed &= verify_github_server()
    all_passed &= verify_github_registration()
    all_passed &= verify_github_tools()

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All MCP verifications passed!")
        return 0
    else:
        print("✗ Some MCP verifications failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())