"""
Convenience script to run all advanced promptfoo evaluations.

This script runs all four advanced evaluation topics in sequence:
1. RAG Pipeline Evaluation
2. Hallucination Prevention
3. Temperature Optimization
4. Factuality Evaluation

Results are logged to MLflow for centralized tracking.
"""

import subprocess
import sys
from pathlib import Path
from typing import Final

from beartype import beartype
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

from promptfoo_evaluation.shared.config import get_zhipu_api_key

# Initialize rich console
console: Final[Console] = Console()

# Topics to run
TOPICS: Final[tuple[str, ...]] = (
    "rag_pipeline",
    "prevent_hallucination",
    "choosing_right_temperature",
    "evaluating_factuality",
)


@beartype
def print_banner() -> None:
    """Print the welcome banner."""
    console.print(
        Panel.fit(
            "[bold cyan]Advanced Promptfoo Evaluation Suite[/bold cyan]\n"
            "Running all 4 advanced evaluation topics",
            border_style="cyan",
        )
    )


@beartype
def validate_environment() -> bool:
    """
    Validate that required environment is set up.

    Returns:
        True if environment is valid, False otherwise.

    """
    try:
        # Check API key
        _ = get_zhipu_api_key()
        console.print("[green]Environment validated[/green]")
        return True
    except ValueError as e:
        console.print(f"[red]Environment validation failed:[/red] {e}")
        return False


@beartype
def run_topic(topic: str) -> bool:
    """
    Run a single advanced topic evaluation.

    Args:
        topic: Name of the topic directory.

    Returns:
        True if evaluation succeeded, False otherwise.

    """
    topic_dir = Path(__file__).parent / topic
    test_file = topic_dir / f"{topic}_test.py"

    if not test_file.exists():
        console.print(f"[yellow]Warning:[/yellow] Test file not found: {test_file}")
        return False

    console.print(f"\n[bold cyan]Running:[/bold cyan] {topic}")

    try:
        result = subprocess.run(
            ["uv", "run", "python", str(test_file)],
            cwd=str(topic_dir),
            check=True,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed:[/red] {topic} (exit code: {e.returncode})")
        return False
    except FileNotFoundError:
        console.print(f"[yellow]Warning:[/yellow] uv not found, trying direct python")
        try:
            result = subprocess.run(
                ["python", str(test_file)],
                cwd=str(topic_dir),
                check=True,
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            console.print(f"[red]Failed:[/red] {topic}")
            return False


@beartype
def print_summary(results: dict[str, bool]) -> None:
    """
    Print summary of all evaluation results.

    Args:
        results: Dictionary mapping topic names to success status.

    """
    console.print("\n" + "=" * 50)
    console.print("[bold]Evaluation Summary[/bold]")
    console.print("=" * 50 + "\n")

    for topic, success in results.items():
        status = "[green]PASSED[/green]" if success else "[red]FAILED[/red]"
        console.print(f"  {topic:35} {status}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)

    console.print(f"\n  Total: {passed}/{total} evaluations passed")

    if passed == total:
        console.print("\n[green]All evaluations completed successfully![/green]")
    else:
        console.print("\n[yellow]Some evaluations failed. Check output above for details.[/yellow]")

    console.print("\n[cyan]View results in MLflow:[/cyan]")
    console.print("  mlflow ui")
    console.print("\n[cyan]View results in promptfoo:[/cyan]")
    console.print("  npx promptfoo view")


@beartype
def main() -> int:
    """
    Run all advanced evaluation topics.

    Returns:
        Exit code (0 for success, 1 for failure).

    """
    print_banner()

    if not validate_environment():
        return 1

    results: dict[str, bool] = {}

    for topic in TOPICS:
        results[topic] = run_topic(topic)

    print_summary(results)

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
