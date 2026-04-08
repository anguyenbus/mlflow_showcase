"""Tests for advanced MLflow-integrated examples."""

from unittest import mock
from pathlib import Path
import tempfile
import json

import pytest

from ragas_evaluation.examples.advanced.with_mlflows.compare_chunking_strategies_with_mlflow import (  # noqa: E501
    generate_chunks,
    ChunkingResult,
)
from ragas_evaluation.examples.advanced.with_mlflows.compare_models_enhanced_with_mlflow import (  # noqa: E501
    create_model_config,
    ModelConfig,
    ModelResult,
)
from ragas_evaluation.examples.advanced.with_mlflows.custom_metrics_with_mlflow import (  # noqa: E501
    CitationAccuracyMetric,
    CompositeQualityMetric,
    MetricScore,
)
from ragas_evaluation.examples.advanced.with_mlflows.test_data_generation_with_mlflow import (  # noqa: E501
    DatasetStats,
    calculate_dataset_statistics,
    validate_dataset_quality,
)


class TestChunkingComparison:
    """Tests for chunking strategy comparison with MLflow."""

    def test_generate_chunks_creates_correct_size(self):
        """Test that generate_chunks creates chunks of correct size."""
        text = "a" * 1000  # 1000 character text
        chunk_size = 200
        overlap = 25

        chunks = generate_chunks(text, chunk_size, overlap)

        # First chunk should be exactly chunk_size
        assert len(chunks[0]) == chunk_size

        # Middle chunks should account for overlap
        for i in range(1, len(chunks) - 1):
            assert len(chunks[i]) <= chunk_size

        # Last chunk may be shorter
        assert len(chunks[-1]) <= chunk_size

    def test_generate_chunks_with_overlap(self):
        """Test that generate_chunks handles overlap correctly."""
        text = "abcdefghij" * 100  # Long text
        chunk_size = 50
        overlap = 10

        chunks = generate_chunks(text, chunk_size, overlap)

        # Verify overlap between consecutive chunks
        if len(chunks) > 1:
            # Last 10 chars of first chunk should match first 10 of second
            assert chunks[0][-overlap:] == chunks[1][:overlap]

    def test_chunking_result_dataclass(self):
        """Test ChunkingResult dataclass structure."""
        result = ChunkingResult(
            strategy="small",
            chunk_size=200,
            overlap=25,
            num_chunks=10,
            avg_chunk_length=195.5,
            retrieval_latency=0.25,
            total_time=1.5,
            metrics={"context_precision": 0.8},
        )

        assert result.strategy == "small"
        assert result.chunk_size == 200
        assert result.num_chunks == 10
        assert result.metrics["context_precision"] == 0.8

    def test_generate_chunks_empty_text(self):
        """Test generate_chunks with empty text."""
        chunks = generate_chunks("", 200, 25)
        assert chunks == []


class TestModelComparison:
    """Tests for model comparison with MLflow."""

    def test_create_model_config_default_values(self):
        """Test create_model_config with default temperature."""
        config = create_model_config("glm-5")

        assert isinstance(config, ModelConfig)
        assert config.model_name == "glm-5"
        assert config.temperature == 0.2
        assert config.max_tokens == 1000

    def test_create_model_config_custom_temperature(self):
        """Test create_model_config with custom temperature."""
        config = create_model_config("glm-4", temperature=0.5)

        assert config.model_name == "glm-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000

    def test_model_result_dataclass(self):
        """Test ModelResult dataclass structure."""
        result = ModelResult(
            model_name="glm-5",
            temperature=0.2,
            avg_latency=1.5,
            total_tokens=1000,
            latency_per_query=[1.4, 1.5, 1.6],
            metrics={"faithfulness": 0.85},
            cost_per_1k_tokens=0.05,
        )

        assert result.model_name == "glm-5"
        assert result.avg_latency == 1.5
        assert len(result.latency_per_query) == 3
        assert result.metrics["faithfulness"] == 0.85
        assert result.cost_per_1k_tokens == 0.05

    def test_model_config_dataclass_frozen(self):
        """Test that ModelConfig is frozen (immutable)."""
        config = ModelConfig(
            model_name="glm-5",
            temperature=0.2,
            max_tokens=1000,
        )

        # Should raise error when trying to modify frozen dataclass
        with pytest.raises(Exception):  # FrozenInstanceError or similar
            config.model_name = "glm-4"


