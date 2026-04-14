"""
Unified analysis script for all Garak evaluation topics.

This script runs all topic evaluations and generates a consolidated
report with CPH Sec lifecycle phase summaries.
"""

import sys
from pathlib import Path
from typing import Any, Final

from beartype import beartype
from dotenv import load_dotenv
from rich.console import Console

# NOTE: Add parent directories to path for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))
env_path = project_root / ".env"
load_dotenv(env_path)

from garak_evaluation.shared.analysis import (
    calculate_aggregated_metrics,
    generate_recommendations,
    get_common_failure_patterns,
)
from garak_evaluation.shared.config import get_config
from garak_evaluation.shared.console_output import (
    print_error,
    print_section_header,
    print_success,
)
from garak_evaluation.shared.probe_manager import get_owasp_category
from garak_evaluation.shared.reporting import (
    create_report_template,
    create_summary_table,
    generate_markdown_report,
)

# Initialize rich console
console: Final[Console] = Console()

# Topics to analyze
TOPICS: Final[tuple[str, ...]] = (
    "prompt_injection",
    "jailbreaks",
    "data_leakage",
    "malicious_content",
)


@beartype
def get_topic_results(topic: str) -> dict[str, Any]:
    """
    Get mock results for a topic.

    In production, this would load actual Garak results.

    Args:
        topic: Topic name.

    Returns:
        Dictionary with topic results.

    """
    # Mock results - in production, load from JSONL files
    from garak_evaluation.shared.result_parser import ProbeResult

    # Different mock results per topic
    topic_configs = {
        "prompt_injection": {"pass_rate": 0.70, "refusal_rate": None},
        "jailbreaks": {"pass_rate": 0.72, "refusal_rate": 0.72},
        "data_leakage": {"pass_rate": 0.78, "leakage_rate": 0.22},
        "malicious_content": {"pass_rate": 0.83, "refusal_rate": 0.83},
    }

    config = topic_configs.get(topic, {"pass_rate": 0.75})
    pass_rate = config["pass_rate"]

    mock_probes = [
        ProbeResult(
            probe_name=f"{topic}.Probe1",
            detector_type="keyword",
            pass_rate=pass_rate + 0.05,
            fail_rate=0.95 - pass_rate,
            total_tests=10,
            passed_tests=int((pass_rate + 0.05) * 10),
            failed_tests=int((0.95 - pass_rate) * 10),
            detector_score=pass_rate + 0.03,
        ),
        ProbeResult(
            probe_name=f"{topic}.Probe2",
            detector_type="classifier",
            pass_rate=pass_rate - 0.05,
            fail_rate=1.05 - pass_rate,
            total_tests=10,
            passed_tests=int((pass_rate - 0.05) * 10),
            failed_tests=int((1.05 - pass_rate) * 10),
            detector_score=pass_rate - 0.02,
        ),
    ]

    metrics = calculate_aggregated_metrics(mock_probes)
    patterns = get_common_failure_patterns(mock_probes)
    recommendations = generate_recommendations(metrics, patterns)

    return {
        "topic": topic,
        "metrics": metrics,
        "patterns": patterns,
        "recommendations": recommendations,
        "owasp_category": get_owasp_category(topic),
    }


@beartype
def analyze_all_topics() -> dict[str, dict[str, Any]]:
    """
    Analyze all Garak evaluation topics.

    Returns:
        Dictionary mapping topic names to their analysis results.

    """
    print_section_header("Garak Comprehensive Analysis", level=1)

    all_results: dict[str, dict[str, Any]] = {}

    for topic in TOPICS:
        console.print(f"\n[cyan]Analyzing:[/cyan] {topic}")
        results = get_topic_results(topic)
        all_results[topic] = results

    return all_results


@beartype
def display_overall_summary(all_results: dict[str, dict[str, Any]]) -> None:
    """
    Display overall summary of all topics.

    Args:
        all_results: Dictionary of all topic results.

    """
    print_section_header("Overall Summary", level=2)

    # Create summary table
    table_data = {}
    for topic, results in all_results.items():
        table_data[topic] = {
            "metrics": results["metrics"],
            "owasp_category": results["owasp_category"],
        }

    summary_table = create_summary_table(table_data)
    console.print(summary_table)

    # Calculate overall metrics across all topics
    total_probes = sum(r["metrics"]["total_probes"] for r in all_results.values())
    total_tests = sum(r["metrics"]["total_tests"] for r in all_results.values())
    total_vulnerable = sum(
        r["metrics"]["vulnerable_probe_count"] for r in all_results.values()
    )

    avg_pass_rate = sum(
        r["metrics"]["overall_pass_rate"] for r in all_results.values()
    ) / len(all_results)

    console.print("\n[bold]Overall Statistics:[/bold]")
    console.print(f"  Total Topics Analyzed: {len(all_results)}")
    console.print(f"  Total Probes: {total_probes}")
    console.print(f"  Total Tests: {total_tests}")
    console.print(f"  Vulnerable Probes: {total_vulnerable}")
    console.print(f"  Average Pass Rate: {avg_pass_rate:.1%}")


