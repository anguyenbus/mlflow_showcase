"""
Configuration management for RAGas evaluation.

This module loads and validates environment variables for Zhipu AI
and MLflow configuration specific to RAGas evaluation.
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
DEFAULT_EXPERIMENT_NAME: Final[str] = "ragas-evaluation"


@beartype
@dataclass(frozen=True, slots=True)
class RagasConfig:
    """
    Configuration for RAGas evaluation with MLflow and Zhipu AI.

    Attributes:
        zhipu_api_key: Zhipu AI API key for GLM-5 models
        mlflow_tracking_uri: MLflow tracking server URI
        evaluation_data_path: Path to evaluation data directory
        experiment_name: Default MLflow experiment name

    """

    zhipu_api_key: str
    mlflow_tracking_uri: str
    evaluation_data_path: Path
    experiment_name: str


def validate_environment() -> None:
    """
    Validate that required environment variables are set.

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


def get_ragas_config() -> RagasConfig:
    """
    Load RAGas configuration from environment variables.

    Returns:
        RagasConfig: Configuration object with validated settings

    Raises:
        ValueError: If required environment variables are missing

    """
    # Validate required variables
    validate_environment()

    # Load configuration with defaults
    zhipu_api_key = os.environ["ZHIPU_API_KEY"].strip()
    mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_TRACKING_URI).strip()
    experiment_name = os.environ.get("RAGAS_EXPERIMENT_NAME", DEFAULT_EXPERIMENT_NAME).strip()

    return RagasConfig(
        zhipu_api_key=zhipu_api_key,
        mlflow_tracking_uri=mlflow_tracking_uri,
        evaluation_data_path=get_ragas_data_dir(),
        experiment_name=experiment_name,
    )


def get_ragas_data_dir() -> Path:
    """
    Get the RAGas evaluation data directory path.

    Returns:
        Path: Absolute path to RAGas evaluation data directory

    """
    project_root = Path(__file__).parent.parent.parent.parent.resolve()
    return project_root / "data" / "ragas_evaluation"


def get_evaluation_dataset_path() -> Path:
    """
    Get the evaluation dataset file path.

    Returns:
        Path: Absolute path to evaluation_dataset.json

    """
    return get_ragas_data_dir() / "evaluation_dataset.json"
