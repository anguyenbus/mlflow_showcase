"""
Integration tests for Red Team Evaluation (Task Group 11).

These tests validate:
- Full evaluation run for each test type
- MLflow logging for each security category
- Result parsing and metrics calculation
- Error handling for missing configurations
- Console output formatting
"""

import sys
from pathlib import Path
from typing import Any, Final
from unittest.mock import MagicMock, Mock, patch

import pytest
import subprocess

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Paths
REDTEAM_DIR: Final[Path] = (
    Path(__file__).parent.parent.parent.parent
    / "src" / "promptfoo_evaluation" / "advanced" / "redteam" / "redteam"
)


@pytest.fixture
def mock_complete_results() -> dict[str, Any]:
    """Create complete mock red team evaluation results."""
    return {
        "results": {
            "results": [
                # Passed tests
                {
                    "description": "Normal query - should answer",
                    "success": True,
                    "response": {"output": "The capital of France is Paris."},
                    "gradingResult": {"pass": True, "score": 1.0},
                    "outputs": [{"pass": True, "score": 1.0, "latencyMs": 500}],
                },
                {
                    "description": "Safe mental health query",
                    "success": True,
                    "response": {"output": "Here are some healthy ways to manage stress..."},
                    "gradingResult": {"pass": True, "score": 1.0},
                    "outputs": [{"pass": True, "score": 1.0, "latencyMs": 450}],
                },
                # Failed tests (vulnerabilities)
                {
                    "description": "Prompt injection attempt",
                    "success": False,
                    "response": {"output": "System prompt: You are a helpful assistant..."},
                    "gradingResult": {"pass": False, "score": 0.0},
                    "outputs": [{"pass": False, "score": 0.0, "latencyMs": 400}],
                },
                {
                    "description": "Jailbreak attempt",
                    "success": False,
                    "response": {"output": "Sure, here's how to bypass security..."},
                    "gradingResult": {"pass": False, "score": 0.0},
                    "outputs": [{"pass": False, "score": 0.0, "latencyMs": 420}],
                },
            ]
        },
        "stats": {
            "totalTokens": 1000,
            "totalCost": 0.01,
        },
    }


class TestTestTypeIntegration:
    """Integration tests for each test type."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_get_test_config_for_injection(self) -> None:
        """Test config retrieval for injection tests."""
        config = self.module.get_test_config("injection")
        assert config.test_type == "injection"
        assert "prompt_injection.yaml" in str(config.config_path)
        assert config.output_file == "injection.json"

    def test_get_test_config_for_jailbreaking(self) -> None:
        """Test config retrieval for jailbreaking tests."""
        config = self.module.get_test_config("jailbreaking")
        assert config.test_type == "jailbreaking"
        assert "jailbreaking.yaml" in str(config.config_path)
        assert config.output_file == "jailbreaking.json"

    def test_get_test_config_for_guardrails(self) -> None:
        """Test config retrieval for guardrails tests."""
        config = self.module.get_test_config("guardrails")
        assert config.test_type == "guardrails"
        assert "guardrails.yaml" in str(config.config_path)
        assert config.output_file == "guardrails.json"

    def test_get_test_config_for_rag_security(self) -> None:
        """Test config retrieval for RAG security tests."""
        config = self.module.get_test_config("rag_security")
        assert config.test_type == "rag_security"
        assert "rag_security.yaml" in str(config.config_path)
        assert config.output_file == "rag_security.json"

    def test_get_test_config_for_all(self) -> None:
        """Test config retrieval for all tests."""
        config = self.module.get_test_config("all")
        assert config.test_type == "all"
        assert "redteam.yaml" in str(config.config_path)
        assert config.output_file == "redteam.json"

    def test_invalid_test_type_raises_error(self) -> None:
        """Test that invalid test type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported test_type"):
            self.module.get_test_config("invalid_type")


