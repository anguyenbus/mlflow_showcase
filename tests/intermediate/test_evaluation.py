"""Evaluation framework tests.

Tests ROUGE metric calculation, exact match evaluation,
evaluation dataset loading, and custom metric creation.
"""

import pandas as pd
from unittest import mock
import pytest


@pytest.fixture(autouse=True)
def mock_config():
    """Mock configuration for all tests."""
    with mock.patch("src.intermediate.evaluate_summarization.get_config") as mock_cfg, \
         mock.patch("src.intermediate.evaluate_qa.get_config") as mock_cfg2:
        mock_cfg.return_value = mock.Mock(
            zhipu_api_key="test-api-key",
            mlflow_tracking_uri="sqlite:///mlflow.db"
        )
        mock_cfg2.return_value = mock.Mock(
            zhipu_api_key="test-api-key",
            mlflow_tracking_uri="sqlite:///mlflow.db"
        )
        yield


def test_rouge_metric_calculation() -> None:
    """Test ROUGE metric calculation for summarization."""
    with mock.patch("mlflow.evaluate") as mock_evaluate, \
         mock.patch("mlflow.start_run"), \
         mock.patch("mlflow.langchain.log_model"):

        mock_result = mock.Mock()
        mock_result.metrics = {"rouge1": 0.85, "rouge2": 0.75, "rougeL": 0.80}
        mock_evaluate.return_value = mock_result

        from src.intermediate.evaluate_summarization import evaluate_summarization

        eval_df = pd.DataFrame({
            "inputs": ["Summarize: Test document"],
            "ground_truth": ["Test summary"],
        })

        result = evaluate_summarization(eval_df, "test-model")

        assert result.metrics["rouge1"] == 0.85
        mock_evaluate.assert_called_once()


def test_exact_match_evaluation() -> None:
    """Test exact match metric for QA evaluation."""
    with mock.patch("mlflow.evaluate") as mock_evaluate, \
         mock.patch("mlflow.start_run"), \
         mock.patch("mlflow.openai.log_model"):

        mock_result = mock.Mock()
        mock_result.metrics = {"exact_match": 0.8}
        mock_evaluate.return_value = mock_result

        from src.intermediate.evaluate_qa import evaluate_qa

        eval_df = pd.DataFrame({
            "inputs": ["What is MLflow?", "What is Python?"],
            "ground_truth": [
                "MLflow is an open-source platform",
                "Python is a programming language",
            ],
        })

        result = evaluate_qa(eval_df, "test-model")

        assert result.metrics["exact_match"] == 0.8
        mock_evaluate.assert_called_once()


def test_evaluation_dataset_loading() -> None:
    """Test loading evaluation dataset from CSV."""
    from pathlib import Path
    import tempfile

    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("question,answer,category\n")
        f.write("What is tax?,Tax is a financial charge,tax_basics\n")
        f.write("Explain GST,GST is goods and services tax,tax_basics\n")
        temp_path = f.name

    try:
        from src.intermediate.evaluate_qa import load_evaluation_dataset

        df = load_evaluation_dataset(temp_path)

        assert len(df) == 2
        # NOTE: load_evaluation_dataset renames columns to MLflow format
        assert "inputs" in df.columns  # Renamed from "question"
        assert "ground_truth" in df.columns  # Renamed from "answer"
        assert "category" in df.columns
    finally:
        Path(temp_path).unlink()


def test_custom_metric_creation() -> None:
    """Test creating a custom evaluation metric."""
    with mock.patch("mlflow.metrics.make_metric") as mock_make_metric, \
         mock.patch("mlflow.evaluate") as mock_evaluate:

        from src.intermediate.evaluate_qa import create_custom_metric

        mock_metric = mock.Mock()
        mock_make_metric.return_value = mock_metric

        metric = create_custom_metric(
            name="legal_citation_accuracy",
            definition="Measure legal citation accuracy",
        )

        mock_make_metric.assert_called_once()
        # Verify the metric function was called
        assert metric is not None
