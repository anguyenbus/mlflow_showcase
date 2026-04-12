"""
Python runner for JavaScript assertions evaluation.

This script demonstrates JavaScript-based assertions for
cross-platform compatibility using promptfoo.
"""

import os
import subprocess
import sys
from pathlib import Path

from beartype import beartype
from dotenv import load_dotenv
from rich.console import Console

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env file
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

from promptfoo_evaluation.shared.config import (
    get_zhipu_api_key,
    validate_promptfoo_installation,
)

# Initialize rich console
console = Console()


@beartype
def run_promptfoo_eval(
    config_path: str | Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    """
    Run promptfoo evaluation with the given configuration.

    Args:
        config_path: Path to the promptfoo YAML configuration file.
        extra_args: Additional command-line arguments for promptfoo.

    Returns:
        CompletedProcess object with the result.

    Raises:
        subprocess.CalledProcessError: If promptfoo evaluation fails.
        ValueError: If ZHIPU_API_KEY is not set.

    """
    # Validate environment
    zhipu_api_key = get_zhipu_api_key()
    validate_promptfoo_installation()

    # Build command
    cmd = ["npx", "promptfoo", "eval", "-c", str(config_path)]

    if extra_args:
        cmd.extend(extra_args)

    console.print(f"[cyan]Running:[/cyan] {' '.join(cmd)}")

    # Set environment variables for promptfoo
    env = {
        **os.environ,
        "OPENAI_API_KEY": zhipu_api_key,
        "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
    }

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True,
            env=env,
        )
        console.print("[green]Evaluation completed successfully[/green]")
        return result

    except subprocess.CalledProcessError as e:
        console.print("[red]Evaluation failed[/red]")
        console.print(f"Exit code: {e.returncode}")
        raise
    except FileNotFoundError:
        console.print("[red]ERROR:[/red] npx not found")
        console.print("\n[yellow]To fix:[/yellow]")
        console.print("1. Install Node.js from https://nodejs.org/")
        console.print("2. Or install promptfoo globally: npm install -g promptfoo")
        raise


@beartype
def main() -> None:
    """Run the JavaScript assertions example."""
    config_path = Path(__file__).parent / "javascript_asserts.yaml"

    console.print("\n[bold blue]Promptfoo JavaScript Assertions[/bold blue]")
    console.print("=" * 50)

    console.print("\n[cyan]Configuration:[/cyan]")
    console.print(f"  Config: {config_path}")
    console.print("  Model: glm-5")
    console.print("  Tests: 3 test cases")
    console.print("  Assertions: JavaScript-based validation\n")

    try:
        _ = run_promptfoo_eval(config_path)

        console.print("\n[green]Results saved to:[/green]")
        console.print("  promptfoo_results/javascript_asserts/")

        console.print("\n[cyan]View results:[/cyan]")
        console.print("  npx promptfoo view")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
