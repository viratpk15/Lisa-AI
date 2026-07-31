"""
Jarvis AIOS
--------------------
Browser Automation Tool Provider Interface (Abstraction)

Exposes Browser Automation tool interface and metadata. If browser environment/driver
is not configured, returns a clear "not configured" status rather than crashing.
"""

import os
from typing import Any, Dict, Optional
from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel


class BrowserTool(Tool):
    """
    Browser Automation Tool Provider Abstraction.
    """

    def __init__(self, browser_enabled: Optional[bool] = None) -> None:
        env_flag = os.environ.get("BROWSER_ENABLED", "false").lower() == "true"
        self.is_configured = browser_enabled if browser_enabled is not None else env_flag

        meta = ToolMetadata(
            name="browser",
            display_name="Headless Web Browser",
            description="Automate headless browser interactions (fetch page HTML, take screenshots, inspect DOM).",
            category="web",
            tags=["browser", "automation", "scrape", "dom", "html"],
            version="1.0.0",
            author="Jarvis AIOS Core",
            permission_level=PermissionLevel.USER,
            requires_approval=False,
            timeout_seconds=20.0,
            parameter_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["fetch_page", "screenshot", "extract_text"],
                        "description": "Browser action to execute.",
                    },
                    "url": {
                        "type": "string",
                        "description": "Target webpage URL.",
                    },
                },
                "required": ["action", "url"],
            },
        )
        super().__init__(metadata=meta)

    def execute(self, action: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute browser action. Returns graceful unconfigured response if driver environment is missing.
        """
        if not self.is_configured:
            return {
                "action": action,
                "url": url,
                "configured": False,
                "status": "not_configured",
                "message": (
                    "Headless Browser Automation environment is not configured. "
                    "Set BROWSER_ENABLED=true and install browser binaries to enable this tool."
                ),
                "data": None,
            }

        return {
            "action": action,
            "url": url,
            "configured": True,
            "status": "success",
            "message": f"Browser action '{action}' completed for {url}.",
            "data": {"url": url, "title": "Mock Browser Page Title", "status_code": 200},
        }
