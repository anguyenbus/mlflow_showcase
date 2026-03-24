"""
Simple RAGas evaluation example.

This script demonstrates the basic workflow for evaluating RAG systems
using the ragas package with Zhipu AI backend.

Expected Output:
    Loading evaluation dataset from: /path/to/evaluation_dataset.json
    ✓ Loaded 6 evaluation examples
    Configured Zhipu AI backend for RAGas evaluation: glm-5
      Temperature: 0.2 (low for consistent evaluation)
      Embeddings: embedding-3
    ✓ Created RAGas evaluation with metrics:
      - faithfulness
      - answer_relevancy
      - context_precision
      - context_recall
      - answer_correctness

    Running RAGas evaluation...
    ✓ Evaluation complete!

    Evaluation Results:
    ┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
    ┃ Metric                ┃ Score    ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
    │ faithfulness          │   0.8500 │
    │ answer_relevancy      │   0.9200 │
    │ context_precision     │   0.7800 │
    │ context_recall        │   0.8300 │
    │ answer_correctness    │   0.7900 │
    └───────────────────────┴──────────┘
"""

from beartype import beartype
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ragas_evaluation.shared.config import get_ragas_config
from ragas_evaluation.shared.data_loader import load_evaluation_dataset
from ragas_evaluation.shared.metrics import (
    configure_zhipu_backend,
    create_ragas_evaluation,
    get_metric_description,
)

# Initialize rich console for output
console = Console()


@beartype
def display_results(results: dict) -> None:
    """
    Display evaluation results in a formatted table.

    Args:
        results: Dictionary of metric scores

    """
    console.print("\n[bold cyan]Evaluation Results:[/bold cyan]")

    table = Table(title="RAGas Evaluation Scores")
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Score", style="green", width=10)

    for metric_name, score in results.items():
        # Format score to 4 decimal places
        score_formatted = f"{score:.4f}"
        table.add_row(metric_name, score_formatted)

    console.print(table)


@beartype
def main() -> None:
    """
    Run simple RAGas evaluation example.

    This function demonstrates the complete workflow:
    1. Load configuration
    2. Load evaluation dataset
    3. Configure Zhipu AI backend
    4. Create RAGas evaluation with metrics
    5. Run evaluation on dataset
    6. Display results with rich formatting
    """
    try:
        # Step 1: Load configuration
        console.print("[bold cyan]Step 1:[/bold cyan] Loading configuration...")
        config = get_ragas_config()
        console.print(f"[green]✓[/green] MLflow tracking URI: {config.mlflow_tracking_uri}")

        # Step 2: Load evaluation dataset
        console.print("\n[bold cyan]Step 2:[/bold cyan] Loading evaluation dataset...")
        dataset = load_evaluation_dataset()

        # Step 3: Configure Zhipu AI backend
        console.print("\n[bold cyan]Step 3:[/bold cyan] Configuring Zhipu AI backend...")
        llm, embeddings = configure_zhipu_backend()

        # Step 4: Create RAGas evaluation
        console.print("\n[bold cyan]Step 4:[/bold cyan] Creating RAGas evaluation...")
        eval_config = create_ragas_evaluation(llm=llm, embeddings=embeddings)

        # Step 5: Run evaluation
        console.print("\n[bold cyan]Step 5:[/bold cyan] Running RAGas evaluation...")

        # Import ragas evaluate function
        # Convert dataset to pandas DataFrame for ragas
        import pandas as pd

        from ragas import evaluate as ragas_evaluate

        df = pd.DataFrame(dataset)

        # Run evaluation
        results = ragas_evaluate(
            df=df,
            metrics=eval_config["metrics"],
        )

        console.print("[green]✓[/green] Evaluation complete!")

        # Step 6: Display results
        # Convert results to dict for display
        results_dict = results.to_pandas().iloc[0].to_dict()

        # Extract only the metric columns (exclude input columns)
        metric_results = {
            k: v
            for k, v in results_dict.items()
            if k
            in [
                "faithfulness",
                "answer_relevancy",
                "context_precision",
                "context_recall",
                "answer_correctness",
            ]
        }

        display_results(metric_results)

        # Display metric interpretations
        console.print("\n[bold cyan]Metric Interpretations:[/bold cyan]")
        for metric_name in metric_results.keys():
            description = get_metric_description(metric_name)
            console.print(description)

        # Display summary
        console.print(
            Panel(
                f"[bold green]Evaluation Summary[/bold green]\n"
                f"• Dataset size: {len(dataset)} examples\n"
                f"• Metrics evaluated: {len(metric_results)}\n"
                f"• Average score: {sum(metric_results.values()) / len(metric_results):.4f}\n"
                f"• Backend: Zhipu AI (glm-5)",
                title="[bold cyan]RAGas Evaluation[/bold cyan]",
                border_style="cyan",
            )
        )

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        raise


if __name__ == "__main__":
    main()
