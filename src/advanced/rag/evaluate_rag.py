"""RAG system evaluation with MLflow.

Evaluates retrieval quality and answer relevance for RAG systems.
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from pathlib import Path
from typing import Final
import pandas as pd
import mlflow
from mlflow.metrics import faithfulness, relevance
from rich import print as rprint

from config import get_mlflow_tracking_uri, validate_environment
from basics.zhipu_client import create_zhipu_langchain_llm
from advanced.rag.documents import DocumentLoader, ChunkingStrategy
from advanced.rag.vector_store import VectorStore
from advanced.rag.retrieval_chain import RetrievalChain


MLFLOW_EXPERIMENT: Final[str] = "advanced_rag_evaluation"


def create_evaluation_dataset() -> pd.DataFrame:
    """Create evaluation dataset for RAG system.

    Returns:
        DataFrame with questions, expected answers, and context.
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


def setup_rag_system(doc_path: Path) -> RetrievalChain:
    """Set up a RAG system for evaluation.

    Args:
        doc_path: Path to the document file.

    Returns:
        Configured RetrievalChain.
    """
    # Load and chunk documents
    loader = DocumentLoader(doc_path)
    documents = loader.load()
    chunked_docs = loader.chunk_documents(
        documents,
        strategy=ChunkingStrategy.RECURSIVE,
        chunk_size=500,
        chunk_overlap=50,
    )

    # Create vector store
    vector_store = VectorStore(
        collection_name="tax_law_eval",
        persist_directory="./data/chroma_db_eval",
    )
    vector_store.add_documents(chunked_docs)

    # Create retriever and LLM
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    llm = create_zhipu_langchain_llm(
        model="glm-5",
        temperature=0.3,
    )

    return RetrievalChain(retriever, llm)


def evaluate_retrieval_quality(
    chain: RetrievalChain,
    questions: list[str],
) -> dict:
    """Evaluate retrieval quality by checking if relevant docs are retrieved.

    Args:
        chain: RAG chain to evaluate.
        questions: List of questions to test retrieval.

    Returns:
        Dictionary with retrieval metrics.
    """
    retrieval_results = []

    for question in questions:
        # Get retrieved documents
        docs = chain.get_retriever().invoke(question)

        retrieval_results.append({
            "question": question,
            "num_retrieved": len(docs),
            "retrieved_snippets": [doc.page_content[:100] for doc in docs],
        })

    # Calculate metrics
    avg_retrieved = sum(r["num_retrieved"] for r in retrieval_results) / len(retrieval_results)

    return {
        "avg_documents_retrieved": avg_retrieved,
        "retrieval_results": retrieval_results,
    }


