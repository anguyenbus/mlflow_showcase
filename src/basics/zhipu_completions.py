"""Basic Zhipu AI GLM-5 completions example.

This example demonstrates how to use the Zhipu AI client
to generate text completions with GLM-5 models.

Expected Output:
--------------
Initialized Zhipu AI client with model: glm-5-flash
Prompt: What is machine learning?
Response: Machine learning is a subset of artificial intelligence...
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from basics.zhipu_client import create_zhipu_client


def main() -> None:
    """Run basic completion example."""
    # Create Zhipu AI client
    client = create_zhipu_client(model="glm-5")

    # Generate completion
    prompt = "What is machine learning? Explain in one sentence."
    console.print(f"\n[yellow]Prompt:[/yellow] {prompt}")

    response = client.complete(prompt, temperature=0.7)

    console.print(f"\n[green]Response:[/green] {response}")


if __name__ == "__main__":
    from rich.console import Console

    console = Console()
    main()
