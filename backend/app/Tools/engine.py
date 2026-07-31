"""
Jarvis AIOS
--------------------
Tool Engine

Single execution gate for all tool invocations.
Enforces input validation, permission validation, modular pipeline execution,
and returns standardized provider-independent ToolResult objects.
"""

import asyncio
from typing import Any, Dict, Optional, AsyncGenerator

from app.Tools.metadata import ToolResult, ExecutionStatus
from app.Tools.pipeline import pipeline


class ToolEngine:
    """
    Single execution gate for all tool invocations.
    Delegates to modular ExecutionPipeline and ensures provider-independent
    ToolResult return objects while maintaining 100% backward compatibility.
    """

    async def execute_async(
        self,
        tool_name: str,
        caller_context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute a tool asynchronously through the modular pipeline.

        Returns:
            Provider-independent ToolResult object.
        """
        return await pipeline.run_async(
            tool_name=tool_name,
            kwargs=kwargs,
            caller_context=caller_context,
        )

    async def execute_stream(
        self,
        tool_name: str,
        caller_context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[Any, None]:
        """
        Stream tool output chunks asynchronously.
        """
        async for chunk in pipeline.run_stream(
            tool_name=tool_name,
            kwargs=kwargs,
            caller_context=caller_context,
        ):
            yield chunk

    def execute(
        self,
        tool_name: str,
        caller_context: Optional[Dict[str, Any]] = None,
        return_result_object: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a tool synchronously with backward-compatible return handling.

        Args:
            tool_name: Registered name of the tool.
            caller_context: Optional caller context dictionary.
            return_result_object: If True, returns full ToolResult.
                                  If False (default), returns raw output or raises ValueError on error.
            **kwargs: Arguments to pass to the tool.

        Returns:
            ToolResult object if return_result_object=True, else raw output.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Running inside an event loop (e.g. FastAPI async handler)
            import nest_asyncio
            nest_asyncio.apply()
            result: ToolResult = loop.run_until_complete(
                self.execute_async(tool_name, caller_context=caller_context, **kwargs)
            )
        else:
            result: ToolResult = asyncio.run(
                self.execute_async(tool_name, caller_context=caller_context, **kwargs)
            )

        if return_result_object:
            return result

        if result.status != ExecutionStatus.SUCCESS:
            raise ValueError(result.error or f"Tool '{tool_name}' execution failed with status {result.status.value}.")

        return result.output


engine = ToolEngine()