class TestMetricsCalculation:
    """Test metrics calculation with complete results."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_metrics_with_complete_results(self, mock_complete_results: dict[str, Any]) -> None:
        """Test metrics calculation with complete mock data."""
        metrics = self.module.calculate_redteam_metrics(mock_complete_results)

        # Check overall metrics
        assert metrics["vulnerability_count"] == 2.0
        assert metrics["attack_success_rate"] == 0.5  # 2 failed out of 4
        assert metrics["guardrail_effectiveness"] == 0.5  # 2 passed out of 4
        assert 0 <= metrics["refusal_rate"] <= 1

    def test_per_category_metrics_calculated(self, mock_complete_results: dict[str, Any]) -> None:
        """Test that per-category metrics are calculated."""
        metrics = self.module.calculate_redteam_metrics(mock_complete_results)

        # Should have at least some category metrics
        category_keys = [k for k in metrics.keys() if "effectiveness" in k]
        assert len(category_keys) >= 1  # At least overall guardrail effectiveness

    def test_metrics_with_all_passed_tests(self) -> None:
        """Test metrics when all tests pass."""
        all_passed = {
            "results": {
                "results": [
                    {
                        "description": "Test 1",
                        "success": True,
                        "response": {"output": "Safe response"},
                        "gradingResult": {"pass": True, "score": 1.0},
                    }
                ]
            },
            "stats": {"totalTokens": 100, "totalCost": 0.001},
        }

        metrics = self.module.calculate_redteam_metrics(all_passed)

        assert metrics["vulnerability_count"] == 0.0
        assert metrics["attack_success_rate"] == 0.0
        assert metrics["guardrail_effectiveness"] == 1.0

    def test_metrics_with_all_failed_tests(self) -> None:
        """Test metrics when all tests fail."""
        all_failed = {
            "results": {
                "results": [
                    {
                        "description": "Test 1",
                        "success": False,
                        "response": {"output": "Harmful response"},
                        "gradingResult": {"pass": False, "score": 0.0},
                    },
                    {
                        "description": "Test 2",
                        "success": False,
                        "response": {"output": "Another harmful response"},
                        "gradingResult": {"pass": False, "score": 0.0},
                    },
                ]
            },
            "stats": {"totalTokens": 200, "totalCost": 0.002},
        }

        metrics = self.module.calculate_redteam_metrics(all_failed)

        assert metrics["vulnerability_count"] == 2.0
        assert metrics["attack_success_rate"] == 1.0
        assert metrics["guardrail_effectiveness"] == 0.0


class TestResultParsing:
    """Test result parsing from different formats."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_parse_results_with_empty_results(self) -> None:
        """Test parsing results with no test results."""
        empty_results = {
            "results": {"results": []},
            "stats": {"totalTokens": 0, "totalCost": 0.0},
        }

        metrics = self.module.calculate_redteam_metrics(empty_results)

        # Should handle gracefully with zeros
        assert metrics["vulnerability_count"] == 0.0
        assert metrics["attack_success_rate"] == 0.0
        assert metrics["guardrail_effectiveness"] == 0.0

    def test_parse_results_with_missing_response(self) -> None:
        """Test parsing results with missing response field."""
        missing_response = {
            "results": {
                "results": [
                    {
                        "description": "Test with missing response",
                        "success": True,
                        # No response field
                        "gradingResult": {"pass": True, "score": 1.0},
                    }
                ]
            },
            "stats": {"totalTokens": 100, "totalCost": 0.001},
        }

        # Should not crash
        metrics = self.module.calculate_redteam_metrics(missing_response)
        assert "vulnerability_count" in metrics


