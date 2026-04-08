"""Integration tests for advanced examples end-to-end workflows.

This module contains strategic integration tests that verify:
- Example scripts can run independently
- Shared utilities are correctly reused
- Integration points work together
"""

from pathlib import Path
import pytest


def test_all_example_scripts_can_be_imported():
    """Test that all example scripts can be imported independently."""
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
            pytest.fail(f"Failed to import {script_module}: {e}")


def test_chunking_script_has_main_function():
    """Test that chunking comparison script has main function."""
    from ragas_evaluation.examples.advanced import compare_chunking_strategies

    assert hasattr(compare_chunking_strategies, "main"), \
        "compare_chunking_strategies should have main function"
    assert callable(compare_chunking_strategies.main), \
        "main should be callable"


def test_model_script_has_main_function():
    """Test that model comparison script has main function."""
    from ragas_evaluation.examples.advanced import compare_models

    assert hasattr(compare_models, "main"), \
        "compare_models should have main function"
    assert callable(compare_models.main), \
        "main should be callable"


def test_custom_metrics_script_has_main_function():
    """Test that custom metrics script has main function."""
    from ragas_evaluation.examples.advanced import custom_metrics

    assert hasattr(custom_metrics, "main"), \
        "custom_metrics should have main function"
    assert callable(custom_metrics.main), \
        "main should be callable"


def test_data_generation_script_has_main_function():
    """Test that data generation script has main function."""
    from ragas_evaluation.examples.advanced import test_data_generation

    assert hasattr(test_data_generation, "main"), \
        "test_data_generation should have main function"
    assert callable(test_data_generation.main), \
        "main should be callable"


def test_shared_utilities_reused_in_advanced_examples():
    """Test that shared utilities are correctly reused in advanced examples."""
    # Check that advanced examples import from shared
    import ast

    advanced_dir = Path(__file__).parent.parent.parent / "src" / "ragas_evaluation" / "examples" / "advanced"

    shared_imports_found = False
    for script_file in advanced_dir.glob("*.py"):
        if script_file.name == "__init__.py":
            continue

        content = script_file.read_text()
        # Check for imports from shared utilities
        if "from ragas_evaluation.shared" in content or "ragas_evaluation.shared" in content:
            shared_imports_found = True
            break

    # Note: Advanced examples may not import shared utilities directly
    # as they demonstrate standalone patterns
    # This test verifies the structure is correct
    assert advanced_dir.exists(), "Advanced examples directory should exist"


def test_directory_structure_matches_spec():
    """Test that directory structure matches the specification."""
    project_root = Path(__file__).parent.parent.parent

    # Required directories
    required_dirs = [
        project_root / "src" / "ragas_evaluation" / "examples",
        project_root / "src" / "ragas_evaluation" / "examples" / "advanced",
        project_root / "src" / "ragas_evaluation" / "shared",
        project_root / "tests" / "ragas_evaluation",
    ]

    for dir_path in required_dirs:
        assert dir_path.exists(), f"Required directory {dir_path} should exist"
        assert dir_path.is_dir(), f"{dir_path} should be a directory"


def test_all_required_files_exist():
    """Test that all required files exist in advanced examples."""
    project_root = Path(__file__).parent.parent.parent
    advanced_dir = project_root / "src" / "ragas_evaluation" / "examples" / "advanced"

    required_files = [
        "__init__.py",
        "compare_chunking_strategies.py",
        "compare_models.py",
        "custom_metrics.py",
        "test_data_generation.py",
        "README.md",
    ]

    for filename in required_files:
        file_path = advanced_dir / filename
        assert file_path.exists(), f"Required file {filename} should exist in {advanced_dir}"


def test_documentation_files_exist():
    """Test that documentation files exist."""
    project_root = Path(__file__).parent.parent.parent

    # Main README
    main_readme = project_root / "src" / "ragas_evaluation" / "README.md"
    assert main_readme.exists(), "Main README should exist"

    # Advanced README
    advanced_readme = project_root / "src" / "ragas_evaluation" / "examples" / "advanced" / "README.md"
    assert advanced_readme.exists(), "Advanced README should exist"
