"""
Jarvis AIOS — Production Local Filesystem MCP Server
----------------------------------------------------

Filesystem access through the Model Context Protocol.
Capabilities: read_file, write_file, list_directory, search_files, get_file_metadata, create_directory.

Security: Strict workspace boundary validation against JARVIS_WORKSPACE_ROOT.
Rejects absolute paths (/), parent traversal (..), and home directory traversal (~).
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List
from app.MCP.client import MCPClient, MCPServerConfig

logger = logging.getLogger(__name__)

# Maximum file size limit (2 MB)
MAX_FILE_SIZE_BYTES = 2_000_000

FILESYSTEM_MCP_TOOLS = [
    "read_file",
    "write_file",
    "list_directory",
    "search_files",
    "get_file_metadata",
    "create_directory",
]


def get_workspace_root() -> Path:
    """Get the resolved workspace root Path from env or default workspace dir."""
    env_root = os.environ.get("JARVIS_WORKSPACE_ROOT")
    if env_root:
        p = Path(env_root).resolve(strict=False)
    else:
        p = (Path.cwd() / "workspace").resolve(strict=False)
    p.mkdir(parents=True, exist_ok=True)
    return p


def validate_workspace_path(path_str: str, allowed_root: Path) -> Path:
    """Validate that path_str is strictly contained inside allowed_root."""
    if not path_str or not isinstance(path_str, str):
        raise ValueError("Path argument must be a non-empty string.")

    # 1. Check traversal keywords
    if ".." in Path(path_str).parts:
        raise ValueError("Security violation: '..' directory traversal is forbidden.")

    if path_str.startswith("~"):
        raise ValueError("Security violation: Home directory traversal is forbidden.")

    # 2. Convert to Path
    p = Path(path_str)

    # If user passed absolute path, ensure it is inside workspace root
    if p.is_absolute():
        resolved_p = p.resolve(strict=False)
    else:
        resolved_p = (allowed_root / path_str).resolve(strict=False)

    # 3. Verify containment
    try:
        resolved_p.relative_to(allowed_root)
    except ValueError:
        raise ValueError("Security violation: Access denied outside workspace root.")

    return resolved_p


class FilesystemMCPClient(MCPClient):
    """Production Filesystem MCP client with workspace containment."""

    def __init__(self, config: MCPServerConfig | None = None) -> None:
        self._config = config or MCPServerConfig(
            name="filesystem",
            description="Workspace filesystem access via MCP.",
            enabled=True,
            capabilities=FILESYSTEM_MCP_TOOLS,
        )
        self._tools: dict[str, Any] = {}

    @property
    def config(self) -> MCPServerConfig:
        return self._config

    def list_tools(self) -> list[str]:
        return FILESYSTEM_MCP_TOOLS

    def initialize(self) -> None:
        self._tools = dict.fromkeys(FILESYSTEM_MCP_TOOLS, True)

    def shutdown(self) -> None:
        self._tools.clear()

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        root = get_workspace_root()

        if tool_name not in FILESYSTEM_MCP_TOOLS:
            raise ValueError(f"Unknown Filesystem MCP tool: {tool_name}")

        try:
            if tool_name == "read_file":
                return self._read_file(root, kwargs.get("path", ""))
            elif tool_name == "write_file":
                return self._write_file(root, kwargs.get("path", ""), kwargs.get("content", ""))
            elif tool_name == "list_directory":
                return self._list_directory(root, kwargs.get("path", "."))
            elif tool_name == "search_files":
                return self._search_files(root, kwargs.get("query", ""))
            elif tool_name == "get_file_metadata":
                return self._get_file_metadata(root, kwargs.get("path", ""))
            elif tool_name == "create_directory":
                return self._create_directory(root, kwargs.get("path", ""))
            else:
                raise ValueError(f"Unhandled tool: {tool_name}")
        except Exception as e:
            logger.error("[FILESYSTEM-MCP] Tool '%s' failed: %s", tool_name, str(e))
            raise ValueError(f"Filesystem MCP error: {str(e)}") from e

    def _read_file(self, root: Path, path_str: str) -> str:
        safe_path = validate_workspace_path(path_str, root)
        if not safe_path.exists() or not safe_path.is_file():
            raise ValueError(f"File not found: {path_str}")
        if safe_path.stat().st_size > MAX_FILE_SIZE_BYTES:
            raise ValueError("File exceeds maximum allowed size (2 MB).")
        return safe_path.read_text(encoding="utf-8")

    def _write_file(self, root: Path, path_str: str, content: str) -> Dict[str, Any]:
        safe_path = validate_workspace_path(path_str, root)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")
        return {"status": "success", "bytes_written": len(content.encode("utf-8")), "path": path_str}

    def _list_directory(self, root: Path, path_str: str) -> List[str]:
        target_dir = root if not path_str or path_str == "." else validate_workspace_path(path_str, root)
        if not target_dir.exists() or not target_dir.is_dir():
            raise ValueError(f"Directory not found: {path_str}")
        return sorted([entry.name for entry in target_dir.iterdir()])

    def _search_files(self, root: Path, query: str) -> List[str]:
        q_lower = query.lower()
        matches = []
        for path_item in root.glob("**/*"):
            if path_item.is_file():
                rel = path_item.relative_to(root).as_posix()
                if not q_lower or q_lower in rel.lower():
                    matches.append(rel)
        return matches[:50]

    def _get_file_metadata(self, root: Path, path_str: str) -> Dict[str, Any]:
        safe_path = validate_workspace_path(path_str, root)
        if not safe_path.exists():
            raise ValueError(f"File not found: {path_str}")
        st = safe_path.stat()
        return {
            "name": safe_path.name,
            "size_bytes": st.st_size,
            "is_dir": safe_path.is_dir(),
            "modified_time": st.st_mtime,
        }

    def _create_directory(self, root: Path, path_str: str) -> Dict[str, Any]:
        safe_path = validate_workspace_path(path_str, root)
        safe_path.mkdir(parents=True, exist_ok=True)
        return {"status": "created", "path": path_str}
