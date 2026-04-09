"""
Configuration management for promptfoo evaluation module.

This module extends the base configuration from src/config.py with
promptfoo-specific settings for evaluation, output directories, and
command path resolution.
"""

import os
import shutil

# NOTE: Import base config to reuse patterns
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from beartype import beartype
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import get_data_dir, get_project_root

# Initialize rich console for output
console: Final[Console] = Console()

# Default configuration values
DEFAULT_PROMPTFOO_OUTPUT_DIR: Final[str] = "promptfoo_results"
DEFAULT_PROMPTFOO_SHARE_DIR: Final[str] = "promptfoo_share"

# Zhipu AI configuration
ZHIPU_BASE_URL: Final[str] = "https://open.bigmodel.cn/api/paas/v4/"
ZHIPU_MODELS: Final[tuple[str, ...]] = (
    "glm-5-flash",
    "glm-5-plus",
    "glm-5-std",
)


@beartype
@dataclass(frozen=True, slots=True)
class PromptfooConfig:
    """
    Configuration for promptfoo evaluation.

    Attributes:
        zhipu_api_key: Zhipu AI API key for GLM-5 models
        output_dir: Directory for promptfoo evaluation outputs
        share_dir: Directory for promptfoo view shared results
        base_url: Zhipu AI API base URL

    """

    zhipu_api_key: str
    output_dir: Path
    share_dir: Path
    base_url: str = ZHIPU_BASE_URL


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
def get_promptfoo_output_dir(
    base_dir: Path | None = None,
    subdirectory: str = DEFAULT_PROMPTFOO_OUTPUT_DIR,
) -> Path:
    """
    Get or create the promptfoo output directory.

    Args:
        base_dir: Base directory for outputs (defaults to project root).
        subdirectory: Subdirectory name for promptfoo outputs.

    Returns:
        Path to the promptfoo output directory.

    Example:
        >>> output_dir = get_promptfoo_output_dir()
        >>> str(output_dir).endswith("promptfoo_results")
        True

    """
    if base_dir is None:
        base_dir = get_project_root()

    output_dir = base_dir / subdirectory
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


@beartype
def get_promptfoo_share_dir(
    base_dir: Path | None = None,
) -> Path:
    """
    Get or create the promptfoo share directory for web UI.

    Args:
        base_dir: Base directory for shares (defaults to project root).

    Returns:
        Path to the promptfoo share directory.

    """
    if base_dir is None:
        base_dir = get_project_root()

    share_dir = base_dir / DEFAULT_PROMPTFOO_SHARE_DIR
    share_dir.mkdir(parents=True, exist_ok=True)

    return share_dir


@beartype
def get_promptfoo_config_path(
    config_name: str,
    base_dir: Path | None = None,
) -> Path:
    """
    Get the path to a promptfoo configuration file.

    Args:
        config_name: Name of the configuration file (e.g., "simple_test.yaml").
        base_dir: Base directory containing the config (defaults to module dir).

    Returns:
        Path to the configuration file.

    Example:
        >>> config_path = get_promptfoo_config_path("simple_test.yaml")
        >>> config_path.name
        'simple_test.yaml'

    """
    if base_dir is None:
        # Default to the promptfoo_evaluation module directory
        base_dir = Path(__file__).parent.parent

    return base_dir / config_name


@beartype
def validate_promptfoo_installation() -> None:
    """
    Validate that promptfoo is available via npx or global installation.

    Raises:
        ValueError: If neither npx nor promptfoo global installation is found.

    Example:
        >>> validate_promptfoo_installation()  # No error if promptfoo available

    """
    # Check for npx (preferred for promptfoo)
    npx_path = shutil.which("npx")

    if npx_path:
        return

    # Check for global promptfoo installation
    promptfoo_path = shutil.which("promptfoo")

    if promptfoo_path:
        return

    # Neither available - raise error with helpful message
    console.print("[red]ERROR:[/red] promptfoo is not installed or not accessible")
    console.print("\n[yellow]To install promptfoo:[/yellow]")
    console.print("Option 1 - Install globally with npm:")
    console.print("  npm install -g promptfoo")
    console.print("\nOption 2 - Use npx (no installation required):")
    console.print("  npx promptfoo eval")
    console.print("\nSee: https://promptfoo.dev/docs/quick-start/")
    raise ValueError(
        "promptfoo requires npx or global installation. Install with: npm install -g promptfoo"
    )


@beartype
def get_config() -> PromptfooConfig:
    """
    Load promptfoo configuration from environment and defaults.

    Returns:
        PromptfooConfig: Configuration object with validated settings.

    Raises:
        ValueError: If required environment variables are missing.

    """
    zhipu_api_key = get_zhipu_api_key()
    output_dir = get_promptfoo_output_dir()
    share_dir = get_promptfoo_share_dir()

    return PromptfooConfig(
        zhipu_api_key=zhipu_api_key,
        output_dir=output_dir,
        share_dir=share_dir,
        base_url=ZHIPU_BASE_URL,
    )


@beartype
def get_rag_data_path() -> Path:
    """
    Get the path to RAG test data (tax law documents).

    Returns:
        Path to the RAG data directory.

    """
    return get_data_dir() / "rag" / "australian_tax_law.txt"
