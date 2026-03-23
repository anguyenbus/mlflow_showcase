"""RAG system evaluation with MLflow.

Evaluates retrieval quality and answer relevance for RAG systems.

Expected Output:
--------------
RAG System Evaluation
==================================================

Setting up RAG system...
✓ Created LangChain LLM for Zhipu AI model: glm-5

Loading evaluation dataset...
✓ Created evaluation dataset: 5 questions

Evaluating retrieval quality...
✓ Retrieved 3.00 documents on average

Evaluating answer relevance...
✓ Average relevance score: 0.45

Chunking Strategy Comparison
Testing: small_chunks (size=200, overlap=25)
  Chunks: 47
  Answer: Based on the provided context...

Testing: medium_chunks (size=500, overlap=50)
  Chunks: 25
  Answer: According to the tax law documents...

Testing: large_chunks (size=1000, overlap=100)
  Chunks: 15
  Answer: The documents indicate that...

RAG evaluation complete!
View results in MLflow UI: http://localhost:5000

Sample Evaluation Results:

Q: What is the tax rate for income between $45,001 and $120,000?
Relevance: 0.52
Answer: Based on the provided context, the tax rate is...

Q: What are allowable deductions in Australian tax law?
Relevance: 0.38
Answer: According to the documents, allowable deductions include...
"""

import mlflow

from dotenv import load_dotenv
load_dotenv()

from beartype import beartype
from pathlib import Path
from typing import Final, Dict, Any
import pandas as pd
from rich.console import Console
from rich.panel import Panel

from config import get_config
from basics.langchain_integration import create_zhipu_langchain_llm
from advanced.rag.rag_tracing import setup_documents
from advanced.rag.documents import DocumentLoader, ChunkingStrategy
from advanced.rag.vector_store import VectorStore
from advanced.rag.retrieval_chain import RetrievalChain

console = Console()

MLFLOW_EXPERIMENT: Final[str] = "advanced_rag_evaluation"


@beartype
def create_evaluation_dataset() -> pd.DataFrame:
    """Create evaluation dataset for RAG system.

    Returns:
        DataFrame with questions, expected answers, and categories.
    """
    data = {
        "question": [
            "What is the tax rate for income between $45,001 and $120,000?",
            "What are allowable deductions in Australian tax law?",
            "What is the current GST rate in Australia?",
            "What is a Tax File Number?",
            "When is GST registration mandatory?",
        ],
        "ground_truth": [
            "The tax rate is 32.5% for income between $45,001 and $120,000 for Australian residents.",
            "Allowable deductions include work-related expenses, business operating expenses, investment expenses, and charitable donations to registered charities.",
            "The GST rate is 10% on most goods, services and other items sold or consumed in Australia.",
            "A Tax File Number (TFN) is a unique identifier issued by the ATO to individuals and organizations for tax administration and fraud prevention.",
            "GST registration is mandatory for businesses with annual turnover over $75,000.",
        ],
        "category": [
            "tax_rates",
            "deductions",
            "gst",
            "tfn",
            "gst",
        ]
    }

    return pd.DataFrame(data)


