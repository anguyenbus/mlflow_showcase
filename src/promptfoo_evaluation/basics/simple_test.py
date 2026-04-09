"""
Python runner for simple promptfoo evaluation.

This script demonstrates how to run promptfoo evaluations from Python
using the subprocess module with proper error handling and output capture.
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
# Look for .env in the project root (4 levels up from this file)
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
    # Use npx to run promptfoo without installation
    cmd = ["npx", "promptfoo", "eval", "-c", str(config_path)]

    if extra_args:
        cmd.extend(extra_args)

    console.print(f"[cyan]Running:[/cyan] {' '.join(cmd)}")

    # Set environment variables for promptfoo
    # Map ZHIPU_API_KEY to OPENAI_API_KEY for OpenAI-compatible provider
    # Also set OPENAI_BASE_URL to point to Zhipu AI's servers
    env = {
        **os.environ,
        "OPENAI_API_KEY": zhipu_api_key,
        "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
    }

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        console.print("[green]Evaluation completed successfully[/green]")

        # Print output
        if result.stdout:
            console.print(result.stdout)

        return result

    except subprocess.CalledProcessError as e:
        console.print("[red]Evaluation failed[/red]")
        console.print(f"Exit code: {e.returncode}")

        if e.stderr:
            console.print(f"Error output:\n{e.stderr}")

        raise
    except FileNotFoundError:
        console.print("[red]ERROR:[/red] npx not found")
        console.print("\n[yellow]To fix:[/yellow]")
        console.print("1. Install Node.js from https://nodejs.org/")
        console.print("2. Or install promptfoo globally: npm install -g promptfoo")
        raise


@beartype
def main() -> None:
    """Run the simple test example."""
    config_path = Path(__file__).parent / "simple_test.yaml"

    console.print("\n[bold blue]Promptfoo Simple Test[/bold blue]")
    console.print("=" * 40)

    console.print("\n[cyan]Configuration:[/cyan]")
    console.print(f"  Config: {config_path}")
    console.print("  Model: glm-5")
    console.print("  Tests: 4 assertions\n")

    try:
        # NOTE: result is returned but not used - output is printed in run_promptfoo_eval
        _ = run_promptfoo_eval(config_path)

        console.print("\n[green]Results saved to:[/green]")
        console.print("  promptfoo_results/simple_test/")

        console.print("\n[cyan]View results:[/cyan]")
        console.print("  npx promptfoo view")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
