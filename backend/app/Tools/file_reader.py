"""
Jarvis AIOS
--------------------
File Reader Tool

Reads text files from an approved workspace directory only.
Arbitrary filesystem access and path traversal attacks are
prevented through strict path validation, canonical path
resolution, and containment checking against the allowed
workspace directory.
"""

from pathlib import Path
from typing import Any

from app.Tools.tool import Tool

# The only directory from which files may be read.
# All paths are resolved and validated against this base.
# Change this via environment configuration in production.
_ALLOWED_DIRECTORY: Path = Path.cwd() / "workspace"

# Maximum file size in bytes (1 MB).
# Prevents memory exhaustion from reading extremely large files.
MAX_FILE_SIZE_BYTES: int = 1_000_000


def _validate_path_safety(path: str, allowed_dir: Path) -> Path:
    """Validate a file path and return its canonical, safe form.

    Security checks performed in order:
    1. Reject '..' and '.' path components explicitly.
    2. Reject absolute paths — all paths must be workspace-relative.
    3. Resolve the joined path to its canonical form via resolve(),
       which normalizes '..'/'.' and follows symlinks.
    4. Verify the canonical path is contained within the allowed
       directory.

    This approach provides defense-in-depth: early checks give clear
    error messages for common traversal attempts, while the canonical
    resolution and containment check catch any edge cases (symlink
    escapes, indirect traversal, etc.).

    Args:
        path: The user-provided file path string.
        allowed_dir: The resolved canonical Path of the allowed
            workspace directory.

    Returns:
        A resolved, canonical Path guaranteed to be within the
        allowed directory.

    Raises:
        ValueError: If the path is unsafe for any reason.
    """
    # Step 1: Reject explicit '..' and '.' path components
    # This catches obvious traversal attempts early with a clear message.
    # The check operates on the raw string to prevent encoded bypasses.
    parts = Path(path).parts
    for part in parts:
        if part == "..":
            raise ValueError(
                "Path must not contain '..'. Directory traversal is not allowed."
            )
        if part == ".":
            raise ValueError("Path must not contain '.' components.")

    # Step 2: Reject absolute paths
    # All paths must be relative to the workspace directory.
    # On POSIX, is_absolute() returns True for paths starting with '/'.
    if Path(path).is_absolute():
        raise ValueError(
            "Absolute paths are not allowed. "
            "Provide a relative path within the workspace directory."
        )

    # Step 3: Join with the allowed directory and resolve to canonical form.
    # resolve() normalizes '..' and '.', follows all symlinks, and returns
    # the absolute path. With strict=False, it does not raise if the path
    # or its parents do not exist — non-existent paths are still resolved
    # as much as possible.
    try:
        resolved_path = (allowed_dir / path).resolve(strict=False)
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid file path: {e}") from e

    # Step 4: Verify the resolved canonical path is within the allowed directory.
    # If the path traversed outside via symlinks, '..' after resolution,
    # or any other mechanism, relative_to() will raise ValueError.
    try:
        resolved_path.relative_to(allowed_dir)
    except ValueError:
        raise ValueError(
            "Access denied: the resolved path is outside "
            "the allowed workspace directory."
        )

    return resolved_path


class FileReaderTool(Tool):
    name = "file_reader"

    description = "Reads text from a file."

    def execute(self, **kwargs: Any) -> Any:
        """Read a text file from the approved workspace directory.

        The path is validated to ensure it stays within the allowed
        workspace directory. Directory traversal using '..', absolute
        paths outside the workspace, and symlink escapes are blocked.

        Args:
            path: The file path relative to the allowed workspace
                directory.

        Returns:
            The file contents as a string.

        Raises:
            ValueError: If the path is missing, invalid, traverses
                outside the allowed directory, the file does not
                exist, or the file is too large.
        """
        # --- Input validation ---
        path = kwargs.get("path")

        if path is None:
            raise ValueError(
                "Missing 'path' argument. Provide a file path as a string."
            )

        if not isinstance(path, str):
            raise ValueError("The 'path' argument must be a string.")

        if not path.strip():
            raise ValueError("The 'path' argument must be a non-empty string.")

        # --- Workspace directory setup ---
        # Ensure the allowed workspace directory exists
        try:
            _ALLOWED_DIRECTORY.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ValueError(f"Cannot access workspace directory: {e}") from e

        # Resolve the allowed directory to its canonical absolute path.
        # This must be done at execution time (not import time) because
        # the current working directory may change, and we need to
        # resolve any symlinks in the path.
        try:
            allowed_resolved = _ALLOWED_DIRECTORY.resolve(strict=False)
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Cannot resolve workspace directory: {e}") from e

        # --- Path safety validation ---
        # All traversal, symlink, and containment checks are performed
        # here. The returned path is guaranteed to be safe and canonical.
        requested_path = _validate_path_safety(path, allowed_resolved)

        # --- File existence and type checks ---
        if not requested_path.exists():
            raise ValueError("File not found at the specified path.")

        if not requested_path.is_file():
            raise ValueError("The specified path is not a regular file.")

        # --- File size limit ---
        try:
            file_size = requested_path.stat().st_size
        except OSError as e:
            raise ValueError(f"Cannot access file: {e}") from e

        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                "File too large. Maximum allowed size is approximately 1 MB."
            )

        # --- Read and return file contents ---
        try:
            return requested_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError(
                "The file is not a valid UTF-8 text file. "
                "Binary files are not supported."
            )
        except OSError as e:
            raise ValueError(f"Failed to read file: {e}") from e
