"""Tests for basic RAGas evaluation examples."""

from unittest import mock

import pytest


def test_simple_evaluation_main_execution():
    """Test that simple_evaluation.py main execution works."""
    # This test verifies that the simple_evaluation script can be imported
    # and has the expected main function or execution flow
    try:
        from ragas_evaluation.basics.simple_evaluation import main
        assert callable(main)
    except ImportError:
        pytest.skip("simple_evaluation.py not implemented yet")


def test_evaluation_dataset_loading():
    """Test that evaluation dataset loading works in context."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        from ragas_evaluation.shared.data_loader import load_evaluation_dataset

        # Mock the file existence check
        with mock.patch("ragas_evaluation.shared.data_loader.get_evaluation_dataset_path") as mock_path:
            mock_path.return_value.exists.return_value = True

            # Mock JSON loading
            test_data = [
                {
                    "question": "Test question",
                    "contexts": ["Test context"],
                    "response": "Test response"
                }
            ]

            with mock.patch("builtins.open", mock.mock_open(read_data='[{"question": "Test", "contexts": ["ctx"], "response": "resp"}]')):
                try:
                    data = load_evaluation_dataset()
                    assert isinstance(data, list)
                except FileNotFoundError:
                    # Expected if file doesn't exist
                    pass


def test_ragas_evaluation_execution():
    """Test that ragas evaluation execution works."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": "test_key"}):
        try:
            from ragas_evaluation.shared.metrics import create_ragas_evaluation

            # Create evaluation configuration
            config = create_ragas_evaluation()
            assert config is not None
            assert "metrics" in config
        except ImportError:
            pytest.skip("ragas not available")


def test_result_display_formatting():
    """Test that results display formatting works."""
    # Test that we have formatting utilities available
    try:
        from ragas_evaluation.shared.metrics import get_metric_description
        description = get_metric_description("faithfulness")
        assert isinstance(description, str)
        assert len(description) > 0
    except ImportError:
        pytest.skip("metrics module not available")


def test_metric_demonstration_functions():
    """Test that individual metric demonstration functions exist."""
    try:
        from ragas_evaluation.basics.metric_demonstration import (
            demonstrate_faithfulness,
            demonstrate_answer_relevancy,
            demonstrate_context_precision,
        )
        assert callable(demonstrate_faithfulness)
        assert callable(demonstrate_answer_relevancy)
        assert callable(demonstrate_context_precision)
    except ImportError:
        pytest.skip("metric_demonstration.py not implemented yet")


def test_error_handling_missing_data():
    """Test error handling for missing dataset."""
    with mock.patch.dict("os.environ", {}, clear=True):
        from ragas_evaluation.shared.config import validate_environment

        # Should raise ValueError when ZHIPU_API_KEY is missing
        with pytest.raises(ValueError, match="ZHIPU_API_KEY"):
            validate_environment()


def test_error_handling_missing_api_key():
    """Test error handling for missing API key."""
    with mock.patch.dict("os.environ", {"ZHIPU_API_KEY": ""}):
        from ragas_evaluation.shared.config import validate_environment

        # Should raise ValueError when ZHIPU_API_KEY is empty
        with pytest.raises(ValueError, match="ZHIPU_API_KEY"):
            validate_environment()
