"""Zhipu AI client tests.

Tests API client initialization, basic completion calls,
and error handling for API failures.
"""

from unittest import mock
import pytest

from src.basics.zhipu_client import ZhipuAIClient, ZhipuAIError


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with mock.patch("src.basics.zhipu_client.get_config") as mock_cfg:
        mock_cfg.return_value = mock.Mock(
            zhipu_api_key="test-api-key-12345",
            mlflow_tracking_uri="sqlite:///mlflow.db"
        )
        yield mock_cfg


def test_zhipu_client_initialization(mock_config) -> None:
    """Test that Zhipu AI client initializes correctly."""
    with mock.patch("src.basics.zhipu_client.ZhipuaiSDK"):
        client = ZhipuAIClient()

        assert client.api_key == "test-api-key-12345"
        assert client.model == "glm-5-flash"


def test_zhipu_client_completion_call(mock_config) -> None:
    """Test basic completion call with mocked API."""
    with mock.patch("src.basics.zhipu_client.ZhipuaiSDK") as mock_sdk:
        # Mock the API response
        mock_response = mock.Mock()
        mock_response.choices = [
            mock.Mock(message=mock.Mock(content="Test response"))
        ]
        mock_sdk.return_value.chat.completions.create.return_value = mock_response

        client = ZhipuAIClient()
        response = client.complete("Test prompt")

        assert response == "Test response"
        # Verify API was called correctly
        mock_sdk.return_value.chat.completions.create.assert_called_once()


def test_zhipu_client_handles_api_errors(mock_config) -> None:
    """Test error handling for API failures."""
    with mock.patch("src.basics.zhipu_client.ZhipuaiSDK") as mock_sdk:
        # Mock API error
        mock_sdk.return_value.chat.completions.create.side_effect = Exception("API Error")

        client = ZhipuAIClient()

        with pytest.raises(ZhipuAIError, match="Zhipu AI API call failed"):
            client.complete("Test prompt")


def test_zhipu_client_retry_on_failure(mock_config) -> None:
    """Test that client retries on transient failures."""
    with mock.patch("src.basics.zhipu_client.ZhipuaiSDK") as mock_sdk:
        # Mock API that fails once then succeeds
        mock_response = mock.Mock()
        mock_response.choices = [
            mock.Mock(message=mock.Mock(content="Success after retry"))
        ]

        mock_create = mock_sdk.return_value.chat.completions.create
        mock_create.side_effect = [Exception("Transient error"), mock_response]

        client = ZhipuAIClient()

        # Should succeed after retry
        response = client.complete("Test prompt")

        assert response == "Success after retry"
        assert mock_create.call_count == 2
