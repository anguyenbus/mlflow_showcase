"""
Python runner for temperature optimization evaluation.

This script evaluates the effect of temperature on LLM outputs across
different task types, helping identify optimal temperature settings.
"""

import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Final

import mlflow
from beartype import beartype
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Load environment variables from .env file
# Use resolve() to get absolute path before navigating up
# Path: src/promptfoo_evaluation/advanced/choosing_right_temperature/ -> go up 5 levels to reach project root
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

from promptfoo_evaluation.shared.config import (
    get_promptfoo_output_dir,
    get_zhipu_api_key,
    validate_promptfoo_installation,
)
from promptfoo_evaluation.shared.mlflow_handler import (
    MLflowExperimentManager,
    PromptfooResultParser,
)

# Initialize rich console
console: Final[Console] = Console()

# Experiment name for MLflow
EXPERIMENT_NAME: Final[str] = "promptfoo-advanced-temperature"

# Output file path
OUTPUT_FILE: Final[str] = "temperature_sweep.json"

# Temperature values being tested
TEMPERATURES: Final[tuple[float, ...]] = (0.0, 0.3, 0.7, 1.0)


@beartype
def run_temperature_evaluation(
    config_path: str | Path,
) -> dict[str, Any] | None:
    """
    Run temperature sweep evaluation with promptfoo.

    Args:
        config_path: Path to the promptfoo YAML configuration file.

    Returns:
        Parsed results dictionary if evaluation succeeds, None otherwise.

    Raises:
        subprocess.CalledProcessError: If promptfoo evaluation fails.
        ValueError: If ZHIPU_API_KEY is not set.

    """
    # Validate environment
    zhipu_api_key = get_zhipu_api_key()
    validate_promptfoo_installation()

    console.print("\n[bold cyan]Temperature Optimization Sweep[/bold cyan]")
    console.print("=" * 50)

    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Config: {config_path}")
    console.print("  Model: glm-5")
    console.print(f"  Temperatures: {TEMPERATURES}")
    console.print("  Task Types: 8 different tasks\n")

    # Build command
    cmd = ["npx", "promptfoo", "eval", "-c", str(config_path)]

    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]\n")

    # Set environment variables for promptfoo
    env = {
        **os.environ,
        "OPENAI_API_KEY": zhipu_api_key,
        "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
    }

    try:
        # NOTE: Run with check=False because promptfoo returns exit code 100 when tests fail
        # Exit code 100 is not an error - it just indicates some tests didn't pass
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

        # Check if the command actually failed (exit code != 0 and != 100)
        if result.returncode not in (0, 100):
            console.print("[red]Evaluation failed with unexpected error[/red]")
            console.print(f"Exit code: {result.returncode}")
            if result.stderr:
                console.print(f"Error output:\n{result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

        # Load results
        output_dir = get_promptfoo_output_dir()
        results_path = output_dir / OUTPUT_FILE

        if results_path.exists():
            with open(results_path) as f:
                results = json.load(f)
            return results

        console.print(f"[yellow]Warning:[/yellow] Results file not found at {results_path}")
        return None

    except FileNotFoundError:
        console.print(f"[yellow]Warning:[/yellow] Results file not found")
        return None


@beartype
def calculate_temperature_metrics(
    results: dict[str, Any],
) -> dict[str, dict[str, float]]:
    """
    Calculate temperature-specific metrics from promptfoo results.

    Args:
        results: Raw promptfoo results dictionary.

    Returns:
        Dictionary mapping temperature values to their metrics.
        Format: {temperature_str: {metric_name: value}}

    """
    metrics: dict[str, dict[str, float]] = {}

    # Initialize metrics for each temperature
    for temp in TEMPERATURES:
        temp_key = str(temp)
        metrics[temp_key] = {
            "pass_rate": 0.0,
            "avg_score": 0.0,
            "avg_latency": 0.0,
            "total_tokens": 0.0,
        }

    # Navigate the nested results structure
    results_dict = results.get("results", {})
    if isinstance(results_dict, dict):
        result_list = results_dict.get("results", [])
    else:
        result_list = []

    # Group results by provider (which contains temperature info)
    for result in result_list:
        provider = result.get("provider", {})
        provider_label = provider.get("label", "")

        # Extract temperature from provider label (e.g., "GLM-5 @ 0.0")
        for temp in TEMPERATURES:
            temp_str = str(temp)
            if f"@ {temp_str}" in provider_label:
                # Count this result
                metrics[temp_str]["pass_rate"] += 1 if result.get("success", False) else 0
                metrics[temp_str]["avg_score"] += result.get("score", 0.0)
                metrics[temp_str]["avg_latency"] += result.get("latencyMs", 0.0)

                # Get token usage
                response = result.get("response", {})
                token_usage = response.get("tokenUsage", {})
                metrics[temp_str]["total_tokens"] += token_usage.get("total", 0)
                break

    # Calculate averages (each temperature has 8 test cases)
    test_count = 8  # Number of different task types
    for temp in TEMPERATURES:
        temp_key = str(temp)
        if metrics[temp_key]["pass_rate"] > 0:
            metrics[temp_key]["pass_rate"] /= test_count
            metrics[temp_key]["avg_score"] /= test_count
            metrics[temp_key]["avg_latency"] /= test_count

    return metrics


@beartype
def calculate_variance(
    metrics: dict[str, dict[str, float]],
) -> dict[str, float]:
    """
    Calculate variance across temperature values.

    Args:
        metrics: Temperature-specific metrics dictionary.

    Returns:
        Dictionary with variance statistics for each metric type.

    """
    variance: dict[str, float] = {}

    # Collect values for each metric across temperatures
    metric_names = ["pass_rate", "avg_score", "avg_latency"]

    for metric_name in metric_names:
        values = [metrics[str(temp)][metric_name] for temp in TEMPERATURES]

        if values:
            mean = sum(values) / len(values)
            variance_value = sum((v - mean) ** 2 for v in values) / len(values)
            variance[f"{metric_name}_variance"] = variance_value
            variance[f"{metric_name}_range"] = max(values) - min(values)

    return variance


@beartype
def display_temperature_results(
    parser: PromptfooResultParser,
    temperature_metrics: dict[str, dict[str, float]],
    variance: dict[str, float],
) -> None:
    """
    Display temperature optimization results in formatted tables.

    Args:
        parser: PromptfooResultParser with parsed results.
        temperature_metrics: Metrics per temperature.
        variance: Variance statistics.

    """
    console.print("\n[bold]Temperature Sweep Results:[/bold]\n")

    # Create comparison table
    table = Table(
        title="Performance by Temperature",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Temperature", style="cyan", width=15)
    table.add_column("Pass Rate", style="green", width=12)
    table.add_column("Avg Score", style="green", width=12)
    table.add_column("Latency (ms)", style="yellow", width=15)
    table.add_column("Tokens", style="blue", width=12)
    table.add_column("Best For", style="magenta", width=25)

    # Temperature recommendations
    recommendations = {
        "0.0": "Factual QA, Math, Code",
        "0.3": "Translation, Summarization",
        "0.7": "Balanced tasks",
        "1.0": "Creative writing, Brainstorming",
    }

    for temp in TEMPERATURES:
        temp_key = str(temp)
        temp_metrics = temperature_metrics.get(temp_key, {})

        table.add_row(
            f"{temp}",
            f"{temp_metrics.get('pass_rate', 0):.2%}",
            f"{temp_metrics.get('avg_score', 0):.3f}",
            f"{temp_metrics.get('avg_latency', 0):.1f}",
            f"{int(temp_metrics.get('total_tokens', 0))}",
            recommendations.get(temp_key, ""),
        )

    console.print(table)

    # Display variance analysis
    console.print("\n[bold]Variance Analysis:[/bold]")
    console.print("  Higher variance = temperature has bigger impact\n")

    variance_table = Table(show_header=False)
    variance_table.add_column("Metric", style="cyan", width=25)
    variance_table.add_column("Variance", style="yellow", width=15)
    variance_table.add_column("Range", style="green", width=15)
    variance_table.add_column("Impact", width=20)

    variance_table.add_row(
        "Pass Rate",
        f"{variance.get('pass_rate_variance', 0):.4f}",
        f"{variance.get('pass_rate_range', 0):.2%}",
        _get_impact_level(variance.get('pass_rate_variance', 0)),
    )
    variance_table.add_row(
        "Avg Score",
        f"{variance.get('avg_score_variance', 0):.4f}",
        f"{variance.get('avg_score_range', 0):.3f}",
        _get_impact_level(variance.get('avg_score_variance', 0)),
    )
    variance_table.add_row(
        "Latency",
        f"{variance.get('avg_latency_variance', 0):.1f}",
        f"{variance.get('avg_latency_range', 0):.1f}ms",
        _get_impact_level(variance.get('avg_latency_variance', 0)),
    )

    console.print(variance_table)

    # Recommendations
    console.print("\n[bold]Recommendations:[/bold]\n")

    # Find best temperature for each metric
    best_pass_temp = max(
        TEMPERATURES,
        key=lambda t: temperature_metrics.get(str(t), {}).get("pass_rate", 0),
    )
    best_score_temp = max(
        TEMPERATURES,
        key=lambda t: temperature_metrics.get(str(t), {}).get("avg_score", 0),
    )

    console.print(f"  [cyan]Best Pass Rate:[/cyan] Temperature {best_pass_temp}")
    console.print(f"  [cyan]Best Score:[/cyan] Temperature {best_score_temp}")

    console.print("\n  [bold]Task Type Recommendations:[/bold]")
    console.print("    [green]0.0 - 0.3:[/green] Factual tasks requiring precision")
    console.print("    [yellow]0.3 - 0.7:[/yellow] General purpose tasks")
    console.print("    [magenta]0.7 - 1.0:[/magenta] Creative and exploratory tasks")


@beartype
def _get_impact_level(variance: float) -> str:
    """
    Get impact level description based on variance.

    Args:
        variance: The variance value.

    Returns:
        Formatted impact level string.

    """
    if variance < 0.01:
        return "[dim]Low[/dim]"
    elif variance < 0.05:
        return "[yellow]Medium[/yellow]"
    else:
        return "[red]High[/red]"


@beartype
def log_to_mlflow(
    results: dict[str, Any],
    parser: PromptfooResultParser,
    temperature_metrics: dict[str, dict[str, float]],
    variance: dict[str, float],
) -> str | None:
    """
    Log temperature evaluation results to MLflow.

    Args:
        results: Raw promptfoo results dictionary.
        parser: PromptfooResultParser with parsed results.
        temperature_metrics: Temperature-specific metrics.
        variance: Variance statistics.

    Returns:
        MLflow run ID if logging succeeds, None otherwise.

    """
    try:
        manager = MLflowExperimentManager(EXPERIMENT_NAME)
        experiment_id = manager.get_or_create_experiment()

        console.print(f"\n[cyan]MLflow experiment:[/cyan] {EXPERIMENT_NAME}")
        console.print(f"[dim]Experiment ID:[/dim] {experiment_id}")

        with manager.run_experiment(run_name="temperature-sweep-eval") as run:
            # Log base metrics
            base_metrics = parser.get_metrics()
            manager.log_metrics(base_metrics)

            # Log temperature-specific metrics
            for temp in TEMPERATURES:
                temp_key = str(temp)
                temp_metrics = temperature_metrics.get(temp_key, {})
                for metric_name, value in temp_metrics.items():
                    manager.log_metrics({f"temp_{temp_key}_{metric_name}": value})

            # Log variance metrics
            manager.log_metrics(variance)

            # Log parameters
            params = {
                "model": "glm-5",
                "temperatures_tested": ",".join(str(t) for t in TEMPERATURES),
                "task_count": "8",
            }
            manager.log_params(params)

            # Log tags
            tags = {
                "evaluation_type": "temperature_sweep",
                "framework": "promptfoo",
            }
            mlflow.set_tags(tags)

            # Log results artifact
            output_dir = get_promptfoo_output_dir()
            results_path = output_dir / OUTPUT_FILE
            if results_path.exists():
                manager.log_artifact(results_path)

            # Log summary
            summary_lines = [
                "Temperature Sweep Summary",
                "=" * 40,
            ]

            for temp in TEMPERATURES:
                temp_key = str(temp)
                temp_metrics = temperature_metrics.get(temp_key, {})
                summary_lines.extend([
                    f"Temperature {temp}:",
                    f"  Pass Rate: {temp_metrics.get('pass_rate', 0):.2%}",
                    f"  Avg Score: {temp_metrics.get('avg_score', 0):.3f}",
                    f"  Avg Latency: {temp_metrics.get('avg_latency', 0):.1f}ms",
                    "",
                ])

            summary_lines.extend([
                "Variance Analysis:",
                f"  Pass Rate Variance: {variance.get('pass_rate_variance', 0):.4f}",
                f"  Score Variance: {variance.get('avg_score_variance', 0):.4f}",
            ])

            manager.log_text("\n".join(summary_lines), "summary.txt")

        console.print(f"[green]Results logged to MLflow[/green]")
        console.print(f"[dim]Run ID:[/dim] {run.info.run_id}")

        return run.info.run_id

    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Could not log to MLflow: {e}")
        return None


@beartype
def main() -> None:
    """Run the temperature optimization evaluation."""
    config_path = Path(__file__).parent / "temperature_sweep.yaml"

    try:
        results = run_temperature_evaluation(config_path)

        if results:
            parser = PromptfooResultParser(results)
            temperature_metrics = calculate_temperature_metrics(results)
            variance = calculate_variance(temperature_metrics)

            display_temperature_results(parser, temperature_metrics, variance)

            log_to_mlflow(results, parser, temperature_metrics, variance)

            console.print("\n[green]Evaluation complete![/green]")
            console.print("\n[cyan]View results in web UI:[/cyan]")
            console.print("  npx promptfoo view")

        else:
            console.print("[yellow]No results to display[/yellow]")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
