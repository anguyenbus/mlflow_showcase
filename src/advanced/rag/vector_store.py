"""Vector store implementation using ChromaDB.

Provides semantic search and document retrieval using embeddings.
"""

from pathlib import Path
from typing import Final
from beartype import beartype
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from advanced.rag.embeddings import DeterministicEmbeddings


@beartype
class VectorStore:
    """ChromaDB vector store for semantic document retrieval.

    Attributes:
        collection_name: Name of the ChromaDB collection.
        persist_directory: Directory to persist vector database (None for in-memory).
        embeddings: Embedding model for document vectorization.

    Example:
        >>> store = VectorStore("tax_law_docs", "./chroma_db")
        >>> store.add_documents(documents)
        >>> results = store.search("tax question", k=3)
    """

    __slots__ = ("collection_name", "persist_directory", "embeddings", "_vector_store")

    DEFAULT_COLLECTION: Final[str] = "documents"
    DEFAULT_TOP_K: Final[int] = 4

    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION,
        persist_directory: str | Path | None = None,
    ) -> None:
        """Initialize the vector store.

        Args:
            collection_name: Name for the ChromaDB collection.
            persist_directory: Directory to persist database (None for in-memory).

        NOTE: Uses deterministic embeddings for educational demonstration.
        For production, replace with OpenAIEmbeddings or HuggingFaceEmbeddings.
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory) if persist_directory else None

        # NOTE: Using deterministic embeddings for educational demonstration
        # This allows RAG tracing without external API dependencies
        # For production, replace with:
        # - OpenAIEmbeddings() (requires OPENAI_API_KEY)
        # - HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.embeddings = DeterministicEmbeddings(embedding_dim=384)

        # Initialize ChromaDB client
        if self.persist_directory:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        else:
            client = chromadb.EphemeralClient(
                settings=ChromaSettings(anonymized_telemetry=False)
            )

        # Create LangChain Chroma vector store
        self._vector_store = Chroma(
            client=client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )

    def add_documents(self, documents: list) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of LangChain Document objects to add.
        """
        # WARN: This operation will generate embeddings for all documents
        # which may be expensive for large document sets

        _ = self._vector_store.add_documents(documents)

    def search(
        self,
        query: str,
        k: int = DEFAULT_TOP_K,
        filter_metadata: dict | None = None,
    ) -> list:
        """Search for similar documents.

        Args:
            query: Search query text.
            k: Number of results to return.
            filter_metadata: Optional metadata filters.

        Returns:
            List of similar documents with relevance scores.
        """
        # NOTE: Using similarity search with score for relevance ranking
        if filter_metadata:
            results = self._vector_store.similarity_search_with_score(
                query,
                k=k,
                filter=filter_metadata
            )
        else:
            results = self._vector_store.similarity_search_with_score(query, k=k)

        return results

    def similarity_search(
        self,
        query: str,
        k: int = DEFAULT_TOP_K,
        **kwargs,
    ) -> list:
        """Perform similarity search without scores.

        Args:
            query: Search query text.
            k: Number of results to return.
            **kwargs: Additional arguments for filtering.

        Returns:
            List of similar documents.
        """
        return self._vector_store.similarity_search(query, k=k, **kwargs)

    def as_retriever(self, **kwargs):
        """Return a LangChain retriever interface.

        Args:
            **kwargs: Arguments to pass to retriever configuration.

        Returns:
            LangChain retriever object for use in chains.
        """
        return self._vector_store.as_retriever(**kwargs)

    def delete_collection(self) -> None:
        """Delete the entire collection from the vector store.

        WARN: This operation is irreversible and will delete all documents.
        """
        self._vector_store.delete_collection()
