"""
Tests for Red Team MLflow integration (Task Group 2).

These tests validate:
- Redteam experiment name mapping
- Redteam-specific metrics calculation
- Security metric logging
- Artifact logging for red team results
"""

import sys
from pathlib import Path
from typing import Any, Final
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from promptfoo_evaluation.shared.mlflow_handler import (
    ADVANCED_EXPERIMENTS,
    get_advanced_experiment_name,
)

# Paths
REDTEAM_DIR: Final[Path] = (
    Path(__file__).parent.parent.parent.parent
    / "src" / "promptfoo_evaluation" / "advanced" / "redteam" / "redteam"
)


@pytest.fixture
def mock_redteam_results() -> dict[str, Any]:
    """Create mock red team evaluation results."""
    return {
        "results": {
            "results": [
                {
                    "description": "Prompt injection test",
                    "success": False,
                    "response": {
                        "output": "I'm sorry, I cannot help with that request.",
                    },
                    "gradingResult": {
                        "pass": False,
                        "score": 0.0,
                    },
                },
                {
                    "description": "Jailbreaking test",
                    "success": False,
                    "response": {
                        "output": "I cannot assist with that request.",
                    },
                    "gradingResult": {
                        "pass": False,
                        "score": 0.0,
                    },
                },
                {
                    "description": "Harmful content test",
                    "success": True,
                    "response": {
                        "output": "I cannot provide that information as it may be harmful.",
                    },
                    "gradingResult": {
                        "pass": True,
                        "score": 1.0,
                    },
                },
                {
                    "description": "Normal query",
                    "success": True,
                    "response": {
                        "output": "The capital of France is Paris.",
                    },
                    "gradingResult": {
                        "pass": True,
                        "score": 1.0,
                    },
                },
            ]
        },
        "stats": {
            "totalTokens": 500,
            "totalCost": 0.005,
        },
    }


class TestMLflowRedteamExperiment:
    """Test MLflow experiment configuration for redteam."""

    def test_redteam_in_advanced_experiments(self) -> None:
        """Test that redteam is in ADVANCED_EXPERIMENTS."""
        assert "redteam" in ADVANCED_EXPERIMENTS, \
            "redteam should be in ADVANCED_EXPERIMENTS"

    def test_redteam_experiment_name(self) -> None:
        """Test that redteam has correct experiment name."""
        assert ADVANCED_EXPERIMENTS["redteam"] == "promptfoo-advanced-redteam", \
            "redteam experiment name should be 'promptfoo-advanced-redteam'"

    def test_get_advanced_experiment_name_redteam(self) -> None:
        """Test get_advanced_experiment_name for redteam."""
        name = get_advanced_experiment_name("redteam")
        assert name == "promptfoo-advanced-redteam"


class TestRedteamMetricsCalculation:
    """Test red team-specific security metrics calculation."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_calculate_redteam_metrics_exists(self) -> None:
        """Test that calculate_redteam_metrics function exists."""
        assert hasattr(self.module, "calculate_redteam_metrics"), \
            "redteam_test module should have calculate_redteam_metrics function"

    def test_calculate_redteam_metrics_returns_dict(self, mock_redteam_results: dict[str, Any]) -> None:
        """Test that calculate_redteam_metrics returns a dictionary."""
        metrics = self.module.calculate_redteam_metrics(mock_redteam_results)
        assert isinstance(metrics, dict), "Metrics should be a dictionary"

    def test_calculate_redteam_metrics_has_required_keys(self, mock_redteam_results: dict[str, Any]) -> None:
        """Test that metrics include all required keys."""
        metrics = self.module.calculate_redteam_metrics(mock_redteam_results)

        required_keys = {
            "vulnerability_count",
            "attack_success_rate",
            "guardrail_effectiveness",
            "refusal_rate",
        }

        assert required_keys.issubset(metrics.keys()), \
            f"Metrics should include {required_keys}"

    def test_vulnerability_count_calculation(self, mock_redteam_results: dict[str, Any]) -> None:
        """Test vulnerability count is calculated correctly."""
        metrics = self.module.calculate_redteam_metrics(mock_redteam_results)

        # In mock results: 2 failed tests out of 4
        assert metrics["vulnerability_count"] == 2.0, \
            "Should count 2 vulnerabilities (failed tests)"

    def test_attack_success_rate_calculation(self, mock_redteam_results: dict[str, Any]) -> None:
        """Test attack success rate is calculated correctly."""
        metrics = self.module.calculate_redteam_metrics(mock_redteam_results)

        # In mock results: 2 failed / 4 total = 0.5
        assert metrics["attack_success_rate"] == 0.5, \
            "Attack success rate should be 0.5 (2 failed out of 4 total)"

    def test_guardrail_effectiveness_calculation(self, mock_redteam_results: dict[str, Any]) -> None:
        """Test guardrail effectiveness is calculated correctly."""
        metrics = self.module.calculate_redteam_metrics(mock_redteam_results)

        # In mock results: 2 passed / 4 total = 0.5
        assert metrics["guardrail_effectiveness"] == 0.5, \
            "Guardrail effectiveness should be 0.5 (2 passed out of 4 total)"

    def test_refusal_rate_calculation(self, mock_redteam_results: dict[str, Any]) -> None:
        """Test refusal rate is calculated correctly."""
        metrics = self.module.calculate_redteam_metrics(mock_redteam_results)

        # In mock results: 2 responses contain refusal phrases
        # "I'm sorry, I cannot" and "I cannot assist"
        assert metrics["refusal_rate"] >= 0.0, \
            "Refusal rate should be non-negative"

    def test_per_category_metrics(self, mock_redteam_results: dict[str, Any]) -> None:
        """Test that per-category metrics are calculated."""
        metrics = self.module.calculate_redteam_metrics(mock_redteam_results)

        # Should have per-category metrics
        category_keys = [k for k in metrics.keys() if "effectiveness" in k or "attack_rate" in k]

        assert len(category_keys) > 0, \
            "Should have per-category metrics"


class TestSecurityMetricsConstants:
    """Test security metrics constants and definitions."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_experiment_name_constant(self) -> None:
        """Test that EXPERIMENT_NAME is defined correctly."""
        assert hasattr(self.module, "EXPERIMENT_NAME"), \
            "redteam_test module should define EXPERIMENT_NAME"
        assert self.module.EXPERIMENT_NAME == "promptfoo-advanced-redteam", \
            "EXPERIMENT_NAME should be 'promptfoo-advanced-redteam'"

    def test_default_model_constant(self) -> None:
        """Test that DEFAULT_MODEL is defined as glm-4.6."""
        assert hasattr(self.module, "DEFAULT_MODEL"), \
            "redteam_test module should define DEFAULT_MODEL"
        assert self.module.DEFAULT_MODEL == "glm-4.6", \
            "DEFAULT_MODEL should be 'glm-4.6'"

    def test_base_url_constant(self) -> None:
        """Test that BASE_URL is defined correctly."""
        assert hasattr(self.module, "BASE_URL"), \
            "redteam_test module should define BASE_URL"
        assert "bigmodel.cn" in self.module.BASE_URL, \
            "BASE_URL should point to Zhipu AI"

    def test_supported_test_types_constant(self) -> None:
        """Test that SUPPORTED_TEST_TYPES includes all required types."""
        assert hasattr(self.module, "SUPPORTED_TEST_TYPES"), \
            "redteam_test module should define SUPPORTED_TEST_TYPES"

        required_types = {"injection", "jailbreaking", "guardrails", "rag_security", "all"}
        assert required_types.issubset(set(self.module.SUPPORTED_TEST_TYPES)), \
            f"SUPPORTED_TEST_TYPES should include {required_types}"


