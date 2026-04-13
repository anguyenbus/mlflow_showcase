"""
MLflow integration for promptfoo evaluation results.

This module provides utilities for parsing promptfoo evaluation outputs
and logging them to MLflow for centralized experiment tracking.

Extended with support for advanced topic-specific metrics including:
- RAG metrics: context relevance, faithfulness, recall
- Hallucination metrics: refusal rate, hallucination rate
- Temperature metrics: per-temperature pass rates
- Factuality metrics: category-specific accuracy
"""

import json
from pathlib import Path
from typing import Any, Final

import mlflow
from beartype import beartype
from rich.console import Console

# Initialize rich console
console: Final[Console] = Console()

# Default experiment name
DEFAULT_EXPERIMENT_NAME: Final[str] = "promptfoo-evaluation"

# Advanced experiment names
ADVANCED_EXPERIMENTS: Final[dict[str, str]] = {
    "rag_pipeline": "promptfoo-advanced-rag",
    "prevent_hallucination": "promptfoo-advanced-hallucination",
    "choosing_right_temperature": "promptfoo-advanced-temperature",
    "evaluating_factuality": "promptfoo-advanced-factuality",
    "redteam": "promptfoo-advanced-redteam",
}


@beartype
class PromptfooResultParser:
    """
    Parser for promptfoo evaluation result JSON.

    Extracts metrics, pass rates, costs, and latency from promptfoo outputs.

    Attributes:
        results: Raw promptfoo results dictionary.

    Example:
        >>> parser = PromptfooResultParser(promptfoo_results)
        >>> pass_rate = parser.get_pass_rate()
        >>> metrics = parser.get_metrics()

    """

    __slots__ = ("results",)

    def __init__(self, results: dict[str, Any]) -> None:
        """
        Initialize the parser with promptfoo results.

        Args:
            results: Raw results dictionary from promptfoo eval output.

        """
        self.results = results

    def get_pass_rate(self) -> float:
        """
        Calculate the overall pass rate from results.

        Returns:
            Pass rate as a float between 0 and 1.

        """
        total_tests = 0
        passed_tests = 0

        for result in self.results.get("results", []):
            for output in result.get("outputs", []):
                total_tests += 1
                if output.get("pass", False):
                    passed_tests += 1

        if total_tests == 0:
            return 0.0

        return passed_tests / total_tests

    def get_average_score(self) -> float:
        """
        Calculate average score from all results.

        Returns:
            Average score across all test outputs.

        """
        scores = []

        for result in self.results.get("results", []):
            for output in result.get("outputs", []):
                if "score" in output:
                    scores.append(output["score"])

        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    def get_total_tokens(self) -> int:
        """
        Get total tokens used in evaluation.

        Returns:
            Total token count from stats.

        """
        stats = self.results.get("stats", {})
        return stats.get("totalTokens", 0)

    def get_total_cost(self) -> float:
        """
        Get total cost of evaluation.

        Returns:
            Total cost from stats.

        """
        stats = self.results.get("stats", {})
        return stats.get("totalCost", 0.0)

    def get_latency_stats(self) -> dict[str, float]:
        """
        Calculate latency statistics from results.

        Returns:
            Dictionary with avg_latency_ms, min_latency_ms, max_latency_ms.

        """
        latencies = []

        for result in self.results.get("results", []):
            for output in result.get("outputs", []):
                if "latencyMs" in output:
                    latencies.append(output["latencyMs"])

        if not latencies:
            return {
                "avg_latency_ms": 0.0,
                "min_latency_ms": 0.0,
                "max_latency_ms": 0.0,
            }

        return {
            "avg_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
        }

    def get_metrics(self) -> dict[str, float]:
        """
        Extract all metrics as a dictionary for MLflow logging.

        Returns:
            Dictionary with pass_rate, average_score, total_tokens,
            total_cost, and latency stats.

        """
        metrics = {
            "pass_rate": self.get_pass_rate(),
            "average_score": self.get_average_score(),
            "total_tokens": float(self.get_total_tokens()),
            "total_cost": self.get_total_cost(),
        }

        # Add latency stats
        latency_stats = self.get_latency_stats()
        metrics.update(latency_stats)

        return metrics

    def get_assertion_scores(self, assertion_type: str) -> list[float]:
        """
        Extract scores for a specific assertion type.

        Args:
            assertion_type: Type of assertion to extract scores for
                (e.g., "context-relevance", "factuality").

        Returns:
            List of scores for the specified assertion type.

        """
        scores: list[float] = []

        for result in self.results.get("results", []):
            for output in result.get("outputs", []):
                grading_result = output.get("gradingResult", {})
                if isinstance(grading_result, dict):
                    for key, value in grading_result.items():
                        if assertion_type.lower() in key.lower():
                            if isinstance(value, dict):
                                score = value.get("score", 0.0)
                                if score > 0:
                                    scores.append(score)
                            elif isinstance(value, (float, int)):
                                scores.append(float(value))

        return scores

    def get_scenario_metrics(self) -> dict[str, dict[str, float]]:
        """
        Extract metrics grouped by scenario (useful for temperature comparisons).

        Returns:
            Dictionary mapping scenario descriptions to their metrics.

        """
        scenario_metrics: dict[str, dict[str, float]] = {}

        for result in self.results.get("results", []):
            scenario = result.get("description", "unknown")
            outputs = result.get("outputs", [])

            passed = sum(1 for o in outputs if o.get("pass", False))
            total = len(outputs)
            pass_rate = passed / total if total > 0 else 0.0

            scores = [o.get("score", 0.0) for o in outputs if "score" in o]
            avg_score = sum(scores) / len(scores) if scores else 0.0

            scenario_metrics[scenario] = {
                "pass_rate": pass_rate,
                "avg_score": avg_score,
                "total": total,
            }

        return scenario_metrics


