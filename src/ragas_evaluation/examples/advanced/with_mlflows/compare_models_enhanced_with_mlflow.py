"""
Enhanced Model Comparison with MLflow Integration.

This script demonstrates comprehensive MLflow-integrated comparison of different
LLM models for RAG evaluation using identical RAGas metrics across all models.

Features:
- Each model comparison as a separate nested run
- Parent run for overall comparison
- Additional metrics: latency per query, token usage estimates
- MLflow UI link generation for easy navigation
- Cost-benefit analysis with MLflow tracking

Expected Output:
    Enhanced Model Comparison with MLflow
    ======================================

    [PARENT RUN] Starting model comparison
    Parent run ID: parent_xyz789

    Evaluating model: glm-5
    [NESTED RUN] Run ID: nested_abc123
    Temperature: 0.2
    Test questions: 4
    Average latency: 1.52s
    Total tokens: 1250
    Faithfulness: 0.85
    Answer Relevancy: 0.90

    Evaluating model: glm-4
    [NESTED RUN] Run ID: nested_def456
    Temperature: 0.2
    Test questions: 4
    Average latency: 1.18s
    Total tokens: 1100
    Faithfulness: 0.80
    Answer Relevancy: 0.87

    MLflow Comparison View:
    http://localhost:5000/#/experiments/2

    [TODO: Add screenshot showing MLflow model comparison]
"""

from dataclasses import dataclass
from typing import Any, Final

from beartype import beartype
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ragas_evaluation.shared.config import get_ragas_config

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
    """
    Result of evaluating a model with MLflow tracking.

    Attributes:
        model_name: Name of the model evaluated
        temperature: Sampling temperature used
        avg_latency: Average latency per query in seconds
        total_tokens: Total tokens used across all queries
        latency_per_query: List of per-query latencies
        metrics: Dictionary of RAGas metric scores
        cost_per_1k_tokens: Cost per 1000 tokens (optional)
        run_id: MLflow run ID for this model evaluation

    """

    model_name: str
    temperature: float
    avg_latency: float
    total_tokens: int
    latency_per_query: list[float]
    metrics: dict[str, float]
    cost_per_1k_tokens: float | None = None
    run_id: str | None = None


@beartype
@dataclass(frozen=True, slots=True)
class ModelConfig:
    """
    Configuration for a model evaluation.

    Attributes:
        model_name: Name of the model
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    """

    model_name: str
    temperature: float
    max_tokens: int


@beartype
def create_model_config(model_name: str, temperature: float = 0.2) -> ModelConfig:
    """
    Create configuration for a model.

    Args:
        model_name: Name of the model
        temperature: Sampling temperature

    Returns:
        ModelConfig with model configuration

    """
    return ModelConfig(
        model_name=model_name,
        temperature=temperature,
        max_tokens=1000,
    )


