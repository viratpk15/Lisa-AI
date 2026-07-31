"""
Jarvis AIOS
--------------------
Base Tool Interface

Abstract Base Class for all Jarvis AIOS tools supporting sync,
async, streaming execution, metadata introspection, and JSON schema binding.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict

from app.Tools.metadata import ToolMetadata, PermissionLevel


class Tool(ABC):
    """
    Base class for all tools in Jarvis AIOS.

    Subclasses can define static name and description attributes or pass a full
    ToolMetadata instance. Backward compatibility is maintained for all existing tools.
    """

    name: str = ""
    description: str = ""
    metadata: ToolMetadata

    def __init__(self, metadata: ToolMetadata | None = None) -> None:
        """Initialize tool metadata, syncing legacy class attributes if necessary."""
        if metadata is not None:
            self.metadata = metadata
        else:
            # Auto-construct metadata from class properties if not explicitly provided
            self.metadata = ToolMetadata(
                name=self.name or self.__class__.__name__,
                description=self.description or (self.__doc__ or "").strip(),
                permission_level=PermissionLevel.USER,
            )

        # Ensure legacy attributes mirror metadata
        self.name = self.metadata.name
        self.description = self.metadata.description

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the tool synchronously.
        Must be implemented by all non-async-only subclasses.
        """
        raise NotImplementedError("Synchronous execution is not implemented for this tool.")

    async def execute_async(self, **kwargs: Any) -> Any:
        """
        Execute the tool asynchronously.
        Default implementation delegates synchronous `execute` to a worker thread.
        Can be overridden by native async tools.
        """
        return await asyncio.to_thread(self.execute, **kwargs)

    async def execute_stream(self, **kwargs: Any) -> AsyncGenerator[Any, None]:
        """
        Execute the tool in streaming mode yielding chunk responses.
        Default implementation yields single result from `execute_async`.
        """
        result = await self.execute_async(**kwargs)
        yield result

    def to_schema(self) -> Dict[str, Any]:
        """
        Export tool definition as an OpenAI / LLM compatible JSON Schema format.
        """
        param_schema = self.metadata.parameter_schema
        if not param_schema:
            param_schema = {
                "type": "object",
                "properties": {},
                "required": [],
            }

        return {
            "type": "function",
            "function": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "parameters": param_schema,
            },
        }
