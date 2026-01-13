"""Core functionality for demo package."""


def greet(name: str) -> str:
    """
    Generate a greeting message.

    Args:
        name: The name to greet

    Returns:
        A greeting message string
    """
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """
    Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b
