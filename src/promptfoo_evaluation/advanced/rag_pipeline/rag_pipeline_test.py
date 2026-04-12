"""
Python runner for RAG pipeline evaluation.

This script demonstrates how to evaluate RAG (Retrieval-Augmented Generation)
systems using promptfoo with context quality assertions. It logs metrics to
MLflow for experiment tracking.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Final

import mlflow
import requests
from beartype import beartype
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Load environment variables from .env file
# Use resolve() to get absolute path before navigating up
# Path: src/promptfoo_evaluation/advanced/rag_pipeline/ -> go up 5 levels to reach project root
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
EXPERIMENT_NAME: Final[str] = "promptfoo-advanced-rag"

# Output file path
OUTPUT_FILE: Final[str] = "rag_pipeline.json"

# Zhipu AI API endpoint
ZHIPU_API_URL: Final[str] = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


@beartype
def score_rag_response_with_glm5(
    context: str,
    query: str,
    response: str,
    api_key: str,
) -> dict[str, float] | None:
    """
    Score a RAG response using GLM-5 model.

    Args:
        context: The retrieved context.
        query: The user's query.
        response: The model's response.
        api_key: Zhipu AI API key.

    Returns:
        Dictionary with context_relevance, context_faithfulness, answer_relevance scores,
        or None if scoring fails.
    """
    scoring_prompt = f"""You are evaluating a RAG (Retrieval-Augmented Generation) system. Rate the following on a scale of 0.0 to 1.0:

CONTEXT RELEVANCE (0-1): How relevant is the retrieved context to answering the query? Does it contain the necessary information?

CONTEXT FAITHFULNESS (0-1): Does the answer stay grounded in the provided context without adding external information or hallucinating?

ANSWER RELEVANCE (0-1): How relevant and complete is the answer to the original query?

Context: {context}

Query: {query}

Response: {response}

Provide your response as a JSON with exactly these keys (no markdown, just raw JSON):
{{
  "context_relevance": <score between 0 and 1>,
  "context_faithfulness": <score between 0 and 1>,
  "answer_relevance": <score between 0 and 1>,
  "reason": "<brief explanation>"
}}"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": "glm-5",
        "messages": [
            {
                "role": "user",
                "content": scoring_prompt,
            }
        ],
        "temperature": 0,
    }

    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # Extract JSON from response (handle markdown code blocks)
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.rstrip("`").strip()

        scores = json.loads(content)
        return {
            "context_relevance": scores.get("context_relevance", 0.0),
            "context_faithfulness": scores.get("context_faithfulness", 0.0),
            "answer_relevance": scores.get("answer_relevance", 0.0),
        }

    except Exception as e:
        console.print(f"[yellow]Warning: Could not score response: {e}[/yellow]")
        return None


