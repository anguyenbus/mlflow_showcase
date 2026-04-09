"""Tests for promptfoo evaluation examples.

These tests follow TDD principles - tests were written first, then implementation.
"""

from pathlib import Path

import yaml

from promptfoo_evaluation.shared.config import get_promptfoo_config_path


class TestBasicExamplesYAML:
    """Tests for basic example YAML configurations."""

    def test_simple_test_yaml_exists(self) -> None:
        """Test that simple_test.yaml exists and is valid YAML."""
        config_path = get_promptfoo_config_path(
            "basics/simple_test.yaml",
            base_dir=Path(__file__).parent.parent.parent / "src" / "promptfoo_evaluation",
        )
        assert config_path.exists()

        with open(config_path) as f:
            content = yaml.safe_load(f)

        # Validate required structure
        assert "prompts" in content or "prompt" in content
        assert "providers" in content
        assert "tests" in content

    def test_simple_test_yaml_has_zhipu_provider(self) -> None:
        """Test that simple_test.yaml uses Zhipu AI provider."""
        config_path = get_promptfoo_config_path(
            "basics/simple_test.yaml",
            base_dir=Path(__file__).parent.parent.parent / "src" / "promptfoo_evaluation",
        )

        with open(config_path) as f:
            content = yaml.safe_load(f)

        providers = content.get("providers", [])
        assert any("glm" in str(p).lower() for p in providers)

    def test_prompt_comparison_yaml_has_multiple_prompts(self) -> None:
        """Test that prompt_comparison.yaml has multiple prompt variants."""
        config_path = get_promptfoo_config_path(
            "basics/prompt_comparison.yaml",
            base_dir=Path(__file__).parent.parent.parent / "src" / "promptfoo_evaluation",
        )

        with open(config_path) as f:
            content = yaml.safe_load(f)

        prompts = content.get("prompts", [])
        assert len(prompts) >= 2

    def test_model_comparison_yaml_has_multiple_models(self) -> None:
        """Test that model_comparison.yaml compares multiple GLM models."""
        config_path = get_promptfoo_config_path(
            "basics/model_comparison.yaml",
            base_dir=Path(__file__).parent.parent.parent / "src" / "promptfoo_evaluation",
        )

        with open(config_path) as f:
            content = yaml.safe_load(f)

        providers = content.get("providers", [])
        assert len(providers) >= 2
        # Check for GLM variants
        provider_str = str(providers)
        assert "glm" in provider_str.lower()

    def test_assertions_guide_yaml_has_various_assertions(self) -> None:
        """Test that assertions_guide.yaml demonstrates various assertion types."""
        config_path = get_promptfoo_config_path(
            "basics/assertions_guide.yaml",
            base_dir=Path(__file__).parent.parent.parent / "src" / "promptfoo_evaluation",
        )

        with open(config_path) as f:
            content = yaml.safe_load(f)

        tests = content.get("tests", [])
        assert len(tests) > 0

        # Check for various assertion types
        all_assertions = []
        for test in tests:
            assert_list = test.get("assert", [])
            if isinstance(assert_list, list):
                all_assertions.extend(assert_list)
            elif isinstance(assert_list, dict):
                all_assertions.append(assert_list)

        # Look for assertion types
        assertion_types = set()
        for assertion in all_assertions:
            if isinstance(assertion, dict):
                assertion_types.update(assertion.keys())

        # Should have at least some basic assertion types
        assert len(assertion_types) > 0
