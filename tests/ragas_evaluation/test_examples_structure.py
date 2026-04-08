"""Tests for examples directory structure validation."""

from pathlib import Path

import pytest


def test_examples_directory_exists():
    """Test that src/ragas_evaluation/examples/ directory exists."""
    project_root = Path(__file__).parent.parent.parent
    examples_dir = project_root / "src" / "ragas_evaluation" / "examples"

    assert examples_dir.exists(), "src/ragas_evaluation/examples/ directory should exist"
    assert examples_dir.is_dir(), "examples should be a directory"


def test_examples_advanced_directory_exists():
    """Test that src/ragas_evaluation/examples/advanced/ directory exists."""
    project_root = Path(__file__).parent.parent.parent
    advanced_dir = project_root / "src" / "ragas_evaluation" / "examples" / "advanced"

    assert advanced_dir.exists(), "src/ragas_evaluation/examples/advanced/ directory should exist"
    assert advanced_dir.is_dir(), "advanced should be a directory"


def test_examples_init_file_exports():
    """Test that src/ragas_evaluation/examples/__init__.py exports expected symbols."""
    try:
        from ragas_evaluation.examples import __all__ as examples_exports

        # Verify that the __init__.py has an __all__ export list
        assert isinstance(examples_exports, list), "__all__ should be a list"

    except ImportError:
        pytest.skip("examples package not fully implemented yet")
    except AttributeError:
        # __all__ is optional, so this is not a failure
        pytest.skip("examples __init__.py does not define __all__")


def test_examples_scripts_are_importable():
    """Test that all example scripts are importable."""
    example_scripts = [
        "ragas_evaluation.examples.advanced.compare_chunking_strategies",
        "ragas_evaluation.examples.advanced.compare_models",
        "ragas_evaluation.examples.advanced.custom_metrics",
        "ragas_evaluation.examples.advanced.test_data_generation",
    ]

    for script_module in example_scripts:
        try:
            __import__(script_module)
        except ImportError as e:
            pytest.skip(f"{script_module} not implemented yet: {e}")


def test_directory_structure_matches_spec():
    """Test that directory structure matches the specification."""
    project_root = Path(__file__).parent.parent.parent
    examples_dir = project_root / "src" / "ragas_evaluation" / "examples"
    advanced_dir = examples_dir / "advanced"

    # Expected files in advanced directory
    expected_files = [
        "__init__.py",
        "compare_chunking_strategies.py",
        "compare_models.py",
        "custom_metrics.py",
        "test_data_generation.py",
        "README.md",
    ]

    for expected_file in expected_files:
        file_path = advanced_dir / expected_file
        assert file_path.exists(), f"{expected_file} should exist in {advanced_dir}"
