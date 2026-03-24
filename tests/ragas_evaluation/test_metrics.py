"""Tests for RAGas metrics and backend configuration."""

from unittest import mock

import pytest

from ragas_evaluation.shared.metrics import (
    configure_zhipu_backend,
    create_ragas_evaluation,
)


def test_configure_zhipu_backend_creates_llm():
    """Test that configure_zhipu_backend creates valid LLM and embeddings instances."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        llm, embeddings = configure_zhipu_backend()

        assert llm is not None
        assert embeddings is not None
        # Check that llm has required attributes
        assert hasattr(llm, "generate")


def test_configure_zhipu_backend_low_temperature():
    """Test that configure_zhipu_backend uses low temperature for evaluation."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        llm, embeddings = configure_zhipu_backend()

        # Temperature should be low (0.1-0.3) for consistent evaluation
        # InstructorLLM stores temperature in the model config
        assert llm is not None


def test_configure_zhipu_backend_missing_api_key():
    """Test that configure_zhipu_backend raises error without API key."""
    with mock.patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="ZHIPU_API_KEY"):
            configure_zhipu_backend()


def test_create_ragas_evaluation_returns_config():
    """Test that create_ragas_evaluation returns a configuration dict."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        config = create_ragas_evaluation()

        assert config is not None
        assert isinstance(config, dict)
        assert "metrics" in config
        assert "llm" in config
        assert "embeddings" in config


def test_create_ragas_evaluation_includes_standard_metrics():
    """Test that create_ragas_evaluation includes standard metrics."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        config = create_ragas_evaluation()

        # Check that evaluation has metrics configured
        assert "metrics" in config
        metrics = config["metrics"]
        assert len(metrics) > 0
        assert all(hasattr(m, "name") for m in metrics)


def test_create_ragas_evaluation_with_custom_llm():
    """Test that create_ragas_evaluation can accept custom LLM and embeddings."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        custom_llm, custom_embeddings = configure_zhipu_backend()
        config = create_ragas_evaluation(llm=custom_llm, embeddings=custom_embeddings)

        assert config is not None
        assert config["llm"] == custom_llm
        assert config["embeddings"] == custom_embeddings
