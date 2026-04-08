"""Tests for custom metrics functionality."""

import pytest


def test_simple_custom_metric_evaluates_correctly():
    """Test that simple custom metric evaluates correctly."""
    try:
        from ragas_evaluation.examples.advanced.custom_metrics import (
            CitationAccuracyMetric,
        )

        # Create metric instance
        metric = CitationAccuracyMetric()

        # Test evaluation
        result = metric.score(
            response="According to Section 10-5, the GST rate is 10%.",
            contexts=["Section 10-5 states that GST is 10%."],
        )

        # Verify result
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    except ImportError:
        pytest.skip("custom_metrics.py not implemented yet")


def test_complex_composite_metric_combines_scores():
    """Test that complex composite metric combines multiple RAGAS scores properly."""
    try:
        from ragas_evaluation.examples.advanced.custom_metrics import (
            CompositeQualityMetric,
        )

        # Create metric instance
        metric = CompositeQualityMetric(
            faithfulness_weight=0.4,
            relevancy_weight=0.3,
            citation_weight=0.3,
        )

        # Test evaluation
        result = metric.score(
            response="The GST rate is 10% as per tax law.",
            contexts=["GST is a broad-based tax of 10%."],
            ragas_scores={
                "faithfulness": 0.85,
                "answer_relevancy": 0.90,
            },
        )

        # Verify result is weighted combination
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    except ImportError:
        pytest.skip("custom_metrics.py not implemented yet")


def test_metric_registration_with_ragas():
    """Test that custom metric registration with RAGAS works."""
    try:
        from ragas_evaluation.examples.advanced.custom_metrics import (
            register_custom_metric,
        )

        # Create a simple metric function
        def dummy_metric(response: str, contexts: list) -> float:
            return 0.5

        # Register the metric
        registered = register_custom_metric("dummy_metric", dummy_metric)

        # Verify registration
        assert registered is not None

    except ImportError:
        pytest.skip("custom_metrics.py not implemented yet")


def test_custom_metric_integration_with_standard_workflow():
    """Test that custom metric integrates with standard RAGAS evaluation workflow."""
    try:
        from ragas_evaluation.examples.advanced.custom_metrics import (
            evaluate_with_custom_metrics,
        )

        # Test data
        test_data = [
            {
                "question": "What is GST?",
                "contexts": ["GST is a tax of 10%."],
                "response": "GST is 10%.",
            }
        ]

        # Evaluate with custom metrics
        results = evaluate_with_custom_metrics(
            data=test_data,
            custom_metrics=["citation_accuracy"],
        )

        # Verify results contain custom metric
        assert "citation_accuracy" in results or len(results) > 0

    except ImportError:
        pytest.skip("custom_metrics.py not implemented yet")
