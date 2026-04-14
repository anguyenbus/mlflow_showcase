"""
Configuration management for Garak evaluation tutorials.

This module provides utilities for environment variable validation,
output directory management, and Garak installation validation.
"""

import os

# NOTE: Import base config to reuse patterns from src/config.py
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from beartype import beartype
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from config import get_project_root

# Initialize rich console for output
console: Final[Console] = Console()

# Default configuration values
DEFAULT_GARAK_OUTPUT_DIR: Final[str] = "garak_results"
GARAK_REQUIRED: Final[bool] = True


@beartype
@dataclass(frozen=True, slots=True)
class GarakConfig:
    """
    Configuration for Garak evaluation.

    Attributes:
        zhipu_api_key: Zhipu AI API key for GLM-5 models
        output_dir: Directory for Garak evaluation outputs
        base_url: Zhipu AI API base URL
        model_name: Default Zhipu model to use

    """

    zhipu_api_key: str
    output_dir: Path
    base_url: str
    model_name: str


# Zhipu AI configuration
ZHIPU_BASE_URL: Final[str] = "https://open.bigmodel.cn/api/paas/v4/"
ZHIPU_MODELS: Final[tuple[str, ...]] = (
    "glm-5-flash",
    "glm-5-plus",
    "glm-5-std",
)

DEFAULT_MODEL: Final[str] = "glm-5-flash"


@beartype
def get_zhipu_api_key() -> str:
    """
    Get Zhipu AI API key from environment.

    Returns:
        ZHIPU_API_KEY value from environment.

    Raises:
        ValueError: If ZHIPU_API_KEY is not set or is empty.

    """
    zhipu_api_key = os.environ.get("ZHIPU_API_KEY", "").strip()

    if not zhipu_api_key:
        console.print("[red]ERROR:[/red] ZHIPU_API_KEY environment variable is not set")
        console.print("\n[yellow]To fix:[/yellow]")
        console.print("1. Get your API key from https://open.bigmodel.cn/")
        console.print("2. Copy .env.example to .env")
        console.print("3. Add your API key: ZHIPU_API_KEY=your_key_here")
        console.print("4. Run: source .env  # or load .env in your IDE")
        raise ValueError("ZHIPU_API_KEY environment variable is required but not set")

    return zhipu_api_key


@beartype
def get_garak_output_dir(
    base_dir: Path | None = None,
    subdirectory: str = DEFAULT_GARAK_OUTPUT_DIR,
) -> Path:
    """
    Get or create the Garak output directory.

    Args:
        base_dir: Base directory for outputs (defaults to project root).
        subdirectory: Subdirectory name for Garak outputs.

    Returns:
        Path to the Garak output directory.

    Example:
        >>> output_dir = get_garak_output_dir()
        >>> str(output_dir).endswith("garak_results")
        True

    """
    if base_dir is None:
        base_dir = get_project_root()

    output_dir = base_dir / subdirectory
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


@beartype
def validate_garak_installation() -> None:
    """
    Validate that Garak is installed and importable.

    Raises:
        ImportError: If Garak is not installed.

    Example:
        >>> validate_garak_installation()  # No error if Garak available

    """
    try:
        import garak  # noqa: F401

        console.print("[green]Garak installation validated[/green]")
    except ImportError as e:
        console.print("[red]ERROR:[/red] Garak is not installed")
        console.print("\n[yellow]To install Garak:[/yellow]")
        console.print("  uv pip install garak")
        console.print("\nSee: https://github.com/NVIDIA/garak")
        raise ImportError(
            "Garak is required. Install with: uv pip install garak"
        ) from e


@beartype
def get_config() -> GarakConfig:
    """
    Load Garak configuration from environment and defaults.

    Returns:
        GarakConfig: Configuration object with validated settings.

    Raises:
        ValueError: If required environment variables are missing.

    """
    zhipu_api_key = get_zhipu_api_key()
    output_dir = get_garak_output_dir()

    return GarakConfig(
        zhipu_api_key=zhipu_api_key,
        output_dir=output_dir,
        base_url=ZHIPU_BASE_URL,
        model_name=DEFAULT_MODEL,
    )


@beartype
def get_garak_config_path(
    config_name: str,
    base_dir: Path | None = None,
) -> Path:
    """
    Get the path to a Garak YAML configuration file.

    Args:
        config_name: Name of the configuration file (e.g., "prompt_injection_cli.yaml").
        base_dir: Base directory containing the config (defaults to module dir).

    Returns:
        Path to the configuration file.

    Example:
        >>> config_path = get_garak_config_path("prompt_injection_cli.yaml")
        >>> config_path.name
        'prompt_injection_cli.yaml'

    """
    if base_dir is None:
        # Default to the garak_evaluation module directory
        base_dir = Path(__file__).parent.parent

    return base_dir / config_name


@beartype
def get_topic_dir(topic_name: str) -> Path:
    """
    Get the path to a topic directory.

    Args:
        topic_name: Name of the topic (e.g., "prompt_injection").

    Returns:
        Path to the topic directory.

    Example:
        >>> topic_dir = get_topic_dir("prompt_injection")
        >>> topic_dir.name
        'prompt_injection'

    """
    return Path(__file__).parent.parent / "advanced" / topic_name


@beartype
def get_test_data_path(topic_name: str, filename: str = "test_cases.txt") -> Path:
    """
    Get the path to a topic's test data file.

    Args:
        topic_name: Name of the topic.
        filename: Name of the test data file.

    Returns:
        Path to the test data file.

    """
    return get_topic_dir(topic_name) / "data" / filename
