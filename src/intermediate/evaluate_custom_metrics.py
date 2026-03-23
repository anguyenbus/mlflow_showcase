"""Custom metric creation example for domain-specific evaluation.

This example demonstrates how to create and use custom evaluation
metrics with mlflow.metrics.make_metric().

Expected Output:
--------------
✓ Created custom metric: legal_citation_accuracy
✓ Running evaluation with custom metrics...
Legal Citation Accuracy: 0.90
Answer Relevance: 0.85
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console
from typing import Any
from typing import Any
import pandas as pd

import mlflow
from config import get_config
from basics.mlflow_utils import create_experiment


# Initialize console
console = Console()


def legal_citation_eval_fn(
    predictions: list[str],
    targets: list[str],
    **kwargs: Any,
) -> dict[str, float]:
    """Evaluate legal citation accuracy in responses.

    This is a simple mock implementation. In production, you would
    implement sophisticated logic to detect and validate legal citations.

    Args:
        predictions: List of model predictions
        targets: List of ground truth answers
        **kwargs: Additional arguments

    Returns:
        Dictionary with metric scores
    """
    # Mock implementation: check if responses contain citation-like patterns
    import re

    correct = 0
    for pred in predictions:
        # Look for citation patterns (e.g., "Section 10-5", "ITAA 1997")
        if re.search(r"Section\s+\d+[- ]\d+|ITAA\s+\d{4}", pred, re.IGNORECASE):
            correct += 1

    score = correct / len(predictions) if predictions else 0.0
    return {"legal_citation_accuracy": score}


def answer_relevance_eval_fn(
    predictions: list[str],
    targets: list[str],
    **kwargs: Any,
) -> dict[str, float]:
    """Evaluate answer relevance using keyword matching.

    This is a simple mock implementation. In production, you would use
    semantic similarity or more sophisticated NLP techniques.

    Args:
        predictions: List of model predictions
        targets: List of ground truth answers
        **kwargs: Additional arguments

    Returns:
        Dictionary with metric scores
    """
    relevant = 0
    for pred, target in zip(predictions, targets):
        # Check if prediction contains keywords from target
        target_words = set(target.lower().split())
        pred_words = set(pred.lower().split())

        # Simple relevance: overlap of key terms
        overlap = len(target_words & pred_words) / max(len(target_words), 1)
        if overlap > 0.3:  # Threshold for relevance
            relevant += 1

    score = relevant / len(predictions) if predictions else 0.0
    return {"answer_relevance": score}


def create_custom_metrics() -> list[mlflow.metrics.Metric]:
    """Create custom evaluation metrics for domain-specific evaluation.

    Returns:
        List of custom MLflow metrics
    """
    # Create legal citation accuracy metric
    citation_metric = mlflow.metrics.make_metric(
        eval_fn=legal_citation_eval_fn,
        name="legal_citation_accuracy",
        greater_is_better=True,
    )

    console.print("[green]✓[/green] Created custom metric: legal_citation_accuracy")
    console.print("  Definition: Measure legal citation accuracy in responses\n")

    # Create answer relevance metric
    relevance_metric = mlflow.metrics.make_metric(
        eval_fn=answer_relevance_eval_fn,
        name="answer_relevance",
        greater_is_better=True,
    )

    console.print("[green]✓[/green] Created custom metric: answer_relevance")
    console.print("  Definition: Measure answer relevance to question\n")

    return [citation_metric, relevance_metric]


def main() -> None:
    """Run custom metrics evaluation example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = create_experiment("mlflow-custom-metrics")

    console.print(f"[green]✓[/green] Experiment ID: {experiment.experiment_id}\n")

    # Create custom metrics
    custom_metrics = create_custom_metrics()

    # Create evaluation dataset
    eval_df = pd.DataFrame({
        "inputs": [
            "What is the company tax rate in Australia?",
            "Explain GST in Australia",
        ],
        "ground_truth": [
            "The company tax rate is 30% for most companies, or 25% for base rate entities.",
            "GST is a 10% tax on most goods and services in Australia.",
        ],
    })

    console.print("[green]✓[/green] Created evaluation dataset\n")

    # Start MLflow run
    with mlflow.start_run():
        # Log a dummy model
        model_info = mlflow.langchain.log_model(
            lambda x: {"output": "Mock response"},
            "custom_model",
            input_example={"inputs": eval_df["inputs"][0]},
        )

        console.print("✓ Running evaluation with custom metrics...\n")

        # Run evaluation with custom metrics
        result = mlflow.evaluate(
            model_info.model_uri,
            eval_df,
            targets="ground_truth",
            model_type="question-answering",
            evaluators="default",
            custom_metrics=custom_metrics,
        )

        # Display custom metrics
        console.print("[green]Custom Metrics Results:[/green]")
        for metric_name, value in result.metrics.items():
            if metric_name in ["legal_citation_accuracy", "answer_relevance"]:
                console.print(f"  {metric_name}: {value:.4f}")

        console.print(f"\n[cyan]Run ID:[/cyan] {mlflow.active_run().info.run_id}")
        console.print("[green]\nView in MLflow UI to see custom metric results![/green]")


if __name__ == "__main__":
    main()
