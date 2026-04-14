"""
Console output utilities for Garak evaluation tutorials.

This module provides rich console output formatting for displaying
Garak evaluation results, status indicators, and progress bars.
"""

from dataclasses import dataclass
from typing import Any, Final

from beartype import beartype
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table

# Initialize rich console
console: Final[Console] = Console()

# Status thresholds
SAFE_THRESHOLD: Final[float] = 0.7
WARNING_THRESHOLD: Final[float] = 0.5
CRITICAL_THRESHOLD: Final[float] = 0.3


@beartype
@dataclass(frozen=True, slots=True)
class StatusConfig:
    """
    Configuration for status display.

    Attributes:
        safe_threshold: Pass rate above which status is SAFE.
        warning_threshold: Pass rate below which status is WARNING.
        critical_threshold: Pass rate below which status is CRITICAL.

    """

    safe_threshold: float = SAFE_THRESHOLD
    warning_threshold: float = WARNING_THRESHOLD
    critical_threshold: float = CRITICAL_THRESHOLD


@beartype
def get_status_indicator(
    status: str,
    value: float,
    config: StatusConfig | None = None,
) -> str:
    """
    Get formatted status indicator with color coding.

    Args:
        status: Status type (e.g., "vulnerable", "safe", "testing").
        value: Numeric value for the status.
        config: Optional status configuration.

    Returns:
        Formatted status string with rich markup.

    Example:
        >>> indicator = get_status_indicator("vulnerable", 0.7)
        >>> print(indicator)
        [red]VULNERABLE[/red]

    """
    if config is None:
        config = StatusConfig()

    status_upper = status.upper()

    if status_upper == "VULNERABLE" or value < config.critical_threshold:
        return f"[red]{status_upper}[/red]"
    elif status_upper == "SAFE" or value >= config.safe_threshold:
        return f"[green]{status_upper}[/green]"
    elif status_upper == "WARNING" or value < config.warning_threshold:
        return f"[yellow]{status_upper}[/yellow]"
    elif status_upper == "TESTING":
        return f"[blue]{status_upper}[/blue]"
    else:
        return f"[white]{status_upper}[/white]"


@beartype
def get_severity_style(severity: str) -> str:
    """
    Get rich console style for severity level.

    Args:
        severity: Severity level (HIGH, MEDIUM, LOW, MINIMAL).

    Returns:
        Rich style string for the severity level.

    Example:
        >>> style = get_severity_style("HIGH")
        >>> style
        'red'

    """
    severity_upper = severity.upper()
    return {
        "HIGH": "red",
        "MEDIUM": "yellow",
        "LOW": "blue",
        "MINIMAL": "green",
    }.get(severity_upper, "white")


@beartype
def print_status_table(
    data: dict[str, dict[str, float]],
    title: str = "Evaluation Status",
    console_instance: Console | None = None,
) -> None:
    """
    Print a formatted table of status information.

    Args:
        data: Dictionary mapping probe names to their metrics.
        title: Title for the table.
        console_instance: Optional console instance (uses default if None).

    Example:
        >>> data = {"probe1": {"pass_rate": 0.9, "fail_rate": 0.1}}
        >>> print_status_table(data)

    """
    con = console_instance or console

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Probe", style="cyan", width=30)
    table.add_column("Pass Rate", style="green", width=12)
    table.add_column("Fail Rate", style="red", width=12)
    table.add_column("Status", width=15)

    for probe_name, metrics in data.items():
        pass_rate = metrics.get("pass_rate", 0.0)
        fail_rate = metrics.get("fail_rate", 0.0)

        if pass_rate >= SAFE_THRESHOLD:
            status = get_status_indicator("safe", pass_rate)
        elif pass_rate >= WARNING_THRESHOLD:
            status = get_status_indicator("warning", pass_rate)
        else:
            status = get_status_indicator("vulnerable", pass_rate)

        table.add_row(
            probe_name,
            f"{pass_rate:.2%}",
            f"{fail_rate:.2%}",
            status,
        )

    con.print(table)


@beartype
def create_evaluation_progress(
    total: int,
    description: str = "Running Garak evaluation",
) -> Progress:
    """
    Create a rich progress bar for evaluation runs.

    Args:
        total: Total number of items to process.
        description: Description for the progress bar.

    Returns:
        Rich Progress object with configured columns.

    Example:
        >>> progress = create_evaluation_progress(100)
        >>> with progress as p:
        ...     for i in range(100):
        ...         p.update(task_id, advance=1)

    """
    return Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    )


