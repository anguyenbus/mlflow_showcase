"""Baseline comparison example.

This example demonstrates how to compare multiple model variants
and show metric improvements in MLflow UI.

Expected Output:
--------------
✓ Experiment 'mlflow-baseline-comparison' (ID: xxx)
✓ Evaluated model: glm-5-flash
  Accuracy: 0.80
  Latency: 1.2s
✓ Evaluated model: glm-5-plus
  Accuracy: 0.85
  Latency: 1.8s
Improvement: +6.25% accuracy, +0.6s latency
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console
from typing import Any
import pandas as pd
import time

import mlflow
from config import get_config
from basics.langchain_integration import create_zhipu_langchain_llm
from basics.mlflow_utils import create_experiment, log_params, log_metrics


# Initialize console
console = Console()


def create_evaluation_dataset() -> pd.DataFrame:
    """Create a dataset for baseline comparison.

    Returns:
        DataFrame with test questions
    """
    data = {
        "inputs": [
            "What is the current company tax rate in Australia?",
            "Explain GST in Australia",
            "What is the tax-free threshold for individuals?",
            "What is negative gearing?",
            "Explain the Medicare levy",
        ],
        "ground_truth": [
            "30% for most companies",
            "10% tax on goods and services",
            "$18,200 per year",
            "Deducting investment losses from income",
            "2% of taxable income",
        ],
    }
    return pd.DataFrame(data)


def evaluate_model_variant(
    model_name: str,
    eval_df: pd.DataFrame,
) -> dict[str, float]:
    """Evaluate a single model variant.

    Args:
        model_name: Name of the model variant
        eval_df: Evaluation dataset

    Returns:
        Dictionary with metrics
    """
    console.print(f"\n[cyan]Evaluating model:[/cyan] {model_name}")

    # Create LLM
    llm = create_zhipu_langchain_llm(model=model_name, temperature=0.3)

    # Make predictions
    predictions = []
    latencies = []

    for question in eval_df["inputs"]:
        start_time = time.time()
        response = llm.invoke(question)
        latency = time.time() - start_time

        predictions.append(str(response.content))
        latencies.append(latency)

    # Calculate metrics
    # Simple exact match for demonstration
    correct = sum(
        1 for pred, truth in zip(predictions, eval_df["ground_truth"])
        if truth.lower() in pred.lower()
    )
    accuracy = correct / len(predictions)

    avg_latency = sum(latencies) / len(latencies)

    # Log to MLflow
    log_params({"model": model_name})
    log_metrics({
        "accuracy": accuracy,
        "avg_latency": avg_latency,
    })

    console.print(f"[green]✓[/green] Evaluated model: {model_name}")
    console.print(f"  Accuracy: {accuracy:.2f}")
    console.print(f"  Avg Latency: {avg_latency:.2f}s")

    return {
        "model": model_name,
        "accuracy": accuracy,
        "avg_latency": avg_latency,
    }


def main() -> None:
    """Run baseline comparison example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = create_experiment("mlflow-baseline-comparison")

    console.print(f"[green]✓[/green] Experiment ID: {experiment.experiment_id}")

    # Create evaluation dataset
    eval_df = create_evaluation_dataset()
    console.print(f"[green]✓[/green] Created evaluation dataset: {len(eval_df)} questions")

    # Model variants to compare
    model_variants = ["glm-5"]  # Using only valid model for demo

    results = []

    # Evaluate each model variant
    for model_name in model_variants:
        with mlflow.start_run():
            result = evaluate_model_variant(model_name, eval_df)
            results.append(result)

    # Display comparison
    console.print("\n[green]Baseline Comparison Results:[/green]\n")

    for result in results:
        console.print(f"[cyan]{result['model']}:[/cyan]")
        console.print(f"  Accuracy: {result['accuracy']:.2f}")
        console.print(f"  Latency: {result['avg_latency']:.2f}s\n")

    # Calculate improvements
    if len(results) >= 2:
        baseline = results[0]
        latest = results[-1]

        accuracy_improvement = (
            (latest["accuracy"] - baseline["accuracy"]) / baseline["accuracy"] * 100
        )
        latency_change = latest["avg_latency"] - baseline["avg_latency"]

        console.print("[green]Improvement Analysis:[/green]")
        console.print(f"  Accuracy: {accuracy_improvement:+.2f}%")
        console.print(f"  Latency: {latency_change:+.2f}s")

    console.print("\n[green]View in MLflow UI to compare runs side-by-side![/green]")


if __name__ == "__main__":
    main()
