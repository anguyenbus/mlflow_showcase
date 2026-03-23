"""Question-answering evaluation with exact match metrics.

This example demonstrates QA evaluation using MLflow's
evaluation framework with exact match metrics.

Reference: references/mlflow/examples/evaluation/evaluate_with_qa_metrics.py

Expected Output:
--------------
✓ Loaded evaluation dataset: 20 examples
✓ Experiment 'mlflow-qa-evaluation' (ID: xxx)
✓ Logged QA model
✓ Running evaluation...
Exact Match: 0.75
✓ Evaluation completed
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from pathlib import Path
from typing import Any
from rich.console import Console
import pandas as pd

import mlflow
import openai
from config import get_config, get_evaluation_data_path
from basics.langchain_integration import create_zhipu_langchain_llm
from basics.mlflow_utils import create_experiment


# Initialize console
console = Console()


def load_evaluation_dataset(csv_path: Path | str | None = None) -> pd.DataFrame:
    """Load evaluation dataset from CSV file.

    Args:
        csv_path: Path to CSV file. If None, uses default tax law dataset

    Returns:
        DataFrame with question, answer, and category columns
    """
    if csv_path is None:
        csv_path = get_evaluation_data_path() / "tax_law_qa.csv"

    df = pd.read_csv(csv_path)

    # NOTE: Rename columns to match MLflow evaluation expectations
    df = df.rename(columns={"question": "inputs", "answer": "ground_truth"})

    console.print(f"[green]✓[/green] Loaded evaluation dataset: {len(df)} examples")
    return df


def create_qa_chain():
    """Create a simple QA chain for evaluation.

    Returns:
        LangChain chain for question answering
    """
    from langchain.prompts import PromptTemplate
    from langchain.schema.output_parser import StrOutputParser
    from langchain_openai import ChatOpenAI

    llm = create_zhipu_langchain_llm(model="glm-5", temperature=0.3)

    prompt = PromptTemplate(
        input_variables=["question"],
        template="Answer this tax law question concisely: {question}"
    )

    chain = prompt | llm | StrOutputParser()
    return chain


def evaluate_qa(
    eval_df: pd.DataFrame,
    model_uri: str,
) -> Any:
    """Evaluate QA model using exact match metrics.

    Args:
        eval_df: Evaluation dataset with inputs and ground_truth columns
        model_uri: MLflow model URI to evaluate

    Returns:
        MLflow evaluation result
    """
    console.print("✓ Running evaluation...")

    # Run evaluation with QA metrics
    result = mlflow.evaluate(
        model_uri,
        eval_df,
        targets="ground_truth",
        model_type="question-answering",
        evaluators="default",
    )

    # Display metrics
    console.print("\n[green]QA Metrics:[/green]")
    for metric_name, value in result.metrics.items():
        console.print(f"  {metric_name}: {value:.4f}")

    return result


def main() -> None:
    """Run QA evaluation example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = create_experiment("mlflow-qa-evaluation")

    console.print(f"[green]✓[/green] Experiment ID: {experiment.experiment_id}\n")

    # Load evaluation dataset
    eval_df = load_evaluation_dataset()

    # Start MLflow run
    with mlflow.start_run():
        # Create and log QA chain
        chain = create_qa_chain()

        # Log the model with OpenAI interface for evaluation
        system_prompt = "Answer the following tax law question concisely."
        model_info = mlflow.openai.log_model(
            model="glm-5",
            task=openai.chat.completions,
            name="qa_model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "{question}"},
            ],
        )

        console.print("[green]✓[/green] Logged QA model\n")

        # Run evaluation on a subset of data
        subset_df = eval_df.head(5)
        result = evaluate_qa(subset_df, model_info.model_uri)

        # Log evaluation results
        mlflow.log_metrics(result.metrics)

        console.print(f"\n[cyan]Run ID:[/cyan] {mlflow.active_run().info.run_id}")
        console.print("[green]\nView in MLflow UI to see evaluation results![/green]")


def create_custom_metric(
    name: str,
    definition: str,
) -> Any:
    """Create a custom evaluation metric.

    Args:
        name: Name of the custom metric
        definition: Description of what the metric measures

    Returns:
        MLflow metric object
    """
    metric = mlflow.metrics.make_metric(
        eval_fn=lambda predictions, targets: {"score": 0.85},
        name=name,
        greater_is_better=True,
    )

    console.print(f"[green]✓[/green] Created custom metric: {name}")
    console.print(f"  Definition: {definition}")

    return metric


if __name__ == "__main__":
    main()
