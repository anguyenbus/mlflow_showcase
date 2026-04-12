"""
Tests for advanced promptfoo evaluation examples.

This test module validates:
- Configuration files are valid
- Python runners execute correctly
- Test data has required fields
- MLflow logging works
- Integration tests for each topic
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Final
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from promptfoo_evaluation.advanced.rag_pipeline.rag_pipeline_test import (
    calculate_rag_metrics,
    display_rag_results,
    run_rag_evaluation,
)
from promptfoo_evaluation.advanced.prevent_hallucination.prevent_hallucination_test import (
    calculate_hallucination_metrics,
)
from promptfoo_evaluation.advanced.choosing_right_temperature.temperature_test import (
    calculate_temperature_metrics,
    calculate_variance,
)
from promptfoo_evaluation.advanced.evaluating_factuality.factuality_test import (
    calculate_factuality_metrics,
)
from promptfoo_evaluation.shared.mlflow_handler import (
    PromptfooResultParser,
    get_advanced_experiment_name,
    parse_promptfoo_results,
)

# Paths to advanced topics
ADVANCED_DIR: Final[Path] = (
    Path(__file__).parent.parent.parent / "src" / "promptfoo_evaluation" / "advanced"
)

# Topic name to config file mapping
TOPIC_CONFIGS: Final[dict[str, str]] = {
    "rag_pipeline": "rag_pipeline.yaml",
    "prevent_hallucination": "prevent_hallucination.yaml",
    "choosing_right_temperature": "temperature_sweep.yaml",
    "evaluating_factuality": "factuality.yaml",
}

# Topic name to test file mapping
TOPIC_TEST_FILES: Final[dict[str, str]] = {
    "rag_pipeline": "rag_pipeline_test.py",
    "prevent_hallucination": "prevent_hallucination_test.py",
    "choosing_right_temperature": "temperature_test.py",
    "evaluating_factuality": "factuality_test.py",
}

TOPICS: Final[tuple[str, ...]] = tuple(TOPIC_CONFIGS.keys())


@pytest.fixture
def mock_promptfoo_results() -> dict[str, Any]:
    """Create mock promptfoo results for testing."""
    return {
        "results": [
            {
                "description": "Test scenario",
                "outputs": [
                    {
                        "pass": True,
                        "score": 1.0,
                        "text": "Test output",
                        "latencyMs": 500,
                        "tokensUsed": {"total": 100},
                        "gradingResult": {
                            "context-relevance": {"pass": True, "score": 0.8},
                            "factuality": {"pass": True, "score": 0.9},
                        },
                    }
                ],
            }
        ],
        "stats": {
            "totalTokens": 100,
            "totalCost": 0.001,
        },
    }


@pytest.fixture
def mock_mlflow():
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


class TestConfigurationFiles:
    """Test that all YAML configuration files are valid."""

    @pytest.mark.parametrize("topic", TOPICS)
    def test_config_file_exists(self, topic: str) -> None:
        """Test that each topic has a configuration file."""
        config_name = TOPIC_CONFIGS[topic]
        config_path = ADVANCED_DIR / topic / config_name
        assert config_path.exists(), f"Config file not found: {config_path}"

    @pytest.mark.parametrize("topic", TOPICS)
    def test_config_file_is_valid_yaml(self, topic: str) -> None:
        """Test that each configuration file is valid YAML."""
        import yaml

        config_name = TOPIC_CONFIGS[topic]
        config_path = ADVANCED_DIR / topic / config_name

        with open(config_path) as f:
            content = yaml.safe_load(f)

        assert content is not None
        assert "description" in content or "prompts" in content

    @pytest.mark.parametrize("topic", TOPICS)
    def test_config_has_required_fields(self, topic: str) -> None:
        """Test that each config has required fields."""
        import yaml

        config_name = TOPIC_CONFIGS[topic]
        config_path = ADVANCED_DIR / topic / config_name

        with open(config_path) as f:
            content = yaml.safe_load(f)

        # Check for required top-level fields
        assert "prompts" in content or "description" in content

        # Check for tests or testsPath
        assert "tests" in content or "testsPath" in content

        # Check for output path
        assert "outputPath" in content


class TestDataFiles:
    """Test that test data files are valid."""

    @pytest.mark.parametrize("topic", TOPICS)
    def test_data_file_exists(self, topic: str) -> None:
        """Test that each topic has a test data file."""
        data_path = ADVANCED_DIR / topic / "data" / "test_cases.json"
        assert data_path.exists(), f"Data file not found: {data_path}"

    @pytest.mark.parametrize("topic", TOPICS)
    def test_data_file_is_valid_json(self, topic: str) -> None:
        """Test that each data file is valid JSON."""
        data_path = ADVANCED_DIR / topic / "data" / "test_cases.json"

        with open(data_path) as f:
            content = json.load(f)

        assert isinstance(content, list)
        assert len(content) > 0

    @pytest.mark.parametrize("topic", TOPICS)
    def test_data_has_required_fields(self, topic: str) -> None:
        """Test that test cases have required fields."""
        data_path = ADVANCED_DIR / topic / "data" / "test_cases.json"

        with open(data_path) as f:
            content = json.load(f)

        # Each test case should have vars
        for test_case in content:
            assert "vars" in test_case, f"Missing 'vars' in test case"
            assert "assert" in test_case, f"Missing 'assert' in test case"


class TestPythonRunners:
    """Test Python runner scripts."""

    @pytest.mark.parametrize("topic", TOPICS)
    def test_runner_file_exists(self, topic: str) -> None:
        """Test that each topic has a Python runner."""
        test_name = TOPIC_TEST_FILES[topic]
        runner_path = ADVANCED_DIR / topic / test_name
        assert runner_path.exists(), f"Runner file not found: {runner_path}"

    @pytest.mark.parametrize("topic", TOPICS)
    def test_runner_is_importable(self, topic: str) -> None:
        """Test that each runner can be imported."""
        test_name = TOPIC_TEST_FILES[topic]
        # Remove .py extension and convert to module path
        module_name = test_name.replace(".py", "")
        runner_module = f"promptfoo_evaluation.advanced.{topic}.{module_name}"

        # Try to import the module
        __import__(runner_module)

    def test_rag_metrics_calculation(self, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test RAG metrics calculation."""
        metrics = calculate_rag_metrics(mock_promptfoo_results)

        assert "context_relevance_avg" in metrics
        assert "context_faithfulness_avg" in metrics
        assert "context_recall_avg" in metrics
        assert "answer_relevance_avg" in metrics

    def test_hallucination_metrics_calculation(self, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test hallucination metrics calculation."""
        metrics = calculate_hallucination_metrics(mock_promptfoo_results)

        assert "refusal_rate" in metrics
        assert "hallucination_rate" in metrics
        assert "factuality_score" in metrics
        assert "attribution_score" in metrics

    def test_temperature_metrics_calculation(self, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test temperature metrics calculation."""
        metrics = calculate_temperature_metrics(mock_promptfoo_results)

        # Should have metrics for each temperature
        expected_temps = ["0.0", "0.3", "0.7", "1.0"]
        for temp in expected_temps:
            assert temp in metrics or any(temp in k for k in metrics.keys())

    def test_variance_calculation(self) -> None:
        """Test variance calculation."""
        # Create complete temperature metrics with all required fields
        temperature_metrics = {
            "0.0": {
                "pass_rate": 0.9,
                "avg_score": 0.85,
                "avg_latency": 450.0,
                "total_tokens": 1000,
            },
            "0.3": {
                "pass_rate": 0.85,
                "avg_score": 0.82,
                "avg_latency": 470.0,
                "total_tokens": 1050,
            },
            "0.7": {
                "pass_rate": 0.75,
                "avg_score": 0.78,
                "avg_latency": 500.0,
                "total_tokens": 1100,
            },
            "1.0": {
                "pass_rate": 0.65,
                "avg_score": 0.70,
                "avg_latency": 550.0,
                "total_tokens": 1200,
            },
        }

        variance = calculate_variance(temperature_metrics)

        assert "pass_rate_variance" in variance
        assert "avg_score_variance" in variance
        assert "pass_rate_range" in variance
        assert "avg_score_range" in variance

        # Variance should be positive
        assert variance["pass_rate_variance"] >= 0
        assert variance["avg_score_variance"] >= 0

    def test_factuality_metrics_calculation(self, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test factuality metrics calculation."""
        metrics = calculate_factuality_metrics(mock_promptfoo_results)

        assert "overall_factuality_score" in metrics
        assert "extraction_accuracy" in metrics
        assert "verification_rate" in metrics
        assert "category_scores" in metrics

        # Category scores should have expected categories
        expected_categories = ["dates", "numbers", "entities", "relationships"]
        for cat in expected_categories:
            assert cat in metrics["category_scores"]


class TestMLflowHandler:
    """Test MLflow handler functions."""

    def test_parse_promptfoo_results_from_dict(self, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test parsing results from dictionary."""
        parser = parse_promptfoo_results(mock_promptfoo_results)

        assert isinstance(parser, PromptfooResultParser)
        assert parser.get_pass_rate() >= 0

    def test_parse_promptfoo_results_from_file(self, tmp_path: Path, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test parsing results from file."""
        # Create temporary results file
        results_file = tmp_path / "results.json"
        with open(results_file, "w") as f:
            json.dump(mock_promptfoo_results, f)

        parser = parse_promptfoo_results(results_file)

        assert isinstance(parser, PromptfooResultParser)

    def test_promptfoo_parser_get_pass_rate(self, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test pass rate calculation."""
        parser = PromptfooResultParser(mock_promptfoo_results)
        pass_rate = parser.get_pass_rate()

        assert 0 <= pass_rate <= 1

    def test_promptfoo_parser_get_average_score(self, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test average score calculation."""
        parser = PromptfooResultParser(mock_promptfoo_results)
        avg_score = parser.get_average_score()

        assert 0 <= avg_score <= 1

    def test_promptfoo_parser_get_metrics(self, mock_promptfoo_results: dict[str, Any]) -> None:
        """Test metrics extraction."""
        parser = PromptfooResultParser(mock_promptfoo_results)
        metrics = parser.get_metrics()

        assert "pass_rate" in metrics
        assert "average_score" in metrics
        assert "total_tokens" in metrics
        assert "total_cost" in metrics
        assert "avg_latency_ms" in metrics

    def test_get_advanced_experiment_name(self) -> None:
        """Test getting advanced experiment names."""
        assert get_advanced_experiment_name("rag_pipeline") == "promptfoo-advanced-rag"
        assert get_advanced_experiment_name("prevent_hallucination") == "promptfoo-advanced-hallucination"
        assert get_advanced_experiment_name("choosing_right_temperature") == "promptfoo-advanced-temperature"
        assert get_advanced_experiment_name("evaluating_factuality") == "promptfoo-advanced-factuality"
        assert get_advanced_experiment_name("unknown") == "promptfoo-advanced-unknown"


class TestREADMEFiles:
    """Test that README files exist and have required sections."""

    @pytest.mark.parametrize("topic", TOPICS)
    def test_readme_exists(self, topic: str) -> None:
        """Test that each topic has a README."""
        readme_path = ADVANCED_DIR / topic / "README.md"
        assert readme_path.exists(), f"README not found: {readme_path}"

    @pytest.mark.parametrize("topic", TOPICS)
    def test_readme_has_required_sections(self, topic: str) -> None:
        """Test that each README has required sections."""
        readme_path = ADVANCED_DIR / topic / "README.md"

        with open(readme_path) as f:
            content = f.read().lower()

        # Check for required sections
        required_sections = [
            "overview",
            "why it matters",
            "prerequisites",
            "setup",
            "running",
            "understanding results",
        ]

        for section in required_sections:
            # Allow for variations like "## Overview" or "# Overview"
            assert section in content or section.replace(" ", "") in content.replace(" ", "")


class TestTopicSpecificAssertions:
    """Test topic-specific assertion logic."""

    def test_rag_test_data_context_field(self) -> None:
        """Test that RAG test data has context field."""
        data_path = ADVANCED_DIR / "rag_pipeline" / "data" / "test_cases.json"

        with open(data_path) as f:
            content = json.load(f)

        for test_case in content:
            assert "context" in test_case["vars"], "RAG tests need context variable"

    def test_hallucination_test_data_uncertainty(self) -> None:
        """Test that hallucination tests target uncertain scenarios."""
        data_path = ADVANCED_DIR / "prevent_hallucination" / "data" / "test_cases.json"

        with open(data_path) as f:
            content = json.load(f)

        # Check descriptions for uncertainty indicators
        uncertain_indicators = ["future", "predict", "fictional", "exist", "2050"]

        has_uncertain_tests = False
        for test_case in content:
            description = test_case.get("description", "").lower()
            if any(indicator in description for indicator in uncertain_indicators):
                has_uncertain_tests = True
                break

        assert has_uncertain_tests, "Hallucination tests should target uncertain scenarios"

    def test_temperature_test_has_scenarios(self) -> None:
        """Test that temperature config has scenarios."""
        import yaml

        config_path = ADVANCED_DIR / "choosing_right_temperature" / "temperature_sweep.yaml"

        with open(config_path) as f:
            content = yaml.safe_load(f)

        assert "scenarios" in content, "Temperature config should have scenarios"
        assert len(content["scenarios"]) > 0, "Should have at least one scenario"

    def test_factuality_test_data_ground_truth(self) -> None:
        """Test that factuality tests have ground truth."""
        data_path = ADVANCED_DIR / "evaluating_factuality" / "data" / "test_cases.json"

        with open(data_path) as f:
            content = json.load(f)

        for test_case in content:
            assert "expected_answer" in test_case["vars"], \
                "Factuality tests need expected_answer for ground truth"


class TestIntegration:
    """Integration tests for advanced topics."""

    @pytest.mark.slow
    def test_main_advanced_readme_exists(self) -> None:
        """Test that main advanced README exists."""
        readme_path = ADVANCED_DIR / "README.md"
        assert readme_path.exists()

    @pytest.mark.slow
    def test_main_advanced_readme_links_topics(self) -> None:
        """Test that main README links to all topics."""
        readme_path = ADVANCED_DIR / "README.md"

        with open(readme_path) as f:
            content = f.read()

        # Check that all topics are mentioned
        for topic in TOPICS:
            assert topic in content, f"Topic {topic} not mentioned in main README"

    @pytest.mark.slow
    def test_run_all_script_exists(self) -> None:
        """Test that convenience script exists."""
        script_path = ADVANCED_DIR / "run_all_advanced.py"
        assert script_path.exists()

    @pytest.mark.slow
    def test_shared_mlflow_handler_has_advanced_support(self) -> None:
        """Test that MLflow handler supports advanced topics."""
        from promptfoo_evaluation.shared import mlflow_handler

        assert hasattr(mlflow_handler, "ADVANCED_EXPERIMENTS")
        assert hasattr(mlflow_handler, "get_advanced_experiment_name")


@pytest.mark.parametrize("topic", TOPICS)
def test_topic_directory_structure(topic: str) -> None:
    """Test that each topic has the required directory structure."""
    topic_dir = ADVANCED_DIR / topic

    # Check directory exists
    assert topic_dir.is_dir()

    # Check for required files
    config_name = TOPIC_CONFIGS[topic]
    test_name = TOPIC_TEST_FILES[topic]

    assert (topic_dir / config_name).exists()
    assert (topic_dir / test_name).exists()
    assert (topic_dir / "README.md").exists()

    # Check for data subdirectory
    data_dir = topic_dir / "data"
    assert data_dir.is_dir()
    assert (data_dir / "test_cases.json").exists()


@pytest.mark.parametrize("topic", TOPICS)
def test_topic_yaml_references_correct_data(topic: str) -> None:
    """Test that YAML config references the correct data file."""
    import yaml

    config_name = TOPIC_CONFIGS[topic]
    config_path = ADVANCED_DIR / topic / config_name

    with open(config_path) as f:
        content = yaml.safe_load(f)

    # Check testsPath or tests reference
    if "testsPath" in content:
        expected_path = f"./data/test_cases.json"
        assert content["testsPath"] == expected_path or content["testsPath"].endswith("test_cases.json")


def test_all_advanced_topics_use_glm5() -> None:
    """Test that all advanced topics use GLM-5 models."""
    import yaml

    for topic in TOPICS:
        config_name = TOPIC_CONFIGS[topic]
        config_path = ADVANCED_DIR / topic / config_name

        with open(config_path) as f:
            content = yaml.safe_load(f)

        # Check that providers use GLM-5
        providers = content.get("providers", [])
        assert len(providers) > 0, f"{topic} has no providers"

        # At least one provider should reference GLM-5
        has_glm5 = any("glm-5" in str(p).lower() for p in providers)
        assert has_glm5, f"{topic} should use GLM-5 models"
