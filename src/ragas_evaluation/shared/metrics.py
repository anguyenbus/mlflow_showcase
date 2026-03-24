"""
RAGas metrics configuration and utilities.

This module provides functions for configuring RAGas metrics
and setting up Zhipu AI backend for evaluation.
"""

from typing import Final

from beartype import beartype
from openai import OpenAI as OpenAIClient
from rich.console import Console

from ragas_evaluation.shared.config import get_ragas_config

# Try to import ragas
try:
    from ragas.embeddings import OpenAIEmbeddings
    from ragas.llms import llm_factory
    from ragas.metrics.collections import (
        AnswerCorrectness,
        AnswerRelevancy,
        ContextPrecision,
        ContextRecall,
        Faithfulness,
    )

    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    Faithfulness = None
    AnswerRelevancy = None
    ContextPrecision = None
    ContextRecall = None
    AnswerCorrectness = None
    llm_factory = None
    OpenAIEmbeddings = None

# Initialize rich console for output
console: Final[Console] = Console()

# Zhipu AI configuration
ZHIPU_BASE_URL: Final[str] = "https://open.bigmodel.cn/api/paas/v4/"
DEFAULT_MODEL: Final[str] = "glm-5"
DEFAULT_EMBEDDING_MODEL: Final[str] = "embedding-3"
EVALUATION_TEMPERATURE: Final[float] = 0.2


@beartype
def configure_zhipu_backend(
    model: str = DEFAULT_MODEL,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    temperature: float = EVALUATION_TEMPERATURE,
) -> tuple:
    """
    Configure Zhipu AI LLM backend for RAGas evaluation.

    Uses low temperature for consistent, reliable evaluation scoring.

    Args:
        model: Model identifier (default: glm-5)
        embedding_model: Embedding model identifier (default: embedding-3)
        temperature: Sampling temperature (default: 0.2 for evaluation)

    Returns:
        Tuple of (llm, embeddings) for RAGas evaluation

    Raises:
        ValueError: If ZHIPU_API_KEY is not set
        ImportError: If ragas is not installed

    """
    if not RAGAS_AVAILABLE:
        raise ImportError("ragas package is not installed. Install it with: pip install ragas")

    config = get_ragas_config()

    # NOTE: Create OpenAI client pointing to Zhipu AI's OpenAI-compatible endpoint
    client = OpenAIClient(
        api_key=config.zhipu_api_key,
        base_url=ZHIPU_BASE_URL,
    )

    # NOTE: Use ragas llm_factory to create InstructorLLM for metrics
    # Use "openai" provider since Zhipu AI has OpenAI-compatible API
    llm = llm_factory(
        model=model,
        client=client,
        temperature=temperature,
    )

    # NOTE: Create embeddings using the same client
    # Zhipu AI supports embedding models via their OpenAI-compatible API
    # Create embeddings directly with OpenAIEmbeddings class
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        client=client,
    )

    console.print(f"[green]✓[/green] Configured Zhipu AI backend for RAGas evaluation: {model}")
    console.print(f"  Temperature: {temperature} (low for consistent evaluation)")
    console.print(f"  Embeddings: {embedding_model}")

    return llm, embeddings


@beartype
def create_ragas_evaluation(
    metrics: list | None = None,
    llm=None,  # type: ignore[type-arg]
    embeddings=None,  # type: ignore[type-arg]
) -> dict:
    """
    Create RAGas evaluation configuration with standard metrics.

    Args:
        metrics: Optional list of metrics to use. If None, uses standard metrics.
        llm: Optional LLM instance for metrics. If None, configures default.
        embeddings: Optional embeddings instance. If None, configures default.

    Returns:
        Dictionary with evaluation configuration (metrics, llm, embeddings)

    Raises:
        ImportError: If ragas is not installed
        ValueError: If ZHIPU_API_KEY is not set

    """
    if not RAGAS_AVAILABLE:
        raise ImportError("ragas package is not installed. Install it with: pip install ragas")

    # Configure LLM and embeddings if not provided
    if llm is None or embeddings is None:
        llm, embeddings = configure_zhipu_backend()

    # Define standard metrics if not provided
    if metrics is None:
        # NOTE: Using standard ragas metrics for comprehensive evaluation
        metrics = [
            Faithfulness(llm=llm),
            AnswerRelevancy(llm=llm, embeddings=embeddings),
            ContextPrecision(llm=llm),
            ContextRecall(llm=llm, embeddings=embeddings),  # Requires ground truth
            AnswerCorrectness(llm=llm, embeddings=embeddings),  # Requires ground truth
        ]

    console.print("[green]✓[/green] Created RAGas evaluation with metrics:")
    for metric in metrics:
        metric_name = metric.name if hasattr(metric, "name") else str(metric)
        console.print(f"  - {metric_name}")

    return {"metrics": metrics, "llm": llm, "embeddings": embeddings}


@beartype
def get_metric_description(metric_name: str) -> str:
    """
    Get description and interpretation guide for a metric.

    Args:
        metric_name: Name of the metric

    Returns:
        Description of what the metric measures and how to interpret scores

    """
    descriptions = {
        "faithfulness": """
        [cyan]Faithfulness:[/cyan] Measures the factual consistency of the generated answer
        against the retrieved context.

        [yellow]Interpretation:[/yellow]
        - Score 0.0-1.0, higher is better
        - High score: Answer is factually consistent with context
        - Low score: Answer contains hallucinations or contradicts context
        """,
        "answer_relevancy": """
        [cyan]Answer Relevancy:[/cyan] Measures how well the answer addresses the question.

        [yellow]Interpretation:[/yellow]
        - Score 0.0-1.0, higher is better
        - High score: Answer directly addresses the question
        - Low score: Answer is incomplete or irrelevant
        """,
        "context_precision": """
        [cyan]Context Precision:[/cyan] Measures the quality of retrieved context passages.

        [yellow]Interpretation:[/yellow]
        - Score 0.0-1.0, higher is better
        - High score: Retrieved contexts are relevant and ranked well
        - Low score: Retrieved contexts contain irrelevant information
        """,
        "context_recall": """
        [cyan]Context Recall:[/cyan] Measures if all relevant information was retrieved.

        [yellow]Interpretation:[/yellow]
        - Score 0.0-1.0, higher is better
        - High score: All relevant context was retrieved
        - Low score: Important context was missed
        [dim](Requires ground truth reference)[/dim]
        """,
        "answer_correctness": """
        "[cyan]Answer Correctness:[/cyan]\n"
        "Measures the accuracy of the answer\n"
        "compared to ground truth.\n"

        [yellow]Interpretation:[/yellow]
        - Score 0.0-1.0, higher is better
        - High score: Answer matches ground truth
        - Low score: Answer differs from ground truth
        [dim](Requires ground truth reference)[/dim]
        """,
    }

    return descriptions.get(metric_name, f"No description available for {metric_name}")
