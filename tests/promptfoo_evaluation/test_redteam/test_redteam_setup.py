"""
Tests for Red Team Evaluation directory structure and setup (Task Group 1).

These tests validate:
- Redteam directory structure exists
- Subdirectories for each attack type
- Main README and configuration files
- Python runner module import
- YAML configuration file creation
"""

import sys
from pathlib import Path
from typing import Final

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Path constants
ADVANCED_DIR: Final[Path] = (
    Path(__file__).parent.parent.parent.parent / "src" / "promptfoo_evaluation" / "advanced"
)
REDTEAM_DIR: Final[Path] = ADVANCED_DIR / "redteam" / "redteam"

# Required subdirectories
REQUIRED_SUBDIRS: Final[tuple[str, ...]] = (
    "prompt_injection",
    "jailbreaking",
    "guardrails",
    "rag_security",
)


class TestRedteamDirectoryStructure:
    """Test that the redteam directory structure exists and is complete."""

    def test_redteam_directory_exists(self) -> None:
        """Test that the main redteam directory exists."""
        assert REDTEAM_DIR.exists(), f"Redteam directory not found: {REDTEAM_DIR}"
        assert REDTEAM_DIR.is_dir(), f"Redteam path is not a directory: {REDTEAM_DIR}"

    @pytest.mark.parametrize("subdir", REQUIRED_SUBDIRS)
    def test_subdirectories_exist(self, subdir: str) -> None:
        """Test that all required subdirectories exist."""
        subdir_path = REDTEAM_DIR / subdir
        assert subdir_path.exists(), f"Subdirectory not found: {subdir_path}"
        assert subdir_path.is_dir(), f"Subdirectory path is not a directory: {subdir_path}"


class TestRedteamReadmeFiles:
    """Test that README files exist for redteam and subdirectories."""

    def test_main_readme_exists(self) -> None:
        """Test that the main redteam README.md exists."""
        readme_path = REDTEAM_DIR / "README.md"
        assert readme_path.exists(), f"Main README not found: {readme_path}"

    def test_main_readme_has_required_sections(self) -> None:
        """Test that the main README has required sections."""
        readme_path = REDTEAM_DIR / "README.md"

        with open(readme_path) as f:
            content = f.read().lower()

        # Check for required sections based on promptfoo.dev guide structure
        required_sections = [
            "overview",
            "quick start",
            "plugin reference",
            "strategy guide",
            "results interpretation",
            "security fix prioritization",
        ]

        for section in required_sections:
            assert section in content or section.replace(" ", "") in content.replace(" ", ""), \
                f"Required section '{section}' not found in README"

    @pytest.mark.parametrize("subdir", REQUIRED_SUBDIRS)
    def test_subdirectory_readme_exists(self, subdir: str) -> None:
        """Test that each subdirectory has a README.md."""
        readme_path = REDTEAM_DIR / subdir / "README.md"
        assert readme_path.exists(), f"README not found for {subdir}: {readme_path}"


class TestRedteamConfigurationFiles:
    """Test that YAML configuration files exist and are valid."""

    def test_main_yaml_config_exists(self) -> None:
        """Test that the main redteam.yaml configuration exists."""
        config_path = REDTEAM_DIR / "redteam.yaml"
        assert config_path.exists(), f"Main config not found: {config_path}"

    def test_main_yaml_has_schema_reference(self) -> None:
        """Test that the main YAML has the promptfoo schema reference."""
        config_path = REDTEAM_DIR / "redteam.yaml"

        with open(config_path) as f:
            content = f.read()

        # Check for schema reference
        expected_schema = "# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json"
        assert expected_schema in content, "YAML schema reference not found"

    def test_main_yaml_has_required_fields(self) -> None:
        """Test that the main YAML has required redteam fields."""
        import yaml

        config_path = REDTEAM_DIR / "redteam.yaml"

        with open(config_path) as f:
            content = yaml.safe_load(f)

        # Check for redteam-specific fields
        assert "redteam" in content, "Missing 'redteam' configuration"
        assert "purpose" in content.get("redteam", {}), "Missing 'redteam.purpose'"

        # Check for basic promptfoo structure
        assert "description" in content or "prompts" in content

    @pytest.mark.parametrize("subdir", REQUIRED_SUBDIRS)
    def test_subdirectory_yaml_exists(self, subdir: str) -> None:
        """Test that each subdirectory has its YAML configuration."""
        config_name = f"{subdir}.yaml"
        config_path = REDTEAM_DIR / subdir / config_name
        assert config_path.exists(), f"Config not found for {subdir}: {config_path}"

    @pytest.mark.parametrize("subdir", REQUIRED_SUBDIRS)
    def test_subdirectory_yaml_valid(self, subdir: str) -> None:
        """Test that each subdirectory YAML is valid."""
        import yaml

        config_name = f"{subdir}.yaml"
        config_path = REDTEAM_DIR / subdir / config_name

        with open(config_path) as f:
            content = yaml.safe_load(f)

        assert content is not None, f"YAML content is None for {subdir}"

        # Check for basic promptfoo structure
        assert "description" in content or "prompts" in content


