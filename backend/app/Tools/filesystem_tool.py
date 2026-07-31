"""
Jarvis AIOS
--------------------
Filesystem Tool Provider

Provides safe, sandboxed workspace operations including list, read, write,
mkdir, exists, and delete with path normalization, sandbox boundary enforcement,
and file size limits.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel

# Default workspace directory relative to project root
DEFAULT_WORKSPACE = Path(__file__).resolve().parent.parent.parent / "workspace"
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class FilesystemTool(Tool):
    """
    Sandboxed Filesystem Provider Tool for Jarvis AIOS.
    """

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        self.workspace_root = (workspace_root or DEFAULT_WORKSPACE).resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)

        meta = ToolMetadata(
            name="filesystem",
            display_name="Filesystem Manager",
            description="Sandboxed file operations (list, read, write, mkdir, exists, delete).",
            category="system",
            tags=["filesystem", "file", "sandbox", "workspace"],
            version="1.0.0",
            author="Jarvis AIOS Core",
            permission_level=PermissionLevel.USER,
            requires_approval=False,
            timeout_seconds=15.0,
            parameter_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "read", "write", "mkdir", "exists", "delete"],
                        "description": "Filesystem operation to perform.",
                    },
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace sandbox root.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content string to write (required for 'write' action).",
                    },
                },
                "required": ["action", "path"],
            },
        )
        super().__init__(metadata=meta)

    def _resolve_safe_path(self, relative_path: str) -> Path:
        """
        Normalize and resolve relative path, verifying it stays inside workspace sandbox.
        Raises ValueError if path traversal outside sandbox is detected.
        """
        if not relative_path or not relative_path.strip():
            target = self.workspace_root
        else:
            # Strip leading slashes to keep path relative
            clean_rel = relative_path.lstrip("/\\")
            target = (self.workspace_root / clean_rel).resolve()

        # Sandbox boundary check
        try:
            target.relative_to(self.workspace_root)
        except ValueError:
            raise ValueError(
                f"Access denied: Path '{relative_path}' attempts to traverse outside "
                f"sandbox workspace '{self.workspace_root}'."
            )

        return target

    def execute(self, action: str, path: str = "", content: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Synchronously execute filesystem operations.
        """
        target_path = self._resolve_safe_path(path)
        action_lower = action.lower().strip()

        if action_lower == "exists":
            return {
                "action": "exists",
                "path": str(path),
                "exists": target_path.exists(),
                "is_file": target_path.is_file(),
                "is_dir": target_path.is_dir(),
            }

        elif action_lower == "list":
            if not target_path.exists():
                raise ValueError(f"Directory '{path}' does not exist.")
            if not target_path.is_dir():
                raise ValueError(f"Path '{path}' is a file, not a directory.")

            items = []
            for child in sorted(target_path.iterdir()):
                rel = child.relative_to(self.workspace_root)
                items.append({
                    "name": child.name,
                    "path": str(rel),
                    "is_dir": child.is_dir(),
                    "size_bytes": child.stat().st_size if child.is_file() else 0,
                })
            return {"action": "list", "path": str(path), "items": items}

        elif action_lower == "read":
            if not target_path.exists():
                raise ValueError(f"File '{path}' does not exist.")
            if not target_path.is_file():
                raise ValueError(f"Path '{path}' is a directory, not a file.")

            size = target_path.stat().st_size
            if size > MAX_FILE_SIZE_BYTES:
                raise ValueError(
                    f"File size ({size} bytes) exceeds maximum limit of {MAX_FILE_SIZE_BYTES} bytes."
                )

            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                data = f.read()

            return {
                "action": "read",
                "path": str(path),
                "content": data,
                "size_bytes": size,
            }

        elif action_lower == "write":
            if content is None:
                raise ValueError("Content string is required for 'write' action.")

            content_bytes = len(content.encode("utf-8"))
            if content_bytes > MAX_FILE_SIZE_BYTES:
                raise ValueError(
                    f"Write payload size ({content_bytes} bytes) exceeds maximum limit of {MAX_FILE_SIZE_BYTES} bytes."
                )

            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "action": "write",
                "path": str(path),
                "bytes_written": content_bytes,
                "status": "success",
            }

        elif action_lower == "mkdir":
            target_path.mkdir(parents=True, exist_ok=True)
            return {
                "action": "mkdir",
                "path": str(path),
                "status": "success",
            }

        elif action_lower == "delete":
            if target_path == self.workspace_root:
                raise ValueError("Cannot delete root workspace directory.")
            if not target_path.exists():
                raise ValueError(f"Path '{path}' does not exist.")

            if target_path.is_dir():
                import shutil
                shutil.rmtree(target_path)
            else:
                target_path.unlink()

            return {
                "action": "delete",
                "path": str(path),
                "status": "success",
            }

        else:
            raise ValueError(
                f"Unknown filesystem action '{action}'. "
                "Supported actions: list, read, write, mkdir, exists, delete."
            )
