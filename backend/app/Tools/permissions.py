"""
Jarvis AIOS
--------------------
Tool Permission & Security Layer

Extensible RBAC and Human-in-the-Loop permission validator.
"""

from typing import Dict, Any, Optional
from app.Tools.metadata import PermissionLevel, ToolMetadata


class ToolPermissionError(PermissionError):
    """Raised when a user or caller lacks permission to execute a tool."""
    pass


class ToolDisabledError(ValueError):
    """Raised when an attempt is made to execute a disabled tool."""
    pass


# Numeric ordering of permission levels for hierarchy checks
_PERMISSION_HIERARCHY: Dict[PermissionLevel, int] = {
    PermissionLevel.PUBLIC: 0,
    PermissionLevel.USER: 10,
    PermissionLevel.ADMIN: 20,
    PermissionLevel.SYSTEM: 30,
    PermissionLevel.INTERNAL: 40,
}


class ToolPermissionValidator:
    """
    Validates execution rights, caller roles, and approval rules before
    tool invocation.
    """

    @staticmethod
    def parse_permission_level(val: Any) -> PermissionLevel:
        """Parse string or enum into PermissionLevel."""
        if isinstance(val, PermissionLevel):
            return val
        if isinstance(val, str):
            val_upper = val.upper()
            if val_upper in PermissionLevel.__members__:
                return PermissionLevel[val_upper]
        return PermissionLevel.USER

    def validate(
        self,
        metadata: ToolMetadata,
        caller_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Validate whether the tool can be executed given the caller context.

        Args:
            metadata: The ToolMetadata of the tool to be executed.
            caller_context: Optional dict containing caller details like:
                - "user_id": str/int
                - "role" or "permission_level": str/PermissionLevel
                - "is_approved": bool (for human-in-the-loop)

        Raises:
            ToolDisabledError: If tool.enabled is False.
            ToolPermissionError: If caller permission is below required tool level.
        """
        # 1. Check if tool is globally enabled
        if not metadata.enabled:
            raise ToolDisabledError(
                f"Tool '{metadata.name}' is currently disabled by administrator."
            )

        caller_context = caller_context or {}

        # 2. Check Permission Level Hierarchy
        required_level = metadata.permission_level
        caller_level_raw = caller_context.get("permission_level") or caller_context.get("role") or PermissionLevel.USER
        caller_level = self.parse_permission_level(caller_level_raw)

        required_rank = _PERMISSION_HIERARCHY.get(required_level, 10)
        caller_rank = _PERMISSION_HIERARCHY.get(caller_level, 10)

        if caller_rank < required_rank:
            raise ToolPermissionError(
                f"Permission denied for tool '{metadata.name}'. "
                f"Requires '{required_level.value}' access, but caller has '{caller_level.value}'."
            )

    def is_approval_required(
        self,
        metadata: ToolMetadata,
        caller_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if tool execution requires explicit Human-in-the-Loop approval.

        Args:
            metadata: ToolMetadata.
            caller_context: Optional dict containing "is_approved" boolean.

        Returns:
            True if approval is required and not yet granted in context.
        """
        if not metadata.requires_approval:
            return False

        caller_context = caller_context or {}
        # If caller context explicitly contains "is_approved"=True, approval was already granted
        return not bool(caller_context.get("is_approved", False))


permission_validator = ToolPermissionValidator()
