"""
Python runner for prompt injection evaluation.

This script evaluates LLM resistance to prompt injection attacks
using Garak probes and displays results with rich console output.
"""

import sys
from pathlib import Path
from typing import Any, Final

from beartype import beartype
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# NOTE: Add parent directories to path for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
env_path = project_root / ".env"
load_dotenv(env_path)

from garak_evaluation.shared.config import (
    get_config,
)
from garak_evaluation.shared.console_output import (
    SAFE_THRESHOLD,
    WARNING_THRESHOLD,
    create_evaluation_progress,
    print_error,
    print_interpretation,
    print_metric,
    print_section_header,
    print_success,
)
from garak_evaluation.shared.lifecycle_mapper import (
    get_category_lifecycle_mapping,
    get_owasp_category,
)
from garak_evaluation.shared.probe_manager import (
    get_recommended_probes,
)

# Initialize rich console
console: Final[Console] = Console()

# Constants
TOPIC_NAME: Final[str] = "prompt_injection"
EXPERIMENT_NAME: Final[str] = "garak-prompt-injection"


@beartype
def run_prompt_injection_evaluation(
    probe_names: list[str] | None = None,
    model_name: str = "glm-5-flash",
) -> dict[str, Any]:
    """
    Run prompt injection evaluation using Garak Python API.

    Args:
        probe_names: List of probe names to run. If None, uses recommended probes.
        model_name: Name of the model to evaluate.

    Returns:
        Dictionary with evaluation results and metrics.

    Raises:
        ImportError: If Garak is not installed.
        ValueError: If API key is not configured.

    """
    # Validate configuration
    try:
        config = get_config()
    except ValueError as e:
        print_error(str(e))
        raise

    # Get recommended probes if none specified
    if probe_names is None:
        probe_names = get_recommended_probes(TOPIC_NAME, max_probes=5)

    print_section_header("Prompt Injection Evaluation", level=1)

    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Model: {model_name}")
    console.print(f"  Probes: {len(probe_names)}")
    console.print(f"  OWASP Category: {get_owasp_category(TOPIC_NAME)}")

    # NOTE: This is a mock implementation since actual Garak runs
    # require the model to be available. In production, this would use:
    # import garak.generators
    # import garak.probes
    #
    # generator = garak.generators.Generator(model_name)
    # results = []
    # for probe_name in probe_names:
    #     probe = garak.probes.Probe(probe_name)
    #     result = probe.run(generator)
    #     results.append(result)

    # Mock results for demonstration
    results = _mock_garak_run(probe_names, model_name)

    return results


@beartype
def _mock_garak_run(
    probe_names: list[str],
    model_name: str,
) -> dict[str, Any]:
    """
    Mock Garak evaluation run for demonstration.

    In production, this would use actual Garak API calls.

    Args:
        probe_names: List of probe names.
        model_name: Model name.

    Returns:
        Mock results dictionary.

    """
    console.print("\n[yellow]Note:[/yellow] Running mock evaluation for demonstration")
    console.print("[dim]In production, this would call Garak probes directly[/dim]\n")

    mock_results = {
        "model_name": model_name,
        "probes": [],
        "summary": {
            "total_probes": len(probe_names),
            "overall_pass_rate": 0.0,
            "overall_fail_rate": 0.0,
        },
    }

    total_pass = 0.0
    total_tests = 0

    with create_evaluation_progress(len(probe_names), "Running probes") as progress:
        task = progress.add_task("Evaluating probes", total=len(probe_names))

        for probe in probe_names:
            # Simulate probe execution
            progress.update(task, advance=1)

            # Mock results with varying pass rates
            if "B64" in probe:
                pass_rate = 0.85
            elif "web_injection" in probe:
                pass_rate = 0.65
            elif "Latent" in probe:
                pass_rate = 0.55
            else:
                pass_rate = 0.75

            test_count = 10
            passed = int(pass_rate * test_count)
            failed = test_count - passed

            mock_results["probes"].append({
                "probe_name": probe,
                "pass_rate": pass_rate,
                "fail_rate": 1.0 - pass_rate,
                "total_tests": test_count,
                "passed_tests": passed,
                "failed_tests": failed,
            })

            total_pass += (pass_rate * test_count)
            total_tests += test_count

    # Calculate summary
    if total_tests > 0:
        mock_results["summary"]["overall_pass_rate"] = total_pass / total_tests
        mock_results["summary"]["overall_fail_rate"] = 1.0 - (
            total_pass / total_tests
        )

    return mock_results


@beartype
def display_prompt_injection_results(results: dict[str, Any]) -> None:
    """
    Display prompt injection evaluation results.

    Args:
        results: Evaluation results dictionary.

    """
    print_section_header("Prompt Injection Results", level=2)

    # Create results table
    table = Table(title="Probe Results", show_header=True, header_style="bold cyan")
    table.add_column("Probe", style="cyan", width=35)
    table.add_column("Pass Rate", style="green", width=12)
    table.add_column("Fail Rate", style="red", width=12)
    table.add_column("Tests", width=8)
    table.add_column("Status", width=12)

    for probe_result in results["probes"]:
        probe_name = probe_result["probe_name"]
        pass_rate = probe_result["pass_rate"]
        fail_rate = probe_result["fail_rate"]
        total = probe_result["total_tests"]

        # Determine status
        if pass_rate >= SAFE_THRESHOLD:
            status = "[green]SAFE[/green]"
        elif pass_rate >= WARNING_THRESHOLD:
            status = "[yellow]WARNING[/yellow]"
        else:
            status = "[red]VULNERABLE[/red]"

        table.add_row(
            probe_name,
            f"{pass_rate:.1%}",
            f"{fail_rate:.1%}",
            str(total),
            status,
        )

    console.print(table)

    # Display summary
    print_section_header("Summary Metrics", level=2)

    summary = results["summary"]
    print_metric("Overall Pass Rate", summary["overall_pass_rate"], target=">70%")
    print_metric("Overall Fail Rate", summary["overall_fail_rate"], target="<30%")
    print_metric("Total Probes", summary["total_probes"])

    # Display interpretation
    print_interpretation(
        summary["overall_pass_rate"],
        "Prompt Injection Resistance",
    )


@beartype
def print_lifecycle_context() -> None:
    """Print CPH Sec lifecycle context for this evaluation."""
    print_section_header("CPH Sec Lifecycle Context", level=2)

    mapping = get_category_lifecycle_mapping(TOPIC_NAME)

    console.print(f"Primary Phase: [cyan]{mapping.primary_phase}[/cyan]")
    console.print(f"OWASP Category: {mapping.owasp_category}")

    console.print("\n[bold]Activities in this phase:[/bold]")
    console.print("  - Selecting appropriate Garak probes for injection testing")
    console.print("  - Configuring test parameters (model, detectors)")
    console.print("  - Preparing test data and payloads")
    console.print("  - Setting up monitoring and logging")


@beartype
def main() -> None:
    """Run the prompt injection evaluation."""
    try:
        # Print lifecycle context
        print_lifecycle_context()

        # Run evaluation
        results = run_prompt_injection_evaluation()

        # Display results
        display_prompt_injection_results(results)

        # Print completion message
        print_success("\nEvaluation complete!")

        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  1. Review vulnerable probes above")
        console.print("  2. Check ../prompt_injection/README.md for mitigation strategies")
        console.print("  3. Re-run after implementing mitigations")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
