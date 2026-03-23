"""Configuration module tests.

Tests environment variable validation, configuration defaults,
and missing required variables.
"""

import os
from pathlib import Path
from typing import Final
import pytest

from src.config import get_config, validate_environment


@pytest.fixture(autouse=True)
def clean_env() -> None:
    """Reset environment before each test."""
    # Preserve original values
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def test_config_defaults_with_valid_env() -> None:
    """Test that configuration loads with valid environment variables."""
    os.environ["ZHIPU_API_KEY"] = "test-key-12345"
    os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"

    config = get_config()

    assert config.zhipu_api_key == "test-key-12345"
    assert config.mlflow_tracking_uri == "http://localhost:5000"


def test_config_mlflow_tracking_uri_default() -> None:
    """Test that MLflow tracking URI defaults to local SQLite backend."""
    os.environ["ZHIPU_API_KEY"] = "test-key-12345"

    config = get_config()

    assert config.mlflow_tracking_uri == "sqlite:///mlflow.db"


def test_validate_environment_raises_on_missing_api_key() -> None:
    """Test that validation raises error when ZHIPU_API_KEY is missing."""
    # Don't set ZHIPU_API_KEY
    with pytest.raises(ValueError, match="ZHIPU_API_KEY environment variable"):
        validate_environment()


def test_validate_environment_succeeds_with_valid_key() -> None:
    """Test that validation succeeds with valid API key."""
    os.environ["ZHIPU_API_KEY"] = "test-key-12345"

    # Should not raise
    validate_environment()
