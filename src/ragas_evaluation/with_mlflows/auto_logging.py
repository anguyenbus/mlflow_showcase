"""
MLflow automatic logging example for RAGas evaluation.

This script demonstrates how to use MLflow's automatic logging with ragas
evaluation using mlflow.evaluate() with the ragas evaluator.

Expected Output:
    Loading evaluation dataset from: /path/to/evaluation_dataset.json
    ✓ Loaded 6 evaluation examples
    Configured Zhipu AI backend for RAGas evaluation: glm-5
      Temperature: 0.2 (low for consistent evaluation)
      Embeddings: embedding-3

    Setting up MLflow experiment: ragas-auto-logging
    ✓ Using existing MLflow experiment: ragas-auto-logging

    Running MLflow evaluation with automatic logging...
    ✓ MLflow evaluation complete!

    MLflow Run Information:
    ┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Field                 ┃ Value                 ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
    │ Run ID                │ abc123def456          │
    │ Experiment            │ ragas-auto-logging    │
    │ Status                │ COMPLETED             │
    └───────────────────────┴──────────────────────┘

    View results in MLflow UI: http://localhost:5000/#/runs/abc123def456

    SCREENSHOT CHECKPOINT:
    1. Open MLflow UI at http://localhost:5000
    2. Navigate to Experiments → ragas-auto-logging
    3. Click on the latest run
    4. Take screenshot of metrics view
    5. Suggested filename: mlflow_auto_logging_metrics.png
"""

from typing import Any

from beartype import beartype
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ragas_evaluation.shared.config import get_ragas_config
from ragas_evaluation.shared.data_loader import load_evaluation_dataset
from ragas_evaluation.shared.metrics import (
    configure_zhipu_backend,
    create_ragas_evaluation,
)
from ragas_evaluation.shared.mlflow_handler import get_mlflow_ui_url

# Initialize rich console for output
console = Console()


@beartype
def dataset_to_dataframe(dataset: list[dict]) -> Any:
    """
    Convert evaluation dataset to pandas DataFrame for MLflow.

    Args:
        dataset: List of evaluation examples

    Returns:
        pandas DataFrame with evaluation data

    """
    import pandas as pd

    df = pd.DataFrame(dataset)

    console.print(f"[green]✓[/green] Converted dataset to DataFrame: {len(df)} rows")

    return df


@beartype
def main() -> None:
    """
    Run MLflow automatic logging example.

    This function demonstrates:
    1. Loading configuration and dataset
    2. Converting dataset to pandas DataFrame
    3. Setting up MLflow experiment
    4. Using mlflow.evaluate() with ragas evaluator
    5. Automatic metric logging
    6. Displaying run information and UI URL
    """
    try:
        import mlflow

        # Step 1: Load configuration
        console.print("[bold cyan]Step 1:[/bold cyan] Loading configuration...")
        config = get_ragas_config()

        # Step 2: Load evaluation dataset
        console.print("\n[bold cyan]Step 2:[/bold cyan] Loading evaluation dataset...")
        dataset = load_evaluation_dataset()

        # Step 3: Configure Zhipu AI backend
        console.print("\n[bold cyan]Step 3:[/bold cyan] Configuring Zhipu AI backend...")
        llm, embeddings = configure_zhipu_backend()

        # Step 4: Create RAGas evaluation
        console.print("\n[bold cyan]Step 4:[/bold cyan] Creating RAGas evaluation...")
        eval_config = create_ragas_evaluation(llm=llm, embeddings=embeddings)

        # Step 5: Convert dataset to DataFrame
        console.print("\n[bold cyan]Step 5:[/bold cyan] Converting dataset to DataFrame...")
        df = dataset_to_dataframe(dataset)

        # Step 6: Set up MLflow experiment
        console.print("\n[bold cyan]Step 6:[/bold cyan] Setting up MLflow experiment...")
        experiment_name = "ragas-auto-logging"
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)

        # Set experiment (will create if doesn't exist)
        mlflow.set_experiment(experiment_name)
        console.print(f"[green]✓[/green] Using MLflow experiment: {experiment_name}")

        # Step 7: Run MLflow evaluation with automatic logging
        console.print(
            "\n[bold cyan]Step 7:[/bold cyan] Running MLflow\nevaluation with automatic logging..."
        )

        # Start MLflow run
        with mlflow.start_run() as run:
            run_id = run.info.run_id

            # Use mlflow.evaluate with ragas evaluator
            # NOTE: This automatically logs all parameters, metrics, and artifacts
            _ = mlflow.evaluate(
                data=df,
                targets="response",
                evaluators=["ragas"],
                evaluator_config={
                    "ragas": {
                        "metrics": eval_config["metrics"],
                        "column_mapping": {
                            "question": "question",
                            "contexts": "contexts",
                            "response": "response",
                            "ground_truth": "reference_answer",
                        },
                    }
                },
            )

            console.print("[green]✓[/green] MLflow evaluation complete!")

            # Step 8: Display run information
            console.print("\n[bold cyan]MLflow Run Information:[/bold cyan]")

            table = Table(title="MLflow Run Details")
            table.add_column("Field", style="cyan", width=20)
            table.add_column("Value", style="green", width=40)

            table.add_row("Run ID", run_id)
            table.add_row("Experiment", experiment_name)
            table.add_row("Status", "COMPLETED")

            console.print(table)

            # Step 9: Display MLflow UI URL
            ui_url = get_mlflow_ui_url(
                tracking_uri=config.mlflow_tracking_uri,
                experiment_id=run.info.experiment_id,
                run_id=run_id,
            )

            console.print(f"\n[bold cyan]View results in MLflow UI:[/bold cyan] {ui_url}")

            # Display screenshot checkpoint
            console.print(
                Panel(
                    "[bold yellow]SCREENSHOT CHECKPOINT:[/bold yellow]\n"
                    "1. Open MLflow UI at http://localhost:5000\n"
                    f"2. Navigate to Experiments → {experiment_name}\n"
                    "3. Click on the latest run\n"
                    "4. Take screenshot of metrics view\n"
                    "5. Suggested filename: mlflow_auto_logging_metrics.png\n\n"
                    "[dim]Capture: Metrics table showing all ragas scores[/dim]",
                    title="[bold cyan]Screenshot Instructions[/bold cyan]",
                    border_style="yellow",
                )
            )

            # Display summary
            console.print(
                Panel(
                    f"[bold green]Automatic Logging Summary[/bold green]\n"
                    f"• Dataset size: {len(dataset)} examples\n"
                    f"• Metrics logged automatically: {len(eval_config['metrics'])}\n"
                    f"• Run ID: {run_id}\n"
                    f"• Experiment: {experiment_name}\n"
                    f"• Tracking URI: {config.mlflow_tracking_uri}",
                    title="[bold cyan]MLflow Automatic Logging[/bold cyan]",
                    border_style="cyan",
                )
            )

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        raise


if __name__ == "__main__":
    main()
