"""Tests for promptfoo_evaluation MLflow handler.

These tests follow TDD principles - tests were written first, then implementation.
"""

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from promptfoo_evaluation.shared.mlflow_handler import (
    MLflowExperimentManager,
    PromptfooResultParser,
    log_promptfoo_run_to_mlflow,
)


class TestPromptfooResultParser:
    """Tests for parsing promptfoo JSON output."""

    def test_parse_minimal_results(self) -> None:
        """Test parsing minimal promptfoo results structure."""
        minimal_results = {
            "results": [
                {
                    "provider": "openai:chat:glm-5-flash",
                    "prompt": {"raw": "Test prompt"},
                    "outputs": [
                        {
                            "pass": True,
                            "score": 1.0,
                            "text": "Test output",
                            "gradingResult": {"pass": True, "reason": "Output matches expected"},
                        }
                    ],
                }
            ],
            "stats": {"totalTokens": 100, "totalCost": 0.001},
        }

        parser = PromptfooResultParser(minimal_results)
        assert parser.get_pass_rate() == 1.0
        assert parser.get_total_tokens() == 100
        assert parser.get_total_cost() == 0.001

    def test_parse_results_with_failures(self) -> None:
        """Test parsing results with mixed pass/fail."""
        results_with_failures = {
            "results": [
                {"outputs": [{"pass": True}]},
                {"outputs": [{"pass": False}]},
                {"outputs": [{"pass": True}]},
            ]
        }

        parser = PromptfooResultParser(results_with_failures)
        assert parser.get_pass_rate() == pytest.approx(0.666, rel=0.01)

    def test_get_average_score(self) -> None:
        """Test calculating average score from results."""
        scored_results = {
            "results": [
                {"outputs": [{"score": 0.8}]},
                {"outputs": [{"score": 0.6}]},
                {"outputs": [{"score": 1.0}]},
            ]
        }

        parser = PromptfooResultParser(scored_results)
        assert parser.get_average_score() == pytest.approx(0.8, rel=0.01)

    def test_get_metrics_dict(self) -> None:
        """Test extracting metrics as dictionary."""
        results = {
            "results": [
                {
                    "provider": "glm-5-flash",
                    "outputs": [{"pass": True, "score": 0.9, "latencyMs": 500}],
                }
            ],
            "stats": {"totalTokens": 150, "totalCost": 0.002},
        }

        parser = PromptfooResultParser(results)
        metrics = parser.get_metrics()

        assert "pass_rate" in metrics
        assert "average_score" in metrics
        assert "total_tokens" in metrics
        assert "total_cost" in metrics
        assert metrics["pass_rate"] == 1.0
        assert metrics["total_tokens"] == 150

    def test_get_latency_stats(self) -> None:
        """Test extracting latency statistics."""
        results_with_latency = {
            "results": [
                {"outputs": [{"latencyMs": 500}]},
                {"outputs": [{"latencyMs": 1000}]},
                {"outputs": [{"latencyMs": 750}]},
            ]
        }

        parser = PromptfooResultParser(results_with_latency)
        latency = parser.get_latency_stats()

        assert "avg_latency_ms" in latency
        assert latency["avg_latency_ms"] == 750


class TestMLflowExperimentManager:
    """Tests for MLflow experiment management."""

    def test_create_experiment(self) -> None:
        """Test creating a new MLflow experiment."""
        with mock.patch("mlflow.create_experiment") as mock_create:
            mock_create.return_value = "experiment-123"

            manager = MLflowExperimentManager(experiment_name="test-promptfoo")
            manager.create_experiment()

            mock_create.assert_called_once_with("test-promptfoo", tags={"framework": "promptfoo"})

    def test_get_or_create_experiment_existing(self) -> None:
        """Test getting existing experiment."""
        with mock.patch("mlflow.get_experiment_by_name") as mock_get:
            mock_exp = mock.Mock()
            mock_exp.experiment_id = "existing-123"
            mock_get.return_value = mock_exp

            manager = MLflowExperimentManager(experiment_name="existing")
            experiment_id = manager.get_or_create_experiment()

            assert experiment_id == "existing-123"

    def test_log_metrics(self) -> None:
        """Test logging metrics to MLflow."""
        with mock.patch("mlflow.log_metrics") as mock_log:
            manager = MLflowExperimentManager()
            manager.log_metrics({"pass_rate": 0.9, "cost": 0.01})

            mock_log.assert_called_once()

    def test_log_artifact_from_path(self) -> None:
        """Test logging artifact from file path."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name

        try:
            with mock.patch("mlflow.log_artifact") as mock_log:
                manager = MLflowExperimentManager()
                manager.log_artifact(Path(temp_path))

                mock_log.assert_called_once()
                args, _ = mock_log.call_args
                assert str(args[0]) == temp_path
        finally:
            Path(temp_path).unlink()

    def test_run_experiment_context(self) -> None:
        """Test using experiment context manager."""
        # NOTE: mock_end is not used, only mock_start
        with mock.patch("mlflow.start_run") as mock_start:
            mock_run = mock.Mock()
            mock_run.info.run_id = "run-456"
            mock_start.return_value.__enter__.return_value = mock_run

            manager = MLflowExperimentManager()
            with manager.run_experiment() as run:
                assert run.info.run_id == "run-456"


class TestIntegration:
    """Integration tests for MLflow handler utilities."""

    def test_parse_and_log_flow(self) -> None:
        """Test the full parse and log workflow."""
        results = {
            "results": [{"outputs": [{"pass": True, "score": 0.9}]}],
            "stats": {"totalTokens": 100, "totalCost": 0.001},
        }

        with mock.patch("mlflow.log_metrics"), mock.patch("mlflow.set_tag"):
            log_promptfoo_run_to_mlflow(results=results, run_name="test-run")