@beartype
class MLflowExperimentManager:
    """
    Manager for MLflow experiment operations.

    Handles experiment creation, retrieval, and run management.

    Attributes:
        experiment_name: Name of the MLflow experiment.

    Example:
        >>> manager = MLflowExperimentManager("promptfoo-basics")
        >>> experiment_id = manager.get_or_create_experiment()
        >>> with manager.run_experiment():
        ...     # Log metrics and artifacts
        ...     manager.log_metrics({"pass_rate": 0.9})

    """

    __slots__ = ("experiment_name",)

    def __init__(self, experiment_name: str = DEFAULT_EXPERIMENT_NAME) -> None:
        """
        Initialize the MLflow experiment manager.

        Args:
            experiment_name: Name for the MLflow experiment.

        """
        self.experiment_name = experiment_name

    def create_experiment(self, tags: dict[str, str] | None = None) -> str:
        """
        Create a new MLflow experiment.

        Args:
            tags: Optional tags to add to the experiment.

        Returns:
            The experiment ID.

        """
        # Default tags for promptfoo experiments
        default_tags = {"framework": "promptfoo"}
        if tags:
            default_tags.update(tags)

        experiment_id = mlflow.create_experiment(self.experiment_name, tags=default_tags)

        console.print(f"[green]Created MLflow experiment:[/green] {self.experiment_name}")

        return experiment_id

    def get_or_create_experiment(self) -> str:
        """
        Get existing experiment or create new one.

        Returns:
            The experiment ID.

        """
        experiment = mlflow.get_experiment_by_name(self.experiment_name)

        if experiment is not None:
            return experiment.experiment_id

        return self.create_experiment()

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        """
        Log metrics to current MLflow run.

        Args:
            metrics: Dictionary of metric names to values.
            step: Optional step number for time-series metrics.

        """
        mlflow.log_metrics(metrics, step=step)

    def log_params(self, params: dict[str, str]) -> None:
        """
        Log parameters to current MLflow run.

        Args:
            params: Dictionary of parameter names to values.

        """
        mlflow.log_params(params)

    def log_artifact(self, artifact_path: Path | str) -> None:
        """
        Log an artifact file to current MLflow run.

        Args:
            artifact_path: Path to the artifact file.

        """
        mlflow.log_artifact(str(artifact_path))

    def log_text(self, text: str, artifact_file: str) -> None:
        """
        Log text as an artifact file.

        Args:
            text: Text content to log.
            artifact_file: Filename for the artifact.

        """
        mlflow.log_text(text, artifact_file)

    def run_experiment(self, run_name: str | None = None):
        """
        Context manager for an MLflow run.

        Args:
            run_name: Optional name for the run.

        Yields:
            The active MLflow run object.

        """
        return mlflow.start_run(run_name=run_name)