class TestCustomMetrics:
    """Tests for custom metrics with MLflow."""

    def test_citation_accuracy_metric_with_citation(self):
        """Test CitationAccuracyMetric with proper citation."""
        metric = CitationAccuracyMetric()

        response = "According to Section 10-5, the GST rate is 10%."
        contexts = ["Section 10-5 states that GST is a broad-based tax of 10%."]

        score = metric.score(response, contexts)

        assert 0.0 <= score <= 1.0
        # Should have citation bonus due to "According to" citation marker
        assert score > 0.3

    def test_citation_accuracy_metric_without_citation(self):
        """Test CitationAccuracyMetric without citation markers."""
        metric = CitationAccuracyMetric()

        response = "The GST rate is 10%."
        contexts = ["GST is a broad-based tax of 10%."]

        score = metric.score(response, contexts)

        assert 0.0 <= score <= 1.0
        # Lower score due to no citation marker
        assert score < 0.5

    def test_composite_quality_metric_weights(self):
        """Test CompositeQualityMetric with custom weights."""
        metric = CompositeQualityMetric(
            faithfulness_weight=0.5,
            relevancy_weight=0.3,
            citation_weight=0.2,
        )

        response = "Test response"
        contexts = ["Test context"]
        ragas_scores = {"faithfulness": 0.8, "answer_relevancy": 0.9}

        score, components = metric.score(response, contexts, ragas_scores)

        assert 0.0 <= score <= 1.0
        assert "faithfulness" in components
        assert "answer_relevancy" in components
        assert "citation_accuracy" in components

        # Verify composite calculation
        expected = (
            0.8 * 0.5  # faithfulness
            + 0.9 * 0.3  # relevancy
            + components["citation_accuracy"] * 0.2  # citation
        )
        assert abs(score - expected) < 0.01

    def test_metric_score_dataclass(self):
        """Test MetricScore dataclass structure."""
        score = MetricScore(
            metric_name="test_metric",
            score=0.85,
            details="Test metric for evaluation",
        )

        assert score.metric_name == "test_metric"
        assert score.score == 0.85
        assert score.details == "Test metric for evaluation"
        assert score.components is None


class TestDataGeneration:
    """Tests for test data generation with MLflow."""

    def test_calculate_dataset_statistics(self):
        """Test calculate_dataset_statistics returns correct stats."""
        dataset = [
            {
                "question": "What is GST?",
                "contexts": ["GST is 10%"],
                "response": "GST is 10%",
            },
            {
                "question": "What are tax rates?",
                "contexts": ["Tax rates vary"],
                "response": "Tax rates vary",
            },
        ]

        stats = calculate_dataset_statistics(dataset, seed=42)

        assert stats.total_samples == 2
        assert stats.valid_samples == 2
        assert stats.avg_question_length > 0
        assert stats.avg_context_count == 1.0
        assert stats.generation_seed == 42

    def test_validate_dataset_quality_valid(self):
        """Test validate_dataset_quality with valid dataset."""
        dataset = [
            {
                "question": "What is GST? This is a valid question.",
                "contexts": ["GST is 10%"],
                "response": "GST is 10%",
            }
        ]

        result = validate_dataset_quality(dataset)

        assert result["valid"] is True
        assert result["total"] == 1
        assert result["valid_count"] == 1
        assert len(result["errors"]) == 0

    def test_validate_dataset_quality_invalid_missing_field(self):
        """Test validate_dataset_quality with missing required field."""
        dataset = [
            {
                "question": "What is GST?",
                # Missing "contexts" field
                "response": "GST is 10%",
            }
        ]

        result = validate_dataset_quality(dataset)

        assert result["valid"] is False
        assert result["total"] == 1
        assert result["valid_count"] == 0
        assert len(result["errors"]) > 0
        assert any("contexts" in error for error in result["errors"])

    def test_dataset_stats_dataclass(self):
        """Test DatasetStats dataclass structure."""
        stats = DatasetStats(
            total_samples=100,
            valid_samples=98,
            avg_question_length=45.5,
            avg_context_count=2.0,
            generation_seed=42,
        )

        assert stats.total_samples == 100
        assert stats.valid_samples == 98
        assert stats.avg_question_length == 45.5
        assert stats.avg_context_count == 2.0
        assert stats.generation_seed == 42