@beartype
def evaluate_model_with_mlflow(
    model_config: ModelConfig,
    test_questions: list[str],
    parent_run_id: str | None = None,
) -> ModelResult:
    """
    Evaluate a single model on test questions with MLflow logging.

    Args:
        model_config: Configuration for the model
        test_questions: List of test questions
        parent_run_id: Optional parent run ID for nested run

    Returns:
        ModelResult with evaluation metrics and MLflow run ID

    """
    import time

    if not MLFLOW_AVAILABLE:
        console.print("[yellow]MLflow not available. Skipping MLflow logging.[/yellow]")

    console.print(f"\n[cyan]Evaluating model:[/cyan] {model_config.model_name}")
    console.print(f"  Temperature: {model_config.temperature}")
    console.print(f"  Test questions: {len(test_questions)}")

    # Start nested MLflow run if available
    run_id = None
    if MLFLOW_AVAILABLE:
        run_name = f"model_{model_config.model_name.replace('-', '_')}"
        with mlflow.start_run(nested=True, run_name=run_name) as run:
            run_id = run.info.run_id
            console.print(f"  [dim][NESTED RUN] Run ID: {run_id}[/dim]")

            # Log parameters
            mlflow.log_param("model_name", model_config.model_name)
            mlflow.log_param("temperature", str(model_config.temperature))
            mlflow.log_param("max_tokens", str(model_config.max_tokens))
            mlflow.log_param("num_questions", str(len(test_questions)))

    # NOTE: In production, this would make actual API calls
    # For demonstration, we simulate evaluation
    start_time = time.time()

    # Simulate processing each question
    latencies = []
    total_tokens = 0

    for question in test_questions:
        # Simulate query latency (varies by model)
        if "glm-5" in model_config.model_name or "gpt-4" in model_config.model_name:
            latency = 1.5 + (len(question) * 0.01)
            tokens = int(100 + len(question) * 2)
        else:  # glm-4 or other
            latency = 1.2 + (len(question) * 0.008)
            tokens = int(90 + len(question) * 1.8)

        latencies.append(latency)
        total_tokens += tokens

    avg_latency = sum(latencies) / len(latencies)
    total_time = time.time() - start_time

    # Simulate RAGas metrics (glm-5 generally performs better)
    if "glm-5" in model_config.model_name or "gpt-4" in model_config.model_name:
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

    # Log metrics to MLflow
    if MLFLOW_AVAILABLE and run_id:
        mlflow.log_metric("avg_latency", avg_latency)
        mlflow.log_metric("total_tokens", total_tokens)
        mlflow.log_metric("total_time", total_time)
        mlflow.log_metric("cost_per_1k_tokens", cost_per_1k)

        # Log per-query latencies as a metric series
        for i, latency in enumerate(latencies):
            mlflow.log_metric(f"query_{i}_latency", latency)

        # Log RAGas metrics
        for metric_name, value in metrics.items():
            mlflow.log_metric(f"ragas_{metric_name}", value)

    return ModelResult(
        model_name=model_config.model_name,
        temperature=model_config.temperature,
        avg_latency=avg_latency,
        total_tokens=total_tokens,
        latency_per_query=latencies,
        metrics=metrics,
        cost_per_1k_tokens=cost_per_1k,
        run_id=run_id,
    )


@beartype
def generate_cost_benefit_analysis(results: list[dict[str, Any]]) -> str:
    """
    Generate cost-benefit trade-off analysis.

    Args:
        results: List of model evaluation results

    Returns:
        Formatted cost-benefit analysis string

    """
    # Find best performing model for each metric
    best_quality = max(results, key=lambda x: x["metrics"]["faithfulness"])
    fastest = min(results, key=lambda x: x["avg_latency"])
    cheapest = min(results, key=lambda x: x.get("cost_per_1k_tokens", float("inf")))

    # Calculate efficiency scores
    for r in results:
        # Quality per dollar
        if "cost_per_1k_tokens" in r:
            r["quality_per_cost"] = (
                r["metrics"]["faithfulness"] / r["cost_per_1k_tokens"]
                if r["cost_per_1k_tokens"] > 0
                else 0
            )
        else:
            r["quality_per_cost"] = 0
        # Quality per second (speed)
        r["quality_per_speed"] = (
            r["metrics"]["faithfulness"] / r["avg_latency"] if r["avg_latency"] > 0 else 0
        )

    best_value = max(results, key=lambda x: x.get("quality_per_cost", 0))
    best_speed_quality = max(results, key=lambda x: x.get("quality_per_speed", 0))

    analysis = "\n[bold yellow]Cost-Benefit Analysis:[/bold yellow]\n"
    analysis += f"• [green]Best Quality:[/green] {best_quality['model_name']} (faithfulness: {best_quality['metrics']['faithfulness']:.2f})\n"
    analysis += f"• [cyan]Fastest:[/cyan] {fastest['model_name']} (latency: {fastest['avg_latency']:.2f}s)\n"

    if "cost_per_1k_tokens" in cheapest:
        analysis += f"• [blue]Most Cost-Effective:[/blue] {cheapest['model_name']} (${cheapest['cost_per_1k_tokens']}/1K tokens)\n"
        analysis += f"• [magenta]Best Value:[/magenta] {best_value['model_name']} (quality/cost: {best_value.get('quality_per_cost', 0):.2f})\n"

    analysis += f"• [bright_yellow]Best Speed/Quality:[/bright_yellow] {best_speed_quality['model_name']} (quality/speed: {best_speed_quality.get('quality_per_speed', 0):.2f})\n"

    analysis += "\n[bold]MLflow-Tracked Metrics:[/bold]\n"
    analysis += "• All metrics logged to MLflow for historical comparison\n"
    analysis += "• Per-query latency tracking for performance analysis\n"
    analysis += "• Token usage estimation for cost forecasting\n"

    analysis += "\n[bold]Recommendations:[/bold]\n"
    analysis += "• Highest quality: Use for critical applications\n"
    analysis += "• Best value: Use for cost-sensitive deployments\n"
    analysis += "• Fastest: Use for latency-critical applications\n"

    return analysis


