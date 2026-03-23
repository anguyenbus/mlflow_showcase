"""Basic MLflow tracking example.

This example demonstrates how to track experiments, log parameters,
metrics, and artifacts with MLflow.

Expected Output:
--------------
✓ Experiment 'mlflow-basics' (ID: 1234567890123456)
✓ Started run: test-run-id
✓ Logged 3 parameters
✓ Logged 2 metrics
✓ Logged artifact: sample_data.txt
Run ID: 9876543210987654321
View results at: http://localhost:5000
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from rich.console import Console

import mlflow
from basics.mlflow_utils import (
    create_experiment,
    log_params,
    log_metrics,
    log_artifact,
)


def main() -> None:
    """Run basic MLflow tracking example."""
    console = Console()

    # Create experiment
    experiment = create_experiment("mlflow-basics")

    # Start a run
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        console.print(f"[green]✓[/green] Started run: {run_id}")

        # Log parameters
        params = {
            "model": "glm-5",
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        log_params(params)

        # Log metrics
        metrics = {
            "accuracy": 0.85,
            "latency": 1.23,
        }
        log_metrics(metrics)

        # Log artifact
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Sample evaluation data\n")
            f.write("Question 1: Answer 1\n")
            f.write("Question 2: Answer 2\n")
            temp_path = f.name

        try:
            log_artifact(temp_path)
        finally:
            Path(temp_path).unlink()

        console.print(f"\n[cyan]Run ID:[/cyan] {run_id}")
        console.print("[cyan]View results at:[/cyan] http://localhost:5000")


if __name__ == "__main__":
    main()
