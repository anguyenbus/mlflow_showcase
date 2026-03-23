"""LLM-as-a-judge evaluation example.

This example demonstrates using GLM-5 to evaluate the quality
of responses using qualitative assessment.

Expected Output:
--------------
✓ Created LLM judge
✓ Evaluating responses with LLM judge...
Response 1 score: 8.5/10
Response 2 score: 7.0/10
Average quality score: 7.75
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console
from typing import Any
from typing import Any
import pandas as pd

import mlflow
from config import get_config
from basics.langchain_integration import create_zhipu_langchain_llm
from basics.mlflow_utils import create_experiment


# Initialize console
console = Console()


JUDGE_PROMPT = """You are an expert evaluator of AI responses. Please assess the quality of the following response to the given question.

Question: {question}

Response: {response}

Evaluate based on:
1. Accuracy: Is the information correct?
2. Completeness: Does it answer the question fully?
3. Clarity: Is the response clear and well-structured?

Provide a score from 1-10 and a brief justification.
Format your response as:
Score: X/10
Justification: [your justification]"""


def create_llm_judge():
    """Create an LLM judge for evaluation.

    Returns:
        LangChain LLM configured as a judge
    """
    # NOTE: Use lower temperature for more consistent evaluations
    judge_llm = create_zhipu_langchain_llm(
        model="glm-5",
        temperature=0.3,
    )

    console.print("[green]✓[/green] Created LLM judge\n")
    return judge_llm


def llm_judge_eval_fn(
    predictions: list[str],
    targets: list[str],
    judge_llm: Any,
    questions: list[str],
    **kwargs: Any,
) -> dict[str, float]:
    """Evaluate responses using LLM as a judge.

    Args:
        predictions: List of model predictions
        targets: List of ground truth answers
        judge_llm: LLM to use for judging
        questions: List of questions asked
        **kwargs: Additional arguments

    Returns:
        Dictionary with metric scores
    """
    scores = []

    for question, prediction in zip(questions, predictions):
        # Create judge prompt
        prompt = JUDGE_PROMPT.format(
            question=question,
            response=prediction,
        )

        # Get evaluation from judge LLM
        evaluation = judge_llm.invoke(prompt)

        # Extract score from evaluation
        # NOTE: In production, use more robust parsing
        import re
        score_match = re.search(r"Score:\s*(\d+(?:\.\d+)?)", evaluation)
        if score_match:
            score = float(score_match.group(1))
            scores.append(score)

            # Display score
            console.print(f"  Response score: {score}/10")

    avg_score = sum(scores) / len(scores) if scores else 0.0
    return {"llm_judge_score": avg_score}


def main() -> None:
    """Run LLM-as-a-judge evaluation example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = create_experiment("mlflow-llm-judge")

    console.print(f"[green]✓[/green] Experiment ID: {experiment.experiment_id}\n")

    # Create LLM judge
    judge_llm = create_llm_judge()

    # Create evaluation dataset
    eval_df = pd.DataFrame({
        "questions": [
            "What is the current company tax rate in Australia?",
            "Explain what GST is and when it was introduced in Australia.",
        ],
        "inputs": [
            "What is the current company tax rate in Australia?",
            "Explain what GST is and when it was introduced in Australia.",
        ],
        "ground_truth": [
            "The company tax rate is 30% for most companies.",
            "GST is a 10% tax introduced on 1 July 2000.",
        ],
    })

    # Create mock predictions (in reality, these would come from your model)
    predictions = [
        "The current company tax rate in Australia is 30% for most companies. "
        "However, base rate entities with turnover under $50 million pay 25%.",
        "GST stands for Goods and Services Tax. It is a 10% tax on most goods "
        "and services in Australia. It was introduced on July 1, 2000.",
    ]

    console.print("✓ Evaluating responses with LLM judge...\n")

    # Start MLflow run
    with mlflow.start_run():
        # Log a dummy model
        model_info = mlflow.langchain.log_model(
            lambda x: {"output": predictions[0]},
            "llm_judge_model",
            input_example={"inputs": eval_df["inputs"][0]},
        )

        # Create custom metric with LLM judge
        llm_judge_metric = mlflow.metrics.make_metric(
            eval_fn=lambda predictions, targets, **kwargs: llm_judge_eval_fn(
                predictions,
                targets,
                judge_llm,
                eval_df["questions"].tolist(),
                **kwargs,
            ),
            name="llm_judge_score",
            greater_is_better=True,
        )

        # Run evaluation
        result = mlflow.evaluate(
            model_info.model_uri,
            eval_df,
            targets="ground_truth",
            model_type="question-answering",
            evaluators="default",
            custom_metrics=[llm_judge_metric],
        )

        # Display results
        avg_score = result.metrics.get("llm_judge_score", 0)
        console.print(f"\n[green]Average quality score:[/green] {avg_score:.2f}/10")

        # Log to MLflow
        mlflow.log_metrics({"llm_judge_score": avg_score})

        console.print(f"\n[cyan]Run ID:[/cyan] {mlflow.active_run().info.run_id}")
        console.print("[green]\nView in MLflow UI to see LLM judge evaluation![/green]")


if __name__ == "__main__":
    main()
