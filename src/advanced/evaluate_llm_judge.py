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
from rich.table import Table

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
    # Use lower temperature for more consistent evaluations
    judge_llm = create_zhipu_langchain_llm(
        model="glm-5",
        temperature=0.3,
    )

    console.print("[green]✓[/green] Created LLM judge\n")
    return judge_llm


def evaluate_response(question: str, response: str, judge_llm) -> dict:
    """Evaluate a single response using LLM judge.

    Args:
        question: The original question
        response: The response to evaluate
        judge_llm: LLM to use for judging

    Returns:
        Dictionary with score and justification
    """
    # Create judge prompt
    prompt = JUDGE_PROMPT.format(
        question=question,
        response=response,
    )

    # Get evaluation from judge LLM
    evaluation = judge_llm.invoke(prompt)

    # Extract score from evaluation
    import re
    score_match = re.search(r"Score:\s*(\d+(?:\.\d+)?)", evaluation.content)
    justification_match = re.search(r"Justification:\s*(.+?)(?:\n|$)", evaluation.content, re.DOTALL)

    score = float(score_match.group(1)) if score_match else 0.0
    justification = justification_match.group(1).strip() if justification_match else "No justification provided"

    return {
        "score": score,
        "justification": justification,
        "evaluation": evaluation.content
    }


def main():
    """Run LLM-as-a-judge evaluation example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = create_experiment("mlflow-llm-judge")

    console.print("\n[bold cyan]LLM Judge Evaluation Demo[/bold cyan]\n")
    console.print(f"[green]✓[/green] Experiment ID: {experiment.experiment_id}\n")

    # Create LLM judge
    judge_llm = create_llm_judge()

    # Test data: questions and model responses
    test_cases = [
        {
            "question": "What is the current company tax rate in Australia?",
            "response": "The current company tax rate in Australia is 30% for most companies. "
                       "However, base rate entities with turnover under $50 million pay 25%.",
            "expected": "Should mention 30% for most companies, 25% for small businesses"
        },
        {
            "question": "Explain what GST is and when it was introduced in Australia.",
            "response": "GST stands for Goods and Services Tax. It is a 10% tax on most goods "
                       "and services in Australia. It was introduced on July 1, 2000.",
            "expected": "Should mention 10%, goods and services tax, July 2000"
        },
        {
            "question": "What is the tax-free threshold for individuals in Australia?",
            "response": "The tax-free threshold for Australian residents is $18,200 per year. "
                       "This means you don't pay tax if you earn this amount or less.",
            "expected": "Should mention $18,200"
        }
    ]

    console.print("Evaluating responses with LLM judge...\n")

    # Create a nice table for results
    table = Table(title="LLM Judge Evaluation Results")
    table.add_column("Question", style="cyan", no_wrap=False)
    table.add_column("Score", style="magenta")
    table.add_column("Justification", style="green")

    scores = []

    # Evaluate each response with MLflow tracking
    with mlflow.start_run():
        for i, test_case in enumerate(test_cases, 1):
            console.print(f"[cyan]Evaluating Response {i}:[/cyan]")
            console.print(f"  Question: {test_case['question'][:50]}...")

            # Evaluate with LLM judge
            with mlflow.start_span(name=f"evaluate_response_{i}") as span:
                span.set_inputs({
                    "question": test_case['question'],
                    "response": test_case['response'][:100] + "..."
                })

                result = evaluate_response(
                    test_case['question'],
                    test_case['response'],
                    judge_llm
                )

                span.set_outputs({
                    "score": result['score'],
                    "justification": result['justification']
                })

            scores.append(result['score'])

            console.print(f"  [magenta]Score:[/magenta] {result['score']}/10")
            console.print(f"  [green]Justification:[/green] {result['justification']}\n")

            # Add to table
            table.add_row(
                test_case['question'][:50] + "...",
                f"{result['score']}/10",
                result['justification'][:80] + "..."
            )

        # Calculate average
        avg_score = sum(scores) / len(scores)

        # Log metrics to MLflow
        mlflow.log_metric("llm_judge_avg_score", avg_score)
        mlflow.log_metric("num_responses_evaluated", len(scores))

        console.print(table)
        console.print(f"\n[bold green]Average quality score:[/bold green] {avg_score:.2f}/10")

        # Log evaluation summary
        summary = f"Evaluated {len(scores)} responses with LLM judge. Average score: {avg_score:.2f}/10"
        mlflow.log_text(summary, artifact_file="evaluation_summary.txt")

        console.print(f"\n[green]✓ Evaluation complete![/green]")
        console.print(f"\n[cyan]View run at:[/cyan] http://localhost:5000/#/experiments/16")
        console.print("[cyan]Look for:[/cyan]")
        console.print("  • Individual evaluation spans with scores")
        console.print("  • Average LLM judge score metric")
        console.print("  • Evaluation summary artifact")


if __name__ == "__main__":
    main()
