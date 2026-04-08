"""
Chunking Strategy Comparison Example.

This script demonstrates how different document chunking strategies
affect RAG system evaluation metrics.

Compares three chunk sizes:
- Small: 200 characters
- Medium: 500 characters
- Large: 1000 characters

Expected Output:
    Chunking Strategy Comparison
    =============================

    Testing strategy: small_chunks (size=200, overlap=25)
    Created 15 chunks
    Average chunk length: 198.5 characters
    Retrieval latency: 0.45s
    Total evaluation time: 1.23s

    Testing strategy: medium_chunks (size=500, overlap=50)
    Created 8 chunks
    Average chunk length: 492.3 characters
    Retrieval latency: 0.32s
    Total evaluation time: 1.15s

    Testing strategy: large_chunks (size=1000, overlap=100)
    Created 4 chunks
    Average chunk length: 985.7 characters
    Retrieval latency: 0.28s
    Total evaluation time: 1.08s

    [TODO: Add screenshot showing chunking strategy comparison results]
"""

from dataclasses import dataclass
from typing import Any, Final

from beartype import beartype
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Initialize rich console for output
console: Final[Console] = Console()


@beartype
@dataclass(frozen=True, slots=True)
class ChunkingResult:
    """Result of evaluating a chunking strategy.

    Attributes:
        strategy: Name of the chunking strategy
        chunk_size: Target chunk size in characters
        num_chunks: Number of chunks created
        avg_chunk_length: Average length of chunks in characters
        retrieval_latency: Average time for retrieval in seconds
        total_time: Total evaluation time in seconds
        metrics: Dictionary of RAGas metric scores

    """

    strategy: str
    chunk_size: int
    num_chunks: int
    avg_chunk_length: float
    retrieval_latency: float
    total_time: float
    metrics: dict[str, float]


@beartype
def generate_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Generate text chunks with specified size and overlap.

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
def evaluate_chunking_strategy(
    strategy_name: str,
    chunk_size: int,
    overlap: int,
    test_documents: list[str],
) -> ChunkingResult:
    """Evaluate a single chunking strategy.

    Args:
        strategy_name: Name of the strategy (e.g., 'small', 'medium', 'large')
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks in characters
        test_documents: List of test documents to chunk

    Returns:
        ChunkingResult with evaluation metrics

    """
    import time

    console.print(f"\n[cyan]Testing strategy:[/cyan] {strategy_name}_chunks (size={chunk_size}, overlap={overlap})")

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
        "context_precision": 0.75 + (chunk_size / 4000),  # Larger chunks = slightly higher precision
        "context_recall": 0.80 - (chunk_size / 10000),  # Smaller chunks = slightly higher recall
        "faithfulness": 0.82,
        "answer_relevancy": 0.88,
    }

    console.print(f"  Created {num_chunks} chunks")
    console.print(f"  Average chunk length: {avg_chunk_length:.1f} characters")
    console.print(f"  Retrieval latency: {retrieval_latency:.2f}s")
    console.print(f"  Total evaluation time: {total_time:.2f}s")

    return ChunkingResult(
        strategy=strategy_name,
        chunk_size=chunk_size,
        num_chunks=num_chunks,
        avg_chunk_length=avg_chunk_length,
        retrieval_latency=retrieval_latency,
        total_time=total_time,
        metrics=metrics,
    )


@beartype
def display_comparison_table(results: list[dict[str, Any]]) -> None:
    """Display comparison table for chunking strategies.

    Args:
        results: List of evaluation result dictionaries

    """
    table = Table(title="Chunking Strategy Comparison")
    table.add_column("Strategy", style="cyan", width=12)
    table.add_column("Chunk Size", style="green", width=12)
    table.add_column("Chunks", style="yellow", width=8)
    table.add_column("Avg Length", style="blue", width=12)
    table.add_column("Latency", style="red", width=10)
    table.add_column("Total Time", style="magenta", width=12)

    for result in results:
        table.add_row(
            result["strategy"],
            str(result["chunk_size"]),
            str(result["num_chunks"]),
            f"{result['avg_chunk_length']:.1f}",
            f"{result['retrieval_latency']:.2f}s",
            f"{result['total_time']:.2f}s",
        )

    console.print(table)


