"""Tests for RAGas configuration utilities."""

import os
from pathlib import Path
from unittest import mock

import pytest
from beartype.roar import BeartypeCallHintParamViolation

from ragas_evaluation.shared.config import (
    RagasConfig,
    get_ragas_config,
    get_ragas_data_dir,
    get_evaluation_dataset_path,
)


def test_ragas_config_creation():
    """Test that RagasConfig can be created with valid parameters."""
    config = RagasConfig(
        zhipu_api_key="test_key",
        mlflow_tracking_uri="sqlite:///mlflow.db",
        evaluation_data_path=Path("/data/ragas_evaluation"),
        experiment_name="test-experiment",
    )

    assert config.zhipu_api_key == "test_key"
    assert config.mlflow_tracking_uri == "sqlite:///mlflow.db"
    assert config.evaluation_data_path == Path("/data/ragas_evaluation")
    assert config.experiment_name == "test-experiment"


def test_ragas_config_frozen():
    """Test that RagasConfig is frozen and immutable."""
    config = RagasConfig(
        zhipu_api_key="test_key",
        mlflow_tracking_uri="sqlite:///mlflow.db",
        evaluation_data_path=Path("/data/ragas_evaluation"),
        experiment_name="test-experiment",
    )

    with pytest.raises(AttributeError):
        config.zhipu_api_key = "new_key"


def test_get_ragas_config_with_env():
    """Test get_ragas_config with environment variables set."""
    with mock.patch.dict(
        os.environ,
        {
            "ZHIPU_API_KEY": "test_api_key",
            "MLFLOW_TRACKING_URI": "sqlite:///test_mlflow.db",
        },
        clear=False,
    ):
        config = get_ragas_config()

        assert config.zhipu_api_key == "test_api_key"
        assert config.mlflow_tracking_uri == "sqlite:///test_mlflow.db"
        assert isinstance(config.evaluation_data_path, Path)
        assert config.experiment_name == "ragas-evaluation"


def test_get_ragas_config_default_values():
    """Test get_ragas_config uses defaults when env vars not set."""
    with mock.patch.dict(
        os.environ,
        {"ZHIPU_API_KEY": "test_api_key"},
        clear=False,
    ):
        # Clear MLFLOW_TRACKING_URI if it exists
        os.environ.pop("MLFLOW_TRACKING_URI", None)

        config = get_ragas_config()

        assert config.mlflow_tracking_uri == "sqlite:///mlflow.db"


def test_get_ragas_config_missing_api_key():
    """Test get_ragas_config raises error when ZHIPU_API_KEY is missing."""
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="ZHIPU_API_KEY"):
            get_ragas_config()


def test_get_ragas_data_dir():
    """Test get_ragas_data_dir returns correct path."""
    data_dir = get_ragas_data_dir()

    assert isinstance(data_dir, Path)
    assert data_dir.name == "ragas_evaluation"
    assert "data" in data_dir.parts


def test_get_evaluation_dataset_path():
    """Test get_evaluation_dataset_path returns correct path."""
    dataset_path = get_evaluation_dataset_path()

    assert isinstance(dataset_path, Path)
    assert dataset_path.name == "evaluation_dataset.json"
    assert "ragas_evaluation" in dataset_path.parts
