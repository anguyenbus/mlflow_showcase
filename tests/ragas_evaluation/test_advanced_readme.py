"""Tests for advanced README documentation structure."""

from pathlib import Path
import pytest


def test_advanced_readme_exists():
    """Test that README.md exists at correct path."""
    project_root = Path(__file__).parent.parent.parent
    readme_path = project_root / "src" / "ragas_evaluation" / "examples" / "advanced" / "README.md"

    assert readme_path.exists(), f"README.md should exist at {readme_path}"


def test_readme_contains_required_sections():
    """Test that README contains required sections."""
    project_root = Path(__file__).parent.parent.parent
    readme_path = project_root / "src" / "ragas_evaluation" / "examples" / "advanced" / "README.md"

    content = readme_path.read_text()

    # Check for required sections
    required_sections = [
        "## Overview",
        "## Prerequisites",
        "## Examples",
        "## Troubleshooting",
        "## Real-World Use Cases",
        "## Key Concepts Learned",
    ]

    for section in required_sections:
        assert section in content, f"README should contain section: {section}"


def test_all_example_scripts_referenced():
    """Test that all example scripts are referenced in README."""
    project_root = Path(__file__).parent.parent.parent
    readme_path = project_root / "src" / "ragas_evaluation" / "examples" / "advanced" / "README.md"

    content = readme_path.read_text()

    # Check for example script references
    example_scripts = [
        "compare_chunking_strategies.py",
        "compare_models.py",
        "custom_metrics.py",
        "test_data_generation.py",
    ]

    for script in example_scripts:
        assert script in content, f"README should reference {script}"


def test_screenshot_placeholders_present():
    """Test that screenshot placeholder markers are included."""
    project_root = Path(__file__).parent.parent.parent
    readme_path = project_root / "src" / "ragas_evaluation" / "examples" / "advanced" / "README.md"

    content = readme_path.read_text()

    # Check for screenshot placeholder markers
    assert "[TODO: Add screenshot" in content or "TODO: Add screenshot" in content, \
        "README should contain screenshot placeholder markers"
