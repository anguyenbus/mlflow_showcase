"""Display all prompts from the registry with full details."""

import mlflow
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()
mlflow.set_tracking_uri("http://localhost:5000")

# Get all prompts
prompts = mlflow.genai.search_prompts()

console.print("\n")
console.print(Panel.fit(
    "[bold cyan]MLflow Prompt Registry - All Prompts[/bold cyan]",
    border_style="cyan"
))

# Create table for overview
table = Table(title="Registered Prompts Overview")
table.add_column("Name", style="cyan", width=25)
table.add_column("Type", style="yellow")
table.add_column("Latest Version", style="magenta")
table.add_column("Template Length", style="green")

for prompt_search in prompts:
    prompt = mlflow.genai.load_prompt(prompt_search.name)
    table.add_row(
        prompt.name,
        "Chat" if not prompt.is_text_prompt else "Text",
        str(prompt.version),
        str(len(prompt.template))
    )

console.print(table)

# Show details for each prompt
console.print("\n")

for prompt_search in prompts:
    prompt = mlflow.genai.load_prompt(prompt_search.name)

    console.print(Panel.fit(
        f"[bold]{prompt.name}[/bold] (Version {prompt.version})\n\n"
        f"Type: {'Chat' if not prompt.is_text_prompt else 'Text'}\n"
        f"Commit: {prompt.commit_message}\n"
        f"Tags: {prompt.tags}\n\n"
        f"[bold]Template:[/bold]\n{prompt.template}",
        border_style="blue",
        title=prompt.name,
        width=120
    ))
    console.print("\n")
