"""
Reporting utilities for Garak evaluation results.

This module provides functions for generating reports, mapping
to CPH Sec lifecycle phases, and creating remediation recommendations.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final

from beartype import beartype
from rich.console import Console
from rich.table import Table

# NOTE: Import analysis modules
from garak_evaluation.shared.lifecycle_mapper import (
    LIFECYCLE_PHASES,
    get_category_lifecycle_mapping,
    get_remediation_guidance,
)

# Initialize rich console
console: Final[Console] = Console()


@beartype
@dataclass(frozen=True, slots=True)
class ReportSection:
    """
    A section of a Garak evaluation report.

    Attributes:
        title: Section title.
        content: Section content (can be string, table, or list).
        severity: Optional severity level for the section.

    """

    title: str
    content: Any
    severity: str | None = None


@beartype
def create_report_template(
    evaluation_name: str,
    model_name: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """
    Create a report template with metadata.

    Args:
        evaluation_name: Name of the evaluation.
        model_name: Name of the model evaluated.
        timestamp: Optional timestamp (defaults to current time).

    Returns:
        Dictionary with report template.

    Example:
        >>> template = create_report_template("prompt_injection", "glm-5-flash")
        >>> template["evaluation_name"]
        'prompt_injection'

    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    return {
        "evaluation_name": evaluation_name,
        "model_name": model_name,
        "timestamp": timestamp,
        "sections": [],
        "metadata": {
            "generator": "Garak Evaluation Tutorials",
            "version": "1.0.0",
        },
    }


@beartype
def add_lifecycle_section(
    report: dict[str, Any],
    category: str,
) -> dict[str, Any]:
    """
    Add CPH Sec lifecycle phase information to report.

    Args:
        report: Report dictionary.
        category: Probe category name.

    Returns:
        Updated report dictionary.

    Example:
        >>> report = create_report_template("test", "model")
        >>> report = add_lifecycle_section(report, "prompt_injection")
        >>> "lifecycle" in report
        True

    """
    mapping = get_category_lifecycle_mapping(category)
    primary_phase = LIFECYCLE_PHASES.get(mapping.primary_phase, {})

    report["lifecycle"] = {
        "category": category,
        "owasp_category": mapping.owasp_category,
        "primary_phase": mapping.primary_phase,
        "secondary_phases": mapping.secondary_phases,
        "primary_phase_name": primary_phase.get("name", "Unknown"),
        "primary_phase_description": primary_phase.get("description", ""),
    }

    return report


@beartype
def add_owasp_mapping_section(
    report: dict[str, Any],
    category: str,
) -> dict[str, Any]:
    """
    Add OWASP LLM Top 10 mapping to report.

    Args:
        report: Report dictionary.
        category: Probe category name.

    Returns:
        Updated report dictionary.

    """
    mapping = get_category_lifecycle_mapping(category)

    report["owasp_mapping"] = {
        "category": category,
        "owasp_category": mapping.owasp_category,
        "description": _get_owasp_description(mapping.owasp_category),
    }

    return report


@beartype
def _get_owasp_description(owasp_category: str) -> str:
    """
    Get description for OWASP LLM Top 10 category.

    Args:
        owasp_category: OWASP category identifier.

    Returns:
        Description of the category.

    """
    descriptions = {
        "LLM01": "Prompt Injection: Input designed to cause LLM to bypass controls.",
        "LLM02": "Insecure Output Handling: LLM output passed directly to downstream systems.",
        "LLM03": "Training Data Poisoning: Manipulation of training data or model.",
        "LLM04": "Model Denial of Service: Resource exhaustion attacks.",
        "LLM05": "Supply Chain Vulnerabilities: Vulnerabilities in model dependencies.",
        "LLM06": "Sensitive Information Disclosure: Exposure of sensitive data.",
        "LLM07": "Insecure Plugin Design: Insecure plugin implementations.",
        "LLM08": "Excessive Agency: LLM given too much autonomy.",
        "LLM09": "Overreliance: Overdependence on LLM output.",
        "LLM10": "Model Theft: Unauthorized access to model weights.",
    }

    return descriptions.get(owasp_category, "Unknown category")


@beartype
def create_remediation_section(
    category: str,
    severity: str = "MEDIUM",
) -> dict[str, str]:
    """
    Create remediation recommendations section.

    Args:
        category: Probe category name.
        severity: Severity level (HIGH, MEDIUM, LOW).

    Returns:
        Dictionary with remediation recommendations.

    Example:
        >>> remediation = create_remediation_section("prompt_injection", "HIGH")
        >>> "immediate" in remediation
        True

    """
    guidance = get_remediation_guidance(category, severity)

    return {
        "category": category,
        "severity": severity,
        "immediate_action": guidance.get("immediate", "Review findings"),
        "recommended_actions": guidance.get("recommended", "Document findings"),
        "optional_actions": guidance.get("optional", "Monitor for related issues"),
    }


