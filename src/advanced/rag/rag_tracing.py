"""RAG system with comprehensive MLflow tracing.

Demonstrates end-to-end observability for retrieval-augmented generation,
including embeddings, retrieval, and generation tracing.
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from pathlib import Path
from typing import Final
import mlflow
from rich import print as rprint

from config import get_config, validate_environment
from basics.langchain_integration import create_zhipu_langchain_llm
from advanced.rag.documents import DocumentLoader, ChunkingStrategy
from advanced.rag.vector_store import VectorStore
from advanced.rag.retrieval_chain import RetrievalChain


MLFLOW_EXPERIMENT: Final[str] = "advanced_rag_tracing"


def setup_documents() -> Path:
    """Create sample tax law documents for RAG demonstration.

    Returns:
        Path to the created document file.
    """
    # Create data directory if it doesn't exist
    data_dir = Path("data/rag")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Sample Australian tax law content
    tax_law_content = """
Australian Tax Law Overview

Income Tax Assessment Act 1936
The Income Tax Assessment Act 1936 is the primary legislation governing income taxation in Australia.
It establishes the framework for assessing and collecting income tax from individuals and companies.

Taxable Income
Taxable income in Australia is calculated as assessable income minus allowable deductions.
Assessable income includes:
- Salary and wages
- Business income
- Investment income (dividends, interest, rent)
- Capital gains
- Foreign income with Australian tax payable

Allowable Deductions
Individuals and businesses can claim deductions for expenses incurred in earning assessable income.
Common deductions include:
- Work-related expenses (uniforms, tools, home office)
- Business operating expenses
- Investment expenses (management fees, borrowing costs)
- Charitable donations (for registered charities)

Tax Rates 2024-25
For Australian residents:
- 0% on income up to $18,200
- 19% on income between $18,201 and $45,000
- 32.5% on income between $45,001 and $120,000
- 37% on income between $120,001 and $180,000
- 45% on income over $180,000

Goods and Services Tax (GST)
GST is a 10% broad-based tax on most goods, services and other items sold or consumed in Australia.
Businesses with annual turnover over $75,000 must register for GST.

Tax File Number (TFN)
A TFN is a unique identifier issued by the Australian Taxation Office (ATO) to individuals and organizations.
It's used for tax administration and helps prevent tax fraud.
"""

    doc_path = data_dir / "australian_tax_law.txt"
    doc_path.write_text(tax_law_content.strip())

    return doc_path


@mlflow.trace
def create_rag_system(
    doc_path: Path,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    top_k: int = 3,
) -> RetrievalChain:
    """Create a complete RAG system with tracing.

    This function is traced to show embeddings, retrieval setup, and chain construction.

    Args:
        doc_path: Path to the document file.
        chunk_size: Size of document chunks.
        chunk_overlap: Overlap between chunks.
        top_k: Number of documents to retrieve.

    Returns:
        Configured RetrievalChain ready for queries.
    """
    # Load documents
    rprint("[cyan]Loading documents...[/cyan]")
    loader = DocumentLoader(doc_path)
    documents = loader.load()
    mlflow.log_param("document_count", len(documents))

    # Chunk documents
    rprint("[cyan]Chunking documents...[/cyan]")
    chunked_docs = loader.chunk_documents(
        documents,
        strategy=ChunkingStrategy.RECURSIVE,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    mlflow.log_param("chunk_count", len(chunked_docs))
    mlflow.log_param("chunk_size", chunk_size)
    mlflow.log_param("chunk_overlap", chunk_overlap)

    # Create vector store
    rprint("[cyan]Creating vector store...[/cyan]")
    vector_store = VectorStore(
        collection_name="tax_law_docs",
        persist_directory="./data/chroma_db",
    )
    vector_store.add_documents(chunked_docs)

    # Create retriever
    retriever = vector_store.as_retriever(
        search_kwargs={"k": top_k}
    )
    mlflow.log_param("top_k", top_k)

    # Create LLM
    rprint("[cyan]Initializing LLM...[/cyan]")
    llm = create_zhipu_langchain_llm(
        model="glm-5",
        temperature=0.3,
    )

    # Create RAG chain
    rprint("[cyan]Building RAG chain...[/cyan]")
    chain = RetrievalChain(retriever, llm)

    return chain


@mlflow.trace
def query_rag(chain: RetrievalChain, query: str) -> str:
    """Query the RAG system with tracing.

    Args:
        chain: The RAG chain to query.
        query: User question.

    Returns:
        Generated answer.
    """
    rprint(f"\n[bold yellow]Query:[/bold yellow] {query}")

    # Use enhanced tracing to capture retrieved chunks
    response, docs = chain.invoke_with_tracing(query)

    # Display retrieved chunks
    rprint(f"\n[bold cyan]Retrieved {len(docs)} chunks:[/bold cyan]")
    for i, doc in enumerate(docs, 1):
        content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
        rprint(f"  {i}. {content_preview}")

    rprint(f"\n[bold green]Answer:[/bold green]")
    rprint(response)

    return response


def main() -> None:
    """Run the RAG tracing demonstration."""
    # Validate environment
    validate_environment()

    # Set up MLflow
    mlflow.set_tracking_uri(get_config().mlflow_tracking_uri)
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    # Start MLflow run
    with mlflow.start_run(run_name="rag_tracing_demo"):
        rprint("[bold cyan]RAG System Tracing Demo[/bold cyan]")
        rprint("=" * 50)

        # Log parameters
        mlflow.log_params({
            "model": "glm-5",
            "temperature": 0.3,
            "chunking_strategy": "recursive",
        })

        # Create RAG system
        doc_path = setup_documents()
        rag_chain = create_rag_system(
            doc_path,
            chunk_size=500,
            chunk_overlap=50,
            top_k=3,
        )

        # Run sample queries
        rprint("\n[bold cyan]Running sample queries...[/bold cyan]\n")

        queries = [
            "What is the tax rate for income between $45,001 and $120,000?",
            "What can be claimed as allowable deductions?",
            "Do I need to register for GST?",
            "What is a Tax File Number used for?",
        ]

        for i, query in enumerate(queries, 1):
            rprint(f"\n[bold]Query {i}:[/bold]")
            answer = query_rag(rag_chain, query)

            # Log query and answer
            mlflow.log_text(f"Q: {query}\n\nA: {answer}", artifact_file=f"query_{i}.txt")

        # Log artifact
        mlflow.log_artifact(str(doc_path))

        rprint("\n[bold green]RAG tracing complete![/bold green]")
        rprint(f"View traces in MLflow UI: {get_config().mlflow_tracking_uri}")

        # Get trace info
        run_id = mlflow.active_run().info.run_id
        rprint(f"\n[bold]Run ID:[/bold] {run_id}")
        rprint("[bold]Traces captured:[/bold]")
        rprint("  - Document loading and chunking")
        rprint("  - Vector store creation and embedding")
        rprint("  - RAG chain invocation")
        rprint("  - Individual query execution")


if __name__ == "__main__":
    main()
