"""LangChain integration with MLflow tracing example.

This example demonstrates how to use LangChain with MLflow tracking,
including automatic tracing and manual logging.

Expected Output:
--------------
✓ Created LangChain LLM for Zhipu AI model: glm-5
✓ Created LangChain chain

Query 1: What is machine learning?
Response: [AI response about machine learning]

Query 2: What is deep learning?
Response: [AI response about deep learning]

Trace IDs: [trace-ids]
View in MLflow UI to see LangChain chain traces!
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console

import mlflow
from config import get_config
from basics.mlflow_utils import create_experiment
from basics.langchain_integration import create_zhipu_langchain_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize console
console = Console()


def main():
    """Run LangChain integration example with MLflow tracking."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = create_experiment("mlflow-langchain-integration")

    # Enable LangChain autologging for automatic tracing
    mlflow.langchain.autolog()

    console.print("\n[bold cyan]LangChain Integration with MLflow[/bold cyan]\n")
    console.print("✓ Enabled LangChain autologging\n")

    # Create LangChain LLM
    llm = create_zhipu_langchain_llm()
    console.print(f"✓ Created LangChain LLM for Zhipu AI model: {llm.model_name}\n")

    # Create a simple chain
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful assistant. Answer the following question in one sentence.\n\nQuestion: {question}\n\nAnswer:"
    )

    # Build the chain using LCEL (LangChain Expression Language)
    chain = prompt | llm | StrOutputParser()

    console.print("✓ Created LangChain chain\n")
    console.print("Running sample queries...\n")

    # Run queries with MLflow tracking
    with mlflow.start_run():
        queries = [
            "What is machine learning?",
            "What is deep learning?"
        ]

        trace_ids = []

        for i, query in enumerate(queries, 1):
            console.print(f"Query {i}: {query}")

            # Invoke the chain
            response = chain.invoke({"question": query})

            console.print(f"Response: {response}\n")

            # Get the trace ID if available
            try:
                # Search for traces in this run
                traces = mlflow.search_traces(
                    experiment_ids=[experiment.experiment_id],
                    max_results=10
                )
                if traces:
                    trace_ids.append(traces[-1].info.trace_id)
            except Exception as e:
                console.print(f"[dim]Note: Trace search skipped: {e}[/dim]\n")

    console.print("\n[bold green]LangChain integration complete![/bold green]")
    if trace_ids:
        console.print(f"\nTrace IDs: {[t[:8] + '...' for t in trace_ids]}")
    console.print("\nView in MLflow UI to see LangChain chain traces!")
    console.print("You'll see:")
    console.print("  • Chain invocation spans")
    console.print("  • Prompt template inputs")
    console.print("  • LLM call spans")
    console.print("  • Response parsing")


if __name__ == "__main__":
    main()
