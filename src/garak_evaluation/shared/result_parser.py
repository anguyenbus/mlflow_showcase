"""
JSONL result parser for Garak evaluation outputs.

This module provides utilities for parsing Garak JSONL output files,
extracting pass/fail metrics, calculating detector scores, and
aggregating vulnerability metrics.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from beartype import beartype
from rich.console import Console
from rich.table import Table

# Initialize rich console
console: Final[Console] = Console()


@beartype
@dataclass(slots=True)
class ProbeResult:
    """
    Result from a single Garak probe run.

    Attributes:
        probe_name: Name of the probe that was run.
        detector_type: Type of detector used.
        pass_rate: Proportion of tests that passed (0.0 to 1.0).
        fail_rate: Proportion of tests that failed (0.0 to 1.0).
        total_tests: Total number of test cases run.
        passed_tests: Number of tests that passed.
        failed_tests: Number of tests that failed.
        detector_score: Average detector score.

    """

    probe_name: str
    detector_type: str
    pass_rate: float
    fail_rate: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    detector_score: float


@beartype
@dataclass(slots=True)
class GarakEvaluationSummary:
    """
    Summary of a Garak evaluation run.

    Attributes:
        total_probes: Total number of probes run.
        total_tests: Total number of test cases across all probes.
        overall_pass_rate: Overall pass rate across all probes.
        overall_fail_rate: Overall fail rate across all probes.
        probe_results: List of individual probe results.
        vulnerable_probes: List of probes with high failure rates.

    """

    total_probes: int
    total_tests: int
    overall_pass_rate: float
    overall_fail_rate: float
    probe_results: list[ProbeResult]
    vulnerable_probes: list[str]


@beartype
class GarakResultParser:
    """
    Parser for Garak JSONL evaluation results.

    This class reads and parses Garak's JSONL output files,
    extracting metrics and generating summary statistics.

    Attributes:
        results_path: Path to the Garak JSONL results file.
        raw_results: List of parsed JSONL entries.

    Example:
        >>> parser = GarakResultParser("garak_results.jsonl")
        >>> summary = parser.get_summary()
        >>> print(f"Overall pass rate: {summary.overall_pass_rate:.2%}")

    """

    __slots__ = ("results_path", "raw_results", "_summary")

    def __init__(self, results_path: Path | str) -> None:
        """
        Initialize the parser with a results file path.

        Args:
            results_path: Path to the Garak JSONL results file.

        Raises:
            FileNotFoundError: If the results file doesn't exist.
            ValueError: If the results file is not valid JSONL.

        """
        self.results_path = Path(results_path)
        self.raw_results: list[dict[str, Any]] = []
        self._summary: GarakEvaluationSummary | None = None

        if not self.results_path.exists():
            raise FileNotFoundError(f"Results file not found: {results_path}")

        self._load_results()

    def _load_results(self) -> None:
        """Load and parse JSONL results from file."""
        try:
            with open(self.results_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.raw_results.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSONL in results file: {e}") from e

    def get_summary(self, high_failure_threshold: float = 0.5) -> GarakEvaluationSummary:
        """
        Generate a summary of the Garak evaluation results.

        Args:
            high_failure_threshold: Threshold for considering a probe
                as having high failure rate (default 0.5 = 50%).

        Returns:
            GarakEvaluationSummary with aggregated metrics.

        """
        if self._summary is not None:
            return self._summary

        probe_results: list[ProbeResult] = []
        total_tests = 0
        total_passed = 0
        vulnerable_probes: list[str] = []

        for entry in self.raw_results:
            probe_name = entry.get("probe", "unknown")
            detector_type = entry.get("detector", "unknown")

            # Extract test results
            total = entry.get("total", 0)
            passed = entry.get("passed", 0)
            failed = entry.get("failed", total - passed)

            # Calculate rates
            pass_rate = passed / total if total > 0 else 0.0
            fail_rate = failed / total if total > 0 else 0.0

            # Detector score (if available)
            detector_score = entry.get("detector_score", pass_rate)

            result = ProbeResult(
                probe_name=probe_name,
                detector_type=detector_type,
                pass_rate=pass_rate,
                fail_rate=fail_rate,
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                detector_score=detector_score,
            )
            probe_results.append(result)

            total_tests += total
            total_passed += passed

            # Track vulnerable probes
            if fail_rate >= high_failure_threshold:
                vulnerable_probes.append(probe_name)

        overall_pass_rate = total_passed / total_tests if total_tests > 0 else 0.0
        overall_fail_rate = 1.0 - overall_pass_rate

        self._summary = GarakEvaluationSummary(
            total_probes=len(probe_results),
            total_tests=total_tests,
            overall_pass_rate=overall_pass_rate,
            overall_fail_rate=overall_fail_rate,
            probe_results=probe_results,
            vulnerable_probes=vulnerable_probes,
        )

        return self._summary

    def get_pass_fail_rates(self) -> dict[str, dict[str, float]]:
        """
        Get pass/fail rates grouped by probe.

        Returns:
            Dictionary mapping probe names to their pass/fail rates.

        """
        summary = self.get_summary()
        rates: dict[str, dict[str, float]] = {}

        for result in summary.probe_results:
            rates[result.probe_name] = {
                "pass_rate": result.pass_rate,
                "fail_rate": result.fail_rate,
            }

        return rates

    def get_detector_scores(self) -> dict[str, float]:
        """
        Get detector scores for all probes.

        Returns:
            Dictionary mapping probe names to detector scores.

        """
        summary = self.get_summary()
        return {result.probe_name: result.detector_score for result in summary.probe_results}

    def get_aggregated_metrics(self) -> dict[str, float]:
        """
        Get aggregated metrics across all probes.

        Returns:
            Dictionary with aggregated metrics.

        """
        summary = self.get_summary()

        return {
            "total_probes": float(summary.total_probes),
            "total_tests": float(summary.total_tests),
            "overall_pass_rate": summary.overall_pass_rate,
            "overall_fail_rate": summary.overall_fail_rate,
            "vulnerable_probe_count": float(len(summary.vulnerable_probes)),
        }

    def classify_severity(
        self,
        low_threshold: float = 0.1,
        medium_threshold: float = 0.3,
        high_threshold: float = 0.5,
    ) -> dict[str, str]:
        """
        Classify vulnerability severity for each probe.

        Args:
            low_threshold: Failure rate threshold for low severity.
            medium_threshold: Failure rate threshold for medium severity.
            high_threshold: Failure rate threshold for high severity.

        Returns:
            Dictionary mapping probe names to severity levels.

        """
        summary = self.get_summary()
        severity: dict[str, str] = {}

        for result in summary.probe_results:
            if result.fail_rate >= high_threshold:
                severity[result.probe_name] = "HIGH"
            elif result.fail_rate >= medium_threshold:
                severity[result.probe_name] = "MEDIUM"
            elif result.fail_rate >= low_threshold:
                severity[result.probe_name] = "LOW"
            else:
                severity[result.probe_name] = "MINIMAL"

        return severity


@beartype
def parse_garak_results(results_path: Path | str) -> GarakResultParser:
    """
    Parse Garak results from file path.

    Convenience function for creating a GarakResultParser.

    Args:
        results_path: Path to the Garak JSONL results file.

    Returns:
        GarakResultParser instance for accessing metrics.

    Example:
        >>> parser = parse_garak_results("garak_results.jsonl")
        >>> summary = parser.get_summary()
        >>> print(f"Pass rate: {summary.overall_pass_rate:.2%}")

    """
    return GarakResultParser(results_path)


@beartype
def display_results_table(summary: GarakEvaluationSummary) -> None:
    """
    Display Garak evaluation results in a formatted table.

    Args:
        summary: GarakEvaluationSummary to display.

    """
    table = Table(title="Garak Evaluation Results", show_header=True, header_style="bold cyan")
    table.add_column("Probe", style="cyan", width=30)
    table.add_column("Pass Rate", style="green", width=12)
    table.add_column("Fail Rate", style="red", width=12)
    table.add_column("Tests", width=8)
    table.add_column("Severity", width=10)

    # Get severity classification
    parser = GarakResultParser.__new__(GarakResultParser)
    parser._summary = summary
    severity = parser.classify_severity()

    for result in summary.probe_results:
        severity_level = severity.get(result.probe_name, "UNKNOWN")
        severity_style = {
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "blue",
            "MINIMAL": "green",
        }.get(severity_level, "white")

        table.add_row(
            result.probe_name,
            f"{result.pass_rate:.2%}",
            f"{result.fail_rate:.2%}",
            str(result.total_tests),
            f"[{severity_style}]{severity_level}[/{severity_style}]",
        )

    console.print(table)

    # Display summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Total Probes: {summary.total_probes}")
    console.print(f"  Total Tests: {summary.total_tests}")
    console.print(f"  Overall Pass Rate: [green]{summary.overall_pass_rate:.2%}[/green]")
    console.print(f"  Overall Fail Rate: [red]{summary.overall_fail_rate:.2%}[/red]")
    console.print(f"  Vulnerable Probes: {len(summary.vulnerable_probes)}")
