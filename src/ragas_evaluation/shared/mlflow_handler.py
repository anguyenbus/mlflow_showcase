"""
MLflow handling utilities for RAGas evaluation.

This module provides functions for setting up MLflow experiments
and logging RAGas evaluation results.
"""

from typing import Any, Final

from beartype import beartype
from rich.console import Console

# Initialize rich console for output
console: Final[Console] = Console()

# Try to import mlflow
try:
    import mlflow

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None


@beartype
def setup_mlflow_experiment(tracking_uri: str, experiment_name: str) -> tuple[str, str]:
    """
    Set up MLflow experiment for RAGas evaluation.

    Args:
        tracking_uri: MLflow tracking server URI
        experiment_name: Name of the experiment to create or get

    Returns:
        Tuple of (experiment_id, experiment_name)

    Raises:
        ImportError: If mlflow is not installed
        ValueError: If experiment setup fails

    """
    if not MLFLOW_AVAILABLE:
        raise ImportError("mlflow package is not installed. Install it with: pip install mlflow")

    # Set tracking URI
    mlflow.set_tracking_uri(tracking_uri)

    # Check if experiment exists
    experiment = mlflow.get_experiment_by_name(experiment_name)

    if experiment is None:
        # Create new experiment
        experiment_id = mlflow.create_experiment(experiment_name)
        console.print(f"[green]✓[/green] Created new MLflow experiment: {experiment_name}")
    else:
        # Use existing experiment
        experiment_id = experiment.experiment_id
        console.print(f"[green]✓[/green] Using existing MLflow experiment: {experiment_name}")

    return experiment_id, experiment_name


@beartype
def log_ragas_results(
    parameters: dict[str, Any],
    metrics: dict[str, float],
    dataset_path: str,
    tags: dict[str, str] | None = None,
) -> None:
    """
    Log RAGas evaluation results to MLflow.

    Args:
        parameters: Dictionary of parameters to log (model, temperature, etc.)
        metrics: Dictionary of metric scores (faithfulness, answer_relevancy, etc.)
        dataset_path: Path to dataset file to log as artifact
        tags: Optional dictionary of tags for organization

    Raises:
        ImportError: If mlflow is not installed
        ValueError: If logging fails

    """
    if not MLFLOW_AVAILABLE:
        raise ImportError("mlflow package is not installed. Install it with: pip install mlflow")

    # Log parameters
    mlflow.log_params(parameters)
    console.print(f"[green]✓[/green] Logged {len(parameters)} parameters")

    # Log metrics
    mlflow.log_metrics(metrics)
    console.print(f"[green]✓[/green] Logged {len(metrics)} metrics")

    # Log dataset as artifact
    mlflow.log_artifact(dataset_path)
    console.print(f"[green]✓[/green] Logged dataset artifact: {dataset_path}")

    # Set custom tags if provided
    if tags:
        mlflow.set_tags(tags)
        console.print(f"[green]✓[/green] Set {len(tags)} custom tags")


@beartype
def get_mlflow_ui_url(
    tracking_uri: str, experiment_id: str | None = None, run_id: str | None = None
) -> str:
    """
    Get MLflow UI URL for viewing results.

    Args:
        tracking_uri: MLflow tracking server URI
        experiment_id: Optional experiment ID for direct link
        run_id: Optional run ID for direct link

    Returns:
        MLflow UI URL as string

    """
    # For local sqlite tracking, use localhost
    if tracking_uri.startswith("sqlite:///"):
        base_url = "http://localhost:5000"

        # Build URL with specific path if run_id is provided
        if run_id:
            return f"{base_url}/#/runs/{run_id}"
        elif experiment_id:
            return f"{base_url}/#/experiments/{experiment_id}"
        else:
            return base_url

    # For remote tracking, extract host from URI
    # This is a simplified version - production code would need more robust parsing
    if "://" in tracking_uri:
        # Remove protocol and path for basic URL construction
        host_port = tracking_uri.split("://")[1].split("/")[0]
        return f"http://{host_port}"

    # Fallback to localhost
    return "http://localhost:5000"
