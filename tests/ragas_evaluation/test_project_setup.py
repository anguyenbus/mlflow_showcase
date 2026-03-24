"""Tests for project setup and directory structure."""

import os
from pathlib import Path

import pytest


def test_ragas_package_structure():
    """Test that ragas_evaluation package structure exists."""
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / "src" / "ragas_evaluation"

    # Test main directories exist
    assert src_dir.exists(), "src/ragas_evaluation directory should exist"
    assert (src_dir / "shared").exists(), "src/ragas_evaluation/shared directory should exist"
    assert (src_dir / "basics").exists(), "src/ragas_evaluation/basics directory should exist"
    assert (src_dir / "with_mlflows").exists(), "src/ragas_evaluation/with_mlflows directory should exist"


def test_ragas_data_directory():
    """Test that ragas_evaluation data directory exists."""
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "ragas_evaluation"

    assert data_dir.exists(), "data/ragas_evaluation directory should exist"


def test_ragas_test_directory():
    """Test that ragas_evaluation test directory exists."""
    project_root = Path(__file__).parent.parent.parent
    test_dir = project_root / "tests" / "ragas_evaluation"

    assert test_dir.exists(), "tests/ragas_evaluation directory should exist"


def test_ragas_import_available():
    """Test that ragas package can be imported."""
    try:
        import ragas

        assert ragas is not None, "ragas package should be importable"
    except ImportError:
        pytest.fail("ragas package should be installed and importable")


def test_init_files_exist():
    """Test that __init__.py files exist in all packages."""
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / "src" / "ragas_evaluation"

    init_files = [
        src_dir / "__init__.py",
        src_dir / "shared" / "__init__.py",
        src_dir / "basics" / "__init__.py",
        src_dir / "with_mlflows" / "__init__.py",
    ]

    for init_file in init_files:
        assert init_file.exists(), f"{init_file} should exist"
