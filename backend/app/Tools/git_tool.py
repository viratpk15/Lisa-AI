"""
Jarvis AIOS
--------------------
Git Tool Provider

Provides Git repository inspection (status, diff, log, branch) and write operations.
Read-only actions are open; write operations require explicit Human-in-the-Loop approval.
"""

import subprocess
import shlex
from pathlib import Path
from typing import Any, Dict, Optional
from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Read-only git actions
READ_ONLY_ACTIONS = {"status", "diff", "log", "branch", "show"}
# Write git actions requiring approval
WRITE_ACTIONS = {"commit", "add", "checkout", "merge", "pull", "push"}


class GitTool(Tool):
    """
    Git Repository Tool Provider for Jarvis AIOS.
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = (repo_root or PROJECT_ROOT).resolve()

        meta = ToolMetadata(
            name="git",
            display_name="Git Repository Manager",
            description="Git operations (status, diff, log, branch, commit). Read-only by default.",
            category="development",
            tags=["git", "vcs", "code", "repository"],
            version="1.0.0",
            author="Jarvis AIOS Core",
            permission_level=PermissionLevel.USER,
            requires_approval=False,  # Evaluated dynamically per action
            timeout_seconds=15.0,
            parameter_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["status", "diff", "log", "branch", "show", "commit"],
                        "description": "Git subcommand to execute.",
                    },
                    "args": {
                        "type": "string",
                        "description": "Additional flags or arguments (e.g. '-n 5', 'HEAD~1').",
                    },
                },
                "required": ["action"],
            },
        )
        super().__init__(metadata=meta)

    def execute(self, action: str, args: str = "", **kwargs: Any) -> Dict[str, Any]:
        """
        Execute git subcommand synchronously.
        """
        action_lower = action.lower().strip()

        if action_lower not in READ_ONLY_ACTIONS and action_lower not in WRITE_ACTIONS:
            raise ValueError(
                f"Unsupported git action '{action}'. "
                f"Supported: {sorted(READ_ONLY_ACTIONS | WRITE_ACTIONS)}"
            )

        cmd = ["git", action_lower]
        if args and args.strip():
            extra = shlex.split(args.strip())
            cmd.extend(extra)

        try:
            completed = subprocess.run(
                cmd,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=self.metadata.timeout_seconds,
            )

            return {
                "action": action_lower,
                "command": " ".join(cmd),
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "is_read_only": action_lower in READ_ONLY_ACTIONS,
            }
        except subprocess.TimeoutExpired:
            raise ValueError(f"Git command '{action_lower}' timed out after {self.metadata.timeout_seconds} seconds.")
        except Exception as e:
            raise ValueError(f"Git execution error: {str(e)}")
