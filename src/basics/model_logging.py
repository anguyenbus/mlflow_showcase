"""Model logging example with LangChain and MLflow.

This example demonstrates how to log LangChain chains with MLflow
and load them back for inference.

Expected Output:
--------------
✓ Experiment 'mlflow-model-logging' (ID: 1234567890123456)
✓ Logged LangChain model
Model URI: runs:/9876543210987654321/model
✓ Loaded model from MLflow
Response: LangChain is a framework for developing applications...
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
from basics.mlflow_utils import create_experiment


def main() -> None:
    """Run model logging example."""
    console = Console()

    # Create experiment
    experiment = create_experiment("mlflow-model-logging")

    # Create LangChain chain using LCEL syntax
    prompt = PromptTemplate(
        input_variables=["question"],
        template="Answer this question concisely: {question}"
    )

    llm = create_zhipu_langchain_llm(model="glm-5", temperature=0.7)

    # NOTE: Use LCEL (LangChain Expression Language) syntax
    chain = prompt | llm | StrOutputParser()

    # Start MLflow run
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        console.print(f"[green]✓[/green] Started run: {run_id}")

        # Log the LangChain chain
        model_info = mlflow.langchain.log_model(
            chain,
            "model",
            input_example={"question": "What is LangChain?"},
        )

        console.print("[green]✓[/green] Logged LangChain model")
        console.print(f"[cyan]Model URI:[/cyan] {model_info.model_uri}")

        # Load the model back
        loaded_model = mlflow.pyfunc.load_model(model_info.model_uri)
        console.print("[green]✓[/green] Loaded model from MLflow")

        # Make predictions
        response = loaded_model.predict({"question": "What is LangChain?"})
        console.print(f"\n[green]Response:[/green] {response}")


if __name__ == "__main__":
    main()
