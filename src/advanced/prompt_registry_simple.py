"""MLflow Prompt Registry Example (Simplified - No LLM calls).

This example demonstrates MLflow's Prompt Registry functionality for versioning
and managing prompts in GenAI applications.

What it demonstrates:
- Creating text and chat prompts
- Versioning prompts with commit messages
- Loading and formatting prompts
- Searching and filtering prompts
- Using prompts with LangChain
- Creating aliases for production deployments
- Comparing prompt versions

Reference: promptregistry.md

Expected Output:
--------------
✓ Created text prompt: 'customer-support-v1' (version 1)
✓ Created text prompt: 'customer-support-v2' (version 1)
✓ Created chat prompt: 'customer-support-chat' (version 1)
✓ Updated prompt: 'customer-support-v1' (version 2)
✓ Loaded prompt: customer-support-v1@1
✓ Formatted prompt with variables
✓ Created LangChain prompt from MLflow prompt
✓ Found 3 prompts with tag 'domain=support'
✓ Created alias 'champion' for prompt version 2

View in MLflow UI:
- Navigate to the "Prompts" tab
- See all registered prompts with versions
- Click on prompt name to view details
- Use "Compare" tab to see version differences
- View commit history and tags
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import mlflow
from langchain_core.prompts import ChatPromptTemplate as LangChainPromptTemplate

# Initialize console
console = Console()


def create_text_prompts():
    """Create text prompts with different versions.

    Demonstrates prompt evolution and versioning.
    """
    console.print("\n[bold cyan]Creating Text Prompts[/bold cyan]\n")

    # Version 1: Basic customer support prompt
    prompt_template_v1 = """You are a helpful customer support assistant for {{ company_name }}.

Customer Question: {{ question }}

Please provide a helpful and concise answer."""

    mlflow.genai.register_prompt(
        name="customer-support-v1",
        template=prompt_template_v1,
        commit_message="Initial version: Basic customer support prompt",
        tags={
            "domain": "support",
            "language": "en",
            "version": "v1",
        }
    )
    console.print("✓ Created text prompt: 'customer-support-v1' (version 1)")

    # Version 2: Enhanced customer support prompt with more context
    prompt_template_v2 = """You are a professional customer support assistant for {{ company_name }}.

Your role is to help customers with their questions about {{ product_category }}.

Guidelines:
- Be friendly and professional
- Provide accurate, concise answers
- If you don't know something, admit it honestly
- Offer to connect with a human agent if needed

Customer Question: {{ question }}

