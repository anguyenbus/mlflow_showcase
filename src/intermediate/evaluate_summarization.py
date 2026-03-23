"""ROUGE evaluation for summarization tasks.

This example demonstrates how to use MLflow's evaluation
framework with ROUGE metrics for text summarization.

Expected Output:
--------------
✓ Experiment 'mlflow-rouge-evaluation' (ID: xxx)
✓ Logged summarization model
✓ Running evaluation...
ROUGE-1: 0.85
ROUGE-2: 0.75
ROUGE-L: 0.80
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console
from typing import Any
import pandas as pd

import mlflow
from config import get_config
from basics.mlflow_utils import create_experiment


# Initialize console
console = Console()


def create_summarization_dataset() -> pd.DataFrame:
    """Create a sample summarization evaluation dataset.

    Returns:
        DataFrame with inputs and ground truth summaries
    """
    data = {
        "inputs": [
            "The Australian Taxation Office (ATO) is the principal revenue collection "
            "agency of the Australian government, responsible for administering the "
            "Australian taxation system, superannuation legislation, and other related matters.",
            "Goods and Services Tax (GST) is a broad-based tax of 10% on most goods, "
            "services, and other items sold or consumed in Australia, introduced on 1 July 2000.",
            "The Medicare levy is 2% of taxable income that helps fund Australia's public "
            "healthcare system, with most taxpayers paying this levy.",
        ],
        "ground_truth": [
            "The ATO is Australia's main tax collection agency, administering taxation "
            "and superannuation systems.",
            "GST is a 10% tax on most goods and services in Australia, introduced in 2000.",
            "Medicare levy is a 2% tax funding Australia's healthcare system.",
        ],
    }
    return pd.DataFrame(data)


def evaluate_summarization(
    eval_df: pd.DataFrame,
    model_uri: str,
) -> Any:
    """Evaluate summarization model using ROUGE metrics.

    Args:
        eval_df: Evaluation dataset with inputs and ground_truth columns
        model_uri: MLflow model URI to evaluate

    Returns:
        MLflow evaluation result
    """
    console.print("✓ Running evaluation...")

    # Run evaluation with ROUGE metrics
    result = mlflow.evaluate(
        model_uri,
        eval_df,
        targets="ground_truth",
        model_type="summarization",
        evaluators="default",
    )

    # Display metrics
    console.print("\n[green]ROUGE Metrics:[/green]")
    for metric_name, value in result.metrics.items():
        if metric_name.startswith("rouge"):
            console.print(f"  {metric_name}: {value:.4f}")

    return result


def main() -> None:
    """Run ROUGE evaluation example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = create_experiment("mlflow-rouge-evaluation")

    console.print(f"[green]✓[/green] Experiment ID: {experiment.experiment_id}\n")

    # Create evaluation dataset
    eval_df = create_summarization_dataset()
    console.print(f"[green]✓[/green] Created evaluation dataset: {len(eval_df)} examples\n")

    # Start MLflow run
    with mlflow.start_run():
        # Log a dummy model for evaluation
        # NOTE: In real scenarios, log your actual model
        model_info = mlflow.langchain.log_model(
            lambda x: {"output": "Mock summary"},
            "summarization_model",
            input_example={"inputs": eval_df["inputs"][0]},
        )

        console.print("[green]✓[/green] Logged summarization model\n")

        # Run evaluation
        result = evaluate_summarization(eval_df, model_info.model_uri)

        # Log evaluation results
        mlflow.log_metrics(result.metrics)

        console.print(f"\n[cyan]Run ID:[/cyan] {mlflow.active_run().info.run_id}")
        console.print("[green]\nView in MLflow UI to see evaluation results![/green]")


if __name__ == "__main__":
    main()
