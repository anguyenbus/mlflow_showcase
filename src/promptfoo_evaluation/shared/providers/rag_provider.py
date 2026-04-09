"""
RAG provider for promptfoo evaluation.

This module provides a custom promptfoo provider that integrates with
the existing RAG infrastructure for retrieval-augmented generation testing.
"""

# NOTE: Import RAG components from existing infrastructure
import sys
from pathlib import Path
from typing import Any, Final, Protocol, runtime_checkable

from beartype import beartype

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import actual VectorStore for type reference
# NOTE: These imports must come after sys.path modification
from advanced.rag.retrieval_chain import RetrievalChain  # noqa: E402
from advanced.rag.vector_store import VectorStore  # noqa: E402


# Protocol for vector store interface (allows mocking in tests)
@runtime_checkable
class VectorStoreProtocol(Protocol):
    """Protocol for vector store interface."""

    def search(self, query: str, k: int, filter_metadata: dict | None = None) -> list:
        """Search for similar documents."""
        ...

    def similarity_search(self, query: str, k: int, **kwargs) -> list:
        """Perform similarity search."""
        ...

    def as_retriever(self, **kwargs) -> Any:
        """Return a retriever interface."""
        ...


# Default top_k for retrieval
DEFAULT_TOP_K: Final[int] = 4


@beartype
class RAGProvider:
    """
    Custom promptfoo provider for RAG evaluation.

    This provider integrates with the existing VectorStore and RetrievalChain
    to enable dynamic RAG testing within promptfoo evaluations.

    Attributes:
        vector_store: VectorStore instance for document retrieval.
        top_k: Number of documents to retrieve.

    Example:
        >>> from promptfoo_evaluation.shared.providers.rag_provider import RAGProvider
        >>> provider = RAGProvider(vector_store, top_k=3)
        >>> context = provider.retrieve("What is tax?")
        >>> assert len(context) > 0

    """

    __slots__ = ("vector_store", "top_k")

    def __init__(
        self,
        vector_store: VectorStoreProtocol,
        top_k: int = DEFAULT_TOP_K,
    ) -> None:
        """
        Initialize the RAG provider.

        Args:
            vector_store: VectorStore instance for document retrieval.
            top_k: Number of documents to retrieve (default: 4).

        """
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str) -> list:
        """
        Retrieve documents for the given query.

        Args:
            query: Search query text.

        Returns:
            List of retrieved documents with scores.

        """
        if not query or not query.strip():
            return []

        results = self.vector_store.search(query, k=self.top_k)
        return results

    def format_context(self, documents: list) -> str:
        """
        Format retrieved documents into context string.

        Args:
            documents: List of documents from vector store.

        Returns:
            Formatted context string.

        """
        if not documents:
            return ""

        context_parts = []
        for item in documents:
            # Handle both (doc, score) tuples and plain doc objects
            if isinstance(item, tuple) and len(item) >= 2:
                doc, _score = item[0], item[1]  # score unused
                context_parts.append(f"{doc.page_content}")
            elif hasattr(item, "page_content"):
                context_parts.append(f"{item.page_content}")
            else:
                context_parts.append(str(item))

        return "\n\n".join(context_parts)

    def get_retrieval_chain(
        self,
        llm,
        prompt_template: str | None = None,
    ) -> RetrievalChain:
        """
        Create a RetrievalChain with this provider's vector store.

        Args:
            llm: Language model for generation.
            prompt_template: Optional custom prompt template.

        Returns:
            Configured RetrievalChain instance.

        """
        retriever = self.vector_store.as_retriever(search_kwargs={"k": self.top_k})
        return RetrievalChain(retriever, llm, prompt_template)


@beartype
def get_assertion_output(prompt: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Get assertion output for promptfoo RAG assertions.

    This function implements the promptfoo provider interface for
    custom assertions with RAG context.

    Args:
        prompt: The prompt or assertion being evaluated.
        context: Context dict containing output, vars, and other data.

    Returns:
        Assertion result dict with pass/score/reason fields.

    Example:
        >>> result = get_assertion_output(
        ...     prompt="Summarize the answer",
        ...     context={"output": "The answer is 42"}
        ... )
        >>> assert "pass" in result

    """
    output = context.get("output", "")
    vars_dict = context.get("vars", {})

    # Default assertion result structure
    result: dict[str, Any] = {"pass": True, "reason": ""}

    # Check if output exists
    if not output:
        result["pass"] = False
        result["reason"] = "Output is empty"
        return result

    # Check context recall (if retrieved_docs provided)
    retrieved_docs = context.get("retrieved_docs", [])
    if retrieved_docs:
        # Simple check: answer should reference context
        # NOTE: context_text constructed but not used - simple length check instead
        _ = " ".join(retrieved_docs)
        if len(output) < 10:
            result["pass"] = False
            result["reason"] = "Answer too short for context-based question"
            return result

    # Check for expected answer
    if "expected" in vars_dict:
        expected = vars_dict["expected"]
        if expected.lower() not in output.lower():
            result["pass"] = False
            result["reason"] = f"Expected '{expected}' not found in output"
            return result

    result["reason"] = "Assertion passed"
    return result


@beartype
def create_rag_assertion_context(
    query: str,
    retrieved_docs: list,
    answer: str,
) -> dict[str, Any]:
    """
    Create assertion context for RAG evaluation.

    Builds a context dictionary suitable for use with RAG assertions.

    Args:
        query: The original query.
        retrieved_docs: List of retrieved document objects.
        answer: The generated answer.

    Returns:
        Context dictionary with query, context, answer, and documents.

    Example:
        >>> context = create_rag_assertion_context(
        ...     query="What is tax?",
        ...     retrieved_docs=[doc1, doc2],
        ...     answer="Tax is a financial obligation"
        ... )
        >>> assert context["query"] == "What is tax?"

    """
    # Format context from documents
    context_parts = []
    documents_meta = []

    for doc in retrieved_docs:
        # Handle both LangChain Document objects and plain dicts
        if hasattr(doc, "page_content"):
            content = doc.page_content
            metadata = getattr(doc, "metadata", {})
        elif isinstance(doc, dict):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
        else:
            content = str(doc)
            metadata = {}

        context_parts.append(content)
        documents_meta.append(
            {
                "content": content[:200] + "..." if len(content) > 200 else content,
                "metadata": metadata,
            }
        )

    return {
        "query": query,
        "context": "\n\n".join(context_parts),
        "answer": answer,
        "documents": documents_meta,
        "num_docs": len(retrieved_docs),
    }


@beartype
def create_rag_provider_from_config(config: dict[str, Any]) -> RAGProvider:
    """
    Create RAGProvider from configuration.

    Factory function to create RAGProvider from configuration.

    Args:
        config: Configuration dict with vector_store_path and top_k.

    Returns:
        Configured RAGProvider instance.

    Example:
        >>> provider = create_rag_provider_from_config({
        ...     "vector_store_path": "./chroma_db",
        ...     "top_k": 3
        ... })

    """
    vector_store_path = config.get("vector_store_path")
    top_k = config.get("top_k", DEFAULT_TOP_K)
    collection_name = config.get("collection_name", "documents")

    vector_store = VectorStore(
        collection_name=collection_name,
        persist_directory=vector_store_path,
    )

    return RAGProvider(vector_store=vector_store, top_k=top_k)