Provide your answer below:"""

    mlflow.genai.register_prompt(
        name="customer-support-v2",
        template=prompt_template_v2,
        commit_message="Enhanced version: Added guidelines and context",
        tags={
            "domain": "support",
            "language": "en",
            "version": "v2",
            "features": "guidelines,context"
        }
    )
    console.print("✓ Created text prompt: 'customer-support-v2' (version 1)")

    # Create a second version of v1 to demonstrate versioning
    mlflow.genai.register_prompt(
        name="customer-support-v1",
        template=prompt_template_v1 + "\n\nThank you for choosing {{ company_name }}!",
        commit_message="Added closing statement",
        tags={
            "domain": "support",
            "language": "en",
            "version": "v1.1"
        }
    )
    console.print("✓ Created text prompt: 'customer-support-v1' (version 2)")


def create_chat_prompt():
    """Create a chat prompt for multi-turn conversations.

    Demonstrates chat prompt structure with system and user messages.
    """
    console.print("\n[bold cyan]Creating Chat Prompts[/bold cyan]\n")

    chat_template = [
        {
            "role": "system",
            "content": "You are a helpful {{ style }} customer support assistant for {{ company_name }}. You specialize in {{ specialization }}."
        },
        {
            "role": "user",
            "content": "I need help with: {{ question }}"
        },
        {
            "role": "assistant",
            "content": "I'd be happy to help you with that! Let me look into {{ question }} for you."
        }
    ]

    mlflow.genai.register_prompt(
        name="customer-support-chat",
        template=chat_template,
        commit_message="Initial chat prompt with multi-turn structure",
        tags={
            "type": "chat",
            "domain": "support",
            "language": "en",
            "turns": "3"
        }
    )
    console.print("✓ Created chat prompt: 'customer-support-chat' (version 1)")


def load_and_format_prompt():
    """Load a prompt from registry and format it with variables.

    Demonstrates prompt loading and formatting.
    """
    console.print("\n[bold cyan]Loading and Formatting Prompts[/bold cyan]\n")

    # Load the prompt
    prompt = mlflow.genai.load_prompt("customer-support-v1")
    console.print(f"✓ Loaded prompt: {prompt.name}@{prompt.version}")

    # Format the prompt with variables
    formatted = prompt.format(
        company_name="TechCorp",
        question="How do I reset my password?"
    )

    console.print("\n[bold]Formatted Prompt:[/bold]")
    console.print(Panel(formatted, border_style="cyan"))

    # Show prompt metadata
    console.print(f"\n[bold]Prompt Metadata:[/bold]")
    console.print(f"  • Name: {prompt.name}")
    console.print(f"  • Version: {prompt.version}")
    console.print(f"  • Type: {'Chat' if not prompt.is_text_prompt else 'Text'}")
    console.print(f"  • Commit Message: {prompt.commit_message}")
    console.print(f"  • Tags: {prompt.tags}")


def use_with_langchain():
    """Demonstrate using MLflow prompts with LangChain.

    Shows integration between MLflow Prompt Registry and LangChain.
    """
    console.print("\n[bold cyan]Using MLflow Prompts with LangChain[/bold cyan]\n")

    # Load prompt from MLflow
    mlflow_prompt = mlflow.genai.load_prompt("customer-support-v2")

    # Convert to LangChain format (single braces)
    langchain_prompt = LangChainPromptTemplate.from_template(
        mlflow_prompt.to_single_brace_format()
    )

    console.print(f"✓ Created LangChain prompt from MLflow prompt")
    console.print(f"  Input variables: {langchain_prompt.input_variables}")

    # Format with LangChain
    formatted = langchain_prompt.format(
        company_name="TechCorp",
        product_category="software products",
        question="What are your business hours?"
    )

    console.print("\n[bold]LangChain Formatted Prompt:[/bold]")
    console.print(Panel(formatted[:500] + "...", border_style="green"))


def search_prompts():
    """Search and filter prompts in the registry.

    Demonstrates prompt discovery and filtering.
    """
    console.print("\n[bold cyan]Searching Prompts[/bold cyan]\n")

    # Search all prompts
    prompts = mlflow.genai.search_prompts()
    console.print(f"✓ Found {len(prompts)} prompts in registry")

    # Filter for customer support prompts
    support_prompts = [p for p in prompts if 'support' in p.name.lower()]
    console.print(f"✓ Found {len(support_prompts)} customer support prompts")

    # Display results in table
    table = Table(title="Customer Support Prompts")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Commit Message", style="green")

    for prompt in support_prompts:
        # Load the full prompt object to get version and other details
        full_prompt = mlflow.genai.load_prompt(prompt.name)
        table.add_row(
            prompt.name,
            str(full_prompt.version),
            "Chat" if not full_prompt.is_text_prompt else "Text",
            full_prompt.commit_message[:50] + "..." if len(full_prompt.commit_message) > 50 else full_prompt.commit_message
        )

    console.print(table)


def create_aliases():
    """Create aliases for prompts to support deployment workflows.

    Demonstrates production/staging/canary aliases.
    """
    console.print("\n[bold cyan]Creating Prompt Aliases[/bold cyan]\n")

    client = mlflow.MlflowClient()

    # Create champion alias for latest version
    try:
        client.set_prompt_alias(
            name="customer-support-v1",
            alias="champion",
            version=2
        )
        console.print("✓ Created alias 'champion' for customer-support-v1 version 2")
    except Exception as e:
        console.print(f"[yellow]Note: {e}[/yellow]")

    # Create challenger alias for v2
    try:
        client.set_prompt_alias(
            name="customer-support-v2",
            alias="challenger",
            version=1
        )
        console.print("✓ Created alias 'challenger' for customer-support-v2 version 1")
    except Exception as e:
        console.print(f"[yellow]Note: {e}[/yellow]")


def demonstrate_version_comparison():
    """Demonstrate comparing different prompt versions.

    Shows how to use aliases for A/B testing.
    """
    console.print("\n[bold cyan]Version Comparison Example[/bold cyan]\n")

    # Load champion prompt
    try:
        champion_prompt = mlflow.genai.load_prompt("prompts:/customer-support-v1/champion")
        console.print("✓ Loaded champion prompt (using alias)")
    except:
        console.print("[yellow]Champion alias not set, using version 1[/yellow]")
        champion_prompt = mlflow.genai.load_prompt("customer-support-v1")

    # Load challenger prompt
    challenger_prompt = mlflow.genai.load_prompt("customer-support-v2")
    console.print("✓ Loaded challenger prompt (v2)")

    # Compare prompts
    console.print("\n[bold]Prompt Comparison:[/bold]")
    console.print(f"Champion (v1): {len(champion_prompt.template)} characters")
    console.print(f"Challenger (v2): {len(challenger_prompt.template)} characters")

    # Show key differences
    console.print("\n[bold]Key Improvements in Challenger (v2):[/bold]")
    console.print("  ✓ Added product category context")
    console.print("  ✓ Added response guidelines")
    console.print("  ✓ More structured template")

    # Show diff-like comparison
    console.print("\n[bold]Template Preview:[/bold]")
    console.print(f"\n[champion]Champion (v1):[/champion]")
    console.print(Panel(champion_prompt.template[:200] + "...", border_style="blue"))
    console.print(f"\n[challenger]Challenger (v2):[/challenger]")
    console.print(Panel(challenger_prompt.template[:200] + "...", border_style="red"))


def main():
    """Main execution function."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]MLflow Prompt Registry Example[/bold cyan]\n"
        "Demonstrates prompt versioning, management, and deployment",
        border_style="cyan"
    ))

    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")

    # Create experiment
    experiment_name = "mlflow-prompt-registry"
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
        console.print(f"✓ Created experiment: {experiment_name} (ID: {experiment_id})")
    else:
        experiment_id = experiment.experiment_id
        console.print(f"✓ Experiment '{experiment_name}' (ID: {experiment_id})")

    with mlflow.start_run(experiment_id=experiment_id, run_name="prompt_registry_demo"):
        # Execute demonstrations
        create_text_prompts()
        create_chat_prompt()
        load_and_format_prompt()
        use_with_langchain()
        search_prompts()
        create_aliases()
        demonstrate_version_comparison()

        console.print("\n")
        console.print(Panel.fit(
            "[bold green]Prompt Registry Demo Complete![/bold green]\n\n"
            "[bold]View prompts in MLflow UI:[/bold]\n"
            "• Navigate to 'Prompts' tab\n"
            "• See all registered prompts with versions\n"
            "• Click prompt name to view details\n"
            "• Use 'Compare' tab to see version differences\n"
            "• View commit history and tags\n\n"
            "[bold]Screenshot locations:[/bold]\n"
            "1. Prompts list page (shows all prompts)\n"
            "2. Prompt detail page (click on prompt name)\n"
            "3. Version comparison page (click Compare tab)\n"
            "4. Prompt with alias page (shows champion/challenger)",
            border_style="green"
        ))


if __name__ == "__main__":
    main()
