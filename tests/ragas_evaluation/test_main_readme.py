"""Tests for main README documentation structure."""

from pathlib import Path
import pytest


def test_main_readme_exists():
    """Test that main README.md exists at correct path."""
    project_root = Path(__file__).parent.parent.parent
    readme_path = project_root / "src" / "ragas_evaluation" / "README.md"

    assert readme_path.exists(), f"README.md should exist at {readme_path}"


def test_advanced_examples_section_present():
    """Test that advanced examples section is present."""
    project_root = Path(__file__).parent.parent.parent
    readme_path = project_root / "src" / "ragas_evaluation" / "README.md"

    content = readme_path.read_text()

    # Check for advanced examples section
    assert "Advanced Examples" in content or "examples/advanced" in content, \
        "README should contain advanced examples section"


def test_all_examples_linked_correctly():
    """Test that all examples are linked correctly."""
    project_root = Path(__file__).parent.parent.parent
    readme_path = project_root / "src" / "ragas_evaluation" / "README.md"

    content = readme_path.read_text()

    # Check for links to all example directories
    example_links = [
        "basics/",
        "with_mlflows/",
        "examples/advanced/",
    ]

    for link in example_links:
        assert link in content, f"README should link to {link}"


def test_navigation_structure_complete():
    """Test that navigation structure is complete."""
    project_root = Path(__file__).parent.parent.parent
    readme_path = project_root / "src" / "ragas_evaluation" / "README.md"

    content = readme_path.read_text()

    # Check for navigation elements
    nav_elements = ["## Overview", "## Examples", "## Quick Reference"]
    present = sum(1 for element in nav_elements if element in content)

    assert present >= 2, "README should contain navigation elements"
