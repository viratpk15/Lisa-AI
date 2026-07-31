"""
Jarvis AIOS
--------------------
Date Time Tool
"""

from datetime import datetime
from typing import Any

from app.Tools.tool import Tool


class DateTimeTool(Tool):
    name = "datetime"

    description = "Returns the current date and time."

    def execute(self, **kwargs: Any) -> Any:

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