@beartype
def run_rag_evaluation(
    config_path: str | Path,
) -> dict[str, Any] | None:
    """
    Run RAG pipeline evaluation with promptfoo.

    Args:
        config_path: Path to the promptfoo YAML configuration file.

    Returns:
        Parsed results dictionary if evaluation succeeds, None otherwise.

    Raises:
        subprocess.CalledProcessError: If promptfoo evaluation fails.
        ValueError: If ZHIPU_API_KEY is not set.
        FileNotFoundError: If results file is not found.

    """
    # Validate environment
    zhipu_api_key = get_zhipu_api_key()
    validate_promptfoo_installation()

    console.print("\n[bold cyan]RAG Pipeline Evaluation[/bold cyan]")
    console.print("=" * 50)

    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Config: {config_path}")
    console.print("  Model: glm-5")
    console.print("  Metrics: context-relevance, context-faithfulness, context-recall, answer-relevance")
    console.print("  Tests: 10 RAG scenarios\n")

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

        # Load and return results
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
def calculate_rag_metrics(
    results: dict[str, Any],
    api_key: str,
) -> tuple[dict[str, float], list[dict[str, float]]]:
    """
    Calculate RAG-specific metrics using GLM-5 to score each response.

    Args:
        results: Raw promptfoo results dictionary.
        api_key: Zhipu AI API key for scoring.

    Returns:
        Tuple of (metrics dict, list of individual scores for each test).
    """
    metrics: dict[str, float] = {}
    scores_by_test: list[dict[str, float]] = []
    scores: dict[str, list[float]] = {
        "context_relevance": [],
        "context_faithfulness": [],
        "answer_relevance": [],
    }

    # Navigate the nested results structure
    results_dict = results.get("results", {})
    if isinstance(results_dict, dict):
        result_list = results_dict.get("results", [])
    else:
        result_list = []

    console.print("\n[bold cyan]Scoring RAG responses with GLM-5...[/bold cyan]")

    # Score each response using GLM-5
    for i, result in enumerate(result_list, 1):
        vars_data = result.get("vars", {})
        response_obj = result.get("response", {})
        response_text = response_obj.get("output", "")

        context = vars_data.get("context", "")
        query = vars_data.get("query", "")

        if not context or not query or not response_text:
            # Add empty score for this test
            scores_by_test.append({})
            continue

        # Call GLM-5 for scoring
        score_result = score_rag_response_with_glm5(context, query, response_text, api_key)

        if score_result:
            scores["context_relevance"].append(score_result["context_relevance"])
            scores["context_faithfulness"].append(score_result["context_faithfulness"])
            scores["answer_relevance"].append(score_result["answer_relevance"])
            scores_by_test.append(score_result)

            # Show individual score
            console.print(
                f"  [{i}/{len(result_list)}] "
                f"Rel: {score_result['context_relevance']:.2f} | "
                f"Faith: {score_result['context_faithfulness']:.2f} | "
                f"Ans: {score_result['answer_relevance']:.2f}"
            )
        else:
            scores_by_test.append({})

    # Calculate averages
    for key, score_list in scores.items():
        if score_list:
            avg_score = sum(score_list) / len(score_list)
            metrics[f"{key}_avg"] = avg_score
        else:
            metrics[f"{key}_avg"] = 0.0

    return metrics, scores_by_test


@beartype
def save_rag_scores_to_results(
    results: dict[str, Any],
    rag_scores_by_test: list[dict[str, float]],
    results_path: Path,
) -> None:
    """
    Save RAG scores to the results JSON file for display in promptfoo view.

    Args:
        results: Original promptfoo results dictionary.
        rag_scores_by_test: List of RAG scores for each test case.
        results_path: Path to the results JSON file.
    """
    # Navigate to the results list
    results_dict = results.get("results", {})
    if isinstance(results_dict, dict):
        result_list = results_dict.get("results", [])
    else:
        result_list = []

    # Add RAG scores as metadata to each result
    for i, result in enumerate(result_list):
        if i < len(rag_scores_by_test):
            rag_score = rag_scores_by_test[i]
            # Add to metadata
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"]["rag_scores"] = rag_score
            # Also add as a named score for promptfoo to display
            if "namedScores" not in result:
                result["namedScores"] = {}
            result["namedScores"]["context_relevance"] = rag_score.get("context_relevance", 0)
            result["namedScores"]["context_faithfulness"] = rag_score.get("context_faithfulness", 0)
            result["namedScores"]["answer_relevance"] = rag_score.get("answer_relevance", 0)

    # Save updated results
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)


