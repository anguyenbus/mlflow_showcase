"""Tests for Garak console output utilities."""

from io import StringIO

from garak_evaluation.shared.console_output import (
    get_status_indicator,
    get_severity_style,
    print_status_table,
)
from rich.console import Console


def test_status_indicator_vulnerable():
    """Test that VULNERABLE status is formatted correctly."""
    result = get_status_indicator("vulnerable", 0.7)
    assert "[red" in result
    assert "VULNERABLE" in result


def test_status_indicator_safe():
    """Test that SAFE status is formatted correctly."""
    result = get_status_indicator("safe", 0.95)
    assert "[green" in result
    assert "SAFE" in result


def test_severity_style_high():
    """Test that HIGH severity returns correct style."""
    style = get_severity_style("HIGH")
    assert style == "red"


def test_severity_style_minimal():
    """Test that MINIMAL severity returns correct style."""
    style = get_severity_style("MINIMAL")
    assert style == "green"


def test_status_table_rendering():
    """Test that status table renders without errors."""
    console = Console(file=StringIO())
    data = {
        "probe1": {"pass_rate": 0.9, "fail_rate": 0.1},
        "probe2": {"pass_rate": 0.5, "fail_rate": 0.5},
    }

    # Should not raise any errors
    print_status_table(data, console_instance=console)
    output = console.file.getvalue()
    assert "probe1" in output or "probe2" in output
