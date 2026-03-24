"""Tests for MLflow handler utilities."""

from unittest import mock

import pytest

from ragas_evaluation.shared.mlflow_handler import (
    setup_mlflow_experiment,
    log_ragas_results,
    get_mlflow_ui_url,
)


def test_setup_mlflow_experiment_creates_experiment():
    """Test that setup_mlflow_experiment creates or gets an MLflow experiment."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        with mock.patch("mlflow.set_tracking_uri"):
            with mock.patch("mlflow.get_experiment_by_name") as mock_get_exp:
                with mock.patch("mlflow.create_experiment") as mock_create_exp:
                    # Simulate experiment doesn't exist
                    mock_get_exp.return_value = None
                    mock_create_exp.return_value = "test_exp_id"  # Return string directly

                    experiment_id, experiment_name = setup_mlflow_experiment(
                        tracking_uri="sqlite:///mlflow.db",
                        experiment_name="test-experiment"
                    )

                    assert experiment_id == "test_exp_id"
                    assert experiment_name == "test-experiment"


def test_setup_mlflow_experiment_gets_existing():
    """Test that setup_mlflow_experiment gets existing experiment."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        with mock.patch("mlflow.set_tracking_uri"):
            with mock.patch("mlflow.get_experiment_by_name") as mock_get_exp:
                # Simulate experiment exists
                mock_experiment = mock.Mock()
                mock_experiment.experiment_id = "existing_exp_id"
                mock_get_exp.return_value = mock_experiment

                experiment_id, experiment_name = setup_mlflow_experiment(
                    tracking_uri="sqlite:///mlflow.db",
                    experiment_name="test-experiment"
                )

                assert experiment_id == "existing_exp_id"
                assert experiment_name == "test-experiment"


def test_setup_mlflow_experiment_sets_tracking_uri():
    """Test that setup_mlflow_experiment sets MLflow tracking URI."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        with mock.patch("mlflow.set_tracking_uri") as mock_set_uri:
            with mock.patch("mlflow.get_experiment_by_name") as mock_get_exp:
                with mock.patch("mlflow.create_experiment") as mock_create_exp:
                    mock_get_exp.return_value = None
                    mock_create_exp.return_value = "test_exp_id"  # Return string directly

                    _ = setup_mlflow_experiment(
                        tracking_uri="sqlite:///test.db",
                        experiment_name="test-experiment"
                    )

                    mock_set_uri.assert_called_once_with("sqlite:///test.db")


def test_log_ragas_results_logs_parameters():
    """Test that log_ragas_results logs parameters to MLflow."""
    with mock.patch("mlflow.log_params") as mock_log_params:
        with mock.patch("mlflow.log_metrics"):
            with mock.patch("mlflow.log_artifact"):
                with mock.patch("mlflow.set_tags"):
                    parameters = {
                        "model": "glm-5",
                        "temperature": 0.2,
                        "num_samples": 5
                    }

                    log_ragas_results(
                        parameters=parameters,
                        metrics={"faithfulness": 0.85},
                        dataset_path="/path/to/dataset.json"
                    )

                    mock_log_params.assert_called_once()
                    call_args = mock_log_params.call_args[0][0]
                    assert call_args == parameters


def test_log_ragas_results_logs_metrics():
    """Test that log_ragas_results logs metrics to MLflow."""
    with mock.patch("mlflow.log_params"):
        with mock.patch("mlflow.log_metrics") as mock_log_metrics:
            with mock.patch("mlflow.log_artifact"):
                with mock.patch("mlflow.set_tags"):
                    metrics = {
                        "faithfulness": 0.85,
                        "answer_relevancy": 0.92,
                        "context_precision": 0.78
                    }

                    log_ragas_results(
                        parameters={},
                        metrics=metrics,
                        dataset_path="/path/to/dataset.json"
                    )

                    mock_log_metrics.assert_called_once()
                    call_args = mock_log_metrics.call_args[0][0]
                    assert call_args == metrics


def test_log_ragas_results_logs_artifact():
    """Test that log_ragas_results logs dataset as artifact."""
    with mock.patch("mlflow.log_params"):
        with mock.patch("mlflow.log_metrics"):
            with mock.patch("mlflow.log_artifact") as mock_log_artifact:
                with mock.patch("mlflow.set_tags"):
                    dataset_path = "/path/to/evaluation_dataset.json"

                    log_ragas_results(
                        parameters={},
                        metrics={},
                        dataset_path=dataset_path
                    )

                    mock_log_artifact.assert_called_once()
                    call_args = mock_log_artifact.call_args[0][0]
                    assert call_args == dataset_path


def test_log_ragas_results_sets_tags():
    """Test that log_ragas_results sets custom tags."""
    with mock.patch("mlflow.log_params"):
        with mock.patch("mlflow.log_metrics"):
            with mock.patch("mlflow.log_artifact"):
                with mock.patch("mlflow.set_tags") as mock_set_tags:
                    tags = {
                        "evaluation_type": "ragas",
                        "backend": "zhipu",
                        "domain": "tax_evaluation"
                    }

                    log_ragas_results(
                        parameters={},
                        metrics={},
                        dataset_path="/path/to/dataset.json",
                        tags=tags
                    )

                    mock_set_tags.assert_called_once()
                    call_args = mock_set_tags.call_args[0][0]
                    assert call_args == tags


def test_get_mlflow_ui_url_returns_correct_url():
    """Test that get_mlflow_ui_url returns correct MLflow UI URL."""
    tracking_uri = "sqlite:///mlflow.db"
    experiment_id = "test_exp_id"
    run_id = "test_run_id"

    url = get_mlflow_ui_url(
        tracking_uri=tracking_uri,
        experiment_id=experiment_id,
        run_id=run_id
    )

    # Should return localhost URL for local sqlite tracking
    assert "localhost" in url or "127.0.0.1" in url
    assert str(experiment_id) in url or str(run_id) in url


def test_get_mlflow_ui_url_without_run_id():
    """Test that get_mlflow_ui_url works without run_id."""
    tracking_uri = "sqlite:///mlflow.db"
    experiment_id = "test_exp_id"

    url = get_mlflow_ui_url(
        tracking_uri=tracking_uri,
        experiment_id=experiment_id
    )

    assert url is not None
    assert isinstance(url, str)
    assert len(url) > 0
