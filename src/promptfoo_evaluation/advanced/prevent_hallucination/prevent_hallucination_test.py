"""
Python runner for hallucination prevention evaluation.

This script evaluates LLM behavior on questions where hallucination is likely,
measuring the model's ability to refuse to answer when it lacks information.
"""

import json
import os
import re
import subprocess
import sys
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
# Path: src/promptfoo_evaluation/advanced/prevent_hallucination/ -> go up 5 levels to reach project root
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
EXPERIMENT_NAME: Final[str] = "promptfoo-advanced-hallucination"

# Output file path
OUTPUT_FILE: Final[str] = "prevent_hallucination.json"


@beartype
def run_hallucination_evaluation(
    config_path: str | Path,
) -> dict[str, Any] | None:
    """
    Run hallucination prevention evaluation with promptfoo.

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

    console.print("\n[bold cyan]Hallucination Prevention Evaluation[/bold cyan]")
    console.print("=" * 55)

    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Config: {config_path}")
    console.print("  Model: glm-5")
    console.print("  Tests: 10 hallucination-prone questions")
    console.print("  Metrics: factuality, attribution, refusal rate\n")

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
        # NOTE: Don't use check=True because promptfoo returns exit code 100 when tests fail
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
def calculate_hallucination_metrics(
    results: dict[str, Any],
) -> dict[str, float]:
    """
    Calculate hallucination-specific metrics from promptfoo results.

    Args:
        results: Raw promptfoo results dictionary.

    Returns:
        Dictionary with hallucination-specific metrics.

    """
    metrics: dict[str, float] = {
        "refusal_rate": 0.0,
        "hallucination_rate": 0.0,
        "factuality_score": 0.0,
        "attribution_score": 0.0,
    }

    total_tests = 0
    refusals = 0
    hallucinations = 0
    factual_count = 0
    total_factual_score = 0.0

    # Navigate the nested results structure
    results_dict = results.get("results", {})
    if isinstance(results_dict, dict):
        result_list = results_dict.get("results", [])
    else:
        result_list = []

    for result in result_list:
        total_tests += 1
        response = result.get("response", {})
        response_text = response.get("output", "").lower()

        # Check for refusal phrases
        refusal_phrases = [
            "don't know",
            "cannot predict",
            "impossible to know",
            "not sure",
            "uncertain",
            "does not exist",
            "has not been",
        ]
        if any(phrase in response_text for phrase in refusal_phrases):
            refusals += 1

        # Check for test failures (indicates potential hallucination)
        if not result.get("success", True):
            hallucinations += 1

        # Extract score from grading result
        grading_result = result.get("gradingResult", {})
        if isinstance(grading_result, dict):
            score = grading_result.get("score", 0.0)
            if score > 0:
                factual_count += 1
                total_factual_score += score

    # Calculate metrics
    if total_tests > 0:
        metrics["refusal_rate"] = refusals / total_tests
        metrics["hallucination_rate"] = hallucinations / total_tests

    if factual_count > 0:
        metrics["factuality_score"] = total_factual_score / factual_count
    else:
        # Use overall pass rate as fallback
        pass_count = sum(1 for r in result_list if r.get("success", False))
        metrics["factuality_score"] = pass_count / total_tests if total_tests > 0 else 0.0

    # Attribution score: inverse of hallucination rate
    metrics["attribution_score"] = 1.0 - metrics["hallucination_rate"]

    return metrics


@beartype
def display_hallucination_results(
    parser: PromptfooResultParser,
    hallucination_metrics: dict[str, float],
) -> None:
    """
    Display hallucination evaluation results in a formatted table.

    Args:
        parser: PromptfooResultParser with parsed results.
        hallucination_metrics: Hallucination-specific metrics.

    """
    console.print("\n[bold]Hallucination Prevention Results:[/bold]\n")

    # Create metrics table
    table = Table(title="Hallucination Metrics", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Score", style="green", width=15)
    table.add_column("Target", width=15)
    table.add_column("Status", width=15)

    # Try to get base metrics, with fallback
    try:
        base_metrics = parser.get_metrics()
        pass_rate = base_metrics['pass_rate']
    except Exception:
        pass_rate = hallucination_metrics.get('factuality_score', 0.0)

    # Pass rate
    table.add_row(
        "Pass Rate",
        f"{pass_rate:.2%}",
        ">70%",
        _get_status(pass_rate, 0.7),
    )

    table.add_section()

    # Refusal rate (for unanswerable questions, higher is better)
    table.add_row(
        "Refusal Rate",
        f"{hallucination_metrics['refusal_rate']:.2%}",
        ">50%",
        _get_status(hallucination_metrics['refusal_rate'], 0.5, higher_better=True),
    )

    # Hallucination rate (lower is better)
    table.add_row(
        "Hallucination Rate",
        f"{hallucination_metrics['hallucination_rate']:.2%}",
        "<30%",
        _get_status(1 - hallucination_metrics['hallucination_rate'], 0.7),
    )

    # Factuality score
    table.add_row(
        "Factuality Score",
        f"{hallucination_metrics['factuality_score']:.3f}",
        ">0.7",
        _get_status(hallucination_metrics['factuality_score'], 0.7),
    )

    # Attribution score
    table.add_row(
        "Attribution Score",
        f"{hallucination_metrics['attribution_score']:.3f}",
        ">0.7",
        _get_status(hallucination_metrics['attribution_score'], 0.7),
    )

    console.print(table)

    # Performance metrics (with fallback)
    console.print("\n[bold]Performance Metrics:[/bold]")
    try:
        base_metrics = parser.get_metrics()
        console.print(f"  Total Cost: ${base_metrics['total_cost']:.6f}")
        console.print(f"  Avg Latency: {base_metrics['avg_latency_ms']:.1f}ms")
    except Exception:
        console.print("  (Performance metrics not available)")

    # Interpretation
    console.print("\n[bold]Interpretation:[/bold]")
    if hallucination_metrics['hallucination_rate'] < 0.3:
        console.print("  [green]Low hallucination rate[/green] - Model handles uncertainty well")
    elif hallucination_metrics['hallucination_rate'] < 0.5:
        console.print("  [yellow]Moderate hallucination rate[/yellow] - Some room for improvement")
    else:
        console.print("  [red]High hallucination rate[/red] - Consider adding uncertainty prompts")


@beartype
def _get_status(
    value: float,
    threshold: float,
    higher_better: bool = True,
) -> str:
    """
    Get status string based on value and threshold.

    Args:
        value: The metric value.
        threshold: The threshold for passing.
        higher_better: Whether higher values are better.

    Returns:
        Status string with formatting.

    """
    if higher_better:
        passes = value >= threshold
    else:
        passes = value <= threshold

    if passes:
        return "[green]GOOD[/green]"
    elif (higher_better and value >= threshold * 0.8) or (not higher_better and value <= threshold * 1.2):
        return "[yellow]OK[/yellow]"
    else:
        return "[red]POOR[/red]"


@beartype
def log_to_mlflow(
    results: dict[str, Any],
    parser: PromptfooResultParser,
    hallucination_metrics: dict[str, float],
) -> str | None:
    """
    Log hallucination evaluation results to MLflow.

    Args:
        results: Raw promptfoo results dictionary.
        parser: PromptfooResultParser with parsed results.
        hallucination_metrics: Hallucination-specific metrics.

    Returns:
        MLflow run ID if logging succeeds, None otherwise.

    """
    try:
        manager = MLflowExperimentManager(EXPERIMENT_NAME)
        experiment_id = manager.get_or_create_experiment()

        console.print(f"\n[cyan]MLflow experiment:[/cyan] {EXPERIMENT_NAME}")
        console.print(f"[dim]Experiment ID:[/dim] {experiment_id}")

        with manager.run_experiment(run_name="hallucination-prevention-eval") as run:
            # Log base metrics
            base_metrics = parser.get_metrics()
            manager.log_metrics(base_metrics)

            # Log hallucination-specific metrics
            manager.log_metrics(hallucination_metrics)

            # Log parameters
            params = {
                "model": "glm-5",
                "test_count": str(len(results.get("results", []))),
                "focus": "hallucination_prevention",
            }
            manager.log_params(params)

            # Log tags
            tags = {
                "evaluation_type": "hallucination",
                "framework": "promptfoo",
            }
            mlflow.set_tags(tags)

            # Log results artifact
            output_dir = get_promptfoo_output_dir()
            results_path = output_dir / OUTPUT_FILE
            if results_path.exists():
                manager.log_artifact(results_path)

            # Log summary
            summary = (
                f"Hallucination Prevention Summary\n"
                f"{'=' * 40}\n"
                f"Pass Rate: {base_metrics['pass_rate']:.2%}\n"
                f"Refusal Rate: {hallucination_metrics['refusal_rate']:.2%}\n"
                f"Hallucination Rate: {hallucination_metrics['hallucination_rate']:.2%}\n"
                f"Factuality Score: {hallucination_metrics['factuality_score']:.3f}\n"
                f"Attribution Score: {hallucination_metrics['attribution_score']:.3f}\n"
                f"{'=' * 40}\n"
                f"Total Cost: ${base_metrics['total_cost']:.6f}\n"
            )
            manager.log_text(summary, "summary.txt")

        console.print(f"[green]Results logged to MLflow[/green]")
        console.print(f"[dim]Run ID:[/dim] {run.info.run_id}")

        return run.info.run_id

    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Could not log to MLflow: {e}")
        return None


@beartype
def main() -> None:
    """Run the hallucination prevention evaluation."""
    config_path = Path(__file__).parent / "prevent_hallucination.yaml"

    try:
        results = run_hallucination_evaluation(config_path)

        if results:
            parser = PromptfooResultParser(results)
            hallucination_metrics = calculate_hallucination_metrics(results)

            display_hallucination_results(parser, hallucination_metrics)

            log_to_mlflow(results, parser, hallucination_metrics)

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