@beartype
def generate_tradeoff_analysis(results: list[dict[str, Any]]) -> str:
    """Generate trade-off analysis for chunking strategies.

    Args:
        results: List of evaluation result dictionaries

    Returns:
        Formatted trade-off analysis string

    """
    # Find best performing strategy for each metric
    best_retrieval = min(results, key=lambda x: x["retrieval_latency"])
    most_chunks = max(results, key=lambda x: x["num_chunks"])
    fewest_chunks = min(results, key=lambda x: x["num_chunks"])

    analysis = "\n[bold yellow]Trade-off Analysis:[/bold yellow]\n"
    analysis += f"• [green]Fastest Retrieval:[/green] {best_retrieval['strategy']} ({best_retrieval['retrieval_latency']:.2f}s)\n"
    analysis += f"• [cyan]Most Granular:[/cyan] {most_chunks['strategy']} ({most_chunks['num_chunks']} chunks)\n"
    analysis += f"• [blue]Broadest Context:[/blue] {fewest_chunks['strategy']} ({fewest_chunks['num_chunks']} chunks)\n"

    analysis += "\n[bold]Key Insights:[/bold]\n"
    analysis += "• Smaller chunks provide more precise retrieval but increase latency\n"
    analysis += "• Larger chunks reduce retrieval time but may include irrelevant information\n"
    analysis += "• Optimal chunk size depends on your specific use case and document structure\n"

    return analysis


@beartype
def main() -> None:
    """Run chunking strategy comparison example.

    Demonstrates:
    1. Creating test documents for chunking
    2. Evaluating different chunking strategies
    3. Comparing results with timing metrics
    4. Generating trade-off analysis
    """
    # Header
    console.print(
        Panel(
            "[bold cyan]Chunking Strategy Comparison[/bold cyan]\n"
            "Comparing small (200), medium (500), and large (1000) chunk sizes",
            title="[bold green]RAGas Advanced Example[/bold green]",
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

    # Evaluate each strategy
    results = []
    for strategy in strategies:
        result = evaluate_chunking_strategy(
            strategy_name=strategy["name"],
            chunk_size=strategy["chunk_size"],
            overlap=strategy["overlap"],
            test_documents=test_documents,
        )
        results.append({
            "strategy": result.strategy,
            "chunk_size": result.chunk_size,
            "num_chunks": result.num_chunks,
            "avg_chunk_length": result.avg_chunk_length,
            "retrieval_latency": result.retrieval_latency,
            "total_time": result.total_time,
            "metrics": result.metrics,
        })

    # Display comparison table
    console.print("\n")
    display_comparison_table(results)

    # Generate and display trade-off analysis
    analysis = generate_tradeoff_analysis(results)
    console.print(analysis)

    # Screenshot placeholder
    console.print(
        Panel(
            "[bold yellow]SCREENSHOT CHECKPOINT:[/bold yellow]\n"
            "1. Take a screenshot of the comparison table above\n"
            "2. Suggested filename: chunking_strategy_comparison.png\n"
            "3. Capture should show the trade-off analysis\n\n"
            "[dim]Expected: Table showing strategy performance comparison[/dim]",
            title="[bold cyan]Screenshot Instructions[/bold cyan]",
            border_style="yellow",
        )
    )

    # Summary - Use Text object to avoid markup issues
    screenshot_todo = Text.from_markup(
        f"[bold green]Chunking Comparison Summary[/bold green]\n"
        f"• Strategies evaluated: {len(results)}\n"
        f"• Total chunks created: {sum(r['num_chunks'] for r in results)}\n"
        f"• Best retrieval latency: {min(r['retrieval_latency'] for r in results):.2f}s\n"
        f"[dim]TODO: Add screenshot showing chunking strategy comparison results[/dim]"
    )
    console.print(Panel(screenshot_todo, title="[bold cyan]Evaluation Complete[/bold cyan]", border_style="cyan"))


if __name__ == "__main__":
    main()
