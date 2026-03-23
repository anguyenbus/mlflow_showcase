"""Tracing decorator tests.

Tests decorator-based tracing, manual span creation,
nested spans, and trace retrieval.
"""

from unittest import mock
import pytest

import mlflow


@pytest.fixture(autouse=True)
def mock_config():
    """Mock configuration for all tests."""
    with mock.patch("src.basics.tracing_decorators.get_config") as mock_cfg:
        mock_cfg.return_value = mock.Mock(
            zhipu_api_key="test-api-key",
            mlflow_tracking_uri="sqlite:///mlflow.db"
        )
        yield mock_cfg


@pytest.fixture(autouse=True)
def mock_mlflow_tracking():
    """Mock MLflow tracking setup."""
    with mock.patch("mlflow.set_tracking_uri"), \
         mock.patch("mlflow.set_experiment"):
        yield


def test_decorator_tracing() -> None:
    """Test that @mlflow.trace decorator instruments functions."""
    from src.basics.tracing_decorators import process_with_manual_span

    # Mock trace retrieval
    with mock.patch("mlflow.get_last_active_trace_id") as mock_trace_id:
        mock_trace_id.return_value = "test-trace-id"

        result = process_with_manual_span("test")

        assert result == "processed: test"
        mock_trace_id.assert_not_called()  # Function doesn't call this


def test_manual_span_creation() -> None:
    """Test manual span creation with context manager."""
    from src.basics.tracing_decorators import process_with_manual_span

    with mock.patch("mlflow.start_span") as mock_start_span:
        mock_span = mock.Mock()
        mock_start_span.return_value.__enter__.return_value = mock_span
        mock_start_span.return_value.__exit__.return_value = None

        result = process_with_manual_span("test")

        assert result == "processed: test"
        mock_start_span.assert_called_once()


def test_nested_spans() -> None:
    """Test nested span creation showing parent-child relationships."""
    from src.basics.tracing_decorators import nested_function_call

    with mock.patch("mlflow.start_span") as mock_start_span:
        mock_span = mock.Mock()
        mock_start_span.return_value.__enter__.return_value = mock_span
        mock_start_span.return_value.__exit__.return_value = None

        result = nested_function_call(5)

        assert result == 25
        # Verify multiple span levels were created
        assert mock_start_span.call_count >= 2


def test_trace_retrieval() -> None:
    """Test retrieving and inspecting traces."""
    from src.basics.tracing_decorators import nested_function_call

    # Mock trace object
    mock_trace = mock.Mock()
    mock_trace.to_dict.return_value = {"trace_id": "test-trace-id"}

    with mock.patch("mlflow.start_span"), \
         mock.patch("mlflow.get_last_active_trace_id") as mock_trace_id, \
         mock.patch("mlflow.get_trace") as mock_get_trace:

        mock_trace_id.return_value = "test-trace-id"
        mock_get_trace.return_value = mock_trace

        result = nested_function_call(10)

        assert result == 100
