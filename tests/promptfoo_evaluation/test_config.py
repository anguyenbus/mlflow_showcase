"""Tests for promptfoo_evaluation configuration utilities.

These tests follow TDD principles - tests were written first, then implementation.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from promptfoo_evaluation.shared.config import (
    get_promptfoo_config_path,
    get_promptfoo_output_dir,
    get_zhipu_api_key,
    validate_promptfoo_installation,
)


class TestZhipuApiKey:
    """Tests for ZHIPU_API_KEY retrieval and validation."""

    def test_get_zhipu_api_key_from_env(self) -> None:
        """Test that ZHIPU_API_KEY is retrieved from environment."""
        test_key = "test_zhipu_key_12345"
        with mock.patch.dict(os.environ, {"ZHIPU_API_KEY": test_key}):
            assert get_zhipu_api_key() == test_key

    def test_get_zhipu_api_key_missing_raises_error(self) -> None:
        """Test that missing ZHIPU_API_KEY raises ValueError."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ZHIPU_API_KEY environment variable"):
                get_zhipu_api_key()

    def test_get_zhipu_api_key_empty_raises_error(self) -> None:
        """Test that empty ZHIPU_API_KEY raises ValueError."""
        with mock.patch.dict(os.environ, {"ZHIPU_API_KEY": ""}):
            with pytest.raises(ValueError, match="ZHIPU_API_KEY environment variable"):
                get_zhipu_api_key()

    def test_get_zhipu_api_key_whitespace_stripped(self) -> None:
        """Test that whitespace is stripped from API key."""
        test_key = "test_zhipu_key"
        with mock.patch.dict(os.environ, {"ZHIPU_API_KEY": f"  {test_key}  "}):
            assert get_zhipu_api_key() == test_key


class TestPromptfooPaths:
    """Tests for promptfoo path resolution utilities."""

    def test_get_promptfoo_output_dir_default(self) -> None:
        """Test default output directory path generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = get_promptfoo_output_dir(base_dir=Path(tmpdir))
            expected = Path(tmpdir) / "promptfoo_results"
            assert output_dir == expected

    def test_get_promptfoo_output_dir_custom_subdir(self) -> None:
        """Test custom subdirectory in output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = get_promptfoo_output_dir(
                base_dir=Path(tmpdir), subdirectory="custom_evals"
            )
            expected = Path(tmpdir) / "custom_evals"
            assert output_dir == expected

    def test_get_promptfoo_output_dir_creates_directory(self) -> None:
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = get_promptfoo_output_dir(base_dir=Path(tmpdir))
            assert output_dir.exists()
            assert output_dir.is_dir()

    def test_get_promptfoo_config_path(self) -> None:
        """Test config file path resolution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = get_promptfoo_config_path(
                config_name="test_config.yaml", base_dir=Path(tmpdir)
            )
            expected = Path(tmpdir) / "test_config.yaml"
            assert config_path == expected


class TestPromptfooValidation:
    """Tests for promptfoo installation validation."""

    def test_validate_promptfoo_installation_npx_available(self) -> None:
        """Test validation when npx is available."""
        with mock.patch("shutil.which", return_value="/usr/bin/npx"):
            # Should not raise
            validate_promptfoo_installation()

    def test_validate_promptfoo_installation_npx_missing(self) -> None:
        """Test validation when npx is not available."""
        with mock.patch("shutil.which", return_value=None):
            with pytest.raises(ValueError, match="promptfoo requires npx"):
                validate_promptfoo_installation()

    def test_validate_promptfoo_installation_global_available(self) -> None:
        """Test validation when promptfoo is globally installed."""
        with mock.patch("shutil.which") as mock_which:
            # npx not available but promptfoo global is
            mock_which.side_effect = lambda cmd: (
                "/usr/bin/promptfoo" if cmd == "promptfoo" else None
            )
            # Should not raise
            validate_promptfoo_installation()

    def test_validate_promptfoo_installation_neither_available(self) -> None:
        """Test validation when neither npx nor promptfoo global is available."""
        with mock.patch("shutil.which", return_value=None):
            with pytest.raises(ValueError, match="promptfoo requires npx"):
                validate_promptfoo_installation()
