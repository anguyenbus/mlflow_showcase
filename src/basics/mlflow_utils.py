"""MLflow tracking and logging utilities.

This module provides helper functions for MLflow experiment tracking,
parameter/metric logging, and artifact management.
"""

from pathlib import Path
from typing import Final

import mlflow
from beartype import beartype
from rich.console import Console

from config import get_config

# Initialize rich console
console: Final[Console] = Console()


@beartype
def create_experiment(experiment_name: str) -> mlflow.entities.Experiment:
    """Create or get an MLflow experiment.

    Args:
        experiment_name: Name of the experiment

    Returns:
        MLflow Experiment object
    """
    config = get_config()

    # NOTE: Set tracking URI before creating experiment
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)

    experiment = mlflow.set_experiment(experiment_name)

    console.print(
        f"[green]✓[/green] Experiment '{experiment_name}' "
        f"(ID: {experiment.experiment_id})"
    )

    return experiment


@beartype
def log_params(params: dict[str, str | float | int]) -> None:
    """Log parameters to the active MLflow run.

    Args:
        params: Dictionary of parameter names and values

    Raises:
        ValueError: If no active run exists
    """
    if mlflow.active_run() is None:
        raise ValueError("No active MLflow run. Call mlflow.start_run() first.")

    mlflow.log_params(params)

    console.print(f"[green]✓[/green] Logged {len(params)} parameters")


@beartype
def log_metrics(
    metrics: dict[str, float | int],
    step: int | None = None,
) -> None:
    """Log metrics to the active MLflow run.

    Args:
        metrics: Dictionary of metric names and values
        step: Optional training step number

    Raises:
        ValueError: If no active run exists
    """
    if mlflow.active_run() is None:
        raise ValueError("No active MLflow run. Call mlflow.start_run() first.")

    if step is not None:
        mlflow.log_metrics(metrics, step=step)
    else:
        mlflow.log_metrics(metrics)

    console.print(f"[green]✓[/green] Logged {len(metrics)} metrics")


@beartype
def log_artifact(file_path: str | Path, artifact_path: str | None = None) -> None:
    """Log a file as an artifact to the active MLflow run.

    Args:
        file_path: Path to the file to log
        artifact_path: Optional destination path within artifact directory

    Raises:
        ValueError: If no active run exists or file doesn't exist
        FileNotFoundError: If the specified file doesn't exist
    """
    if mlflow.active_run() is None:
        raise ValueError("No active MLflow run. Call mlflow.start_run() first.")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    mlflow.log_artifact(str(path), artifact_path)

    console.print(f"[green]✓[/green] Logged artifact: {path.name}")


@beartype
def log_model_summary(model_info: dict[str, str]) -> None:
    """Log model information as a text artifact.

    Args:
        model_info: Dictionary with model metadata
    """
    import tempfile

    if mlflow.active_run() is None:
        raise ValueError("No active MLflow run. Call mlflow.start_run() first.")

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for key, value in model_info.items():
            f.write(f"{key}: {value}\n")
        temp_path = f.name

    try:
        mlflow.log_artifact(temp_path, "model_summary.txt")
        console.print("[green]✓[/green] Logged model summary artifact")
    finally:
        # Clean up temp file
        Path(temp_path).unlink()
