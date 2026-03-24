"""
MLflow manual logging example for RAGas evaluation.

This script demonstrates fine-grained control over MLflow logging by manually
logging parameters, metrics, and artifacts for RAGas evaluation.

Expected Output:
    Loading evaluation dataset from: /path/to/evaluation_dataset.json
    ✓ Loaded 6 evaluation examples
    Configured Zhipu AI backend for RAGas evaluation: glm-5
      Temperature: 0.2 (low for consistent evaluation)
      Embeddings: embedding-3

    Setting up MLflow experiment: ragas-manual-logging
    ✓ Using existing MLflow experiment: ragas-manual-logging

    Running RAGas evaluation independently...
    ✓ Evaluation complete!

    Logging results to MLflow manually...
    ✓ Logged 5 parameters
    ✓ Logged 5 metrics
    ✓ Logged dataset artifact: /path/to/evaluation_dataset.json
    ✓ Set 3 custom tags

    MLflow Run Information:
    ┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Field                 ┃ Value                 ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
    │ Run ID                │ xyz789abc012          │
    │ Experiment            │ ragas-manual-logging  │
    │ Status                │ COMPLETED             │
    └───────────────────────┴──────────────────────┘

    View results in MLflow UI: http://localhost:5000/#/runs/xyz789abc012

    SCREENSHOT CHECKPOINT:
    1. Open MLflow UI at http://localhost:5000
    2. Navigate to Experiments → ragas-manual-logging
    3. Click on the latest run
    4. Take screenshot of custom parameters view
    5. Suggested filename: mlflow_manual_logging_params.png
    6. Take screenshot of logged metrics
    7. Suggested filename: mlflow_manual_logging_metrics.png
    8. Take screenshot of tag information
    9. Suggested filename: mlflow_manual_logging_tags.png

    COMPARISON WITH AUTO-LOGGING:
    - Manual logging provides fine-grained control
    - You can log custom parameters and metrics
    - You can set custom tags for organization
    - Auto-logging is simpler but less customizable
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
def extract_metrics_from_results(results: Any) -> dict[str, float]:
    """
    Extract metric scores from ragas evaluation results.

    Args:
        results: ragas evaluation results object

    Returns:
        Dictionary of metric names to scores

    """
    # Convert results to pandas DataFrame
    results_df = results.to_pandas()

    # Get the first row (average scores)
    metrics_dict = results_df.iloc[0].to_dict()

    # Extract only the metric columns (exclude input columns)
    metric_results = {
        k: v
        for k, v in metrics_dict.items()
        if k
        in [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
            "answer_correctness",
        ]
    }

    return metric_results


@beartype
def format_parameters_dict(
    model: str,
    temperature: float,
    num_samples: int,
    metrics_list: list[str],
) -> dict[str, Any]:
    """
    Format parameters dictionary for MLflow logging.

    Args:
        model: Model name
        temperature: Temperature setting
        num_samples: Number of samples evaluated
        metrics_list: List of metrics used

    Returns:
        Dictionary of parameters for logging

    """
    return {
        "model": model,
        "temperature": str(temperature),
        "num_samples": str(num_samples),
        "metrics": ",".join(metrics_list),
        "backend": "zhipu",
        "logging_method": "manual",
    }


@beartype
def main() -> None:
    """
    Run MLflow manual logging example.

    This function demonstrates:
    1. Loading configuration and dataset
    2. Setting up MLflow experiment
    3. Running ragas evaluation independently
    4. Manually logging parameters
    5. Manually logging metrics
    6. Logging dataset as artifact
    7. Setting custom tags
    8. Comparison with auto-logging
    """
    try:
        import mlflow

        from ragas import evaluate as ragas_evaluate

        # Step 1: Load configuration
        console.print("[bold cyan]Step 1:[/bold cyan] Loading configuration...")
        config = get_ragas_config()

        # Step 2: Load evaluation dataset
        console.print("\n[bold cyan]Step 2:[/bold cyan] Loading evaluation dataset...")
        dataset = load_evaluation_dataset()
        dataset_path = str(config.evaluation_data_path / "evaluation_dataset.json")

        # Step 3: Configure Zhipu AI backend
        console.print("\n[bold cyan]Step 3:[/bold cyan] Configuring Zhipu AI backend...")
        llm, embeddings = configure_zhipu_backend()

        # Step 4: Create RAGas evaluation
        console.print("\n[bold cyan]Step 4:[/bold cyan] Creating RAGas evaluation...")
        eval_config = create_ragas_evaluation(llm=llm, embeddings=embeddings)
        metrics_list = [m.name for m in eval_config["metrics"]]

        # Step 5: Set up MLflow experiment
        console.print("\n[bold cyan]Step 5:[/bold cyan] Setting up MLflow experiment...")
        experiment_name = "ragas-manual-logging"
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        mlflow.set_experiment(experiment_name)
        console.print(f"[green]✓[/green] Using MLflow experiment: {experiment_name}")

        # Step 6: Run ragas evaluation independently
        console.print("\n[bold cyan]Step 6:[/bold cyan] Running RAGas evaluation independently...")

        import pandas as pd

        df = pd.DataFrame(dataset)
        results = ragas_evaluate(
            df=df,
            metrics=eval_config["metrics"],
        )

        console.print("[green]✓[/green] Evaluation complete!")

        # Step 7: Log results to MLflow manually
        console.print("\n[bold cyan]Step 7:[/bold cyan] Logging results to MLflow manually...")

        with mlflow.start_run() as run:
            run_id = run.info.run_id

            # Manually log parameters
            parameters = format_parameters_dict(
                model="glm-5",
                temperature=0.2,
                num_samples=len(dataset),
                metrics_list=metrics_list,
            )
            mlflow.log_params(parameters)
            console.print(f"[green]✓[/green] Logged {len(parameters)} parameters")

            # Manually log metrics
            metrics = extract_metrics_from_results(results)
            mlflow.log_metrics(metrics)
            console.print(f"[green]✓[/green] Logged {len(metrics)} metrics")

            # Log dataset as artifact
            mlflow.log_artifact(dataset_path)
            console.print(f"[green]✓[/green] Logged dataset artifact: {dataset_path}")

            # Set custom tags
            tags = {
                "evaluation_type": "ragas",
                "backend": "zhipu",
                "domain": "tax_evaluation",
                "logging_method": "manual",
            }
            mlflow.set_tags(tags)
            console.print(f"[green]✓[/green] Set {len(tags)} custom tags")

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

            # Display screenshot checkpoints
            console.print(
                Panel(
                    "[bold yellow]SCREENSHOT CHECKPOINTS:[/bold yellow]\n"
                    "1. Open MLflow UI at http://localhost:5000\n"
                    f"2. Navigate to Experiments → {experiment_name}\n"
                    "3. Click on the latest run\n"
                    "4. Take screenshot of custom parameters view\n"
                    "5. Suggested filename: mlflow_manual_logging_params.png\n"
                    "6. Take screenshot of logged metrics\n"
                    "7. Suggested filename: mlflow_manual_logging_metrics.png\n"
                    "8. Take screenshot of tag information\n"
                    "9. Suggested filename: mlflow_manual_logging_tags.png\n\n"
                    "[dim]Capture: Custom parameters, metrics table, and tags[/dim]",
                    title="[bold cyan]Screenshot Instructions[/bold cyan]",
                    border_style="yellow",
                )
            )

            # Display comparison with auto-logging
            console.print(
                Panel(
                    "[bold cyan]COMPARISON WITH AUTO-LOGGING:[/bold cyan]\n"
                    "[green]Manual Logging Advantages:[/green]\n"
                    "• Fine-grained control over what gets logged\n"
                    "• Custom parameter names and values\n"
                    "• Custom tags for better organization\n"
                    "• Selective metric logging\n"
                    "• Additional artifacts and metadata\n\n"
                    "[yellow]Auto-Logging Advantages:[/yellow]\n"
                    "• Simpler implementation (one-line)\n"
                    "• Automatic parameter capture\n"
                    "• Standardized format\n"
                    "• Less code to maintain\n\n"
                    "[dim]Use manual logging when you need customization.\n"
                    "Use auto-logging for quick, standard evaluation logging.[/dim]",
                    title="[bold cyan]Manual vs Auto Logging[/bold cyan]",
                    border_style="cyan",
                )
            )

            # Display summary
            console.print(
                Panel(
                    f"[bold green]Manual Logging Summary[/bold green]\n"
                    f"• Dataset size: {len(dataset)} examples\n"
                    f"• Parameters logged: {len(parameters)}\n"
                    f"• Metrics logged: {len(metrics)}\n"
                    f"• Custom tags: {len(tags)}\n"
                    f"• Run ID: {run_id}\n"
                    f"• Experiment: {experiment_name}\n"
                    f"• Logging method: Manual",
                    title="[bold cyan]MLflow Manual Logging[/bold cyan]",
                    border_style="cyan",
                )
            )

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        raise


if __name__ == "__main__":
    main()
