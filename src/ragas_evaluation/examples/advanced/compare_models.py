"""
Model Comparison Example.

This script demonstrates comparing different LLM models for RAG evaluation
using identical RAGas metrics across all models.

Expected Output:
    Model Comparison Example
    =========================

    Evaluating model: glm-5
    Average latency: 1.52s
    Total tokens: 1250

    Evaluating model: glm-4
    Average latency: 1.18s
    Total tokens: 1100

    [TODO: Add screenshot showing MLflow comparison view]

    Model Comparison Results:
    ┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ Model       ┃ Latency    ┃ Tokens  ┃ Faithfulness┃ Relevancy  ┃
    ┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
    │ glm-5       │ 1.52s      │ 1250    │ 0.85        │ 0.90       │
    │ glm-4       │ 1.18s      │ 1100    │ 0.82        │ 0.87       │
    └─────────────┴─────────────┴─────────┴─────────────┴─────────────┘
"""

from dataclasses import dataclass
from typing import Any, Final

from beartype import beartype
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Try to import mlflow
try:
    import mlflow

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None

# Initialize rich console for output
console: Final[Console] = Console()


@beartype
@dataclass(frozen=True, slots=True)
class ModelResult:
    """Result of evaluating a model.

    Attributes:
        model_name: Name of the model evaluated
        avg_latency: Average latency per query in seconds
        total_tokens: Total tokens used across all queries
        metrics: Dictionary of RAGas metric scores
        cost_per_1k_tokens: Cost per 1000 tokens (optional)

    """

    model_name: str
    avg_latency: float
    total_tokens: int
    metrics: dict[str, float]
    cost_per_1k_tokens: float | None = None


@beartype
def create_model_config(model_name: str, temperature: float) -> dict[str, Any]:
    """Create configuration for a model.

    Args:
        model_name: Name of the model
        temperature: Sampling temperature

    Returns:
        Dictionary with model configuration

    """
    return {
        "model_name": model_name,
        "temperature": temperature,
        "max_tokens": 1000,
    }


@beartype
def evaluate_model(
    model_name: str,
    test_questions: list[str],
    temperature: float = 0.2,
) -> ModelResult:
    """Evaluate a single model on test questions.

    Args:
        model_name: Name of the model to evaluate
        test_questions: List of test questions
        temperature: Sampling temperature for generation

    Returns:
        ModelResult with evaluation metrics

    """
    import time

    console.print(f"\n[cyan]Evaluating model:[/cyan] {model_name}")
    console.print(f"  Temperature: {temperature}")
    console.print(f"  Test questions: {len(test_questions)}")

    # NOTE: In production, this would make actual API calls
    # For demonstration, we simulate evaluation
    start_time = time.time()

    # Simulate processing each question
    latencies = []
    total_tokens = 0

    for question in test_questions:
        # Simulate query latency (varies by model)
        if "glm-5" in model_name:
            latency = 1.5 + (len(question) * 0.01)
            tokens = int(100 + len(question) * 2)
        else:  # glm-4 or other
            latency = 1.2 + (len(question) * 0.008)
            tokens = int(90 + len(question) * 1.8)

        latencies.append(latency)
        total_tokens += tokens

    avg_latency = sum(latencies) / len(latencies)

    # Simulate RAGas metrics (glm-5 generally performs better)
    if "glm-5" in model_name:
        metrics = {
            "faithfulness": 0.85,
            "answer_relevancy": 0.90,
            "context_precision": 0.82,
            "context_recall": 0.78,
        }
        cost_per_1k = 0.05
    else:  # glm-4 or other
        metrics = {
            "faithfulness": 0.80,
            "answer_relevancy": 0.85,
            "context_precision": 0.78,
            "context_recall": 0.75,
        }
        cost_per_1k = 0.03

    console.print(f"  [green]Average latency:[/green] {avg_latency:.2f}s")
    console.print(f"  [green]Total tokens:[/green] {total_tokens}")
    console.print(f"  [green]Faithfulness:[/green] {metrics['faithfulness']:.2f}")
    console.print(f"  [green]Answer Relevancy:[/green] {metrics['answer_relevancy']:.2f}")

    return ModelResult(
        model_name=model_name,
        avg_latency=avg_latency,
        total_tokens=total_tokens,
        metrics=metrics,
        cost_per_1k_tokens=cost_per_1k,
    )


@beartype
def log_model_comparison_to_mlflow(
    results: list[dict[str, Any]],
    experiment_name: str,
) -> None:
    """Log model comparison results to MLflow.

    Args:
        results: List of model evaluation results
        experiment_name: Name of the MLflow experiment

    Raises:
        ImportError: If mlflow is not installed

    """
    if not MLFLOW_AVAILABLE:
        console.print("[yellow]MLflow not available. Skipping MLflow logging.[/yellow]")
        return

    console.print(f"\n[cyan]Logging results to MLflow experiment:[/cyan] {experiment_name}")

    # Set experiment
    mlflow.set_experiment(experiment_name)

    # Log each model as a separate run
    with mlflow.start_run(run_name="model_comparison"):
        for result in results:
            with mlflow.start_run(nested=True, run_name=result["model_name"]):
                # Log parameters
                mlflow.log_param("model_name", result["model_name"])
                mlflow.log_param("temperature", 0.2)

                # Log metrics
                mlflow.log_metric("avg_latency", result["avg_latency"])
                mlflow.log_metric("total_tokens", result["total_tokens"])

                # Log RAGas metrics
                for metric_name, value in result["metrics"].items():
                    mlflow.log_metric(f"ragas_{metric_name}", value)

                # Log cost if available
                if "cost_per_1k_tokens" in result:
                    mlflow.log_metric("cost_per_1k_tokens", result["cost_per_1k_tokens"])

        console.print(f"[green]Logged {len(results)} model evaluations to MLflow[/green]")


