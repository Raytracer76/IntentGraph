"""Utility functions for testing."""

from main import add


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def double(x: int) -> int:
    """Double a number using add."""
    return add(x, x)
