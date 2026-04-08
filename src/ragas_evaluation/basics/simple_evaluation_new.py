#!/usr/bin/env python
"""
Simple RAGAS evaluation example.

This demonstrates the complete RAGAS evaluation workflow from loading
configuration to displaying results.
"""

import os
import pandas as pd
from pathlib import Path

from beartype import beartype
from rich.console import Console
from rich.table import Table

# Initialize rich console for output
console = Console()


def load_evaluation_dataset() -> list:
    """Load evaluation dataset from JSON file.

    Returns:
        List of evaluation examples with question, contexts, response, reference_answer
    """
    # Get the evaluation data path
    from ragas_evaluation.shared.data_loader import get_evaluation_dataset_path
    data_path = get_evaluation_dataset_path()

    # Load JSON dataset
    import json
    with open(data_path) as f:
        dataset = json.load(f)

    return dataset


def display_results(results: dict) -> None:
    """Display evaluation results in a formatted table.

    Args:
        results: Dictionary of metric names to scores
    """
    table = Table(title="Evaluation Results", show_header=True, show_footer=True)
    table.add_column("Metric", style="cyan", no_wrap=False)
    table.add_column("Score", style="green")

    for metric_name, score in results.items():
        table.add_row(metric_name, f"{score:.4f}")

    console.print("\n")
    console.print(table)


def get_metric_description(metric_name: str) -> str:
    """Get description for a metric.

    Args:
        metric_name: Name of the metric

    Returns:
        Formatted description string
    """
    descriptions = {
        "faithfulness": """
[cyan]Faithfulness:[/cyan] Measures the factual consistency of the generated answer
against the retrieved context.

[yellow]Interpretation:[/yellow]
- Score 0.0-1.0, higher is better
- High score: Answer is factually consistent with context
- Low score: Answer contains hallucinations or contradicts context
""",
        "answer_relevancy": """
[cyan]Answer Relevancy:[/cyan] Measures how well the answer addresses the question.

[yellow]Interpretation:[/yellow]
- Score 0.0-1.0, higher is better
- High score: Answer directly addresses the question
- Low score: Answer is incomplete or irrelevant
""",
        "context_precision": """
[cyan]Context Precision:[/cyan] Measures the quality of retrieved context passages.

[yellow]Interpretation:[/yellow]
- Score 0.0-1.0, higher is better
- High score: Retrieved contexts are relevant and ranked well
- Low score: Retrieved contexts contain irrelevant information
""",
    }

    return descriptions.get(metric_name, f"No description available for {metric_name}")


