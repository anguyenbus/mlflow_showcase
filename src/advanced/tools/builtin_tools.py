"""Built-in tools for LangChain tool calling demonstrations.

Provides simple tools for date/time operations, calculations,
and other utilities to demonstrate MLflow tracing of tool calls.

These tools are designed for educational purposes to show how
MLflow traces tool selection, execution, and results.
"""

import operator
from datetime import datetime
from typing import Union, List

from beartype import beartype
from langchain_core.tools import tool


@tool
def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get the current date and time.

    Returns the current system time formatted according to the
    specified format string.

    Args:
        format: Python strftime format string for date/time display.
            Default: "%Y-%m-%d %H:%M:%S" (e.g., "2026-03-23 14:30:45")

    Returns:
        Formatted current date and time string

    Example:
        >>> get_current_time.invoke({"format": "%Y-%m-%d"})
        '2026-03-23'
    """
    now = datetime.now()
    return now.strftime(format)


@tool
def get_current_date() -> str:
    """Get the current date.

    A simpler version of get_current_time that returns just the date.

    Returns:
        Current date in YYYY-MM-DD format (e.g., "2026-03-23")

    Example:
        >>> get_current_date.invoke({})
        '2026-03-23'
    """
    return datetime.now().strftime("%Y-%m-%d")


@tool
def calculate(expression: str) -> Union[float, int]:
    """Calculate a mathematical expression.

    Evaluates basic arithmetic expressions with safety checks to prevent
    code injection. Only allows numbers, basic operators, and parentheses.

    Supported operations:
        - Addition: +
        - Subtraction: -
        - Multiplication: *
        - Division: /
        - Power: **
        - Parentheses: ()

    Args:
        expression: Mathematical expression to evaluate.
            Examples: "2 + 2", "10 * 5", "2 ** 8", "(15 + 23) * 2"

    Returns:
        Result of the calculation (int or float)

    Raises:
        ValueError: If expression contains invalid characters or operations

    Example:
        >>> calculate.invoke({"expression": "15 * 23"})
        345
        >>> calculate.invoke({"expression": "2 ** 8"})
        256
    """
    try:
        # Safety check: only allow basic math characters
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            raise ValueError(
                f"Expression contains invalid characters. "
                f"Only digits 0-9, operators + - * / **, and parentheses () are allowed."
            )

        # Evaluate expression with restricted builtins for safety
        # NOTE: Using eval with empty builtins prevents access to dangerous functions
        result = eval(expression, {"__builtins__": {}}, {})

        return result
    except Exception as e:
        raise ValueError(f"Invalid expression: {expression}. Error: {str(e)}")


@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together.

    A simple tool to demonstrate multi-parameter tool calling.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        Sum of a and b

    Example:
        >>> add_numbers.invoke({"a": 15, "b": 23})
        38.0
    """
    return a + b


@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers.

    A simple tool to demonstrate multi-parameter tool calling.

    Args:
        a: First number to multiply
        b: Second number to multiply

    Returns:
        Product of a and b

    Example:
        >>> multiply_numbers.invoke({"a": 15, "b": 23})
        345.0
    """
    return a * b


# List of available tools for easy access
# This allows importing all tools at once: from builtin_tools import AVAILABLE_TOOLS
AVAILABLE_TOOLS: List = [
    get_current_time,
    get_current_date,
    calculate,
    add_numbers,
    multiply_numbers
]

# Tool descriptions for display
TOOL_DESCRIPTIONS = {
    "get_current_time": "Get current date/time with custom formatting",
    "get_current_date": "Get current date in YYYY-MM-DD format",
    "calculate": "Evaluate mathematical expressions",
    "add_numbers": "Add two numbers together",
    "multiply_numbers": "Multiply two numbers"
}