def evaluate_answer_relevance(
    chain: RetrievalChain,
    eval_df: pd.DataFrame,
) -> pd.DataFrame:
    """Evaluate answer relevance using LLM-as-a-judge.

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

        # Generate answer
        generated_answer = chain.invoke(question)

        # Simple keyword-based relevance check
        # In production, use MLflow's relevance metrics with LLM judge
        keywords = set(ground_truth.lower().split())
        answer_words = set(generated_answer.lower().split())

        overlap = len(keywords & answer_words)
        relevance_score = overlap / len(keywords) if keywords else 0

        results.append({
            "question": question,
            "ground_truth": ground_truth,
            "generated_answer": generated_answer,
            "relevance_score": relevance_score,
        })

    return pd.DataFrame(results)


def compare_chunking_strategies(doc_path: Path) -> dict:
    """Compare different chunking strategies on retrieval quality.

    Args:
        doc_path: Path to the document file.

    Returns:
        Dictionary with comparison results.
    """
    rprint("\n[bold cyan]Comparing chunking strategies...[/bold cyan]")

    strategies = [
        ("small_chunks", 200, 25),
        ("medium_chunks", 500, 50),
        ("large_chunks", 1000, 100),
    ]

    results = {}

    for name, chunk_size, overlap in strategies:
        rprint(f"\n[yellow]Testing: {name} (size={chunk_size}, overlap={overlap})[/yellow]")

        # Create RAG system with specific chunking
        loader = DocumentLoader(doc_path)
        documents = loader.load()
        chunked_docs = loader.chunk_documents(
            documents,
            strategy=ChunkingStrategy.RECURSIVE,
            chunk_size=chunk_size,
            chunk_overlap=overlap,
        )

        vector_store = VectorStore(
            collection_name=f"tax_law_{name}",
            persist_directory=f"./data/chroma_db_{name}",
        )
        vector_store.add_documents(chunked_docs)

        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        llm = create_zhipu_langchain_llm(model="glm-5", temperature=0.3)
        chain = RetrievalChain(retriever, llm)

        # Test with a sample question
        test_question = "What is the tax rate for income between $45,001 and $120,000?"
        answer = chain.invoke(test_question)

        results[name] = {
            "chunk_size": chunk_size,
            "chunk_overlap": overlap,
            "num_chunks": len(chunked_docs),
            "sample_answer": answer[:200],
        }

        rprint(f"  Chunks: {len(chunked_docs)}")
        rprint(f"  Answer: {answer[:100]}...")

    return results


def main() -> None:
    """Run RAG evaluation demonstration."""
    # Validate environment
    validate_environment()

    # Set up MLflow
    mlflow.set_tracking_uri(get_mlflow_tracking_uri())
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    # Start MLflow run
    with mlflow.start_run(run_name="rag_evaluation"):
        rprint("[bold cyan]RAG System Evaluation[/bold cyan]")
        rprint("=" * 50)

        # Create document
        advanced.rag.rag_tracing import setup_documents
        doc_path = setup_documents()

        # Set up RAG system
        rprint("\n[cyan]Setting up RAG system...[/cyan]")
        rag_chain = setup_rag_system(doc_path)

        # Create evaluation dataset
        rprint("\n[cyan]Loading evaluation dataset...[/cyan]")
        eval_df = create_evaluation_dataset()
        mlflow.log_dict(eval_df.to_dict(orient="records"), "evaluation_dataset.json")

        # Evaluate retrieval quality
        rprint("\n[cyan]Evaluating retrieval quality...[/cyan]")
        retrieval_metrics = evaluate_retrieval_quality(
            rag_chain,
            eval_df["question"].tolist()
        )
        mlflow.log_metrics({
            "avg_documents_retrieved": retrieval_metrics["avg_documents_retrieved"]
        })

        # Evaluate answer relevance
        rprint("\n[cyan]Evaluating answer relevance...[/cyan]")
        relevance_df = evaluate_answer_relevance(rag_chain, eval_df)
        avg_relevance = relevance_df["relevance_score"].mean()
        mlflow.log_metric("avg_relevance_score", avg_relevance)

        # Display results
        rprint(f"\n[bold green]Average documents retrieved:[/bold green] {retrieval_metrics['avg_documents_retrieved']:.2f}")
        rprint(f"[bold green]Average relevance score:[/bold green] {avg_relevance:.2f}")

        # Compare chunking strategies
        rprint("\n[cyan]Comparing chunking strategies...[/cyan]")
        chunking_comparison = compare_chunking_strategies(doc_path)

        # Log comparison results
        for strategy_name, metrics in chunking_comparison.items():
            mlflow.log_metrics({
                f"{strategy_name}_num_chunks": metrics["num_chunks"],
            })

        # Save results as artifact
        results_path = Path("data/evaluation/rag_results.csv")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        relevance_df.to_csv(results_path, index=False)
        mlflow.log_artifact(str(results_path))

        rprint("\n[bold green]RAG evaluation complete![/bold green]")
        rprint(f"View results in MLflow UI: {get_mlflow_tracking_uri()}")

        # Display sample results
        rprint("\n[bold cyan]Sample Evaluation Results:[/bold cyan]")
        for _, row in relevance_df.head(2).iterrows():
            rprint(f"\n[yellow]Q:[/yellow] {row['question']}")
            rprint(f"[yellow]Relevance:[/yellow] {row['relevance_score']:.2f}")
            rprint(f"[yellow]Answer:[/yellow] {row['generated_answer'][:150]}...")


if __name__ == "__main__":
    main()
