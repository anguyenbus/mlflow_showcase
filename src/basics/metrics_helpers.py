"""Custom metric logging helpers for MLflow.

This module provides helper functions for logging metrics with
batch recording, history tracking, and custom aggregation.
"""

from typing import Final
from collections import defaultdict

import mlflow
from beartype import beartype
from rich.console import Console

# Initialize rich console
console: Final[Console] = Console()


@beartype
class MetricHistory:
    """Track metric history over multiple steps.

    Attributes:
        metrics: Dictionary storing metric values by step
    """

    __slots__ = ("metrics",)

    def __init__(self) -> None:
        """Initialize metric history tracker."""
        self.metrics: dict[str, list[tuple[int, float]]] = defaultdict(list)

    def record(self, step: int, metric_name: str, value: float) -> None:
        """Record a metric value at a specific step.

        Args:
            step: Training/evaluation step number
            metric_name: Name of the metric
            value: Metric value
        """
        self.metrics[metric_name].append((step, value))

    def log_to_mlflow(self) -> None:
        """Log all recorded metrics to MLflow."""
        if mlflow.active_run() is None:
            raise ValueError("No active MLflow run. Call mlflow.start_run() first.")

        for metric_name, history in self.metrics.items():
            for step, value in history:
                mlflow.log_metric(metric_name, value, step=step)

        total_metrics = sum(len(h) for h in self.metrics.values())
        console.print(f"[green]✓[/green] Logged {total_metrics} metric points")


@beartype
def log_batch_metrics(
    metrics_list: list[dict[str, float]],
    start_step: int = 0,
) -> int:
    """Log multiple metric batches with incremental step numbers.

    Args:
        metrics_list: List of metric dictionaries
        start_step: Starting step number (default: 0)

    Returns:
        Next step number after logging
    """
    if mlflow.active_run() is None:
        raise ValueError("No active MLflow run. Call mlflow.start_run() first.")

    for step_idx, metrics in enumerate(metrics_list):
        step = start_step + step_idx
        mlflow.log_metrics(metrics, step=step)

    console.print(
        f"[green]✓[/green] Logged {len(metrics_list)} "
        f"metric batches (steps {start_step}-{start_step + len(metrics_list) - 1})"
    )

    return start_step + len(metrics_list)


@beartype
def compute_and_log_accuracy(
    predictions: list[str],
    ground_truth: list[str],
    metric_name: str = "accuracy",
) -> float:
    """Compute exact match accuracy and log to MLflow.

    Args:
        predictions: List of predicted strings
        ground_truth: List of ground truth strings
        metric_name: Name for the metric (default: "accuracy")

    Returns:
        Accuracy score (0.0 to 1.0)
    """
    if len(predictions) != len(ground_truth):
        raise ValueError("Predictions and ground truth must have same length")

    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    accuracy = correct / len(predictions) if predictions else 0.0

    mlflow.log_metric(metric_name, accuracy)
    console.print(f"[green]✓[/green] Logged {metric_name}: {accuracy:.4f}")

    return accuracy


@beartype
def compute_and_log_average_latency(
    latencies: list[float],
    metric_name: str = "avg_latency",
) -> float:
    """Compute average latency and log to MLflow.

    Args:
        latencies: List of latency values in seconds
        metric_name: Name for the metric (default: "avg_latency")

    Returns:
        Average latency
    """
    if not latencies:
        raise ValueError("Latencies list cannot be empty")

    avg_latency = sum(latencies) / len(latencies)

    mlflow.log_metric(metric_name, avg_latency)
    console.print(f"[green]✓[/green] Logged {metric_name}: {avg_latency:.4f}s")

    return avg_latency
