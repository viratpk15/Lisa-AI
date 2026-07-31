"""
Jarvis AIOS
--------------------
Calculator Tool

Evaluates mathematical expressions using ast.literal_eval for safe,
sandboxed evaluation. Only literal expressions (numbers, operators,
parentheses) are accepted — arbitrary code execution is prevented.
"""

import ast
import math
import operator
from typing import Any

from app.Tools.tool import Tool

# Mapping of supported AST node types to safe operator functions.
# This is intentionally restricted to prevent code execution.
_ALLOWED_OPERATORS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Maximum absolute value for intermediate and final results.
# Prevents memory exhaustion from huge integer computations
# (e.g. 10**1000000) that could consume excessive CPU/memory.
_MAX_RESULT_ABSOLUTE: float = 1e100

# Maximum integer value to prevent arbitrary-size integer attacks.
_MAX_INTEGER_VALUE: int = 10**100

# Maximum exponent value for power operations to prevent runaway computation.
_MAX_EXPONENT_VALUE: float = 100.0


def _safe_eval(expression: str) -> float | int:
    """Evaluate a mathematical expression safely using AST parsing.

    Parses the expression into an AST and walks the tree, allowing
    only numbers, operators, and parentheses. No function calls,
    attribute access, or variable lookups are permitted.

    Args:
        expression: A string containing a mathematical expression.

    Returns:
        The computed numeric result.

    Raises:
        ValueError: If the expression is malformed, contains unsafe
            constructs, or fails to evaluate.
    """
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError as e:
        raise ValueError(
            f"Invalid expression syntax: {e}"
        ) from e

    if not isinstance(tree, ast.Expression):
        raise ValueError("Expression must be a valid mathematical expression.")

    def _eval_node(node: ast.AST) -> float | int:
        """Recursively evaluate a single AST node with bounds checking.

        Each evaluated result is checked against the configured
        maximum absolute value to prevent resource exhaustion
        from unbounded integer or float computations.

        Returns:
            The computed numeric result.

        Raises:
            ValueError: If the result exceeds allowed bounds.
        """
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            # Reject NaN and Infinity constants
            if isinstance(node.value, float) and (math.isnan(node.value) or math.isinf(node.value)):
                raise ValueError("NaN and Infinity values are not allowed.")
            # Bound-check integer constants
            if isinstance(node.value, int) and abs(node.value) > _MAX_INTEGER_VALUE:
                raise ValueError("Integer value exceeds maximum allowed size.")
            return node.value

        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
            operand = _eval_node(node.operand)
            result = _ALLOWED_OPERATORS[type(node.op)](operand)
            # Check result bounds
            if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
                raise ValueError("Calculation resulted in NaN or Infinity.")
            if abs(result) > _MAX_RESULT_ABSOLUTE:
                raise ValueError("Result exceeds maximum allowed value.")
            return result

        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
            left = _eval_node(node.left)
            right = _eval_node(node.right)

            # Bound-check exponent to prevent runaway power computation
            if isinstance(node.op, ast.Pow):
                if isinstance(right, (int, float)) and abs(right) > _MAX_EXPONENT_VALUE:
                    raise ValueError(
                        f"Exponent value {right} exceeds maximum allowed "
                        f"exponent of {_MAX_EXPONENT_VALUE}."
                    )

            # Prevent division by zero
            if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(right, (int, float)) and right == 0:
                    raise ValueError("Division by zero is not allowed.")

            result = _ALLOWED_OPERATORS[type(node.op)](left, right)

            # Check result bounds
            if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
                raise ValueError("Calculation resulted in NaN or Infinity.")
            if abs(result) > _MAX_RESULT_ABSOLUTE:
                raise ValueError("Result exceeds maximum allowed value.")

            return result

        raise ValueError(f"Unsupported expression construct: {type(node).__name__}")

    try:
        return _eval_node(tree.body)
    except (ValueError, TypeError, ArithmeticError) as e:
        raise ValueError(f"Calculation failed: {e}") from e


class CalculatorTool(Tool):
    name = "calculator"

    description = "Performs mathematical calculations."

    def execute(self, **kwargs: Any) -> Any:
        """Execute a mathematical expression safely.

        Args:
            expression: The mathematical expression to evaluate.
                Must contain only numbers, operators, parentheses,
                and whitespace.

        Returns:
            The computed result as a float or int.

        Raises:
            ValueError: If the expression is missing, malformed,
                or evaluates to an error.
        """
        expression = kwargs.get("expression")

        if expression is None:
            raise ValueError(
                "Missing 'expression' argument. Provide a mathematical expression "
                "as a string, e.g. '2 + 3 * 4'."
            )

        if not isinstance(expression, str) or not expression.strip():
            raise ValueError(
                "The 'expression' argument must be a non-empty string containing "
                "a mathematical expression."
            )

        if len(expression) > 500:
            raise ValueError(
                "Expression too long. Maximum length is 500 characters."
            )

        return _safe_eval(expression)
