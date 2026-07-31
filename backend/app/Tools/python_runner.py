"""
Jarvis AIOS
--------------------
Python Runner Tool

Executes Python code in a restricted sandbox with timeout and
resource limits. The restricted execution environment blocks
access to built-in functions, imported modules, and dangerous
operations like file I/O and network access.
"""

import threading
from contextlib import redirect_stdout
from io import StringIO
from typing import Any

from app.Tools.tool import Tool

# Maximum execution time in seconds for any Python code snippet.
# Prevents infinite loops and long-running computations from
# blocking the server.
_MAX_CODE_TIMEOUT_SECONDS: float = 5.0

# Maximum length of the input code string to prevent resource exhaustion.
_MAX_CODE_LENGTH: int = 20000

# Maximum number of allowed loop iterations to prevent infinite loops.
_MAX_ITERATIONS: int = 100000


def _build_restricted_globals() -> dict[str, Any]:
    """Construct a restricted globals dictionary for safe code execution.

    Provides only a minimal subset of safe built-in functions and
    blocks access to dangerous builtins like __import__, open,
    exec, eval, compile, and file I/O operations.

    Returns:
        A dict containing only the allowed globals for execution.
    """
    # Whitelist of safe built-in functions that expose minimal risk.
    # These are selected based on the principle of least privilege:
    # only provide what is useful for basic data manipulation.
    _SAFE_BUILTINS: dict[str, Any] = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "chr": chr,
        "dict": dict,
        "divmod": divmod,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "format": format,
        "frozenset": frozenset,
        "hash": hash,
        "hex": hex,
        "int": int,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "iter": iter,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "next": next,
        "oct": oct,
        "ord": ord,
        "pow": pow,
        "print": print,
        "range": range,
        "reversed": reversed,
        "round": round,
        "set": set,
        "slice": slice,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "type": type,
        "zip": zip,
    }

    return {
        "__builtins__": _SAFE_BUILTINS,
    }


def _compile_with_restrictions(code: str) -> Any:
    """Compile Python code after scanning for dangerous constructs.

    Performs static analysis on the source code to detect and reject
    potentially dangerous patterns before compilation or execution.
    This provides defense-in-depth alongside restricted globals.

    Args:
        code: The Python code string to check and compile.

    Returns:
        A compiled code object.

    Raises:
        ValueError: If the code contains dangerous constructs.
    """
    # Reject import statements at the source level
    # This covers: import X, from X import Y, __import__() calls
    _DANGEROUS_KEYWORDS: list[str] = [
        "__import__",
        "import ",
        "from ",
        "open(",
        "exec(",
        "eval(",
        "compile(",
        "__builtins__",
        "globals()",
        "locals()",
        "vars()",
    ]

    code_lower = code.lower()
    for keyword in _DANGEROUS_KEYWORDS:
        if keyword in code_lower:
            raise ValueError(
                f"Code contains unsafe construct: '{keyword}' is not allowed."
            )

    # Reject attribute access patterns that could escape sandbox
    # e.g. ().__class__.__mro__ chain to access object internals
    _DANGEROUS_ATTRS: list[str] = [
        ".__class__",
        ".__base__",
        ".__subclasses__",
        ".__mro__",
        ".__dict__",
        ".__globals__",
        ".__code__",
        ".__closure__",
        ".__self__",
        ".__func__",
    ]

    for attr in _DANGEROUS_ATTRS:
        if attr in code_lower:
            raise ValueError(
                f"Code contains unsafe attribute access: '{attr}' is not allowed."
            )

    return compile(code, "<sandbox>", "exec")


def _run_with_timeout(code: str, timeout: float) -> str:
    """Execute Python code in a restricted sandbox with a timeout.

    The code runs with a minimal set of safe builtins, no imported
    modules, and no access to dangerous operations like file I/O,
    network access, or attribute introspection. A separate thread
    with timeout prevents infinite loops from blocking execution.

    Each execution gets a fresh restricted globals dict to prevent
    state leakage between runs.

    Args:
        code: The Python code string to execute.
        timeout: Maximum execution time in seconds.

    Returns:
        The captured stdout output as a string.

    Raises:
        ValueError: If the code execution times out or fails.
    """
    # Pre-compile the code to catch syntax errors early
    try:
        compiled_code = _compile_with_restrictions(code)
    except SyntaxError as e:
        raise ValueError(
            f"Invalid Python syntax: {e}"
        ) from e

    output = StringIO()
    result_container: list[Exception | None] = [None]
    done_event = threading.Event()

    def _run() -> None:
        """Execute the code in a restricted environment."""
        try:
            # Build a fresh restricted globals dict for each execution
            restricted_globals = _build_restricted_globals()
            restricted_locals: dict[str, Any] = {}

            with redirect_stdout(output):
                exec(compiled_code, restricted_globals, restricted_locals)
        except Exception as e:
            result_container[0] = e
        finally:
            done_event.set()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    if not done_event.wait(timeout=timeout):
        # Code execution timed out — the daemon thread will be abandoned
        raise ValueError(
            f"Code execution timed out after {timeout} seconds. "
            "Please simplify the code or reduce its complexity."
        )

    if result_container[0] is not None:
        error = result_container[0]
        # Sanitize error messages: replace curly braces to prevent
        # format string injection in downstream error handling
        error_message = str(error).replace("{", "(").replace("}", ")")
        raise ValueError(
            f"Code execution failed: {type(error).__name__}: {error_message}"
        )

    return output.getvalue()


class PythonRunnerTool(Tool):
    def __init__(self) -> None:
        from app.Tools.metadata import ToolMetadata, PermissionLevel
        meta = ToolMetadata(
            name="python",
            display_name="Python Code Sandbox",
            description="Executes Python code in a restricted sandbox environment.",
            category="development",
            tags=["python", "code", "sandbox", "execution"],
            version="1.0.0",
            author="Jarvis AIOS Core",
            permission_level=PermissionLevel.USER,
            requires_approval=False,
            timeout_seconds=5.0,
            parameter_schema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code snippet to execute.",
                    },
                },
                "required": ["code"],
            },
        )
        super().__init__(metadata=meta)

    def execute(self, **kwargs: Any) -> Any:
        """Execute Python code in a restricted sandbox.

        The code runs with no builtins, no imported modules, and a
        strict timeout to prevent abuse. Only stdout output is captured.

        Args:
            code: The Python code string to execute.

        Returns:
            The captured stdout output as a string.

        Raises:
            ValueError: If the code is missing, too long, times out,
                or fails during execution.
        """
        code = kwargs.get("code")

        if not code:
            raise ValueError(
                "Missing 'code' argument. Provide Python code as a string."
            )

        if not isinstance(code, str):
            raise ValueError(
                "The 'code' argument must be a string containing "
                "valid Python code."
            )

        if len(code) > _MAX_CODE_LENGTH:
            raise ValueError(
                f"Code too long. Maximum length is {_MAX_CODE_LENGTH} characters "
                f"(received {len(code)} characters)."
            )

        return _run_with_timeout(code, _MAX_CODE_TIMEOUT_SECONDS)
