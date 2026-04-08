"""Tests for model comparison functionality."""

from unittest import mock

import pytest


def test_model_switching_works_with_configuration():
    """Test that model switching works with configuration."""
    try:
        from ragas_evaluation.examples.advanced.compare_models import (
            create_model_config,
        )

        # Test creating configurations for different models
        config1 = create_model_config(model_name="glm-5", temperature=0.2)
        assert config1["model_name"] == "glm-5"
        assert config1["temperature"] == 0.2

        config2 = create_model_config(model_name="glm-4", temperature=0.3)
        assert config2["model_name"] == "glm-4"
        assert config2["temperature"] == 0.3

    except ImportError:
        pytest.skip("compare_models.py not implemented yet")


def test_performance_metrics_are_captured():
    """Test that performance metrics (latency, token usage) are captured."""
    try:
        from ragas_evaluation.examples.advanced.compare_models import (
            ModelResult,
        )

        # Create a result with performance metrics
        result = ModelResult(
            model_name="glm-5",
            avg_latency=1.5,
            total_tokens=1000,
            metrics={"faithfulness": 0.85, "answer_relevancy": 0.90},
        )

        assert result.model_name == "glm-5"
        assert result.avg_latency == 1.5
        assert result.total_tokens == 1000
        assert "faithfulness" in result.metrics

    except ImportError:
        pytest.skip("compare_models.py not implemented yet")


def test_mlflow_logging_stores_run_comparisons():
    """Test that MLflow logging stores run comparisons."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        try:
            from ragas_evaluation.examples.advanced.compare_models import (
                log_model_comparison_to_mlflow,
            )

            # Mock MLflow operations
            with mock.patch("ragas_evaluation.examples.advanced.compare_models.mlflow") as mock_mlflow:
                # Test data
                results = [
                    {
                        "model_name": "glm-5",
                        "avg_latency": 1.5,
                        "total_tokens": 1000,
                        "metrics": {"faithfulness": 0.85},
                    }
                ]

                # This should not raise an error
                log_model_comparison_to_mlflow(results, experiment_name="test_experiment")

                # Verify MLflow was called
                assert mock_mlflow.set_experiment.called

        except ImportError:
            pytest.skip("compare_models.py not implemented yet")


def test_cost_benefit_analysis_output_format():
    """Test cost-benefit trade-off analysis output format."""
    try:
        from ragas_evaluation.examples.advanced.compare_models import (
            generate_cost_benefit_analysis,
        )

        # Create test results
        results = [
            {
                "model_name": "glm-5",
                "avg_latency": 1.5,
                "total_tokens": 1000,
                "metrics": {"faithfulness": 0.85, "answer_relevancy": 0.90},
                "cost_per_1k_tokens": 0.05,
            },
            {
                "model_name": "glm-4",
                "avg_latency": 1.2,
                "total_tokens": 950,
                "metrics": {"faithfulness": 0.80, "answer_relevancy": 0.85},
                "cost_per_1k_tokens": 0.03,
            },
        ]

        # Generate analysis
        analysis = generate_cost_benefit_analysis(results)

        # Verify analysis is generated
        assert isinstance(analysis, str)
        assert len(analysis) > 0
        assert "glm-5" in analysis or "glm-4" in analysis

    except ImportError:
        pytest.skip("compare_models.py not implemented yet")
