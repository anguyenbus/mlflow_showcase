"""Configuration management for MLflow LLM Show Case repository.

This module loads and validates environment variables for Zhipu AI
and MLflow configuration.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from beartype import beartype
from rich.console import Console

# Initialize rich console for output
console: Final[Console] = Console()

# Default configuration values
DEFAULT_MLFLOW_TRACKING_URI: Final[str] = "sqlite:///mlflow.db"


@beartype
@dataclass(frozen=True, slots=True)
class Config:
    """Configuration for MLflow and Zhipu AI integration.

    Attributes:
        zhipu_api_key: Zhipu AI API key for GLM-5 models
        mlflow_tracking_uri: MLflow tracking server URI
    """

    zhipu_api_key: str
    mlflow_tracking_uri: str


def validate_environment() -> None:
    """Validate that required environment variables are set.

    Raises:
        ValueError: If ZHIPU_API_KEY is not set or is empty
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


def get_config() -> Config:
    """Load configuration from environment variables.

    Returns:
        Config: Configuration object with validated settings

    Raises:
        ValueError: If required environment variables are missing
    """
    # Validate required variables
    validate_environment()

    # Load configuration with defaults
    zhipu_api_key = os.environ["ZHIPU_API_KEY"].strip()
    mlflow_tracking_uri = os.environ.get(
        "MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_TRACKING_URI
    ).strip()

    return Config(
        zhipu_api_key=zhipu_api_key,
        mlflow_tracking_uri=mlflow_tracking_uri,
    )


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path: Absolute path to project root
    """
    return Path(__file__).parent.parent.resolve()


def get_data_dir() -> Path:
    """Get the data directory path.

    Returns:
        Path: Absolute path to data directory
    """
    return get_project_root() / "data"


def get_evaluation_data_path() -> Path:
    """Get the evaluation dataset path.

    Returns:
        Path: Absolute path to evaluation data directory
    """
    return get_data_dir() / "evaluation"