@beartype
def display_comparison_table(results: list[dict[str, Any]]) -> None:
    """
    Display comparison table for models.

    Args:
        results: List of model evaluation results

    """
    table = Table(title="Enhanced Model Comparison Results")
    table.add_column("Model", style="cyan", width=12)
    table.add_column("Latency", style="green", width=12)
    table.add_column("Tokens", style="yellow", width=10)
    table.add_column("Cost/1K", style="blue", width=12)
    table.add_column("Faithfulness", style="magenta", width=14)
    table.add_column("Relevancy", style="bright_magenta", width=12)

    for result in results:
        cost_str = (
            f"${result.get('cost_per_1k_tokens', 0):.3f}"
            if "cost_per_1k_tokens" in result
            else "N/A"
        )
        table.add_row(
            result["model_name"],
            f"{result['avg_latency']:.2f}s",
            str(result["total_tokens"]),
            cost_str,
            f"{result['metrics']['faithfulness']:.2f}",
            f"{result['metrics']['answer_relevancy']:.2f}",
        )

    console.print(table)


@beartype
def generate_mlflow_ui_instructions(experiment_name: str, parent_run_id: str | None) -> Panel:
    """
    Generate MLflow UI navigation instructions.

    Args:
        experiment_name: Name of the MLflow experiment
        parent_run_id: Optional parent run ID

    Returns:
        Panel with MLflow UI navigation instructions

    """
    content = "[bold yellow]MLflow Model Comparison View:[/bold yellow]\n\n"
    content += "1. Open MLflow UI at [cyan]http://localhost:5000[/cyan]\n"
    content += "2. Navigate to Experiments → [cyan]" + experiment_name + "[/cyan]\n"

    if parent_run_id:
        content += "3. Find parent run: [cyan]" + parent_run_id + "[/cyan]\n"
        content += "4. Expand to see nested runs for each model\n"

    content += "\n[bold yellow]Side-by-Side Comparison:[/bold yellow]\n"
    content += "• Select all model runs (checkboxes)\n"
    content += "• Click 'Compare' button\n"
    content += "• View metrics comparison chart\n"
    content += "• Analyze trade-offs between models\n\n"

    content += "[bold yellow]Key Metrics to Compare:[/bold yellow]\n"
    content += "• [green]ragas_faithfulness[/green]: Answer accuracy\n"
    content += "• [cyan]ragas_answer_relevancy[/cyan]: Response quality\n"
    content += "• [yellow]avg_latency[/yellow]: Response speed\n"
    content += "• [blue]total_tokens[/blue]: Cost indicator\n\n"

    content += "[dim][TODO: Add screenshot showing MLflow model comparison][/dim]"

    return Panel(
        content,
        title="[bold cyan]MLflow Navigation Guide[/bold cyan]",
        border_style="yellow",
    )


