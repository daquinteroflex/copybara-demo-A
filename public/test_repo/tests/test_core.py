"""Tests for core functionality."""

from demo_package.core import greet, add


def test_greet():
    """Test greet function."""
    assert greet("World") == "Hello, World!"
    assert greet("Copybara") == "Hello, Copybara!"


def test_add():
    """Test add function."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
