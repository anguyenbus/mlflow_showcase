"""
MLflow Integration for Promptfoo Evaluation.

This example demonstrates end-to-end MLflow integration with promptfoo,
including running evaluations, parsing results, and logging to MLflow.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import mlflow
from beartype import beartype
from dotenv import load_dotenv
from rich.console import Console

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env file
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

from promptfoo_evaluation.shared.config import get_zhipu_api_key
from promptfoo_evaluation.shared.mlflow_handler import (
    MLflowExperimentManager,
    PromptfooResultParser,
)

# Initialize rich console
console = Console()


@beartype
def run_promptfoo_for_mlflow(
    config_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """
    Run promptfoo evaluation and return results for MLflow logging.

    Args:
        config_path: Path to promptfoo configuration file.
        output_path: Path for promptfoo output JSON.

    Returns:
        Results dictionary with evaluation metrics.

    Raises:
        subprocess.CalledProcessError: If promptfoo evaluation fails.

    """
    console.print("\n[cyan]Running promptfoo evaluation...[/cyan]")
    console.print(f"  Config: {config_path}")
    console.print(f"  Output: {output_path}")

    # Get Zhipu API key and map to OPENAI_API_KEY for promptfoo
    zhipu_api_key = get_zhipu_api_key()

    # Run promptfoo with JSON output
    cmd = [
        "npx",
        "promptfoo",
        "eval",
        "-c",
        str(config_path),
        "-o",
        str(output_path),
        "--no-progress-bar",
    ]

    # Set environment variables for promptfoo
    env = {
        **os.environ,
        "OPENAI_API_KEY": zhipu_api_key,
    }

    try:
        # NOTE: subprocess.run returns CompletedProcess but we don't use it
        # We check for output file existence instead
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

        # Parse JSON output
        if output_path.exists():
            with open(output_path) as f:
                results = json.load(f)
            return results

        console.print("[yellow]Warning: Output file not found, using empty results[/yellow]")
        return {}

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Promptfoo evaluation failed: {e}[/red]")
        raise


@beartype
def log_rag_evaluation_to_mlflow(
    config_name: str,
    results: dict[str, Any],
) -> str:
    """
    Log RAG evaluation results to MLflow.

    Args:
        config_name: Name of the configuration being evaluated.
        results: Promptfoo evaluation results.

    Returns:
        MLflow run ID.

    """
    # Create experiment manager
    experiment_name = "promptfoo-rag"
    manager = MLflowExperimentManager(experiment_name)

    # Get or create experiment
    _ = manager.get_or_create_experiment()

    console.print("\n[cyan]Logging to MLflow:[/cyan]")
    console.print(f"  Experiment: {experiment_name}")

    # Parse results
    parser = PromptfooResultParser(results)
    metrics = parser.get_metrics()

    # Start MLflow run
    with manager.run_experiment(run_name=config_name) as run:
        # Log metrics
        manager.log_metrics(metrics)

        # Log parameters
        manager.log_params(
            {
                "config_name": config_name,
                "num_tests": str(len(results.get("results", []))),
                "num_providers": str(len(results.get("results", [{}])[0].get("results", []))),
            }
        )

        # Log results as artifact
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(results, f, indent=2)
            temp_path = f.name

        manager.log_artifact(Path(temp_path))
        Path(temp_path).unlink()

        # Log summary
        summary = f"""RAG Evaluation Summary

Configuration: {config_name}
Pass Rate: {metrics["pass_rate"]:.2%}
Average Score: {metrics["average_score"]:.3f}
Total Tokens: {int(metrics["total_tokens"])}
Total Cost: ${metrics["total_cost"]:.6f}
Average Latency: {metrics["avg_latency_ms"]:.1f}ms

Providers Tested:
"""
        # Add provider info
        for result in results.get("results", []):
            provider = result.get("provider", "unknown")
            summary += f"  - {provider}\n"

        manager.log_text(summary, "summary.txt")

        console.print(f"[green]Run ID: {run.info.run_id}[/green]")

    return run.info.run_id


@beartype
def main() -> None:
    """Run the MLflow integration example."""
    # Validate environment
    _ = get_zhipu_api_key()

    # Set MLflow tracking URI
    mlflow.set_tracking_uri("sqlite:///mlflow.db")

    console.print("\n[bold blue]Promptfoo + MLflow Integration[/bold blue]")
    console.print("=" * 50)

    # Define configurations to evaluate
    configs = [
        {
            "name": "rag_basics",
            "path": Path(__file__).parent / "rag_basics.yaml",
        },
        {
            "name": "rag_evaluation",
            "path": Path(__file__).parent / "rag_evaluation.yaml",
        },
        {
            "name": "rag_comparison",
            "path": Path(__file__).parent / "rag_comparison.yaml",
        },
    ]

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "promptfoo_results"
    output_dir.mkdir(exist_ok=True)

    # Run evaluations
    for config in configs:
        if not config["path"].exists():
            console.print(f"[yellow]Skipping {config['name']}: config not found[/yellow]")
            continue

        console.print(f"\n[bold]Evaluating: {config['name']}[/bold]")

        try:
            # Run promptfoo
            output_path = output_dir / f"{config['name']}_output.json"
            results = run_promptfoo_for_mlflow(config["path"], output_path)

            if results:
                # Log to MLflow
                run_id = log_rag_evaluation_to_mlflow(config["name"], results)
                console.print(f"[green]Logged to MLflow: {run_id}[/green]")

        except Exception as e:
            console.print(f"[red]Error evaluating {config['name']}: {e}[/red]")
            continue

    # Summary
    console.print("\n[bold blue]Evaluation Complete[/bold blue]")
    console.print("\n[cyan]View results in MLflow:[/cyan]")
    console.print("  mlflow ui")
    console.print("\n[cyan]View results in promptfoo:[/cyan]")
    console.print("  npx promptfoo view")


if __name__ == "__main__":
    main()
