"""LangChain autologging example with MLflow.

This example demonstrates automatic LangChain chain tracing
using mlflow.langchain.autolog().

Reference: references/mlflow/examples/tracing/langchain_auto.py

Expected Output:
--------------
Enabled LangChain autologging
Invoking chain with question: What is the capital of Japan?
Invoking chain with question: How many animals are there in the world?
Invoking chain with question: Who is the first person to land on the moon?
Retrieved 3 traces
Now run `mlflow ui` and open MLflow UI to see the trace visualization!
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console

import mlflow
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from basics.langchain_integration import create_zhipu_langchain_llm
from config import get_config


# Initialize console
console = Console()


def main() -> None:
    """Run LangChain autologging example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = mlflow.set_experiment("mlflow-langchain-autologging")

    console.print(f"[green]✓[/green] Experiment ID: {experiment.experiment_id}")

    # Enable LangChain autologging
    # NOTE: This automatically traces all LangChain chain executions
    mlflow.langchain.autolog()

    console.print("[green]✓[/green] Enabled LangChain autologging\n")

    # Build a simple LangChain chain using LCEL syntax
    prompt = PromptTemplate(
        input_variables=["question"],
        template="Please answer this question concisely: {question}"
    )

    llm = create_zhipu_langchain_llm(model="glm-5", temperature=0.9)

    # NOTE: Use LCEL (LangChain Expression Language) for chain composition
    chain = prompt | llm | StrOutputParser()

    # Start MLflow run
    with mlflow.start_run():
        # Invoke the chain multiple times
        questions = [
            "What is the capital of Japan?",
            "How many animals are there in the world?",
            "Who is the first person to land on the moon?",
        ]

        for question in questions:
            console.print(f"[cyan]Invoking chain with question:[/cyan] {question}")
            response = chain.invoke({"question": question})
            console.print(f"[green]Response:[/green] {response}\n")

        # Retrieve traces
        console.print(f"\n[cyan]Searching traces for experiment:[/cyan] {experiment.experiment_id}")

        traces = mlflow.search_traces(
            locations=[experiment.experiment_id],
            max_results=3,
            return_type="list",
        )

        console.print(f"[green]✓[/green] Retrieved {len(traces)} traces")

        # Display trace information
        for trace in traces:
            console.print(f"\n[cyan]Trace ID:[/cyan] {trace.info.trace_id}")
            console.print(f"[cyan]Timestamp:[/cyan] {trace.info.timestamp_ms}")
            console.print(f"[cyan]Spans:[/cyan] {len(trace.data.spans)}")

        console.print(
            "\n[green]Now run `mlflow ui` and open MLflow UI to see trace visualization![/green]"
        )


if __name__ == "__main__":
    main()