@beartype
def get_advanced_experiment_name(topic: str) -> str:
    """
    Get the MLflow experiment name for an advanced topic.

    Args:
        topic: Name of the advanced topic.

    Returns:
        MLflow experiment name for the topic.

    Example:
        >>> get_advanced_experiment_name("rag_pipeline")
        'promptfoo-advanced-rag'

    """
    return ADVANCED_EXPERIMENTS.get(topic, f"promptfoo-advanced-{topic}")


@beartype
def parse_promptfoo_results(results: dict[str, Any] | Path | str) -> PromptfooResultParser:
    """
    Parse promptfoo results from dict or file path.

    Args:
        results: Either a results dict or path to JSON file.

    Returns:
        PromptfooResultParser instance for accessing metrics.

    Example:
        >>> parser = parse_promptfoo_results("eval_results.json")
        >>> pass_rate = parser.get_pass_rate()

    """
    if isinstance(results, (Path, str)):
        with open(results) as f:
            results = json.load(f)

    return PromptfooResultParser(results)


@beartype
def log_promptfoo_run_to_mlflow(
    results: dict[str, Any] | Path | str,
    experiment_name: str = DEFAULT_EXPERIMENT_NAME,
    run_name: str | None = None,
    tags: dict[str, str] | None = None,
) -> str:
    """
    Log a promptfoo evaluation run to MLflow.

    This is a convenience function that combines parsing and logging.

    Args:
        results: Promptfoo results dict or path to JSON file.
        experiment_name: MLflow experiment name.
        run_name: Optional name for the MLflow run.
        tags: Optional tags to add to the run.

    Returns:
        The MLflow run ID.

    Example:
        >>> run_id = log_promptfoo_run_to_mlflow(
        ...     results="eval_results.json",
        ...     experiment_name="promptfoo-basics",
        ...     run_name="simple-test"
        ... )

    """
    # Parse results
    parser = parse_promptfoo_results(results)
    metrics = parser.get_metrics()

    # Create manager and get/create experiment
    manager = MLflowExperimentManager(experiment_name)
    manager.get_or_create_experiment()

    # Start run and log everything
    with manager.run_experiment(run_name=run_name) as run:
        # Log metrics
        manager.log_metrics(metrics)

        # Log tags
        if tags:
            mlflow.set_tags(tags)

        # Log results as artifact if it's a file
        if isinstance(results, (Path, str)):
            manager.log_artifact(results)

        # Log summary text
        summary = (
            f"Promptfoo Evaluation Summary\n"
            f"Pass Rate: {metrics['pass_rate']:.2%}\n"
            f"Average Score: {metrics['average_score']:.3f}\n"
            f"Total Tokens: {int(metrics['total_tokens'])}\n"
            f"Total Cost: ${metrics['total_cost']:.6f}\n"
            f"Avg Latency: {metrics['avg_latency_ms']:.1f}ms"
        )
        manager.log_text(summary, "summary.txt")

    console.print(f"[green]Logged results to MLflow[/green] experiment: {experiment_name}")

    return run.info.run_id
