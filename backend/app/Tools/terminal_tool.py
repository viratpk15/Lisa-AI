"""
Jarvis AIOS
--------------------
Terminal Tool Provider

Provides safe command execution with command allowlists, working directory
isolation, timeout controls, and stdout/stderr capture without shell injection risks.
"""

import subprocess
import shlex
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel

DEFAULT_WORKSPACE = Path(__file__).resolve().parent.parent.parent / "workspace"

# Safe default command binaries allowed for execution
DEFAULT_ALLOWLIST = {
    "ls", "pwd", "echo", "cat", "whoami", "date", "find", "grep", "wc", "head", "tail",
    "python", "python3", "pytest", "uv", "pnpm", "git"
}

# Forbidden command tokens that present system destruction or privilege escalation risks
FORBIDDEN_TOKENS = {
    "sudo", "su", "chmod", "chown", "mkfs", "dd", "shutdown", "reboot", "init",
    ":(){:|:&};:", "> /dev/sd", "rm -rf /"
}


class TerminalTool(Tool):
    """
    Terminal / Shell Tool Provider for executing sandboxed commands.
    """

    def __init__(self, workspace_root: Optional[Path] = None, allowlist: Optional[set[str]] = None) -> None:
        self.workspace_root = (workspace_root or DEFAULT_WORKSPACE).resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.allowlist = allowlist or DEFAULT_ALLOWLIST

        meta = ToolMetadata(
            name="terminal",
            display_name="Terminal Executor",
            description="Execute safe shell commands within workspace root.",
            category="system",
            tags=["terminal", "shell", "command", "bash"],
            version="1.0.0",
            author="Jarvis AIOS Core",
            permission_level=PermissionLevel.USER,
            requires_approval=False,
            timeout_seconds=15.0,
            parameter_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute.",
                    },
                },
                "required": ["command"],
            },
        )
        super().__init__(metadata=meta)

    def _validate_command(self, command: str) -> List[str]:
        """
        Validate and tokenize command string.
        Verifies primary binary is in allowlist and no dangerous tokens exist.
        """
        if not command or not command.strip():
            raise ValueError("Command string must not be empty.")

        cmd_str = command.strip()

        # Check for forbidden dangerous tokens
        for forbidden in FORBIDDEN_TOKENS:
            if forbidden in cmd_str:
                raise ValueError(f"Security error: Command contains forbidden token '{forbidden}'.")

        # Split into shell tokens using shlex to prevent injection
        try:
            tokens = shlex.split(cmd_str)
        except Exception as e:
            raise ValueError(f"Command syntax error: Failed to parse shell tokens: {e}")

        if not tokens:
            raise ValueError("Command must contain at least one token.")

        binary = Path(tokens[0]).name
        if binary not in self.allowlist:
            raise ValueError(
                f"Security error: Binary '{binary}' is not in the allowed command list. "
                f"Allowed commands: {sorted(self.allowlist)}"
            )

        return tokens

    def execute(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute command synchronously in a subprocess.
        """
        tokens = self._validate_command(command)

        try:
            completed = subprocess.run(
                tokens,
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=self.metadata.timeout_seconds,
            )

            return {
                "command": command,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "status": "success" if completed.returncode == 0 else "error",
            }
        except subprocess.TimeoutExpired:
            raise ValueError(f"Command execution timed out after {self.metadata.timeout_seconds} seconds.")
        except Exception as e:
            raise ValueError(f"Execution error: {str(e)}")