@beartype
def main() -> None:
    """Main function for simple RAGAS evaluation."""
    try:
        # Step 1: Load configuration
        console.print("[bold cyan]Step 1:[/bold cyan] Loading configuration...")
        from ragas_evaluation.shared.config import get_ragas_config

        config = get_ragas_config()
        console.print(f"[green]✓[/green] MLflow tracking URI: {config.mlflow_tracking_uri}")

        # Set up environment for RAGAS to use Zhipu AI
        os.environ["OPENAI_API_KEY"] = config.zhipu_api_key
        os.environ["OPENAI_BASE_URL"] = "https://open.bigmodel.cn/api/paas/v4/"
        console.print("[green]✓[/green] Configured RAGAS to use Zhipu AI backend")

        # Step 2: Load evaluation dataset
        console.print("\n[bold cyan]Step 2:[/bold cyan] Loading evaluation dataset...")
        dataset = load_evaluation_dataset()

        console.print(f"[green]✓[/green] Loaded {len(dataset)} evaluation examples")

        # Step 3: Prepare data for RAGAS
        console.print("\n[bold cyan]Step 3:[/bold cyan] Preparing data for RAGAS...")

        # Convert to DataFrame
        df = pd.DataFrame(dataset)

        # Rename columns to match RAGAS expected format
        # RAGAS expects: user_input, response, retrieved_contexts, reference
        df_renamed = df.rename(columns={
            "question": "user_input",
            "contexts": "retrieved_contexts",
            "response": "response",
            "reference_answer": "reference"
        })

        # Convert to HuggingFace Dataset
        from datasets import Dataset as HFDataset
        hf_dataset = HFDataset.from_pandas(df_renamed)

        console.print("[green]✓[/green] Data prepared for RAGAS evaluation")

        # Step 4: Create RAGAS metrics
        console.print("\n[bold cyan]Step 4:[/bold cyan] Creating RAGAS metrics...")

        # Import pre-configured metric instances (function-based API)
        # Note: Excluding answer_relevancy for now due to Zhipu embeddings API compatibility
        from ragas.metrics._faithfulness import faithfulness
        from ragas.metrics._context_precision import context_precision
        from ragas.llms.base import llm_factory
        from openai import OpenAI as OpenAIClient
        from ragas.run_config import RunConfig

        # Create Zhipu AI client for RAGAS
        client = OpenAIClient(
            api_key=config.zhipu_api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )

        # Create LLM with glm-5 model - increase max_tokens for longer responses
        ragas_llm = llm_factory(model="glm-5", client=client, max_tokens=4096)

        # Inject LLM into pre-configured metrics
        faithfulness.llm = ragas_llm
        context_precision.llm = ragas_llm

        # Create run config
        run_config = RunConfig(max_retries=3, max_wait=60, timeout=60)

        metrics = [faithfulness, context_precision]

        console.print("[green]✓[/green] Created RAGAS evaluation with metrics:")
        for metric in metrics:
            console.print(f"  - {metric.name}")

        # Step 5: Run evaluation
        console.print("\n[bold cyan]Step 5:[/bold cyan] Running RAGAS evaluation...")

        from ragas import evaluate

        # Run evaluation
        results = evaluate(
            dataset=hf_dataset,
            metrics=metrics,
            run_config=run_config,
        )

        console.print("[green]✓[/green] Evaluation complete!")

        # Step 6: Display results
        # Convert results to dict for display
        results_df = results.to_pandas()

        # Calculate average scores
        metric_results = {}
        for metric in ["faithfulness", "context_precision"]:
            if metric in results_df.columns:
                # Get mean score, ignoring NaN values
                scores = results_df[metric].dropna()
                if len(scores) > 0:
                    metric_results[metric] = scores.mean()

        display_results(metric_results)

        # Display metric interpretations
        console.print("\n[bold cyan]Metric Interpretations:[/bold cyan]")
        for metric_name in metric_results.keys():
            description = get_metric_description(metric_name)
            console.print(description)

        # Display summary
        console.print("\n")
        from rich.panel import Panel

        # Handle empty results
        if metric_results:
            avg_score = sum(metric_results.values()) / len(metric_results)
            summary_text = f"""Evaluation Summary
• Dataset size: {len(dataset)} examples
• Metrics evaluated: {len(metric_results)}
• Average score: {avg_score:.4f}
• Backend: Zhipu AI (glm-5)
"""
        else:
            summary_text = f"""Evaluation Summary
• Dataset size: {len(dataset)} examples
• No metrics returned valid results
• Backend: Zhipu AI (glm-5)
• Check logs for errors
"""

        console.print(Panel.fit(
            summary_text,
            title="RAGas Evaluation Complete",
            border_style="blue",
        ))

        # Screenshot placeholder
        console.print("\n")
        console.print(Panel(
            "[yellow]SCREENSHOT CHECKPOINT[/yellow]"
            "\n1. Open MLflow UI at http://localhost:5000"
            "\n2. Navigate to Experiments → ragas-evaluation"
            "\n3. Click on the latest run"
            "\n4. Take screenshot of metrics view"
            "\n5. Suggested filename: simple_evaluation_metrics.png"
            "\n\nCapture: Metrics table showing all ragas scores",
            title="Screenshot",
            border_style="yellow",
        ))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        raise


if __name__ == "__main__":
    main()
