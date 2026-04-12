"""
Python runner for factuality evaluation.

This script evaluates the factual accuracy of LLM responses by comparing
against known ground truth, measuring factuality scores across different
information types.
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
# Path: src/promptfoo_evaluation/advanced/evaluating_factuality/ -> go up 5 levels to reach project root
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
EXPERIMENT_NAME: Final[str] = "promptfoo-advanced-factuality"

# Output file path
OUTPUT_FILE: Final[str] = "factuality.json"


@beartype
def run_factuality_evaluation(
    config_path: str | Path,
) -> dict[str, Any] | None:
    """
    Run factuality evaluation with promptfoo.

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

    console.print("\n[bold cyan]Factuality Evaluation[/bold cyan]")
    console.print("=" * 40)

    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Config: {config_path}")
    console.print("  Model: glm-5")
    console.print("  Tests: 12 factuality questions")
    console.print("  Categories: Dates, numbers, entities, relationships\n")

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
def calculate_factuality_metrics(
    results: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate factuality-specific metrics from promptfoo results.

    Args:
        results: Raw promptfoo results dictionary.

    Returns:
        Dictionary with factuality metrics including overall score,
        category breakdowns, and error analysis.

    """
    metrics: dict[str, Any] = {
        "overall_factuality_score": 0.0,
        "extraction_accuracy": 0.0,
        "verification_rate": 0.0,
        "category_scores": {
            "dates": {"correct": 0, "total": 0},
            "numbers": {"correct": 0, "total": 0},
            "entities": {"correct": 0, "total": 0},
            "relationships": {"correct": 0, "total": 0},
        },
    }

    # Category keywords for classification
    category_keywords = {
        "dates": ["year", "when", "date", "born", "died", "ended", "began"],
        "numbers": ["how many", "much", "speed", "rate", "percentage", "temperature"],
        "entities": ["who", "what", "where", "which", "capital", "country", "city"],
        "relationships": ["wrote", "painted", "discovered", "invented"],
    }

    total_tests = 0
    correct_facts = 0
    extraction_count = 0
    verification_count = 0

    # Navigate the nested results structure
    results_dict = results.get("results", {})
    if isinstance(results_dict, dict):
        result_list = results_dict.get("results", [])
    else:
        result_list = []

    for result in result_list:
        test_case = result.get("testCase", {})
        description = test_case.get("description", "").lower()

        # Categorize the test
        category = "entities"  # default
        for cat, keywords in category_keywords.items():
            if any(keyword in description for keyword in keywords):
                category = cat
                break

        total_tests += 1
        passed = result.get("success", False)
        grading_result = result.get("gradingResult", {})

        # Update category scores
        metrics["category_scores"][category]["total"] += 1
        if passed:
            metrics["category_scores"][category]["correct"] += 1
            correct_facts += 1

        # Check for extraction (fact extraction from response)
        if isinstance(grading_result, dict):
            component_results = grading_result.get("componentResults", [])
            for component in component_results:
                if component.get("pass", False):
                    extraction_count += 1
                verification_count += 1

    # Calculate overall metrics
    if total_tests > 0:
        metrics["overall_factuality_score"] = correct_facts / total_tests

    if verification_count > 0:
        metrics["extraction_accuracy"] = extraction_count / verification_count
        metrics["verification_rate"] = verification_count / total_tests

    # Calculate category percentages
    for category in metrics["category_scores"]:
        cat_data = metrics["category_scores"][category]
        if cat_data["total"] > 0:
            cat_data["percentage"] = cat_data["correct"] / cat_data["total"]
        else:
            cat_data["percentage"] = 0.0

    return metrics


@beartype
def display_factuality_results(
    parser: PromptfooResultParser,
    factuality_metrics: dict[str, Any],
) -> None:
    """
    Display factuality evaluation results in formatted tables.

    Args:
        parser: PromptfooResultParser with parsed results.
        factuality_metrics: Factuality-specific metrics.

    """
    console.print("\n[bold]Factuality Evaluation Results:[/bold]\n")

    # Overall metrics table
    overall_table = Table(title="Overall Factuality Metrics", show_header=True, header_style="bold cyan")
    overall_table.add_column("Metric", style="cyan", width=30)
    overall_table.add_column("Score", style="green", width=15)
    overall_table.add_column("Target", width=15)
    overall_table.add_column("Status", width=15)

    # Try to get base metrics, with fallback
    try:
        base_metrics = parser.get_metrics()
        pass_rate = base_metrics['pass_rate']
    except Exception:
        pass_rate = factuality_metrics.get('overall_factuality_score', 0.0)

    overall_table.add_row(
        "Pass Rate",
        f"{pass_rate:.2%}",
        ">80%",
        _get_status(pass_rate, 0.8),
    )

    overall_table.add_row(
        "Factuality Score",
        f"{factuality_metrics['overall_factuality_score']:.3f}",
        ">0.8",
        _get_status(factuality_metrics['overall_factuality_score'], 0.8),
    )

    overall_table.add_row(
        "Extraction Accuracy",
        f"{factuality_metrics['extraction_accuracy']:.3f}",
        ">0.8",
        _get_status(factuality_metrics['extraction_accuracy'], 0.8),
    )

    overall_table.add_row(
        "Verification Rate",
        f"{factuality_metrics['verification_rate']:.3f}",
        ">0.9",
        _get_status(factuality_metrics['verification_rate'], 0.9),
    )

    console.print(overall_table)

    # Category breakdown table
    console.print("\n[bold]Category Breakdown:[/bold]\n")

    category_table = Table(title="Factuality by Information Type", show_header=True, header_style="bold cyan")
    category_table.add_column("Category", style="cyan", width=20)
    category_table.add_column("Correct", style="green", width=10)
    category_table.add_column("Total", width=10)
    category_table.add_column("Accuracy", width=15)
    category_table.add_column("Status", width=15)

    for category, data in factuality_metrics["category_scores"].items():
        if data["total"] > 0:
            category_table.add_row(
                category.title(),
                str(data["correct"]),
                str(data["total"]),
                f"{data['percentage']:.1%}",
                _get_status(data['percentage'], 0.8),
            )

    console.print(category_table)

    # Performance metrics (with fallback)
    console.print("\n[bold]Performance Metrics:[/bold]")
    try:
        base_metrics = parser.get_metrics()
        console.print(f"  Total Cost: ${base_metrics['total_cost']:.6f}")
        console.print(f"  Avg Latency: {base_metrics['avg_latency_ms']:.1f}ms")
    except Exception:
        console.print("  (Performance metrics not available)")

    # Recommendations
    console.print("\n[bold]Analysis:[/bold]")

    # Find weakest category
    categories_with_data = [
        (cat, data["percentage"])
        for cat, data in factuality_metrics["category_scores"].items()
        if data["total"] > 0
    ]
    if categories_with_data:
        weakest_cat = min(categories_with_data, key=lambda x: x[1])

    if weakest_cat[1] < 0.8:
        console.print(f"  [yellow]Focus area:[/yellow] {weakest_cat[0].title()} factuality ({weakest_cat[1]:.1%})")
    else:
        console.print("  [green]All categories performing well[/green]")


@beartype
def _get_status(value: float, threshold: float) -> str:
    """
    Get status string based on value and threshold.

    Args:
        value: The metric value.
        threshold: The threshold for passing.

    Returns:
        Status string with formatting.

    """
    if value >= threshold:
        return "[green]PASS[/green]"
    elif value >= threshold * 0.9:
        return "[yellow]OK[/yellow]"
    else:
        return "[red]FAIL[/red]"


@beartype
def log_to_mlflow(
    results: dict[str, Any],
    parser: PromptfooResultParser,
    factuality_metrics: dict[str, Any],
) -> str | None:
    """
    Log factuality evaluation results to MLflow.

    Args:
        results: Raw promptfoo results dictionary.
        parser: PromptfooResultParser with parsed results.
        factuality_metrics: Factuality-specific metrics.

    Returns:
        MLflow run ID if logging succeeds, None otherwise.

    """
    try:
        manager = MLflowExperimentManager(EXPERIMENT_NAME)
        experiment_id = manager.get_or_create_experiment()

        console.print(f"\n[cyan]MLflow experiment:[/cyan] {EXPERIMENT_NAME}")
        console.print(f"[dim]Experiment ID:[/dim] {experiment_id}")

        with manager.run_experiment(run_name="factuality-eval") as run:
            # Log base metrics
            base_metrics = parser.get_metrics()
            manager.log_metrics(base_metrics)

            # Log factuality-specific metrics
            flat_metrics = {
                "overall_factuality_score": factuality_metrics["overall_factuality_score"],
                "extraction_accuracy": factuality_metrics["extraction_accuracy"],
                "verification_rate": factuality_metrics["verification_rate"],
            }

            # Add category scores
            for category, data in factuality_metrics["category_scores"].items():
                if data["total"] > 0:
                    flat_metrics[f"{category}_accuracy"] = data["percentage"]

            manager.log_metrics(flat_metrics)

            # Log parameters
            params = {
                "model": "glm-5",
                "test_count": str(len(results.get("results", []))),
                "categories": "dates,numbers,entities,relationships",
            }
            manager.log_params(params)

            # Log tags
            tags = {
                "evaluation_type": "factuality",
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
                "Factuality Evaluation Summary",
                "=" * 40,
                f"Overall Factuality: {factuality_metrics['overall_factuality_score']:.2%}",
                f"Extraction Accuracy: {factuality_metrics['extraction_accuracy']:.2%}",
                f"Verification Rate: {factuality_metrics['verification_rate']:.2%}",
                "",
                "Category Breakdown:",
            ]

            for category, data in factuality_metrics["category_scores"].items():
                if data["total"] > 0:
                    summary_lines.append(
                        f"  {category.title()}: {data['correct']}/{data['total']} ({data['percentage']:.1%})"
                    )

            summary_lines.extend([
                "",
                f"Total Cost: ${base_metrics['total_cost']:.6f}",
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
    """Run the factuality evaluation."""
    config_path = Path(__file__).parent / "factuality.yaml"

    try:
        results = run_factuality_evaluation(config_path)

        if results:
            parser = PromptfooResultParser(results)
            factuality_metrics = calculate_factuality_metrics(results)

            display_factuality_results(parser, factuality_metrics)

            log_to_mlflow(results, parser, factuality_metrics)

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