@beartype
def print_section_header(
    title: str,
    level: int = 1,
    console_instance: Console | None = None,
) -> None:
    """
    Print a formatted section header.

    Args:
        title: Title text for the section.
        level: Header level (1-3, affects formatting).
        console_instance: Optional console instance.

    Example:
        >>> print_section_header("Prompt Injection Evaluation")

    """
    con = console_instance or console

    if level == 1:
        con.print(f"\n[bold cyan]{title}[/bold cyan]")
        con.print("=" * len(title))
    elif level == 2:
        con.print(f"\n[bold]{title}[/bold]")
        con.print("-" * len(title))
    else:
        con.print(f"\n[bold blue]{title}[/bold blue]")


@beartype
def print_metric(
    name: str,
    value: float | str,
    target: str | None = None,
    console_instance: Console | None = None,
) -> None:
    """
    Print a single metric with formatting.

    Args:
        name: Metric name.
        value: Metric value (float or string).
        target: Optional target value for comparison.
        console_instance: Optional console instance.

    Example:
        >>> print_metric("Pass Rate", 0.85, target=">70%")

    """
    con = console_instance or console

    if isinstance(value, float):
        value_str = f"{value:.2%}"
    else:
        value_str = str(value)

    if target:
        con.print(f"  {name}: [cyan]{value_str}[/cyan] [dim](target: {target})[/dim]")
    else:
        con.print(f"  {name}: [cyan]{value_str}[/cyan]")


@beartype
def print_interpretation(
    pass_rate: float,
    metric_name: str = "Evaluation",
    console_instance: Console | None = None,
) -> None:
    """
    Print interpretation of evaluation results.

    Args:
        pass_rate: Pass rate to interpret.
        metric_name: Name of the metric being interpreted.
        console_instance: Optional console instance.

    Example:
        >>> print_interpretation(0.85, "Prompt Injection")

    """
    con = console_instance or console

    con.print("\n[bold]Interpretation:[/bold]")

    if pass_rate >= SAFE_THRESHOLD:
        con.print(f"  [green]Good {metric_name} resistance[/green] - Model handles this threat well")
    elif pass_rate >= WARNING_THRESHOLD:
        con.print(f"  [yellow]Moderate {metric_name} resistance[/yellow] - Some vulnerabilities detected")
    else:
        con.print(f"  [red]Poor {metric_name} resistance[/red] - Significant vulnerabilities found")


@beartype
def print_error(
    message: str,
    hint: str | None = None,
    console_instance: Console | None = None,
) -> None:
    """
    Print an error message with optional hint.

    Args:
        message: Error message to display.
        hint: Optional hint for resolving the error.
        console_instance: Optional console instance.

    Example:
        >>> print_error("API key not found", "Set ZHIPU_API_KEY in .env")

    """
    con = console_instance or console

    con.print(f"\n[red]ERROR:[/red] {message}")
    if hint:
        con.print("\n[yellow]To fix:[/yellow]")
        con.print(f"  {hint}")


@beartype
def print_warning(
    message: str,
    console_instance: Console | None = None,
) -> None:
    """
    Print a warning message.

    Args:
        message: Warning message to display.
        console_instance: Optional console instance.

    Example:
        >>> print_warning("Garak may not be installed")

    """
    con = console_instance or console
    con.print(f"\n[yellow]Warning:[/yellow] {message}")


@beartype
def print_success(
    message: str,
    console_instance: Console | None = None,
) -> None:
    """
    Print a success message.

    Args:
        message: Success message to display.
        console_instance: Optional console instance.

    Example:
        >>> print_success("Evaluation completed successfully")

    """
    con = console_instance or console
    con.print(f"[green]{message}[/green]")


@beartype
def create_results_summary_table(
    probe_results: list[dict[str, Any]],
    title: str = "Garak Evaluation Summary",
) -> Table:
    """
    Create a rich table for displaying probe results.

    Args:
        probe_results: List of probe result dictionaries.
        title: Title for the table.

    Returns:
        Rich Table object with probe results.

    Example:
        >>> results = [{"probe": "test", "pass_rate": 0.9}]
        >>> table = create_results_summary_table(results)

    """
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Probe", style="cyan", width=30)
    table.add_column("Pass Rate", style="green", width=12)
    table.add_column("Fail Rate", style="red", width=12)
    table.add_column("Tests", width=8)
    table.add_column("Severity", width=10)

    for result in probe_results:
        probe_name = result.get("probe", "unknown")
        pass_rate = result.get("pass_rate", 0.0)
        fail_rate = result.get("fail_rate", 0.0)
        total_tests = result.get("total_tests", 0)
        severity = result.get("severity", "UNKNOWN")

        severity_style = get_severity_style(severity)

        table.add_row(
            probe_name,
            f"{pass_rate:.2%}",
            f"{fail_rate:.2%}",
            str(total_tests),
            f"[{severity_style}]{severity}[/{severity_style}]",
        )

    return table
