"""
Chunking Strategy Comparison with MLflow Integration.

This script demonstrates how different document chunking strategies
affect RAG system evaluation metrics, with comprehensive MLflow tracking.

Compares three chunk sizes:
- Small: 200 characters
- Medium: 500 characters
- Large: 1000 characters

Each strategy is logged as a nested run under a parent comparison run.

Expected Output:
    Chunking Strategy Comparison with MLflow
    =========================================

    [PARENT RUN] Starting chunking strategy comparison
    Parent run ID: parent_abc123

    Testing strategy: small_chunks (size=200, overlap=25)
    [NESTED RUN] Run ID: nested_def456
    Created 15 chunks
    Average chunk length: 198.5 characters
    Retrieval latency: 0.45s

    Testing strategy: medium_chunks (size=500, overlap=50)
    [NESTED RUN] Run ID: nested_ghi789
    Created 8 chunks
    Average chunk length: 492.3 characters
    Retrieval latency: 0.32s

    Testing strategy: large_chunks (size=1000, overlap=100)
    [NESTED RUN] Run ID: nested_jkl012
    Created 4 chunks
    Average chunk length: 985.7 characters
    Retrieval latency: 0.28s

    MLflow Comparison Table:
    View at: http://localhost:5000/#/experiments/1

    [TODO: Add screenshot showing MLflow chunking comparison]
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
class ChunkingResult:
    """
    Result of evaluating a chunking strategy.

    Attributes:
        strategy: Name of the chunking strategy
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks in characters
        num_chunks: Number of chunks created
        avg_chunk_length: Average length of chunks in characters
        retrieval_latency: Average time for retrieval in seconds
        total_time: Total evaluation time in seconds
        metrics: Dictionary of RAGas metric scores
        run_id: MLflow run ID for this strategy

    """

    strategy: str
    chunk_size: int
    overlap: int
    num_chunks: int
    avg_chunk_length: float
    retrieval_latency: float
    total_time: float
    metrics: dict[str, float]
    run_id: str | None = None


@beartype
def generate_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Generate text chunks with specified size and overlap.

    Args:
        text: Input text to chunk
        chunk_size: Target size for each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks

    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        # Move start position, accounting for overlap
        start = end - overlap if end < text_length else text_length

    return chunks


@beartype
def evaluate_chunking_strategy_with_mlflow(
    strategy_name: str,
    chunk_size: int,
    overlap: int,
    test_documents: list[str],
    parent_run_id: str | None = None,
) -> ChunkingResult:
    """
    Evaluate a single chunking strategy with MLflow logging.

    Args:
        strategy_name: Name of the strategy (e.g., 'small', 'medium', 'large')
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks in characters
        test_documents: List of test documents to chunk
        parent_run_id: Optional parent run ID for nested run

    Returns:
        ChunkingResult with evaluation metrics and MLflow run ID

    """
    import time

    if not MLFLOW_AVAILABLE:
        console.print("[yellow]MLflow not available. Skipping MLflow logging.[/yellow]")

    console.print(
        f"\n[cyan]Testing strategy:[/cyan] {strategy_name}_chunks (size={chunk_size}, overlap={overlap})"
    )

    # Start nested MLflow run if available
    run_id = None
    if MLFLOW_AVAILABLE:
        run_name = f"{strategy_name}_chunks_size{chunk_size}"
        with mlflow.start_run(nested=True, run_name=run_name) as run:
            run_id = run.info.run_id
            console.print(f"  [dim][NESTED RUN] Run ID: {run_id}[/dim]")

            # Log parameters
            mlflow.log_param("strategy_name", strategy_name)
            mlflow.log_param("chunk_size", str(chunk_size))
            mlflow.log_param("overlap", str(overlap))

    # Generate all chunks from test documents
    all_chunks = []
    start_time = time.time()

    for doc in test_documents:
        chunks = generate_chunks(doc, chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(chunks)

    total_time = time.time() - start_time

    # Calculate statistics
    num_chunks = len(all_chunks)
    avg_chunk_length = sum(len(c) for c in all_chunks) / num_chunks if num_chunks > 0 else 0

    # NOTE: Simulate retrieval latency based on chunk count
    # More chunks = higher retrieval latency
    retrieval_latency = 0.1 + (num_chunks * 0.02)

    # Create mock metrics for demonstration
    # NOTE: In production, use actual RAGas evaluation
    metrics = {
        "context_precision": 0.75
        + (chunk_size / 4000),  # Larger chunks = slightly higher precision
        "context_recall": 0.80 - (chunk_size / 10000),  # Smaller chunks = slightly higher recall
        "faithfulness": 0.82,
        "answer_relevancy": 0.88,
    }

    console.print(f"  Created {num_chunks} chunks")
    console.print(f"  Average chunk length: {avg_chunk_length:.1f} characters")
    console.print(f"  Retrieval latency: {retrieval_latency:.2f}s")
    console.print(f"  Total evaluation time: {total_time:.2f}s")

    # Log metrics and additional info to MLflow
    if MLFLOW_AVAILABLE and run_id:
        mlflow.log_metric("num_chunks", num_chunks)
        mlflow.log_metric("avg_chunk_length", avg_chunk_length)
        mlflow.log_metric("retrieval_latency", retrieval_latency)
        mlflow.log_metric("total_time", total_time)

        # Log RAGas metrics
        for metric_name, value in metrics.items():
            mlflow.log_metric(f"ragas_{metric_name}", value)

    return ChunkingResult(
        strategy=strategy_name,
        chunk_size=chunk_size,
        overlap=overlap,
        num_chunks=num_chunks,
        avg_chunk_length=avg_chunk_length,
        retrieval_latency=retrieval_latency,
        total_time=total_time,
        metrics=metrics,
        run_id=run_id,
    )


@beartype
def display_comparison_table(results: list[dict[str, Any]]) -> None:
    """
    Display comparison table for chunking strategies.

    Args:
        results: List of evaluation result dictionaries

    """
    table = Table(title="Chunking Strategy Comparison")
    table.add_column("Strategy", style="cyan", width=12)
    table.add_column("Chunk Size", style="green", width=12)
    table.add_column("Chunks", style="yellow", width=8)
    table.add_column("Avg Length", style="blue", width=12)
    table.add_column("Latency", style="red", width=10)
    table.add_column("Context Precision", style="magenta", width=18)
    table.add_column("Context Recall", style="bright_magenta", width=16)

    for result in results:
        table.add_row(
            result["strategy"],
            str(result["chunk_size"]),
            str(result["num_chunks"]),
            f"{result['avg_chunk_length']:.1f}",
            f"{result['retrieval_latency']:.2f}s",
            f"{result['metrics']['context_precision']:.3f}",
            f"{result['metrics']['context_recall']:.3f}",
        )

    console.print(table)


@beartype
def generate_tradeoff_analysis(results: list[dict[str, Any]]) -> str:
    """
    Generate trade-off analysis for chunking strategies.

    Args:
        results: List of evaluation result dictionaries

    Returns:
        Formatted trade-off analysis string

    """
    # Find best performing strategy for each metric
    best_retrieval = min(results, key=lambda x: x["retrieval_latency"])
    most_chunks = max(results, key=lambda x: x["num_chunks"])
    fewest_chunks = min(results, key=lambda x: x["num_chunks"])
    best_precision = max(results, key=lambda x: x["metrics"]["context_precision"])
    best_recall = max(results, key=lambda x: x["metrics"]["context_recall"])

    analysis = "\n[bold yellow]Trade-off Analysis:[/bold yellow]\n"
    analysis += f"• [green]Fastest Retrieval:[/green] {best_retrieval['strategy']} ({best_retrieval['retrieval_latency']:.2f}s)\n"
    analysis += f"• [cyan]Most Granular:[/cyan] {most_chunks['strategy']} ({most_chunks['num_chunks']} chunks)\n"
    analysis += f"• [blue]Broadest Context:[/blue] {fewest_chunks['strategy']} ({fewest_chunks['num_chunks']} chunks)\n"
    analysis += f"• [magenta]Best Context Precision:[/magenta] {best_precision['strategy']} ({best_precision['metrics']['context_precision']:.3f})\n"
    analysis += f"• [bright_magenta]Best Context Recall:[/bright_magenta] {best_recall['strategy']} ({best_recall['metrics']['context_recall']:.3f})\n"

    analysis += "\n[bold]Key Insights:[/bold]\n"
    analysis += "• Smaller chunks provide more precise retrieval but increase latency\n"
    analysis += "• Larger chunks reduce retrieval time but may include irrelevant information\n"
    analysis += "• Optimal chunk size depends on your specific use case and document structure\n"
    analysis += "• MLflow tracking enables historical comparison of chunking experiments\n"

    return analysis


@beartype
def generate_mlflow_comparison_guideline(experiment_name: str, parent_run_id: str | None) -> Panel:
    """
    Generate MLflow UI navigation guidance for chunking comparison.

    Args:
        experiment_name: Name of the MLflow experiment
        parent_run_id: Optional parent run ID

    Returns:
        Panel with MLflow UI navigation instructions

    """
    ui_url = "http://localhost:5000"

    content = "[bold yellow]MLflow UI Navigation:[/bold yellow]\n\n"
    content += "1. Open MLflow UI: Navigate to [cyan]" + ui_url + "[/cyan]\n"
    content += "2. Select experiment: [cyan]" + experiment_name + "[/cyan]\n"

    if parent_run_id:
        content += "3. Find parent run: [cyan]" + parent_run_id + "[/cyan]\n"
        content += "4. View nested runs: Click on parent run to see child runs\n"

    content += "\n[bold yellow]Comparison View:[/bold yellow]\n"
    content += "• Select all nested runs (checkboxes)\n"
    content += "• Click 'Compare' button\n"
    content += "• View side-by-side metrics comparison\n\n"

    content += "[dim][TODO: Add screenshot showing MLflow chunking comparison][/dim]"

    return Panel(
        content,
        title="[bold cyan]MLflow Comparison Guide[/bold cyan]",
        border_style="yellow",
    )


@beartype
def compare_chunking_strategies_with_mlflow() -> dict[str, Any]:
    """
    Run chunking strategy comparison with MLflow integration.

    This function demonstrates:
    1. Creating test documents for chunking
    2. Evaluating different chunking strategies
    3. Logging each strategy as a nested MLflow run
    4. Comparing results with timing metrics
    5. Generating MLflow UI navigation guidance

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
    experiment_name = "ragas_chunking_comparison"
    mlflow.set_experiment(experiment_name)

    # Header
    console.print(
        Panel(
            "[bold cyan]Chunking Strategy Comparison with MLflow[/bold cyan]\n"
            "Comparing small (200), medium (500), and large (1000) chunk sizes\n"
            "with comprehensive MLflow tracking",
            title="[bold green]RAGas Advanced + MLflow[/bold green]",
            border_style="cyan",
        )
    )

    # Create test documents
    # NOTE: In production, load from actual document corpus
    test_documents = [
        "Goods and Services Tax (GST) is a broad-based tax of 10% on most goods, "
        "services and other items in Australia. Some goods and services are GST-free, "
        "including basic food, some medical services, and some educational courses. "
        "GST is applied at the point of sale and is included in the price you pay. "
        "Businesses registered for GST can claim credits for the GST included in "
        "the price of goods and services they purchase for their business. "
        "This means they don't pay GST on their business inputs, only on the value "
        "they add. The GST system was introduced in Australia in July 2000 and has "
        "become an important part of the Australian taxation system.",
        "For the 2024-25 financial year, income tax rates are progressive. "
        "Residents pay 0% on income up to $18,200, 19% on income between $18,201 "
        "and $45,000, 32.5% on income between $45,001 and $120,000, 37% on income "
        "between $120,001 and $180,000, and 45% on income over $180,000. "
        "Foreign residents are taxed at different rates and cannot claim the "
        "tax-free threshold. The marginal tax rate means you only pay the higher "
        "rate on income above the threshold, not on your entire income.",
        "Work-related expenses can be claimed as tax deductions if they directly "
        "relate to earning your income. Common deductions include vehicle and travel "
        "expenses, clothing and laundry expenses, home office expenses, and self-education "
        "expenses. You must have spent the money yourself and have records to prove "
        "your expenses. The expenses must be directly related to your work and not "
        "reimbursed by your employer. Keeping accurate records is essential for "
        "claiming deductions and avoiding issues with the Australian Taxation Office.",
    ]

    # Define chunking strategies to compare
    strategies = [
        {"name": "small", "chunk_size": 200, "overlap": 25},
        {"name": "medium", "chunk_size": 500, "overlap": 50},
        {"name": "large", "chunk_size": 1000, "overlap": 100},
    ]

    # Start parent run
    with mlflow.start_run(run_name="chunking_comparison_parent") as parent_run:
        parent_run_id = parent_run.info.run_id
        console.print("\n[bold][PARENT RUN] Starting chunking strategy comparison[/bold]")
        console.print(f"[dim]Parent run ID: {parent_run_id}[/dim]")

        # Log parent run parameters
        mlflow.log_param("num_strategies", str(len(strategies)))
        mlflow.log_param("num_documents", str(len(test_documents)))
        mlflow.log_param("comparison_type", "chunking_strategy")

        # Evaluate each strategy
        results = []
        for strategy in strategies:
            result = evaluate_chunking_strategy_with_mlflow(
                strategy_name=strategy["name"],
                chunk_size=strategy["chunk_size"],
                overlap=strategy["overlap"],
                test_documents=test_documents,
                parent_run_id=parent_run_id,
            )
            results.append(
                {
                    "strategy": result.strategy,
                    "chunk_size": result.chunk_size,
                    "overlap": result.overlap,
                    "num_chunks": result.num_chunks,
                    "avg_chunk_length": result.avg_chunk_length,
                    "retrieval_latency": result.retrieval_latency,
                    "total_time": result.total_time,
                    "metrics": result.metrics,
                    "run_id": result.run_id,
                }
            )

    # Display comparison table
    console.print("\n")
    display_comparison_table(results)

    # Generate and display trade-off analysis
    analysis = generate_tradeoff_analysis(results)
    console.print(analysis)

    # Display MLflow navigation guidance
    console.print("\n")
    mlflow_guide = generate_mlflow_comparison_guideline(experiment_name, parent_run_id)
    console.print(mlflow_guide)

    # Summary
    run_ids = [r["run_id"] for r in results if r["run_id"]]
    summary_text = Text.from_markup(
        f"[bold green]Chunking Comparison Summary[/bold green]\n"
        f"• Strategies evaluated: {len(results)}\n"
        f"• Total chunks created: {sum(r['num_chunks'] for r in results)}\n"
        f"• Best retrieval latency: {min(r['retrieval_latency'] for r in results):.2f}s\n"
        f"• Parent run ID: {parent_run_id}\n"
        f"• Experiment: {experiment_name}\n"
        f"[dim]TODO: Add screenshot showing MLflow chunking comparison results[/dim]"
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
    """Run chunking strategy comparison example with MLflow integration."""
    try:
        compare_chunking_strategies_with_mlflow()
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
        raise


if __name__ == "__main__":
    main()
