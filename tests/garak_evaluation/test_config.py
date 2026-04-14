"""Tests for garak_evaluation configuration utilities."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_zhipu_api_key_retrieval_with_valid_key():
    """Test that ZHIPU_API_KEY is retrieved correctly when set."""
    # Arrange
    expected_key = "test_zhipu_api_key_12345"

    # Act
    with patch.dict(os.environ, {"ZHIPU_API_KEY": expected_key}, clear=True):
        # Import here to avoid import errors before patching
        from src.garak_evaluation.shared.config import get_zhipu_api_key

        result = get_zhipu_api_key()

    # Assert
    assert result == expected_key


def test_zhipu_api_key_validation_raises_error_when_missing():
    """Test that get_zhipu_api_key raises ValueError when key is not set."""
    # Arrange
    with patch.dict(os.environ, {}, clear=True):
        # Import here to avoid import errors before patching
        from src.garak_evaluation.shared.config import get_zhipu_api_key

        # Act & Assert
        with pytest.raises(ValueError, match="ZHIPU_API_KEY environment variable is required"):
            get_zhipu_api_key()


def test_output_directory_creation(tmp_path):
    """Test that output directory is created when it doesn't exist."""
    # Arrange
    test_subdirectory = "garak_test_output"

    # Act
    from src.garak_evaluation.shared.config import get_garak_output_dir

    result = get_garak_output_dir(base_dir=tmp_path, subdirectory=test_subdirectory)

    # Assert
    assert result == tmp_path / test_subdirectory
    assert result.exists()
    assert result.is_dir()


def test_garak_installation_validation_success():
    """Test that garak installation validation succeeds when garak is available."""
    # Arrange
    from src.garak_evaluation.shared.config import validate_garak_installation

    # Act & Assert - Should not raise when garak is importable
    # We mock the import to simulate garak being available
    with patch("builtins.__import__", return_value=MagicMock()):
        # This should not raise
        validate_garak_installation()