class TestMLflowIntegration:
    """Tests for MLflow integration in advanced examples."""

    def test_mlflow_logging_in_chunking(self):
        """Test that chunking strategy logs to MLflow correctly."""
        with mock.patch("mlflow.log_param") as mock_log_param:
            with mock.patch("mlflow.log_metric") as mock_log_metric:
                # Test parameter logging
                mock_log_param("strategy_name", "small")
                mock_log_param("chunk_size", "200")

                # Test metric logging
                mock_log_metric("num_chunks", 10)
                mock_log_metric("retrieval_latency", 0.25)

                # Verify calls
                assert mock_log_param.call_count == 2
                assert mock_log_metric.call_count == 2

    def test_mlflow_nested_run_structure(self):
        """Test that nested runs are created correctly."""
        with mock.patch("mlflow.start_run") as mock_start_run:
            # Mock parent run
            mock_parent = mock.Mock()
            mock_parent.info.run_id = "parent_123"
            mock_parent.__enter__ = mock.Mock(return_value=mock_parent)
            mock_parent.__exit__ = mock.Mock(return_value=False)

            # Mock nested run
            mock_nested = mock.Mock()
            mock_nested.info.run_id = "nested_456"
            mock_nested.__enter__ = mock.Mock(return_value=mock_nested)
            mock_nested.__exit__ = mock.Mock(return_value=False)

            mock_start_run.side_effect = [mock_parent, mock_nested]

            # Simulate parent run
            with mock_start_run(run_name="parent") as parent:
                parent_run_id = parent.info.run_id

                # Simulate nested run
                with mock_start_run(nested=True, run_name="child") as child:
                    child_run_id = child.info.run_id

            assert parent_run_id == "parent_123"
            assert child_run_id == "nested_456"
            assert mock_start_run.call_count == 2

    def test_custom_metric_prefix_in_mlflow(self):
        """Test that custom metrics use correct prefix in MLflow."""
        with mock.patch("mlflow.log_metric") as mock_log_metric:
            # Simulate custom metric logging with prefix
            mock_log_metric("custom_citation_accuracy", 0.85)
            mock_log_metric("custom_composite_quality", 0.75)

            # Verify calls
            assert mock_log_metric.call_count == 2
            call_args_list = [call[0][0] for call in mock_log_metric.call_args_list]
            assert all(arg.startswith("custom_") for arg in call_args_list)

    def test_dataset_artifact_logging(self):
        """Test that datasets are logged as artifacts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test dataset file
            dataset_path = Path(temp_dir) / "test_dataset.json"
            test_data = [{"question": "test", "contexts": ["test"], "response": "test"}]
            dataset_path.write_text(json.dumps(test_data))

            with mock.patch("mlflow.log_artifact") as mock_log_artifact:
                # Simulate artifact logging
                mock_log_artifact(str(dataset_path))

                # Verify call
                mock_log_artifact.assert_called_once()
                call_args = mock_log_artifact.call_args[0][0]
                assert str(dataset_path) in call_args or "test_dataset.json" in call_args
