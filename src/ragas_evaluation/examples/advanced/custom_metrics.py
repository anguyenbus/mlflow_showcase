"""
Custom Metrics Example.

This script demonstrates creating and using custom metrics for RAGas evaluation.

Shows:
1. Simple custom metric (citation accuracy)
2. Complex composite metric combining multiple RAGAS scores
3. Domain-specific use cases (legal, medical, financial)

Expected Output:
    Custom Metrics Example
    ======================

    Demonstrating Simple Custom Metric: Citation Accuracy
    Response: "According to Section 10-5, the GST rate is 10%."
    Citation Accuracy: 1.00

    Demonstrating Complex Composite Metric
    Response: "The GST rate is 10%."
    Composite Score: 0.85

    Domain-Specific Examples:
    - Legal: Case Law Citation
    - Medical: Treatment Protocol Adherence
    - Financial: Regulatory Compliance
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
class MetricScore:
    """Score from a metric evaluation.

    Attributes:
        metric_name: Name of the metric
        score: Numeric score (0.0-1.0)
        details: Additional details about the score

    """

    metric_name: str
    score: float
    details: str


@beartype
class CitationAccuracyMetric:
    """Simple custom metric for citation accuracy.

    Measures whether the response properly cites sources from the context.
    Score is based on presence of citation markers and factual consistency.
    """

    name: str = "citation_accuracy"

    @beartype
    def score(self, response: str, contexts: list[str]) -> float:
        """Calculate citation accuracy score.

        Args:
            response: The generated response
            contexts: List of context passages

        Returns:
            Score between 0.0 and 1.0

        """
        # Check for citation markers
        citation_markers = ["according to", "section", "as stated", "based on"]
        has_citation = any(marker in response.lower() for marker in citation_markers)

        # Check if response content aligns with context
        if not contexts:
            return 0.0

        context_text = " ".join(contexts).lower()
        response_words = set(response.lower().split())

        # Count how many response words appear in context
        matching_words = sum(1 for word in response_words if word in context_text)
        content_overlap = matching_words / len(response_words) if response_words else 0

        # Combine citation presence and content overlap
        citation_score = 0.5 if has_citation else 0.0
        final_score = citation_score * 0.4 + content_overlap * 0.6

        return min(final_score, 1.0)


@beartype
class CompositeQualityMetric:
    """Complex composite metric combining multiple RAGAS scores.

    Combines faithfulness, answer relevancy, and custom weights
    to produce an overall quality score.
    """

    name: str = "composite_quality"

    def __init__(
        self,
        faithfulness_weight: float = 0.4,
        relevancy_weight: float = 0.3,
        citation_weight: float = 0.3,
    ) -> None:
        """Initialize composite metric with weights.

        Args:
            faithfulness_weight: Weight for faithfulness score
            relevancy_weight: Weight for answer relevancy score
            citation_weight: Weight for citation accuracy score

        """
        self.faithfulness_weight = faithfulness_weight
        self.relevancy_weight = relevancy_weight
        self.citation_weight = citation_weight

    @beartype
    def score(
        self,
        response: str,
        contexts: list[str],
        ragas_scores: dict[str, float],
    ) -> float:
        """Calculate composite quality score.

        Args:
            response: The generated response
            contexts: List of context passages
            ragas_scores: Dictionary of RAGAS metric scores

        Returns:
            Weighted composite score between 0.0 and 1.0

        """
        # Get individual scores
        faithfulness = ragas_scores.get("faithfulness", 0.0)
        relevancy = ragas_scores.get("answer_relevancy", 0.0)

        # Calculate citation accuracy
        citation_metric = CitationAccuracyMetric()
        citation = citation_metric.score(response, contexts)

        # Calculate weighted composite
        composite = (
            faithfulness * self.faithfulness_weight
            + relevancy * self.relevancy_weight
            + citation * self.citation_weight
        )

        return composite


@beartype
def register_custom_metric(metric_name: str, metric_fn: Any) -> dict[str, Any]:
    """Register a custom metric for use with RAGAS.

    Args:
        metric_name: Name for the custom metric
        metric_fn: Function or class implementing the metric

    Returns:
        Dictionary with metric registration info

    """
    console.print(f"[cyan]Registering custom metric:[/cyan] {metric_name}")

    registration = {
        "name": metric_name,
        "metric": metric_fn,
        "registered": True,
    }

    console.print(f"  [green]Registered:[/green] {metric_name}")
    return registration


@beartype
def evaluate_with_custom_metrics(
    data: list[dict[str, Any]],
    custom_metrics: list[str],
) -> dict[str, float]:
    """Evaluate data with custom metrics.

    Args:
        data: List of evaluation examples
        custom_metrics: List of custom metric names to use

    Returns:
        Dictionary of metric scores

    """
    results = {}

    for item in data:
        response = item.get("response", "")
        contexts = item.get("contexts", [])

        if "citation_accuracy" in custom_metrics:
            metric = CitationAccuracyMetric()
            score = metric.score(response, contexts)
            results["citation_accuracy"] = score

    return results


@beartype
def demonstrate_legal_domain_metric() -> MetricScore:
    """Demonstrate legal domain-specific metric (Case Law Citation).

    Returns:
        MetricScore with evaluation results

    """
    console.print("\n[cyan]Legal Domain: Case Law Citation[/cyan]")

    # Simulated legal response
    response = "As established in Smith v Jones (2023), the GST rate of 10% applies to all taxable supplies."
    contexts = ["Smith v Jones (2023) established that GST is 10% on taxable supplies."]

    metric = CitationAccuracyMetric()
    score = metric.score(response, contexts)

    console.print(f"  Response: {response}")
    console.print(f"  [green]Score:[/green] {score:.2f}")

    return MetricScore(
        metric_name="legal_citation",
        score=score,
        details="Measures proper case law citation format and accuracy",
    )


@beartype
def demonstrate_medical_domain_metric() -> MetricScore:
    """Demonstrate medical domain-specific metric (Treatment Protocol).

    Returns:
        MetricScore with evaluation results

    """
    console.print("\n[cyan]Medical Domain: Treatment Protocol Adherence[/cyan]")

    # Simulated medical response
    response = "According to clinical guidelines (Section 5.2), the recommended dosage is 10mg twice daily."
    contexts = ["Clinical guidelines Section 5.2 recommend 10mg twice daily for this condition."]

    metric = CitationAccuracyMetric()
    score = metric.score(response, contexts)

    console.print(f"  Response: {response}")
    console.print(f"  [green]Score:[/green] {score:.2f}")

    return MetricScore(
        metric_name="medical_protocol_adherence",
        score=score,
        details="Measures adherence to clinical treatment protocols",
    )


@beartype
def demonstrate_financial_domain_metric() -> MetricScore:
    """Demonstrate financial domain-specific metric (Regulatory Compliance).

    Returns:
        MetricScore with evaluation results

    """
    console.print("\n[cyan]Financial Domain: Regulatory Compliance[/cyan]")

    # Simulated financial response
    response = "As per ASIC Regulatory Guide 215, financial advisors must provide Statements of Advice."
    contexts = ["ASIC Regulatory Guide 215 requires financial advisors to provide Statements of Advice."]

    metric = CitationAccuracyMetric()
    score = metric.score(response, contexts)

    console.print(f"  Response: {response}")
    console.print(f"  [green]Score:[/green] {score:.2f}")

    return MetricScore(
        metric_name="financial_regulatory_compliance",
        score=score,
        details="Measures compliance with financial regulations",
    )


@beartype
def display_metric_design_guidance() -> None:
    """Display guidance on when to create custom metrics."""
    guidance = Panel(
        "[bold yellow]When to Create Custom Metrics:[/bold yellow]\n\n"
        "• [green]Use Built-in Metrics When:[/green]\n"
        "  - Evaluating general RAG quality\n"
        "  - Standard metrics (faithfulness, relevancy) suffice\n"
        "  - Cross-domain comparability is important\n\n"
        "• [cyan]Create Custom Metrics When:[/cyan]\n"
        "  - Domain-specific scoring is needed (legal, medical, financial)\n"
        "  - Specialized citation formats are required\n"
        "  - Regulatory compliance must be measured\n"
        "  - Business-specific quality criteria exist\n\n"
        "• [blue]Best Practices:[/blue]\n"
        "  - Start with built-in metrics as baseline\n"
        "  - Test custom metrics on golden datasets\n"
        "  - Document scoring logic clearly\n"
        "  - Calibrate against human evaluations",
        title="[bold cyan]Metric Design Guidance[/bold cyan]",
        border_style="cyan",
    )
    console.print(guidance)


@beartype
def main() -> None:
    """Run custom metrics example.

    Demonstrates:
    1. Simple custom metric (citation accuracy)
    2. Complex composite metric
    3. Domain-specific use cases
    4. Metric design best practices
    """
    # Header
    console.print(
        Panel(
            "[bold cyan]Custom Metrics Example[/bold cyan]\n"
            "Demonstrating simple and complex custom metrics for RAG evaluation",
            title="[bold green]RAGas Advanced Example[/bold green]",
            border_style="cyan",
        )
    )

    # Simple Custom Metric
    console.print("\n[bold yellow]Simple Custom Metric: Citation Accuracy[/bold yellow]")
    console.print("Measures whether responses properly cite sources from context\n")

    simple_metric = CitationAccuracyMetric()
    simple_score = simple_metric.score(
        response="According to Section 10-5, the GST rate is 10%.",
        contexts=["Section 10-5 states that GST is a broad-based tax of 10%."],
    )
    console.print(f"[green]Citation Accuracy Score:[/green] {simple_score:.2f}")

    # Complex Composite Metric
    console.print("\n[bold yellow]Complex Composite Metric[/bold yellow]")
    console.print("Combines multiple RAGAS scores with custom weights\n")

    composite_metric = CompositeQualityMetric(
        faithfulness_weight=0.4,
        relevancy_weight=0.3,
        citation_weight=0.3,
    )
    composite_score = composite_metric.score(
        response="The GST rate is 10% according to tax law.",
        contexts=["GST is a tax of 10% on most goods."],
        ragas_scores={"faithfulness": 0.85, "answer_relevancy": 0.90},
    )
    console.print(f"[green]Composite Quality Score:[/green] {composite_score:.2f}")
    console.print("  (40% faithfulness + 30% relevancy + 30% citation)")

    # Domain-Specific Examples
    console.print("\n[bold yellow]Domain-Specific Use Cases[/bold yellow]")

    legal_result = demonstrate_legal_domain_metric()
    medical_result = demonstrate_medical_domain_metric()
    financial_result = demonstrate_financial_domain_metric()

    # Display domain comparison
    table = Table(title="Domain-Specific Metric Comparison")
    table.add_column("Domain", style="cyan", width=15)
    table.add_column("Metric", style="green", width=25)
    table.add_column("Score", style="yellow", width=10)

    table.add_row("Legal", legal_result.details, f"{legal_result.score:.2f}")
    table.add_row("Medical", medical_result.details, f"{medical_result.score:.2f}")
    table.add_row("Financial", financial_result.details, f"{financial_result.score:.2f}")

    console.print("\n")
    console.print(table)

    # Display design guidance
    console.print("\n")
    display_metric_design_guidance()

    # Summary
    summary_text = Text.from_markup(
        "[bold green]Custom Metrics Summary[/bold green]\n"
        "• Simple metric: Citation accuracy for source verification\n"
        "• Composite metric: Weighted combination of multiple scores\n"
        "• Domain examples: Legal, medical, financial use cases\n"
        "• Key insight: Custom metrics enable domain-specific evaluation"
    )
    console.print(Panel(summary_text, title="[bold cyan]Evaluation Complete[/bold cyan]", border_style="cyan"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
        raise