@beartype
def display_lifecycle_summary(all_results: dict[str, dict[str, Any]]) -> None:
    """
    Display CPH Sec lifecycle phase summary.

    Args:
        all_results: Dictionary of all topic results.

    """
    print_section_header("CPH Sec Lifecycle Phase Summary", level=2)

    from garak_evaluation.shared.lifecycle_mapper import (
        LIFECYCLE_PHASES,
        get_category_lifecycle_mapping,
    )

    # Group by primary phase
    phase_topics: dict[str, list[str]] = {}
    for topic in TOPICS:
        mapping = get_category_lifecycle_mapping(topic)
        phase = mapping.primary_phase
        if phase not in phase_topics:
            phase_topics[phase] = []
        phase_topics[phase].append(topic)

    # Display by phase
    for phase_id, topics in phase_topics.items():
        phase_info = LIFECYCLE_PHASES.get(phase_id, {})
        console.print(f"\n[bold cyan]{phase_info.get('name', phase_id)}[/bold cyan]")
        console.print(f"[dim]{phase_info.get('description', '')}[/dim]")
        console.print(f"  Topics: {', '.join(topics)}")


@beartype
def generate_consolidated_report(
    all_results: dict[str, dict[str, Any]],
    output_path: Path | str | None = None,
) -> str:
    """
    Generate a consolidated markdown report.

    Args:
        all_results: Dictionary of all topic results.
        output_path: Optional path to save report.

    Returns:
        Markdown report as string.

    """
    # Create report template
    report = create_report_template(
        "garak_comprehensive",
        "Zhipu GLM-5-Flash",
    )

    # Add overall metrics
    total_probes = sum(r["metrics"]["total_probes"] for r in all_results.values())
    total_tests = sum(r["metrics"]["total_tests"] for r in all_results.values())
    avg_pass_rate = sum(
        r["metrics"]["overall_pass_rate"] for r in all_results.values()
    ) / len(all_results)

    report["metrics"] = {
        "total_probes": total_probes,
        "total_tests": total_tests,
        "overall_pass_rate": avg_pass_rate,
        "overall_fail_rate": 1.0 - avg_pass_rate,
    }

    # Aggregate all recommendations
    all_recommendations: list[str] = []
    for results in all_results.values():
        all_recommendations.extend(results["recommendations"])

    # Remove duplicates while preserving order
    seen: set[str] = set()
    unique_recommendations: list[str] = []
    for rec in all_recommendations:
        if rec not in seen:
            seen.add(rec)
            unique_recommendations.append(rec)

    report["recommendations"] = unique_recommendations[:10]  # Top 10

    # Generate markdown
    markdown = generate_markdown_report(report, output_path)

    return markdown


@beartype
def main() -> None:
    """Run comprehensive analysis of all Garak evaluation topics."""
    try:
        # Validate configuration
        try:
            config = get_config()
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

        console.print("\n[bold cyan]Garak Comprehensive Evaluation Analysis[/bold cyan]")
        console.print("=" * 50)

        console.print("\n[yellow]Note:[/yellow] Running mock analysis for demonstration")
        console.print("[dim]In production, this would load actual Garak results[/dim]")

        # Analyze all topics
        all_results = analyze_all_topics()

        # Display summaries
        display_overall_summary(all_results)
        display_lifecycle_summary(all_results)

        # Generate consolidated report
        output_path = Path(__file__).parent / "garak_analysis_report.md"
        generate_consolidated_report(all_results, output_path)

        # Print completion
        print_success("\nAnalysis complete!")

        console.print(f"\n[cyan]Report generated:[/cyan] {output_path}")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  1. Review individual topic READMEs for details")
        console.print("  2. Address recommendations in the report")
        console.print("  3. Re-run evaluations after implementing fixes")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