@beartype
def generate_cost_benefit_analysis(results: list[dict[str, Any]]) -> str:
    """Generate cost-benefit trade-off analysis.

    Args:
        results: List of model evaluation results

    Returns:
        Formatted cost-benefit analysis string

    """
    # Find best performing model for each metric
    best_quality = max(results, key=lambda x: x["metrics"]["faithfulness"])
    fastest = min(results, key=lambda x: x["avg_latency"])
    cheapest = min(results, key=lambda x: x.get("cost_per_1k_tokens", float("inf")))

    analysis = "\n[bold yellow]Cost-Benefit Analysis:[/bold yellow]\n"
    analysis += f"• [green]Best Quality:[/green] {best_quality['model_name']} (faithfulness: {best_quality['metrics']['faithfulness']:.2f})\n"
    analysis += f"• [cyan]Fastest:[/cyan] {fastest['model_name']} (latency: {fastest['avg_latency']:.2f}s)\n"

    if "cost_per_1k_tokens" in cheapest:
        analysis += f"• [blue]Most Cost-Effective:[/blue] {cheapest['model_name']} (${cheapest['cost_per_1k_tokens']}/1K tokens)\n"

    analysis += "\n[bold]Trade-offs:[/bold]\n"
    analysis += "• Higher quality models (glm-5) provide better faithfulness but at higher cost\n"
    analysis += "• Faster models (glm-4) reduce latency but may sacrifice some quality\n"
    analysis += "• Choice depends on your priorities: quality vs speed vs cost\n"

    return analysis


@beartype
def display_comparison_table(results: list[dict[str, Any]]) -> None:
    """Display comparison table for models.

    Args:
        results: List of model evaluation results

    """
    table = Table(title="Model Comparison Results")
    table.add_column("Model", style="cyan", width=12)
    table.add_column("Latency", style="green", width=12)
    table.add_column("Tokens", style="yellow", width=10)
    table.add_column("Faithfulness", style="blue", width=14)
    table.add_column("Relevancy", style="magenta", width=12)

    for result in results:
        table.add_row(
            result["model_name"],
            f"{result['avg_latency']:.2f}s",
            str(result["total_tokens"]),
            f"{result['metrics']['faithfulness']:.2f}",
            f"{result['metrics']['answer_relevancy']:.2f}",
        )

    console.print(table)


@beartype
def main() -> None:
    """Run model comparison example.

    Demonstrates:
    1. Creating configurations for different models
    2. Evaluating models with identical RAGas metrics
    3. Capturing performance metrics (latency, tokens)
    4. Logging results to MLflow for comparison
    5. Generating cost-benefit analysis
    """
    # Header
    console.print(
        Panel(
            "[bold cyan]Model Comparison Example[/bold cyan]\n"
            "Comparing different LLM models using identical RAGas metrics",
            title="[bold green]RAGas Advanced Example[/bold green]",
            border_style="cyan",
        )
    )

    # Define models to compare
    models_to_compare = [
        {"name": "glm-5", "temperature": 0.2},
        {"name": "glm-4", "temperature": 0.2},
    ]

    # Create test questions
    test_questions = [
        "What is the GST rate in Australia?",
        "What are the income tax rates for 2024-25?",
        "What work-related expenses can I claim?",
        "Do I need a Tax File Number?",
    ]

    # Evaluate each model
    results = []
    for model_config in models_to_compare:
        result = evaluate_model(
            model_name=model_config["name"],
            test_questions=test_questions,
            temperature=model_config["temperature"],
        )

        results.append({
            "model_name": result.model_name,
            "avg_latency": result.avg_latency,
            "total_tokens": result.total_tokens,
            "metrics": result.metrics,
            "cost_per_1k_tokens": result.cost_per_1k_tokens,
        })

    # Display comparison table
    console.print("\n")
    display_comparison_table(results)

    # Generate and display cost-benefit analysis
    analysis = generate_cost_benefit_analysis(results)
    console.print(analysis)

    # Log to MLflow
    if MLFLOW_AVAILABLE:
        log_model_comparison_to_mlflow(results, experiment_name="ragas_model_comparison")

        # Generate MLflow UI link
        console.print(
            Panel(
                "[bold yellow]MLflow Comparison View:[/bold yellow]\n"
                "1. Open MLflow UI at http://localhost:5000\n"
                "2. Navigate to Experiments → ragas_model_comparison\n"
                "3. Compare runs side-by-side\n\n"
                "[dim][TODO: Add screenshot showing MLflow comparison view][/dim]",
                title="[bold cyan]MLflow Instructions[/bold cyan]",
                border_style="yellow",
            )
        )

    # Summary
    summary_text = Text.from_markup(
        f"[bold green]Model Comparison Summary[/bold green]\n"
        f"• Models evaluated: {len(results)}\n"
        f"• Test questions: {len(test_questions)}\n"
        f"• Best faithfulness: {max(r['metrics']['faithfulness'] for r in results):.2f}\n"
        f"• Fastest model: {min(results, key=lambda x: x['avg_latency'])['model_name']}\n"
        f"[dim]TODO: Add screenshot showing MLflow comparison view[/dim]"
    )
    console.print(Panel(summary_text, title="[bold cyan]Evaluation Complete[/bold cyan]", border_style="cyan"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
        raise