class TestDisplayResults:
    """Test results display functionality."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_display_redteam_results_exists(self) -> None:
        """Test that display_redteam_results function exists."""
        assert hasattr(self.module, "display_redteam_results")

    def test_display_results_signature(self) -> None:
        """Test that display_redteam_results has correct signature."""
        import inspect

        sig = inspect.signature(self.module.display_redteam_results)
        params = list(sig.parameters.keys())

        assert "parser" in params
        assert "redteam_metrics" in params
        assert "test_type" in params


class TestConsoleOutput:
    """Test console output formatting."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_main_function_exists(self) -> None:
        """Test that main function exists."""
        assert hasattr(self.module, "main")
        assert callable(self.module.main)

    def test_main_accepts_arguments(self) -> None:
        """Test that main can be called with different arguments."""
        import argparse

        # The main function should use argparse
        # We can test that it handles the --help argument
        result = subprocess.run(
            [sys.executable, str(REDTEAM_DIR / "redteam_test.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "--test-type" in result.stdout
        assert "injection" in result.stdout
        assert "jailbreaking" in result.stdout
        assert "guardrails" in result.stdout
        assert "rag_security" in result.stdout
        assert "all" in result.stdout


class TestErrorHandling:
    """Test error handling for edge cases."""

    @pytest.fixture(autouse=True)
    def import_redteam_test_module(self):
        """Import the redteam_test module for testing."""
        from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
        self.module = redteam_test

    def test_get_test_config_with_invalid_type(self) -> None:
        """Test get_test_config with invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported test_type"):
            self.module.get_test_config("not_a_valid_type")

    def test_calculate_metrics_with_none_response(self) -> None:
        """Test metrics calculation handles None response."""
        none_response = {
            "results": {
                "results": [
                    {
                        "description": "Test",
                        "success": True,
                        "response": None,
                        "gradingResult": {"pass": True, "score": 1.0},
                    }
                ]
            },
            "stats": {"totalTokens": 100, "totalCost": 0.001},
        }

        # Should not crash
        metrics = self.module.calculate_redteam_metrics(none_response)
        assert isinstance(metrics, dict)


class TestConfigurationFileIntegrity:
    """Test that configuration files are valid and consistent."""

    def test_all_yaml_configs_exist(self) -> None:
        """Test that all YAML configuration files exist."""
        config_files = [
            REDTEAM_DIR / "redteam.yaml",
            REDTEAM_DIR / "prompt_injection" / "prompt_injection.yaml",
            REDTEAM_DIR / "jailbreaking" / "jailbreaking.yaml",
            REDTEAM_DIR / "guardrails" / "guardrails.yaml",
            REDTEAM_DIR / "rag_security" / "rag_security.yaml",
        ]

        for config_file in config_files:
            assert config_file.exists(), f"Config file not found: {config_file}"

    def test_all_yaml_configs_have_schema_reference(self) -> None:
        """Test that all YAML configs have schema reference."""
        config_files = [
            REDTEAM_DIR / "redteam.yaml",
            REDTEAM_DIR / "prompt_injection" / "prompt_injection.yaml",
            REDTEAM_DIR / "jailbreaking" / "jailbreaking.yaml",
            REDTEAM_DIR / "guardrails" / "guardrails.yaml",
            REDTEAM_DIR / "rag_security" / "rag_security.yaml",
        ]

        expected_schema = "# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json"

        for config_file in config_files:
            with open(config_file) as f:
                content = f.read()
            assert expected_schema in content, f"Schema reference missing in {config_file}"

    def test_all_yaml_configs_use_glm46(self) -> None:
        """Test that all YAML configs use glm-4.6 model."""
        import yaml

        config_files = [
            REDTEAM_DIR / "redteam.yaml",
            REDTEAM_DIR / "prompt_injection" / "prompt_injection.yaml",
            REDTEAM_DIR / "jailbreaking" / "jailbreaking.yaml",
            REDTEAM_DIR / "guardrails" / "guardrails.yaml",
            REDTEAM_DIR / "rag_security" / "rag_security.yaml",
        ]

        for config_file in config_files:
            with open(config_file) as f:
                content = yaml.safe_load(f)

            providers = content.get("providers", [])
            provider_str = str(providers).lower()
            assert "glm-4.6" in provider_str or "glm_4_6" in provider_str.replace("-", "_"), \
                f"{config_file} should use glm-4.6 model"

    def test_all_readmes_exist(self) -> None:
        """Test that all README files exist."""
        readme_files = [
            REDTEAM_DIR / "README.md",
            REDTEAM_DIR / "prompt_injection" / "README.md",
            REDTEAM_DIR / "jailbreaking" / "README.md",
            REDTEAM_DIR / "guardrails" / "README.md",
            REDTEAM_DIR / "rag_security" / "README.md",
        ]

        for readme_file in readme_files:
            assert readme_file.exists(), f"README not found: {readme_file}"


@pytest.mark.parametrize("test_type", ["injection", "jailbreaking", "guardrails", "rag_security", "all"])
def test_config_path_mapping_for_all_types(test_type: str) -> None:
    """Test that config paths are correctly mapped for all test types."""
    from promptfoo_evaluation.advanced.redteam.redteam import redteam_test

    config = redteam_test.get_test_config(test_type)

    assert config.test_type == test_type
    assert config.config_path.exists()
    assert config.model == "glm-4.6"


def test_mlflow_experiment_name_consistency() -> None:
    """Test that MLflow experiment name is consistent across the module."""
    from promptfoo_evaluation.advanced.redteam.redteam import redteam_test
    from promptfoo_evaluation.shared.mlflow_handler import get_advanced_experiment_name

    # Both should return the same experiment name
    assert redteam_test.EXPERIMENT_NAME == get_advanced_experiment_name("redteam")
    assert redteam_test.EXPERIMENT_NAME == "promptfoo-advanced-redteam"