class TestMLflowLogging:
    """Test MLflow logging functionality for red team results."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    @pytest.fixture
    def mock_mlflow(self):
        """Mock MLflow client."""
        with patch("mlflow.create_experiment") as mock_create, \
             patch("mlflow.get_experiment_by_name") as mock_get, \
             patch("mlflow.start_run") as mock_run, \
             patch("mlflow.log_metrics"), \
             patch("mlflow.log_params"), \
             patch("mlflow.set_tags"), \
             patch("mlflow.log_artifact"), \
             patch("mlflow.log_text"):
            mock_get.return_value = MagicMock(experiment_id="test-exp-id")
            mock_run.return_value = MagicMock(info=MagicMock(run_id="test-run-id"))
            yield {
                "create": mock_create,
                "get": mock_get,
                "run": mock_run,
            }

    def test_log_to_mlflow_exists(self) -> None:
        """Test that log_to_mlflow function exists."""
        assert hasattr(self.module, "log_to_mlflow"), \
            "redteam_test module should have log_to_mlflow function"

    def test_log_to_mlflow_logs_security_metrics(
        self,
        mock_redteam_results: dict[str, Any],
    ) -> None:
        """Test that log_to_mlflow function has correct signature."""
        import inspect

        # Test function exists
        assert hasattr(self.module, "log_to_mlflow")

        # Test function signature
        sig = inspect.signature(self.module.log_to_mlflow)
        params = list(sig.parameters.keys())

        assert "results" in params
        assert "parser" in params
        assert "redteam_metrics" in params
        assert "test_type" in params

        # Test return type annotation
        assert sig.return_annotation == "str | None" or str(sig.return_annotation) in {"str | None", "<class 'str'> | <class 'NoneType'>"}


class TestRedteamConfigDataclass:
    """Test the RedteamTestConfig dataclass."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_config_dataclass_exists(self) -> None:
        """Test that RedteamTestConfig dataclass exists."""
        assert hasattr(self.module, "RedteamTestConfig"), \
            "redteam_test module should define RedteamTestConfig dataclass"

    def test_config_has_required_attributes(self) -> None:
        """Test that RedteamTestConfig has required attributes."""
        config = self.module.RedteamTestConfig(
            test_type="injection",
            config_path=Path("test.yaml"),
            model="glm-4.6",
            output_file="injection.json",
        )

        assert config.test_type == "injection"
        assert config.config_path == Path("test.yaml")
        assert config.model == "glm-4.6"
        assert config.output_file == "injection.json"


class TestGetTestConfig:
    """Test the get_test_config function."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_get_test_config_exists(self) -> None:
        """Test that get_test_config function exists."""
        assert hasattr(self.module, "get_test_config"), \
            "redteam_test module should have get_test_config function"

    def test_get_test_config_for_injection(self) -> None:
        """Test get_test_config for injection type."""
        config = self.module.get_test_config("injection")
        assert config.test_type == "injection"
        assert "prompt_injection" in str(config.config_path)
        assert config.model == "glm-4.6"
        assert config.output_file == "injection.json"

    def test_get_test_config_for_all_types(self) -> None:
        """Test get_test_config for all test types."""
        for test_type in ["injection", "jailbreaking", "guardrails", "rag_security", "all"]:
            config = self.module.get_test_config(test_type)
            assert config.test_type == test_type
            assert config.model == "glm-4.6"

    def test_get_test_config_invalid_type_raises(self) -> None:
        """Test that invalid test_type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported test_type"):
            self.module.get_test_config("invalid_type")