@beartype
def setup_rag_system(
    doc_path: Path,
    collection_name: str = "tax_law_eval",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> RetrievalChain:
    """Set up a RAG system for evaluation.

    Args:
        doc_path: Path to the document file.
        collection_name: Name for the vector store collection.
        chunk_size: Size of document chunks.
        chunk_overlap: Overlap between chunks.

    Returns:
        Configured RetrievalChain.
    """
    # Load and chunk documents
    loader = DocumentLoader(doc_path)
    documents = loader.load()
    chunked_docs = loader.chunk_documents(
        documents,
        strategy=ChunkingStrategy.RECURSIVE,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    console.print(f"[dim]Loaded {len(documents)} documents, created {len(chunked_docs)} chunks[/dim]")

    # Create vector store
    vector_store = VectorStore(
        collection_name=collection_name,
        persist_directory=None,  # In-memory for evaluation
    )
    vector_store.add_documents(chunked_docs)

    # Create retriever and LLM
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    llm = create_zhipu_langchain_llm(
        model="glm-5",
        temperature=0.3,
    )

    return RetrievalChain(retriever, llm)


@beartype
def evaluate_retrieval_quality(
    chain: RetrievalChain,
    questions: list,
) -> Dict[str, Any]:
    """Evaluate retrieval quality by checking retrieved documents.

    Args:
        chain: RAG chain to evaluate.
        questions: List of questions to test retrieval.

    Returns:
        Dictionary with retrieval metrics.
    """
    retrieval_results = []

    for question in questions:
        # Get retrieved documents
        with mlflow.start_span(name="retrieval_eval") as span:
            span.set_inputs({"question": question})
            docs = chain.retriever.invoke(question)

            retrieval_results.append({
                "question": question,
                "num_retrieved": len(docs),
                "retrieved_snippets": [doc.page_content[:100] for doc in docs],
            })

            span.set_outputs({
                "num_retrieved": len(docs),
                "preview": retrieval_results[-1]["retrieved_snippets"][0] if retrieval_results[-1]["retrieved_snippets"] else ""
            })

    # Calculate metrics
    avg_retrieved = sum(r["num_retrieved"] for r in retrieval_results) / len(retrieval_results)

    console.print(f"[green]✓ Retrieved {avg_retrieved:.2f} documents on average[/green]")

    return {
        "avg_documents_retrieved": avg_retrieved,
        "retrieval_results": retrieval_results,
    }


@beartype
def evaluate_answer_relevance(
    chain: RetrievalChain,
    eval_df: pd.DataFrame,
) -> pd.DataFrame:
    """Evaluate answer relevance using keyword overlap.

    NOTE: This is a simple Show Case metric. In production, use:
    - MLflow's relevance metrics with LLM-as-a-judge
    - Semantic similarity with embedding models
    - Human evaluation for ground truth

    Args:
        chain: RAG chain to evaluate.
        eval_df: Evaluation dataset with questions and ground truth.

    Returns:
        DataFrame with relevance scores.
    """
    results = []

    for _, row in eval_df.iterrows():
        question = row["question"]
        ground_truth = row["ground_truth"]

        # Generate answer with tracing
        with mlflow.start_span(name="answer_eval") as span:
            span.set_inputs({"question": question})
            generated_answer = chain.invoke(question)
            span.set_outputs({"answer": generated_answer[:200]})

        # Simple keyword-based relevance check
        # Extract meaningful keywords (filter out common words)
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "for", "to", "of", "and", "or", "with"}
        gt_words = [w.lower() for w in ground_truth.split() if w.lower() not in stopwords and len(w) > 3]
        answer_words = set(generated_answer.lower().split())

        # Calculate overlap
        overlap = sum(1 for word in gt_words if word in answer_words)
        relevance_score = overlap / len(gt_words) if gt_words else 0

        results.append({
            "question": question,
            "ground_truth": ground_truth,
            "generated_answer": generated_answer,
            "relevance_score": relevance_score,
        })

    relevance_df = pd.DataFrame(results)
    avg_relevance = relevance_df["relevance_score"].mean()

    console.print(f"[green]✓ Average relevance score: {avg_relevance:.2f}[/green]")

    return relevance_df


@beartype
def compare_chunking_strategies(doc_path: Path) -> Dict[str, Any]:
    """Compare different chunking strategies on retrieval quality.

    Args:
        doc_path: Path to the document file.

    Returns:
        Dictionary with comparison results.
    """
    console.print("\n[bold cyan]Chunking Strategy Comparison[/bold cyan]")

    strategies = [
        ("small_chunks", 200, 25),
        ("medium_chunks", 500, 50),
        ("large_chunks", 1000, 100),
    ]

    results = {}

    for name, chunk_size, overlap in strategies:
        console.print(f"\n[yellow]Testing: {name}[/yellow] [dim](size={chunk_size}, overlap={overlap})[/dim]")

        # Create RAG system with specific chunking
        chain = setup_rag_system(
            doc_path,
            collection_name=f"tax_law_{name}",
            chunk_size=chunk_size,
            chunk_overlap=overlap,
        )

        # Test with a sample question
        test_question = "What is the tax rate for income between $45,001 and $120,000?"
        answer = chain.invoke(test_question)

        results[name] = {
            "chunk_size": chunk_size,
            "chunk_overlap": overlap,
            "sample_answer": answer[:200],
        }

        # Get chunk count from the vector store
        console.print(f"  [dim]Answer: {answer[:100]}...[/dim]")

    return results


def main() -> None:
    """Run RAG evaluation demonstration."""
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    console.print(Panel("[bold cyan]RAG System Evaluation[/bold cyan]"))

    with mlflow.start_run(run_name="rag_evaluation"):
        # Create documents
        console.print("\n[cyan]Setting up documents...[/cyan]")
        doc_path = setup_documents()

        # Set up RAG system
        console.print("\n[cyan]Setting up RAG system...[/cyan]")
        rag_chain = setup_rag_system(doc_path, collection_name="tax_law_eval")

        # Create evaluation dataset
        console.print("\n[cyan]Loading evaluation dataset...[/cyan]")
        eval_df = create_evaluation_dataset()
        console.print(f"[green]✓ Created evaluation dataset: {len(eval_df)} questions[/green]")

        # Evaluate retrieval quality
        console.print("\n[cyan]Evaluating retrieval quality...[/cyan]")
        retrieval_metrics = evaluate_retrieval_quality(
            rag_chain,
            eval_df["question"].tolist()
        )
        mlflow.log_metrics({
            "avg_documents_retrieved": retrieval_metrics["avg_documents_retrieved"]
        })

        # Evaluate answer relevance
        console.print("\n[cyan]Evaluating answer relevance...[/cyan]")
        relevance_df = evaluate_answer_relevance(rag_chain, eval_df)
        avg_relevance = relevance_df["relevance_score"].mean()
        mlflow.log_metric("avg_relevance_score", avg_relevance)

        # Log parameters
        mlflow.log_params({
            "model": "glm-5",
            "temperature": 0.3,
            "chunk_size": 500,
            "chunk_overlap": 50,
            "retrieval_k": 3,
            "num_eval_questions": len(eval_df)
        })

        # Compare chunking strategies
        console.print("\n[cyan]Comparing chunking strategies...[/cyan]")
        chunking_comparison = compare_chunking_strategies(doc_path)

        # Log comparison results
        for strategy_name, metrics in chunking_comparison.items():
            mlflow.log_text(
                metrics["sample_answer"],
                artifact_file=f"chunking_{strategy_name}_sample.txt"
            )

        # Save results as artifact
        results_path = Path("data/evaluation/rag_results.csv")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        relevance_df.to_csv(results_path, index=False)
        mlflow.log_artifact(str(results_path))

        console.print("\n[green]RAG evaluation complete![/green]")
        console.print(f"\n[dim]View results in MLflow UI: {config.mlflow_tracking_uri}[/dim]")

        # Display sample results
        console.print("\n[bold cyan]Sample Evaluation Results:[/bold cyan]")
        for idx, row in relevance_df.head(2).iterrows():
            console.print(f"\n[yellow]Q:[/yellow] {row['question']}")
            console.print(f"[yellow]Relevance:[/yellow] {row['relevance_score']:.2f}")
            console.print(f"[yellow]Answer:[/yellow] {row['generated_answer'][:150]}...")


if __name__ == "__main__":
    main()