@beartype
def display_rag_results(
    parser: PromptfooResultParser,
    rag_metrics: dict[str, float],
    base_metrics: dict[str, float] | None = None,
) -> None:
    """
    Display RAG evaluation results in a formatted table.

    Args:
        parser: PromptfooResultParser with parsed results.
        rag_metrics: RAG-specific metrics dictionary.
        base_metrics: Optional pre-calculated base metrics to avoid parser issues.

    """
    console.print("\n[bold]RAG Evaluation Results:[/bold]\n")

    # Create results table
    table = Table(title="RAG Quality Metrics", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Score", style="green", width=15)
    table.add_column("Status", width=15)

    # Use provided base_metrics or try to get from parser
    if base_metrics:
        pass_rate = base_metrics.get('pass_rate', 0)
        avg_score = base_metrics.get('average_score', 0)
        total_cost = base_metrics.get('total_cost', 0)
        avg_latency_ms = base_metrics.get('avg_latency_ms', 0)
        total_tokens = base_metrics.get('total_tokens', 0)
    else:
        try:
            base_metrics_dict = parser.get_metrics()
            pass_rate = base_metrics_dict.get('pass_rate', 0)
            avg_score = base_metrics_dict.get('average_score', 0)
            total_cost = base_metrics_dict.get('total_cost', 0)
            avg_latency_ms = base_metrics_dict.get('avg_latency_ms', 0)
            total_tokens = base_metrics_dict.get('total_tokens', 0)
        except Exception:
            pass_rate = 0
            avg_score = 0
            total_cost = 0
            avg_latency_ms = 0
            total_tokens = 0

    table.add_row("Pass Rate", f"{pass_rate:.2%}", _get_status(pass_rate, 0.7))
    table.add_row("Average Score", f"{avg_score:.3f}", _get_status(avg_score, 0.7))

    table.add_section()

    # RAG-specific metrics
    table.add_row("Context Relevance", f"{rag_metrics.get('context_relevance_avg', 0):.3f}", _get_status(rag_metrics.get('context_relevance_avg', 0), 0.7))
    table.add_row("Context Faithfulness", f"{rag_metrics.get('context_faithfulness_avg', 0):.3f}", _get_status(rag_metrics.get('context_faithfulness_avg', 0), 0.6))
    table.add_row("Context Recall", f"{rag_metrics.get('context_recall_avg', 0):.3f}", _get_status(rag_metrics.get('context_recall_avg', 0), 0.7))
    table.add_row("Answer Relevance", f"{rag_metrics.get('answer_relevance_avg', 0):.3f}", _get_status(rag_metrics.get('answer_relevance_avg', 0), 0.7))

    console.print(table)

    # Performance metrics
    console.print("\n[bold]Performance Metrics:[/bold]")
    console.print(f"  Total Cost: ${total_cost:.6f}")
    console.print(f"  Avg Latency: {avg_latency_ms:.1f}ms")
    console.print(f"  Total Tokens: {int(total_tokens)}")


@beartype
def calculate_base_metrics(
    results: dict[str, Any],
) -> dict[str, float]:
    """
    Calculate base metrics directly from promptfoo JSON results.

    Args:
        results: Raw promptfoo results dictionary.

    Returns:
        Dictionary with pass_rate, average_score, total_cost, avg_latency_ms, total_tokens.
    """
    metrics: dict[str, float] = {
        "pass_rate": 0.0,
        "average_score": 0.0,
        "total_cost": 0.0,
        "avg_latency_ms": 0.0,
        "total_tokens": 0,
    }

    # Navigate the nested results structure
    results_dict = results.get("results", {})
    if isinstance(results_dict, dict):
        result_list = results_dict.get("results", [])
        stats = results_dict.get("stats", {})
    else:
        result_list = []
        stats = {}

    # Calculate pass rate and average score
    total_tests = len(result_list)
    passed_tests = 0
    total_score = 0
    latencies = []

    for result in result_list:
        score = result.get("score", 0)
        total_score += score
        if result.get("success", False):
            passed_tests += 1

        latency = result.get("latencyMs", 0)
        if latency:
            latencies.append(latency)

    if total_tests > 0:
        metrics["pass_rate"] = passed_tests / total_tests
        metrics["average_score"] = total_score / total_tests

    if latencies:
        metrics["avg_latency_ms"] = sum(latencies) / len(latencies)

    # Get stats
    metrics["total_cost"] = stats.get("totalCost", 0.0)
    metrics["total_tokens"] = float(stats.get("totalTokens", 0))

    return metrics


@beartype
def _get_status(value: float | int, threshold: float) -> str:
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
    elif value >= threshold * 0.8:
        return "[yellow]OK[/yellow]"
    else:
        return "[red]FAIL[/red]"


@beartype
def log_to_mlflow(
    results: dict[str, Any],
    parser: PromptfooResultParser,
    rag_metrics: dict[str, float],
    base_metrics: dict[str, float] | None = None,
) -> str | None:
    """
    Log RAG evaluation results to MLflow.

    Args:
        results: Raw promptfoo results dictionary.
        parser: PromptfooResultParser with parsed results.
        rag_metrics: RAG-specific metrics dictionary.
        base_metrics: Optional pre-calculated base metrics.

    Returns:
        MLflow run ID if logging succeeds, None otherwise.

    """
    try:
        # Create MLflow manager
        manager = MLflowExperimentManager(EXPERIMENT_NAME)
        experiment_id = manager.get_or_create_experiment()

        console.print(f"\n[cyan]MLflow experiment:[/cyan] {EXPERIMENT_NAME}")
        console.print(f"[dim]Experiment ID:[/dim] {experiment_id}")

        # Start run
        with manager.run_experiment(run_name="rag-pipeline-eval") as run:
            # Log base metrics (use provided or try to get from parser)
            if base_metrics:
                metrics_to_log = base_metrics
            else:
                try:
                    metrics_to_log = parser.get_metrics()
                except Exception:
                    metrics_to_log = {
                        "pass_rate": 0,
                        "average_score": 0,
                        "total_tokens": 0,
                        "total_cost": 0,
                        "avg_latency_ms": 0,
                    }
            manager.log_metrics(metrics_to_log)

            # Log RAG-specific metrics
            manager.log_metrics(rag_metrics)

            # Log parameters
            results_dict = results.get("results", {})
            if isinstance(results_dict, dict):
                test_count = len(results_dict.get("results", []))
            else:
                test_count = 0

            params = {
                "model": "glm-5",
                "test_count": str(test_count),
                "assertion_types": "contains,icontains,contains-any",
            }
            manager.log_params(params)

            # Log tags
            tags = {
                "evaluation_type": "rag",
                "domain": "tax_law",
                "framework": "promptfoo",
            }
            mlflow.set_tags(tags)

            # Log results as artifact
            output_dir = get_promptfoo_output_dir()
            results_path = output_dir / OUTPUT_FILE
            if results_path.exists():
                manager.log_artifact(results_path)

            # Log summary text
            summary = (
                f"RAG Pipeline Evaluation Summary\n"
                f"{'=' * 40}\n"
                f"Pass Rate: {metrics_to_log['pass_rate']:.2%}\n"
                f"Context Relevance: {rag_metrics.get('context_relevance_avg', 0):.3f}\n"
                f"Context Faithfulness: {rag_metrics.get('context_faithfulness_avg', 0):.3f}\n"
                f"Context Recall: {rag_metrics.get('context_recall_avg', 0):.3f}\n"
                f"Answer Relevance: {rag_metrics.get('answer_relevance_avg', 0):.3f}\n"
                f"{'=' * 40}\n"
                f"Total Cost: ${metrics_to_log['total_cost']:.6f}\n"
                f"Avg Latency: {metrics_to_log['avg_latency_ms']:.1f}ms\n"
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
    """Run the RAG pipeline evaluation."""
    config_path = Path(__file__).parent / "rag_pipeline.yaml"

    try:
        # Get API key for scoring
        zhipu_api_key = get_zhipu_api_key()

        # Run evaluation
        results = run_rag_evaluation(config_path)

        if results:
            # NOTE: PromptfooResultParser expects the nested results dict, not the full JSON
            # The JSON structure is: {results: {results: [...], stats: {...}}, ...}
            nested_results = results.get("results", results)
            # Parse results
            parser = PromptfooResultParser(nested_results)

            # Calculate base metrics directly from JSON
            base_metrics = calculate_base_metrics(results)

            # Calculate RAG-specific metrics using GLM-5
            rag_metrics, scores_by_test = calculate_rag_metrics(results, zhipu_api_key)

            # Save RAG scores to results JSON for promptfoo view
            output_dir = get_promptfoo_output_dir()
            results_path = output_dir / OUTPUT_FILE
            save_rag_scores_to_results(results, scores_by_test, results_path)
            console.print("[green]RAG scores saved to results file[/green]")

            # Display results
            display_rag_results(parser, rag_metrics, base_metrics)

            # Log to MLflow
            log_to_mlflow(results, parser, rag_metrics, base_metrics)

            console.print("\n[green]Evaluation complete![/green]")
            console.print("\n[cyan]View results in web UI with RAG scores:[/cyan]")
            console.print("  npx promptfoo view")
            console.print("\n[cyan]View MLflow experiments:[/cyan]")
            console.print("  mlflow ui")

        else:
            console.print("[yellow]No results to display[/yellow]")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
