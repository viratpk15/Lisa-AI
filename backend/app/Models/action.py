"""
Jarvis AIOS
--------------------
Action Schema Models

Defines the validated structure for LLM-generated actions.
The agent node must validate every LLM response against these
models before using them as execution instructions.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ToolArguments(BaseModel):
    """Arguments for a tool execution action."""

    expression: Optional[str] = Field(None, description="Mathematical expression for calculator tool.")
    path: Optional[str] = Field(None, description="File path for file_reader tool.")
    code: Optional[str] = Field(None, description="Python code for python runner tool.")


class ToolAction(BaseModel):
    """An action that executes a registered tool."""

    type: str = Field("tool", pattern="^tool$")
    tool: str = Field(..., min_length=1, description="The registered tool name.")
    arguments: ToolArguments = Field(default_factory=ToolArguments)


class FinalAction(BaseModel):
    """An action that returns a final response to the user."""

    type: str = Field("final", pattern="^final$")
    response: str = Field(..., min_length=1, description="The final response text.")


class ParsedAction(BaseModel):
    """Union-like model for validated LLM actions.

    After parsing and validating, the action_type field indicates
    whether this is a tool call or a final response.
    """

    action_type: str = Field(..., alias="type")
    tool: Optional[str] = Field(None)
    arguments: ToolArguments = Field(default_factory=ToolArguments)
    response: Optional[str] = Field(None)
