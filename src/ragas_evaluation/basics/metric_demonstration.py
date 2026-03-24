"""
RAGas metric demonstration examples.

This script provides individual demonstrations of each RAGas metric
to help understand what each metric measures and how to interpret scores.
"""

from beartype import beartype
from rich.console import Console
from rich.panel import Panel

from ragas_evaluation.shared.config import get_ragas_config
from ragas_evaluation.shared.metrics import (
    get_metric_description,
)

# Initialize rich console for output
console = Console()


@beartype
def demonstrate_faithfulness() -> None:
    """
    Demonstrate faithfulness metric.

    Faithfulness measures the factual consistency of the generated answer
    against the retrieved context. It detects hallucinations and contradictions.

    Interpretation:
    - Score 0.0-1.0, higher is better
    - High score: Answer is factually consistent with context
    - Low score: Answer contains hallucinations or contradicts context
    """
    console.print(
        Panel(
            "[bold cyan]Demonstrating Faithfulness Metric[/bold cyan]\n"
            "Measures factual consistency of answer against retrieved context",
            border_style="cyan",
        )
    )

    # Display metric description
    console.print(get_metric_description("faithfulness"))

    # Example scenario
    console.print("\n[bold yellow]Example Scenario:[/bold yellow]")
    console.print(
        "Question: What is the GST rate in Australia?\n"
        "Context: GST is a broad-based tax of 10%% on\n"
        "most goods, services and other items in Australia.'\n"
        "Response (High Faithfulness): 'The GST rate in Australia is 10%%.'\n"
        "Response (Low Faithfulness): 'The GST rate in Australia is 15%%.'"
    )


@beartype
def demonstrate_answer_relevancy() -> None:
    """
    Demonstrate answer relevancy metric.

    Answer relevancy measures how well the answer addresses the question.
    It penalizes incomplete or irrelevant answers.

    Interpretation:
    - Score 0.0-1.0, higher is better
    - High score: Answer directly addresses the question
    - Low score: Answer is incomplete or irrelevant
    """
    console.print(
        Panel(
            "[bold cyan]Demonstrating Answer Relevancy Metric[/bold cyan]\n"
            "Measures how well the answer addresses the question",
            border_style="cyan",
        )
    )

    # Display metric description
    console.print(get_metric_description("answer_relevancy"))

    # Example scenario
    console.print("\n[bold yellow]Example Scenario:[/bold yellow]")
    console.print(
        "Question: What are the income tax rates for Australian residents?\n"
        "Context: 'Australia has a progressive tax system with rates from 0%% to 45%%.'\n"
        "Response (High Relevancy): Australia uses a\n"
        "progressive tax system with rates ranging from\n"
        "0%% to 45%% depending on income.'\n"
        "Response (Low Relevancy): 'Taxes are important.'"
    )


@beartype
def demonstrate_context_precision() -> None:
    """
    Demonstrate context precision metric.

    Context precision measures the quality of retrieved context passages.
    It evaluates whether retrieved contexts are relevant and properly ranked.

    Interpretation:
    - Score 0.0-1.0, higher is better
    - High score: Retrieved contexts are relevant and ranked well
    - Low score: Retrieved contexts contain irrelevant information
    """
    console.print(
        Panel(
            "[bold cyan]Demonstrating Context Precision Metric[/bold cyan]\n"
            "Measures the quality of retrieved context passages",
            border_style="cyan",
        )
    )

    # Display metric description
    console.print(get_metric_description("context_precision"))

    # Example scenario
    console.print("\n[bold yellow]Example Scenario:[/bold yellow]")
    console.print(
        "Question: What is the tax-free threshold in Australia?\n"
        "Contexts (High Precision):\n"
        "  1. 'The tax-free threshold for Australian residents is $18,200.'\n"
        "  2. 'Residents can earn up to $18,200 tax-free.'\n"
        "Contexts (Low Precision):\n"
        "  1. 'Australia has a goods and services tax (GST).'\n"
        "  2. 'The tax-free threshold is $18,200.'"
    )


@beartype
def demonstrate_context_recall() -> None:
    """
    Demonstrate context recall metric.

    Context recall measures if all relevant information was retrieved.
    It evaluates whether the retrieval system found all necessary context.

    Interpretation:
    - Score 0.0-1.0, higher is better
    - High score: All relevant context was retrieved
    - Low score: Important context was missed
    (Requires ground truth reference)
    """
    console.print(
        Panel(
            "[bold cyan]Demonstrating Context Recall Metric[/bold cyan]\n"
            "Measures if all relevant information was retrieved",
            border_style="cyan",
        )
    )

    # Display metric description
    console.print(get_metric_description("context_recall"))

    # Example scenario
    console.print("\n[bold yellow]Example Scenario:[/bold yellow]")
    console.print(
        "Question: What are the deductions available for work-related expenses?\n"
        "Ground Truth: 'Car expenses, travel expenses,\n"
        "clothing and laundry expenses, home office expenses,\n"
        "self-education expenses, and tools and equipment.'\n"
        "Retrieved Contexts (High Recall): Includes all 6 categories\n"
        "Retrieved Contexts (Low Recall): Only includes car and travel expenses"
    )


@beartype
def demonstrate_answer_correctness() -> None:
    """
    Demonstrate answer correctness metric.

    Answer correctness measures the accuracy of the answer compared to ground truth.
    It evaluates factual accuracy and completeness against reference answers.

    Interpretation:
    - Score 0.0-1.0, higher is better
    - High score: Answer matches ground truth
    - Low score: Answer differs from ground truth
    (Requires ground truth reference)
    """
    console.print(
        Panel(
            "[bold cyan]Demonstrating Answer Correctness Metric[/bold cyan]\n"
            "Measures the accuracy of the answer compared to ground truth",
            border_style="cyan",
        )
    )

    # Display metric description
    console.print(get_metric_description("answer_correctness"))

    # Example scenario
    console.print("\n[bold yellow]Example Scenario:[/bold yellow]")
    console.print(
        "Question: When is the Australian tax year end?\n"
        "Ground Truth: 'The Australian tax year ends on June 30th.'\n"
        "Response (High Correctness): 'The Australian tax year ends on June 30th.'\n"
        "Response (Low Correctness): 'The Australian tax year ends on December 31st.'"
    )


@beartype
def main() -> None:
    """
    Run all metric demonstrations.

    This function demonstrates each RAGas metric individually with
    examples and interpretations.
    """
    try:
        console.print("[bold cyan]RAGas Metrics Demonstration[/bold cyan]\n")

        # Load configuration
        _ = get_ragas_config()

        # Demonstrate each metric
        demonstrate_faithfulness()
        console.print("\n" + "=" * 80 + "\n")

        demonstrate_answer_relevancy()
        console.print("\n" + "=" * 80 + "\n")

        demonstrate_context_precision()
        console.print("\n" + "=" * 80 + "\n")

        demonstrate_context_recall()
        console.print("\n" + "=" * 80 + "\n")

        demonstrate_answer_correctness()

        # Summary
        console.print(
            Panel(
                "[bold green]All Metrics Demonstrated[/bold green]\n"
                "• Faithfulness: Factual consistency with context\n"
                "• Answer Relevancy: How well answer addresses question\n"
                "• Context Precision: Quality of retrieved contexts\n"
                "• Context Recall: Completeness of retrieved contexts (requires ground truth)\n"
                "• Answer Correctness: Accuracy compared to ground truth (requires ground truth)",
                title="[bold cyan]RAGas Metrics Summary[/bold cyan]",
                border_style="cyan",
            )
        )

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        raise


if __name__ == "__main__":
    main()
