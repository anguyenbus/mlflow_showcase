#!/usr/bin/env python
"""Example execution script for MLflow LLM educational repository.

Runs all examples in sequence and verifies expected outputs.
"""

import subprocess
import sys
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.table import Table

console = Console()


# Example scripts to run in order
EXAMPLES = [
    # Basics
    ("Basics - MLflow Tracking", "src/basics/mlflow_tracking.py"),
    ("Basics - Model Logging", "src/basics/model_logging.py"),
    ("Basics - Tracing Decorators", "src/basics/tracing_decorators.py"),
    ("Basics - Metrics Helpers", "src/basics/metrics_helpers.py"),

    # Intermediate
    ("Intermediate - Manual Spans", "src/intermediate/tracing_manual_spans.py"),
    ("Intermediate - Nested Spans", "src/intermediate/tracing_nested.py"),
    ("Intermediate - Distributed Tracing", "src/intermediate/tracing_distributed.py"),
    ("Intermediate - LangChain Tracing", "src/intermediate/tracing_langchain.py"),
    ("Intermediate - QA Evaluation", "src/intermediate/evaluate_qa.py"),

    # Advanced
    ("Advanced - LLM Judge", "src/advanced/evaluate_llm_judge.py"),
    ("Advanced - RAG Tracing", "src/advanced/rag/rag_tracing.py"),
]


def run_example(name: str, script: str) -> bool:
    """Run a single example script.

    Args:
        name: Example name for display.
        script: Path to the script.

    Returns:
        True if successful, False otherwise.
    """
    rprint(f"\n[bold cyan]Running:[/bold cyan] {name}")
    rprint(f"[dim]Script:[/dim] {script}")

    try:
        result = subprocess.run(
            ["uv", "run", "python", script],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            rprint("[green]SUCCESS[/green]")
            # Show first few lines of output
            if result.stdout:
                lines = result.stdout.split("\n")[:5]
                for line in lines:
                    if line.strip():
                        rprint(f"[dim]  {line}[/dim]")
            return True
        else:
            rprint("[red]FAILED[/red]")
            if result.stderr:
                rprint(f"[red]Error:[/red] {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        rprint("[red]TIMEOUT[/red]")
        return False
    except Exception as e:
        rprint(f"[red]ERROR:[/red] {e}")
        return False


def main() -> None:
    """Run all examples and report results."""
    rprint("[bold cyan]MLflow LLM Educational Repository - Example Execution[/bold cyan]")
    rprint("=" * 80)

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        rprint("\n[yellow]Warning:[/yellow] .env file not found")
        rprint("[yellow]Please copy .env.example to .env and add your ZHIPU_API_KEY[/yellow]")
        rprint("\n[yellow]Run:[/yellow] cp .env.example .env")
        rprint("[yellow]Then edit .env to add your API key[/yellow]")
        sys.exit(1)

    # Run examples
    results = []
    for name, script in EXAMPLES:
        # Check if script exists
        script_path = Path(script)
        if not script_path.exists():
            rprint(f"[yellow]SKIP:[/yellow] {name} (script not found)")
            results.append((name, "SKIP"))
            continue

        success = run_example(name, script)
        results.append((name, "SUCCESS" if success else "FAILED"))

    # Print summary table
    rprint("\n[bold cyan]Execution Summary[/bold cyan]")
    rprint("=" * 80)

    table = Table(title="Example Execution Results")
    table.add_column("Example", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")

    success_count = 0
    fail_count = 0
    skip_count = 0

    for name, status in results:
        if status == "SUCCESS":
            table.add_row(name, "[green]SUCCESS[/green]")
            success_count += 1
        elif status == "FAILED":
            table.add_row(name, "[red]FAILED[/red]")
            fail_count += 1
        else:
            table.add_row(name, "[yellow]SKIP[/yellow]")
            skip_count += 1

    console.print(table)

    # Print summary
    rprint(f"\n[bold]Total:[/bold] {len(results)} examples")
    rprint(f"[green]Success:[/green] {success_count}")
    rprint(f"[red]Failed:[/red] {fail_count}")
    rprint(f"[yellow]Skipped:[/yellow] {skip_count}")

    # Provide next steps
    rprint("\n[bold cyan]Next Steps[/bold cyan]")
    rprint("-" * 40)
    rprint("1. View results in MLflow UI: [cyan]mlflow ui[/cyan]")
    rprint("2. Open browser to: [cyan]http://localhost:5000[/cyan]")
    rprint("3. Check experiments, traces, and evaluation results")

    # Exit with appropriate code
    if fail_count > 0:
        rprint(f"\n[red]Some examples failed. Please check the errors above.[/red]")
        sys.exit(1)
    else:
        rprint(f"\n[green]All examples executed successfully![/green]")
        sys.exit(0)


if __name__ == "__main__":
    main()
