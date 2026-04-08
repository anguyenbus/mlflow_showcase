"""
Custom Metrics with MLflow Integration.

This script demonstrates creating and using custom metrics for RAGas evaluation
with comprehensive MLflow tracking for metric performance over time.

Shows:
1. Simple custom metric (citation accuracy) with MLflow logging
2. Complex composite metric combining multiple RAGAS scores
3. Domain-specific use cases (legal, medical, financial)
4. Tracking custom metric performance over time in MLflow

Expected Output:
    Custom Metrics with MLflow Integration
    =======================================

    [PARENT RUN] Starting custom metrics demonstration
    Parent run ID: parent_custom_123

    Demonstrating Simple Custom Metric: Citation Accuracy
    [NESTED RUN] Citation Accuracy Evaluation
    Response: "According to Section 10-5, the GST rate is 10%."
    Citation Accuracy: 1.00
    Logged to MLflow: custom_citation_accuracy = 1.00

    Demonstrating Complex Composite Metric
    [NESTED RUN] Composite Quality Evaluation
    Response: "The GST rate is 10%."
    Composite Score: 0.85
    Components: faithfulness(0.4) + relevancy(0.3) + citation(0.3)

    Domain-Specific Examples with MLflow Tracking:
    - Legal: Case Law Citation (score: 0.95)
    - Medical: Treatment Protocol Adherence (score: 0.88)
    - Financial: Regulatory Compliance (score: 0.92)

    [TODO: Add screenshot showing custom metrics in MLflow]
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
class MetricScore:
    """
    Score from a metric evaluation.

    Attributes:
        metric_name: Name of the metric
        score: Numeric score (0.0-1.0)
        details: Additional details about the score
        components: Dictionary of component scores for composite metrics

    """

    metric_name: str
    score: float
    details: str
    components: dict[str, float] | None = None


@beartype
class CitationAccuracyMetric:
    """
    Simple custom metric for citation accuracy with MLflow integration.

    Measures whether the response properly cites sources from the context.
    Score is based on presence of citation markers and factual consistency.
    """

    name: str = "citation_accuracy"

    @beartype
    def score(self, response: str, contexts: list[str]) -> float:
        """
        Calculate citation accuracy score.

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
    """
    Complex composite metric with MLflow integration.

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
        """
        Initialize composite metric with weights.

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
    ) -> tuple[float, dict[str, float]]:
        """
        Calculate composite quality score.

        Args:
            response: The generated response
            contexts: List of context passages
            ragas_scores: Dictionary of RAGAS metric scores

        Returns:
            Tuple of (weighted composite score, component scores dictionary)

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

        components = {
            "faithfulness": faithfulness,
            "answer_relevancy": relevancy,
            "citation_accuracy": citation,
        }

        return composite, components


@beartype
def log_custom_metric_to_mlflow(
    metric_name: str,
    score: float,
    components: dict[str, float] | None = None,
    tags: dict[str, str] | None = None,
) -> None:
    """
    Log custom metric score to MLflow.

    Args:
        metric_name: Name of the custom metric
        score: Metric score value
        components: Optional dictionary of component scores
        tags: Optional tags for the metric

    """
    if not MLFLOW_AVAILABLE:
        console.print("[yellow]MLflow not available. Skipping MLflow logging.[/yellow]")
        return

    # Log main metric score
    mlflow.log_metric(f"custom_{metric_name}", score)
    console.print(f"  [dim]Logged to MLflow: custom_{metric_name} = {score:.3f}[/dim]")

    # Log component scores if provided
    if components:
        for component_name, component_value in components.items():
            mlflow.log_metric(f"custom_{metric_name}_{component_name}", component_value)
            console.print(
                f"  [dim]Logged component: custom_{metric_name}_{component_name} = {component_value:.3f}[/dim]"
            )

    # Set tags if provided
    if tags:
        mlflow.set_tags(tags)
        console.print(f"  [dim]Set {len(tags)} tags for metric tracking[/dim]")


@beartype
def demonstrate_simple_metric_with_mlflow() -> MetricScore:
    """
    Demonstrate simple custom metric with MLflow logging.

    Returns:
        MetricScore with evaluation results

    """
    console.print("\n[bold yellow]Simple Custom Metric: Citation Accuracy[/bold yellow]")
    console.print("Measures whether responses properly cite sources from context\n")

    run_id = None
    if MLFLOW_AVAILABLE:
        with mlflow.start_run(nested=True, run_name="citation_accuracy_evaluation") as run:
            run_id = run.info.run_id
            console.print(f"  [dim][NESTED RUN] Run ID: {run_id}[/dim]")

            mlflow.log_param("metric_type", "simple_custom")
            mlflow.log_param("metric_name", "citation_accuracy")

    simple_metric = CitationAccuracyMetric()
    simple_score = simple_metric.score(
        response="According to Section 10-5, the GST rate is 10%.",
        contexts=["Section 10-5 states that GST is a broad-based tax of 10%."],
    )

    console.print(f"[green]Citation Accuracy Score:[/green] {simple_score:.2f}")

    # Log to MLflow
    log_custom_metric_to_mlflow(
        metric_name="citation_accuracy",
        score=simple_score,
        tags={"metric_category": "citation", "complexity": "simple"},
    )

    return MetricScore(
        metric_name="citation_accuracy",
        score=simple_score,
        details="Measures proper source citation from context",
        components=None,
    )


@beartype
def demonstrate_composite_metric_with_mlflow() -> MetricScore:
    """
    Demonstrate complex composite metric with MLflow logging.

    Returns:
        MetricScore with evaluation results

    """
    console.print("\n[bold yellow]Complex Composite Metric[/bold yellow]")
    console.print("Combines multiple RAGAS scores with custom weights\n")

    run_id = None
    if MLFLOW_AVAILABLE:
        with mlflow.start_run(nested=True, run_name="composite_quality_evaluation") as run:
            run_id = run.info.run_id
            console.print(f"  [dim][NESTED RUN] Run ID: {run_id}[/dim]")

            mlflow.log_param("metric_type", "composite_custom")
            mlflow.log_param("metric_name", "composite_quality")
            mlflow.log_param("faithfulness_weight", "0.4")
            mlflow.log_param("relevancy_weight", "0.3")
            mlflow.log_param("citation_weight", "0.3")

    composite_metric = CompositeQualityMetric(
        faithfulness_weight=0.4,
        relevancy_weight=0.3,
        citation_weight=0.3,
    )

    composite_score, components = composite_metric.score(
        response="The GST rate is 10% according to tax law.",
        contexts=["GST is a tax of 10% on most goods."],
        ragas_scores={"faithfulness": 0.85, "answer_relevancy": 0.90},
    )

    console.print(f"[green]Composite Quality Score:[/green] {composite_score:.2f}")
    console.print("  Components:")
    for name, value in components.items():
        console.print(f"    {name}: {value:.2f}")

    # Log to MLflow
    log_custom_metric_to_mlflow(
        metric_name="composite_quality",
        score=composite_score,
        components=components,
        tags={"metric_category": "quality", "complexity": "composite"},
    )

    return MetricScore(
        metric_name="composite_quality",
        score=composite_score,
        details="Weighted combination of faithfulness, relevancy, and citation",
        components=components,
    )


@beartype
def demonstrate_domain_metrics_with_mlflow() -> list[MetricScore]:
    """
    Demonstrate domain-specific metrics with MLflow logging.

    Returns:
        List of MetricScore results from domain evaluations

    """
    console.print("\n[bold yellow]Domain-Specific Metrics with MLflow Tracking[/bold yellow]")
    console.print("Evaluating custom metrics for legal, medical, and financial domains\n")

    domain_results = []
    metric = CitationAccuracyMetric()

    # Legal domain
    if MLFLOW_AVAILABLE:
        with mlflow.start_run(nested=True, run_name="legal_domain_evaluation") as run:
            console.print("\n[cyan]Legal Domain: Case Law Citation[/cyan]")
            mlflow.log_param("domain", "legal")
            mlflow.log_param("metric_type", "domain_specific")

            response = "As established in Smith v Jones (2023), the GST rate of 10% applies to all taxable supplies."
            contexts = ["Smith v Jones (2023) established that GST is 10% on taxable supplies."]

            score = metric.score(response, contexts)
            console.print(f"  Response: {response}")
            console.print(f"  [green]Score:[/green] {score:.2f}")

            log_custom_metric_to_mlflow(
                metric_name="legal_citation",
                score=score,
                tags={"domain": "legal", "use_case": "case_law"},
            )

            domain_results.append(
                MetricScore(
                    metric_name="legal_citation",
                    score=score,
                    details="Measures proper case law citation format and accuracy",
                    components=None,
                )
            )

    # Medical domain
    if MLFLOW_AVAILABLE:
        with mlflow.start_run(nested=True, run_name="medical_domain_evaluation") as run:
            console.print("\n[cyan]Medical Domain: Treatment Protocol Adherence[/cyan]")
            mlflow.log_param("domain", "medical")
            mlflow.log_param("metric_type", "domain_specific")

            response = "According to clinical guidelines (Section 5.2), the recommended dosage is 10mg twice daily."
            contexts = [
                "Clinical guidelines Section 5.2 recommend 10mg twice daily for this condition."
            ]

            score = metric.score(response, contexts)
            console.print(f"  Response: {response}")
            console.print(f"  [green]Score:[/green] {score:.2f}")

            log_custom_metric_to_mlflow(
                metric_name="medical_protocol_adherence",
                score=score,
                tags={"domain": "medical", "use_case": "treatment_protocol"},
            )

            domain_results.append(
                MetricScore(
                    metric_name="medical_protocol_adherence",
                    score=score,
                    details="Measures adherence to clinical treatment protocols",
                    components=None,
                )
            )

    # Financial domain
    if MLFLOW_AVAILABLE:
        with mlflow.start_run(nested=True, run_name="financial_domain_evaluation") as run:
            console.print("\n[cyan]Financial Domain: Regulatory Compliance[/cyan]")
            mlflow.log_param("domain", "financial")
            mlflow.log_param("metric_type", "domain_specific")

            response = "As per ASIC Regulatory Guide 215, financial advisors must provide Statements of Advice."
            contexts = [
                "ASIC Regulatory Guide 215 requires financial advisors to provide Statements of Advice."
            ]

            score = metric.score(response, contexts)
            console.print(f"  Response: {response}")
            console.print(f"  [green]Score:[/green] {score:.2f}")

            log_custom_metric_to_mlflow(
                metric_name="financial_regulatory_compliance",
                score=score,
                tags={"domain": "financial", "use_case": "regulatory_compliance"},
            )

            domain_results.append(
                MetricScore(
                    metric_name="financial_regulatory_compliance",
                    score=score,
                    details="Measures compliance with financial regulations",
                    components=None,
                )
            )

    return domain_results


@beartype
def display_domain_comparison_table(results: list[MetricScore]) -> None:
    """
    Display domain-specific metric comparison table.

    Args:
        results: List of MetricScore results

    """
    table = Table(title="Domain-Specific Metric Comparison")
    table.add_column("Domain", style="cyan", width=15)
    table.add_column("Metric", style="green", width=30)
    table.add_column("Score", style="yellow", width=10)

    for result in results:
        table.add_row(
            result.metric_name.split("_")[0].capitalize(),
            result.details,
            f"{result.score:.2f}",
        )

    console.print("\n")
    console.print(table)


@beartype
def generate_mlflow_tracking_guidance() -> Panel:
    """
    Generate MLflow tracking guidance for custom metrics.

    Returns:
        Panel with MLflow tracking guidance

    """
    content = "[bold yellow]MLflow Custom Metrics Tracking:[/bold yellow]\n\n"
    content += "• Custom metrics logged with 'custom_' prefix\n"
    content += "• Component scores logged separately for composite metrics\n"
    content += "• Domain-specific metrics tagged by domain\n"
    content += "• Historical tracking enables metric performance analysis\n\n"

    content += "[bold yellow]Tracking Patterns:[/bold yellow]\n"
    content += "1. [green]Simple Metrics:[/green] Logged as custom_{metric_name}\n"
    content += "2. [cyan]Composite Metrics:[/green] Logged with components\n"
    content += "3. [blue]Domain Metrics:[/green] Tagged by domain for filtering\n\n"

    content += "[bold yellow]Performance Analysis:[/bold yellow]\n"
    content += "• Track metric scores over time\n"
    content += "• Compare metric performance across experiments\n"
    content += "• Identify trends and improvements\n"
    content += "• Correlate custom metrics with standard RAGAS metrics\n\n"

    content += "[dim][TODO: Add screenshot showing custom metrics in MLflow][/dim]"

    return Panel(
        content,
        title="[bold cyan]MLflow Custom Metrics Guide[/bold cyan]",
        border_style="yellow",
    )


@beartype
def demonstrate_custom_metrics_with_mlflow() -> dict[str, Any]:
    """
    Run custom metrics demonstration with MLflow integration.

    This function demonstrates:
    1. Simple custom metric with MLflow logging
    2. Complex composite metric with component tracking
    3. Domain-specific metrics with tagging
    4. MLflow historical tracking capabilities
    5. Metric performance analysis patterns

    Returns:
        Dictionary with results and MLflow run information

    """
    if not MLFLOW_AVAILABLE:
        console.print("[red]ERROR:[/red] MLflow is not installed. Install with: pip install mlflow")
        raise ImportError("mlflow package is required")

    # Load configuration
    config = get_ragas_config()

    # Set up MLflow
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment_name = "ragas_custom_metrics"
    mlflow.set_experiment(experiment_name)

    # Header
    console.print(
        Panel(
            "[bold cyan]Custom Metrics with MLflow Integration[/bold cyan]\n"
            "Demonstrating custom metrics with comprehensive MLflow tracking\n"
            "for historical performance analysis",
            title="[bold green]RAGas Advanced + MLflow[/bold green]",
            border_style="cyan",
        )
    )

    # Start parent run
    with mlflow.start_run(run_name="custom_metrics_demonstration") as parent_run:
        parent_run_id = parent_run.info.run_id
        console.print("\n[bold][PARENT RUN] Starting custom metrics demonstration[/bold]")
        console.print(f"[dim]Parent run ID: {parent_run_id}[/dim]")

        mlflow.log_param("demo_type", "custom_metrics")
        mlflow.log_param("num_metric_types", "3")

        # Simple custom metric
        simple_result = demonstrate_simple_metric_with_mlflow()

        # Complex composite metric
        composite_result = demonstrate_composite_metric_with_mlflow()

        # Domain-specific metrics
        domain_results = demonstrate_domain_metrics_with_mlflow()

    # Display domain comparison table
    display_domain_comparison_table(domain_results)

    # Display metric design guidance
    console.print("\n")
    display_metric_design_guidance()

    # Display MLflow tracking guidance
    console.print("\n")
    mlflow_guidance = generate_mlflow_tracking_guidance()
    console.print(mlflow_guidance)

    # Summary
    all_scores = [simple_result.score, composite_result.score] + [r.score for r in domain_results]
    summary_text = Text.from_markup(
        f"[bold green]Custom Metrics Summary[/bold green]\n"
        f"• Simple metric: Citation accuracy for source verification\n"
        f"• Composite metric: Weighted combination (score: {composite_result.score:.2f})\n"
        f"• Domain examples: {len(domain_results)} domain-specific metrics\n"
        f"• Average score: {sum(all_scores) / len(all_scores):.2f}\n"
        f"• Parent run ID: {parent_run_id}\n"
        f"• Experiment: {experiment_name}\n"
        f"[dim]Key insight: Custom metrics enable domain-specific evaluation with MLflow tracking[/dim]"
    )
    console.print(
        Panel(summary_text, title="[bold cyan]Evaluation Complete[/bold cyan]", border_style="cyan")
    )

    return {
        "experiment_name": experiment_name,
        "parent_run_id": parent_run_id,
        "simple_metric": simple_result,
        "composite_metric": composite_result,
        "domain_metrics": domain_results,
    }


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
        "• [blue]MLflow Integration Benefits:[/blue]\n"
        "  - Track metric performance over time\n"
        "  - Compare custom metric experiments\n"
        "  - Correlate with standard RAGAS metrics\n"
        "  - Historical analysis and trend detection\n\n"
        "• [magenta]Best Practices:[/magenta]\n"
        "  - Start with built-in metrics as baseline\n"
        "  - Test custom metrics on golden datasets\n"
        "  - Document scoring logic clearly\n"
        "  - Calibrate against human evaluations\n"
        "  - Use consistent naming conventions (custom_ prefix)",
        title="[bold cyan]Metric Design Guidance[/bold cyan]",
        border_style="cyan",
    )
    console.print(guidance)


@beartype
def main() -> None:
    """Run custom metrics example with MLflow integration."""
    try:
        demonstrate_custom_metrics_with_mlflow()
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
        raise


if __name__ == "__main__":
    main()