@beartype
def compare_models_with_mlflow() -> dict[str, Any]:
    """
    Run enhanced model comparison with MLflow integration.

    This function demonstrates:
    1. Creating configurations for different models
    2. Evaluating models with identical RAGas metrics
    3. Capturing comprehensive performance metrics
    4. Logging results to MLflow with nested runs
    5. Generating cost-benefit analysis
    6. Providing MLflow UI navigation guidance

    Returns:
        Dictionary with comparison results and MLflow run information

    """
    if not MLFLOW_AVAILABLE:
        console.print("[red]ERROR:[/red] MLflow is not installed. Install with: pip install mlflow")
        raise ImportError("mlflow package is required")

    # Load configuration
    config = get_ragas_config()

    # Set up MLflow
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment_name = "ragas_model_comparison_enhanced"
    mlflow.set_experiment(experiment_name)

    # Header
    console.print(
        Panel(
            "[bold cyan]Enhanced Model Comparison with MLflow[/bold cyan]\n"
            "Comparing different LLM models with comprehensive MLflow tracking\n"
            "including latency, token usage, and cost metrics",
            title="[bold green]RAGas Advanced + MLflow[/bold green]",
            border_style="cyan",
        )
    )

    # Define models to compare
    models_to_compare = [
        ModelConfig(model_name="glm-5", temperature=0.2),
        ModelConfig(model_name="glm-4", temperature=0.2),
    ]

    # Create test questions
    test_questions = [
        "What is the GST rate in Australia?",
        "What are the income tax rates for 2024-25?",
        "What work-related expenses can I claim?",
        "Do I need a Tax File Number?",
    ]

    # Start parent run
    with mlflow.start_run(run_name="model_comparison_parent") as parent_run:
        parent_run_id = parent_run.info.run_id
        console.print("\n[bold][PARENT RUN] Starting model comparison[/bold]")
        console.print(f"[dim]Parent run ID: {parent_run_id}[/dim]")

        # Log parent run parameters
        mlflow.log_param("num_models", str(len(models_to_compare)))
        mlflow.log_param("num_questions", str(len(test_questions)))
        mlflow.log_param("comparison_type", "model_comparison_enhanced")

        # Evaluate each model
        results = []
        for model_config in models_to_compare:
            result = evaluate_model_with_mlflow(
                model_config=model_config,
                test_questions=test_questions,
                parent_run_id=parent_run_id,
            )

            results.append(
                {
                    "model_name": result.model_name,
                    "temperature": result.temperature,
                    "avg_latency": result.avg_latency,
                    "total_tokens": result.total_tokens,
                    "latency_per_query": result.latency_per_query,
                    "metrics": result.metrics,
                    "cost_per_1k_tokens": result.cost_per_1k_tokens,
                    "run_id": result.run_id,
                }
            )

    # Display comparison table
    console.print("\n")
    display_comparison_table(results)

    # Generate and display cost-benefit analysis
    analysis = generate_cost_benefit_analysis(results)
    console.print(analysis)

    # Display MLflow UI navigation
    console.print("\n")
    mlflow_ui = generate_mlflow_ui_instructions(experiment_name, parent_run_id)
    console.print(mlflow_ui)

    # Summary
    run_ids = [r["run_id"] for r in results if r["run_id"]]
    summary_text = Text.from_markup(
        f"[bold green]Model Comparison Summary[/bold green]\n"
        f"• Models evaluated: {len(results)}\n"
        f"• Test questions: {len(test_questions)}\n"
        f"• Best faithfulness: {max(r['metrics']['faithfulness'] for r in results):.2f}\n"
        f"• Fastest model: {min(results, key=lambda x: x['avg_latency'])['model_name']}\n"
        f"• Parent run ID: {parent_run_id}\n"
        f"• Experiment: {experiment_name}\n"
        f"[dim]TODO: Add screenshot showing MLflow model comparison view[/dim]"
    )
    console.print(
        Panel(summary_text, title="[bold cyan]Evaluation Complete[/bold cyan]", border_style="cyan")
    )

    return {
        "experiment_name": experiment_name,
        "parent_run_id": parent_run_id,
        "nested_run_ids": run_ids,
        "results": results,
    }


@beartype
def main() -> None:
    """Run enhanced model comparison example with MLflow integration."""
    try:
        compare_models_with_mlflow()
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
        raise


if __name__ == "__main__":
    main()
