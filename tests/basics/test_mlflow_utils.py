"""MLflow utilities tests.

Tests experiment creation, run logging (params, metrics),
and artifact logging.
"""

from pathlib import Path
import tempfile
from unittest import mock
import pytest

from src.basics.mlflow_utils import (
    log_params,
    log_metrics,
    log_artifact,
)


@pytest.fixture(autouse=True)
def mock_config():
    """Mock configuration for all tests."""
    with mock.patch("src.basics.mlflow_utils.get_config") as mock_cfg:
        mock_cfg.return_value = mock.Mock(
            zhipu_api_key="test-api-key",
            mlflow_tracking_uri="sqlite:///mlflow.db"
        )
        yield mock_cfg


@pytest.fixture(autouse=True)
def mock_active_run():
    """Mock active MLflow run for tests that need it."""
    with mock.patch("mlflow.active_run") as mock_run:
        mock_run.return_value = mock.Mock(info=mock.Mock(run_id="test-run-id"))
        yield mock_run


def test_create_experiment() -> None:
    """Test that MLflow experiment is created successfully."""
    import mlflow
    from src.basics.mlflow_utils import create_experiment

    # Create a proper mock experiment
    mock_exp = mock.MagicMock(spec=mlflow.entities.Experiment)
    mock_exp.experiment_id = "test-exp-id"

    with mock.patch("mlflow.set_experiment") as mock_set_exp, \
         mock.patch("mlflow.set_tracking_uri"):

        mock_set_exp.return_value = mock_exp

        exp = create_experiment("test_experiment")

        assert exp.experiment_id == "test-exp-id"
        mock_set_exp.assert_called_once_with("test_experiment")


def test_log_params_and_metrics() -> None:
    """Test logging parameters and metrics to MLflow run."""
    with mock.patch("mlflow.log_params") as mock_log_params, \
         mock.patch("mlflow.log_metrics") as mock_log_metrics:

        params = {"param1": "value1", "param2": "value2"}
        metrics = {"metric1": 0.85, "metric2": 1.23}

        log_params(params)
        log_metrics(metrics)

        mock_log_params.assert_called_once_with(params)
        mock_log_metrics.assert_called_once_with(metrics)


def test_log_artifact() -> None:
    """Test logging an artifact file to MLflow."""
    with tempfile.TemporaryDirectory() as tmpdir, \
         mock.patch("mlflow.log_artifact") as mock_log:

        # Create a test file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("Test content")

        log_artifact(str(test_file))

        mock_log.assert_called_once_with(str(test_file), None)


def test_log_batch_metrics() -> None:
    """Test batch metric recording with steps."""
    with mock.patch("mlflow.log_metrics") as mock_log:
        metrics_history = [
            {"accuracy": 0.7, "loss": 0.5},
            {"accuracy": 0.8, "loss": 0.4},
            {"accuracy": 0.85, "loss": 0.3},
        ]

        for step, metrics in enumerate(metrics_history):
            log_metrics(metrics, step=step)

        # Verify log_metrics was called 3 times
        assert mock_log.call_count == 3