class TestRedteamPythonRunner:
    """Test that the Python runner script exists and is importable."""

    def test_runner_file_exists(self) -> None:
        """Test that redteam_test.py exists."""
        runner_path = REDTEAM_DIR / "redteam_test.py"
        assert runner_path.exists(), f"Runner file not found: {runner_path}"

    def test_runner_is_importable(self) -> None:
        """Test that the runner module can be imported."""
        # The module should be importable
        module_path = "promptfoo_evaluation.advanced.redteam.redteam.redteam_test"
        try:
            __import__(module_path)
        except ImportError as e:
            pytest.fail(f"Failed to import redteam_test module: {e}")

    def test_runner_has_main_function(self) -> None:
        """Test that the runner has a main function."""
        from promptfoo_evaluation.advanced.redteam.redteam.redteam_test import main

        assert callable(main), "main function is not callable"


class TestRedteamModelConfiguration:
    """Test that the default model configuration is correct."""

    def test_default_model_is_glm46(self) -> None:
        """Test that the default model is glm-4.6."""
        import yaml

        config_path = REDTEAM_DIR / "redteam.yaml"

        with open(config_path) as f:
            content = yaml.safe_load(f)

        # Check for glm-4.6 in providers
        providers = content.get("providers", [])
        provider_str = str(providers).lower()

        assert "glm-4.6" in provider_str or "glm_4_6" in provider_str.replace("-", "_"), \
            "Default model should be glm-4.6"

    def test_base_url_configured(self) -> None:
        """Test that the Zhipu AI base URL is configured."""
        import yaml

        config_path = REDTEAM_DIR / "redteam.yaml"

        with open(config_path) as f:
            content = yaml.safe_load(f)

        # Check for base URL
        config_str = str(content)
        assert "https://open.bigmodel.cn/api/paas/v4/" in config_str or \
               "bigmodel.cn" in config_str, \
            "Base URL should point to Zhipu AI API"


class TestRedteamTestTypeSupport:
    """Test that the runner supports --test-type argument."""

    def test_runner_accepts_test_type_argument(self) -> None:
        """Test that the runner accepts --test-type argument."""
        import subprocess
        import sys

        runner_path = REDTEAM_DIR / "redteam_test.py"

        # Test with --help to see if --test-type is documented
        result = subprocess.run(
            [sys.executable, str(runner_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, "Runner --help failed"
        assert "--test-type" in result.stdout or "test_type" in result.stdout, \
            "--test-type argument not documented"

    @pytest.mark.parametrize("test_type", [
        "injection",
        "jailbreaking",
        "guardrails",
        "rag_security",
        "all",
    ])
    def test_supported_test_types(self, test_type: str) -> None:
        """Test that all required test types are supported."""
        from promptfoo_evaluation.advanced.redteam.redteam.redteam_test import SUPPORTED_TEST_TYPES

        assert test_type in SUPPORTED_TEST_TYPES, \
            f"Test type '{test_type}' not in SUPPORTED_TEST_TYPES"


@pytest.mark.parametrize("subdir", REQUIRED_SUBDIRS)
def test_redteam_directory_is_complete(subdir: str) -> None:
    """Test that each subdirectory has all required files."""
    subdir_path = REDTEAM_DIR / subdir

    # Check directory exists
    assert subdir_path.is_dir()

    # Check for required files
    config_name = f"{subdir}.yaml"
    assert (subdir_path / config_name).exists(), f"Missing {config_name}"
    assert (subdir_path / "README.md").exists(), "Missing README.md"


def test_redteam_follows_advanced_topic_structure() -> None:
    """Test that redteam follows the same structure as other advanced topics."""
    # Check that redteam has the same basic structure as prevent_hallucination
    prevent_hallucination_dir = ADVANCED_DIR / "prevent_hallucination"

    # Both should have these files
    required_files = [
        ("README.md", "README documentation"),
        ("_test.py", "Python runner (ends with _test.py)"),
    ]

    for file_pattern, description in required_files:
        # For prevent_hallucination
        if file_pattern == "_test.py":
            ph_file = any(f.suffix == ".py" and "test" in f.name
                          for f in prevent_hallucination_dir.glob("*.py"))
            rt_file = any(f.suffix == ".py" and "test" in f.name
                          for f in REDTEAM_DIR.glob("*.py"))
        else:
            ph_file = (prevent_hallucination_dir / file_pattern).exists()
            rt_file = (REDTEAM_DIR / file_pattern).exists()

        assert ph_file, f"prevent_hallucination missing {description}"
        assert rt_file, f"redteam missing {description}"