@beartype
def generate_markdown_report(
    report: dict[str, Any],
    output_path: Path | str | None = None,
) -> str:
    """
    Generate a markdown report from report dictionary.

    Args:
        report: Report dictionary.
        output_path: Optional path to save report.

    Returns:
        Markdown report as string.

    Example:
        >>> report = create_report_template("test", "model")
        >>> markdown = generate_markdown_report(report)
        >>> "# Garak Evaluation Report" in markdown
        True

    """
    lines: list[str] = []

    # Header
    lines.append("# Garak Evaluation Report")
    lines.append("")
    lines.append(f"**Evaluation:** {report.get('evaluation_name', 'Unknown')}")
    lines.append(f"**Model:** {report.get('model_name', 'Unknown')}")
    lines.append(f"**Timestamp:** {report.get('timestamp', 'Unknown')}")
    lines.append("")

    # OWASP Mapping
    if "owasp_mapping" in report:
        owasp = report["owasp_mapping"]
        lines.append("## OWASP LLM Top 10 Mapping")
        lines.append("")
        lines.append(f"- **Category:** {owasp.get('owasp_category', 'Unknown')}")
        lines.append(f"- **Description:** {owasp.get('description', 'Unknown')}")
        lines.append("")

    # Lifecycle Phase
    if "lifecycle" in report:
        lifecycle = report["lifecycle"]
        lines.append("## CPH Sec AI Red Team Lifecycle")
        lines.append("")
        lines.append(f"- **Primary Phase:** {lifecycle.get('primary_phase_name', 'Unknown')}")
        lines.append(f"- **Description:** {lifecycle.get('primary_phase_description', 'Unknown')}")
        lines.append("")

    # Metrics
    if "metrics" in report:
        metrics = report["metrics"]
        lines.append("## Metrics Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Probes | {metrics.get('total_probes', 0)} |")
        lines.append(f"| Total Tests | {metrics.get('total_tests', 0)} |")
        lines.append(
            f"| Overall Pass Rate | {metrics.get('overall_pass_rate', 0):.1%} |"
        )
        lines.append(
            f"| Overall Fail Rate | {metrics.get('overall_fail_rate', 0):.1%} |"
        )
        lines.append("")

        # Severity distribution
        severity_dist = metrics.get('severity_distribution', {})
        if severity_dist:
            lines.append("### Severity Distribution")
            lines.append("")
            lines.append("| Severity | Count |")
            lines.append("|----------|-------|")
            for severity, count in severity_dist.items():
                lines.append(f"| {severity} | {count} |")
            lines.append("")

    # Recommendations
    if "recommendations" in report:
        recommendations = report["recommendations"]
        lines.append("## Recommendations")
        lines.append("")
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    # Remediation
    if "remediation" in report:
        remediation = report["remediation"]
        lines.append("## Remediation")
        lines.append("")
        lines.append(f"**Severity:** {remediation.get('severity', 'Unknown')}")
        lines.append("")
        lines.append("### Immediate Action")
        lines.append(f"{remediation.get('immediate_action', 'None')}")
        lines.append("")
        lines.append("### Recommended Actions")
        lines.append(f"{remediation.get('recommended_actions', 'None')}")
        lines.append("")

    markdown = "\n".join(lines)

    # Save to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(markdown)
        console.print(f"[green]Report saved to:[/green] {output_path}")

    return markdown


@beartype
def create_summary_table(
    all_results: dict[str, dict[str, Any]],
) -> Table:
    """
    Create a summary table for multiple evaluation results.

    Args:
        all_results: Dictionary mapping topic names to their results.

    Returns:
        Rich Table object with summary.

    Example:
        >>> results = {"prompt_injection": {...}, "jailbreaks": {...}}
        >>> table = create_summary_table(results)

    """
    table = Table(title="Garak Evaluation Summary", show_header=True, header_style="bold cyan")
    table.add_column("Topic", style="cyan", width=20)
    table.add_column("OWASP", style="green", width=8)
    table.add_column("Pass Rate", style="green", width=12)
    table.add_column("Vulnerable", style="red", width=10)
    table.add_column("Severity", width=10)

    for topic, results in all_results.items():
        metrics = results.get("metrics", {})
        pass_rate = metrics.get("overall_pass_rate", 0.0)
        vulnerable = metrics.get("vulnerable_probe_count", 0)
        owasp = results.get("owasp_category", "Unknown")

        # Determine overall severity
        if pass_rate < 0.5:
            severity = "[red]HIGH[/red]"
        elif pass_rate < 0.7:
            severity = "[yellow]MEDIUM[/yellow]"
        else:
            severity = "[green]LOW[/green]"

        table.add_row(
            topic.title(),
            owasp,
            f"{pass_rate:.1%}",
            str(vulnerable),
            severity,
        )

    return table


@beartype
def print_lifecycle_report(
    category: str,
    metrics: dict[str, Any],
) -> None:
    """
    Print a lifecycle-focused report for a category.

    Args:
        category: Probe category name.
        metrics: Aggregated metrics.

    """
    mapping = get_category_lifecycle_mapping(category)
    primary_phase = LIFECYCLE_PHASES.get(mapping.primary_phase, {})

    console.print(f"\n[bold cyan]CPH Sec Lifecycle Report: {category}[/bold cyan]")
    console.print("=" * (30 + len(category)))

    console.print(f"\n[bold]Primary Phase:[/bold] {primary_phase.get('name', 'Unknown')}")
    console.print(f"[dim]{primary_phase.get('description', '')}[/dim]")

    console.print(f"\n[bold]OWASP Category:[/bold] {mapping.owasp_category}")

    console.print("\n[bold]Evaluation Results:[/bold]")
    console.print(f"  Overall Pass Rate: {metrics.get('overall_pass_rate', 0):.1%}")
    console.print(f"  Vulnerable Probes: {metrics.get('vulnerable_probe_count', 0)}")

    # Get remediation guidance
    severity = "HIGH" if metrics.get('overall_pass_rate', 1.0) < 0.5 else "MEDIUM"
    guidance = get_remediation_guidance(category, severity)

    console.print("\n[bold]Remediation:[/bold]")
    console.print(f"  {guidance.get('immediate', 'Review findings')}")
