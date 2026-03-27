"""MLflow Prompt Registry Example.

This example demonstrates MLflow's Prompt Registry functionality for versioning,
managing, and deploying prompts in GenAI applications.

What it demonstrates:
- Creating text and chat prompts
- Versioning prompts with commit messages
- Loading and using prompts with LLMs
- Searching and filtering prompts
- Using prompts with LangChain
- Prompt comparison and A/B testing
- Aliasing for production deployments

Reference: promptregistry.md

Expected Output:
--------------
✓ Created text prompt: 'customer-support-v1' (version 1)
✓ Created chat prompt: 'customer-support-chat' (version 1)
✓ Created text prompt: 'customer-support-v2' (version 1)
✓ Loaded prompt: customer-support-v1@1
✓ Formatted prompt with variables
✓ Created LangChain prompt from MLflow prompt
✓ Found 3 prompts with tag 'domain=support'
✓ Created alias 'production' for prompt version 2

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

from pathlib import Path
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import mlflow
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate as LangChainPromptTemplate
from config import get_config, get_evaluation_data_path
from basics.langchain_integration import create_zhipu_langchain_llm

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

    mlflow.genai.create_prompt(
        name="customer-support-v1",
        template=prompt_template_v1,
        commit_message="Initial version: Basic customer support prompt",
        tags={
            "domain": "support",
            "language": "en",
            "version": "v1",
            "company": "{{ company_name }}"
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

    mlflow.genai.create_prompt(
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
    mlflow.genai.create_prompt(
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

    mlflow.genai.create_prompt(
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


def load_and_use_prompt():
    """Load a prompt from registry and use it with an LLM.

    Demonstrates prompt loading and formatting.
    """
    console.print("\n[bold cyan]Loading and Using Prompts[/bold cyan]\n")

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

    # Use with Zhipu LLM
    llm = create_zhipu_langchain_llm()

    with mlflow.start_run(nested=True):
        mlflow.log_param("prompt_name", "customer-support-v1")
        mlflow.log_param("prompt_version", prompt.version)

        response = llm.invoke(formatted)
        console.print("\n[bold]LLM Response:[/bold]")
        console.print(Panel(str(response.content), border_style="green"))

        mlflow.log_text(str(response.content), "llm_response.txt")


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

    # Create LangChain chain
    llm = create_zhipu_langchain_llm()
    chain = langchain_prompt | llm

    # Invoke the chain
    with mlflow.start_run(nested=True):
        response = chain.invoke({
            "company_name": "TechCorp",
            "product_category": "software products",
            "question": "What are your business hours?"
        })

        console.print("\n[bold]LangChain Response:[/bold]")
        console.print(Panel(str(response.content), border_style="green"))


def search_prompts():
    """Search and filter prompts in the registry.

    Demonstrates prompt discovery and filtering.
    """
    console.print("\n[bold cyan]Searching Prompts[/bold cyan]\n")

    # Search by tag
    prompts = mlflow.genai.search_prompts(filter_string="domain='support'")
    console.print(f"✓ Found {len(prompts)} prompts with tag 'domain=support'")

    # Display results in table
    table = Table(title="Customer Support Prompts")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Commit Message", style="green")

    for prompt in prompts:
        table.add_row(
            prompt.name,
            str(prompt.version),
            "Chat" if not prompt.is_text_prompt else "Text",
            prompt.commit_message[:50] + "..." if len(prompt.commit_message) > 50 else prompt.commit_message
        )

    console.print(table)


def create_aliases():
    """Create aliases for prompts to support deployment workflows.

    Demonstrates production/staging/canary aliases.
    """
    console.print("\n[bold cyan]Creating Prompt Aliases[/bold cyan]\n")

    client = mlflow.MlflowClient()

    # Create production alias
    try:
        client.set_prompt_alias(
            name="customer-support-v1",
            alias="production",
            version=2
        )
        console.print("✓ Created alias 'production' for customer-support-v1 version 2")
    except Exception as e:
        console.print(f"[yellow]Note: {e}[/yellow]")

    # Create staging alias
    try:
        client.set_prompt_alias(
            name="customer-support-v2",
            alias="staging",
            version=1
        )
        console.print("✓ Created alias 'staging' for customer-support-v2 version 1")
    except Exception as e:
        console.print(f"[yellow]Note: {e}[/yellow]")


def demonstrate_ab_testing():
    """Demonstrate A/B testing with different prompt versions.

    Shows how to use aliases for A/B testing.
    """
    console.print("\n[bold cyan]A/B Testing Example[/bold cyan]\n")

    # Load production prompt
    try:
        production_prompt = mlflow.genai.load_prompt("prompts:/customer-support-v1/production")
        console.print("✓ Loaded production prompt (alias)")
    except:
        console.print("[yellow]Production alias not set, using version 1[/yellow]")
        production_prompt = mlflow.genai.load_prompt("customer-support-v1")

    # Load staging prompt
    staging_prompt = mlflow.genai.load_prompt("customer-support-v2")
    console.print("✓ Loaded staging prompt (v2)")

    # Compare prompts
    console.print("\n[bold]Prompt Comparison:[/bold]")
    console.print(f"Production: {len(production_prompt.template)} characters")
    console.print(f"Staging: {len(staging_prompt.template)} characters")

    # Show key differences
    console.print("\n[bold]Key Improvements in Staging:[/bold]")
    console.print("  ✓ Added product category context")
    console.print("  ✓ Added response guidelines")
    console.print("  ✓ More structured template")


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
        load_and_use_prompt()
        use_with_langchain()
        search_prompts()
        create_aliases()
        demonstrate_ab_testing()

        console.print("\n")
        console.print(Panel.fit(
            "[bold green]Prompt Registry Demo Complete![/bold green]\n\n"
            "View prompts in MLflow UI:\n"
            "• Navigate to 'Prompts' tab\n"
            "• See all registered prompts with versions\n"
            "• Click prompt name to view details\n"
            "• Use 'Compare' tab to see version differences",
            border_style="green"
        ))


if __name__ == "__main__":
    main()
