"""Tests for RAG provider implementation.

These tests follow TDD principles - tests were written first, then implementation.
"""

from unittest import mock

from promptfoo_evaluation.shared.providers.rag_provider import (
    RAGProvider,
    create_rag_assertion_context,
    get_assertion_output,
)


def create_mock_vector_store():
    """Create a mock vector store that conforms to the protocol."""
    mock_store = mock.Mock()
    # Ensure the mock has the required protocol methods
    mock_store.search = mock.Mock(return_value=[])
    mock_store.similarity_search = mock.Mock(return_value=[])
    mock_store.as_retriever = mock.Mock(return_value=mock.Mock())
    return mock_store


class TestRAGProvider:
    """Tests for RAG provider class."""

    def test_provider_initialization(self) -> None:
        """Test RAG provider initialization with required parameters."""
        mock_vector_store = create_mock_vector_store()

        provider = RAGProvider(vector_store=mock_vector_store, top_k=3)

        assert provider.vector_store == mock_vector_store
        assert provider.top_k == 3

    def test_provider_default_top_k(self) -> None:
        """Test RAG provider uses default top_k value."""
        mock_vector_store = create_mock_vector_store()

        provider = RAGProvider(vector_store=mock_vector_store)

        assert provider.top_k == 4  # Default from VectorStore

    def test_retrieve_documents(self) -> None:
        """Test document retrieval from vector store."""
        mock_vector_store = create_mock_vector_store()
        # Return a list of tuples as VectorStore.search does
        mock_docs = [
            (mock.Mock(page_content="Document 1", metadata={"source": "test"}), 0.9),
            (mock.Mock(page_content="Document 2", metadata={"source": "test"}), 0.8),
        ]
        mock_vector_store.search.return_value = mock_docs

        provider = RAGProvider(vector_store=mock_vector_store, top_k=2)
        results = provider.retrieve("test query")

        assert len(results) == 2
        mock_vector_store.search.assert_called_once_with("test query", k=2)

    def test_retrieve_empty_query(self) -> None:
        """Test retrieval with empty query returns empty list."""
        mock_vector_store = create_mock_vector_store()

        provider = RAGProvider(vector_store=mock_vector_store)
        results = provider.retrieve("")

        assert results == []
        mock_vector_store.search.assert_not_called()

    def test_format_context_from_docs(self) -> None:
        """Test formatting context from retrieved documents."""
        mock_docs = [
            (mock.Mock(page_content="First document"), 0.9),
            (mock.Mock(page_content="Second document"), 0.8),
        ]

        provider = RAGProvider(vector_store=create_mock_vector_store())
        context = provider.format_context(mock_docs)

        assert "First document" in context
        assert "Second document" in context


class TestAssertionOutput:
    """Tests for assertion output generation."""

    def test_get_assertion_output_basic(self) -> None:
        """Test basic assertion output generation."""
        prompt = "Test prompt"
        context = {"output": "Test output"}

        result = get_assertion_output(prompt, context)

        assert isinstance(result, dict)
        assert "pass" in result or "output" in result

    def test_get_assertion_output_with_rag_context(self) -> None:
        """Test assertion output with RAG context."""
        prompt = "Answer based on context"
        context = {"output": "The answer", "retrieved_docs": ["Doc 1", "Doc 2"]}

        result = get_assertion_output(prompt, context)

        assert isinstance(result, dict)

    def test_get_assertion_output_missing_context(self) -> None:
        """Test assertion output with missing required context."""
        prompt = "Test prompt"
        context = {}  # Missing expected keys

        result = get_assertion_output(prompt, context)

        # Should handle gracefully
        assert isinstance(result, dict)

    def test_assertion_pass_result(self) -> None:
        """Test assertion that passes."""
        prompt = "Summarize: Hello world"
        context = {"output": "A greeting"}

        result = get_assertion_output(prompt, context)

        # Check for valid assertion format
        assert "pass" in result
        assert isinstance(result["pass"], bool)

    def test_assertion_with_score(self) -> None:
        """Test assertion with numeric score."""
        prompt = "Rate this response"
        context = {"output": "Excellent response", "expected_score": 0.9}

        result = get_assertion_output(prompt, context)

        # Score can be present
        if "score" in result:
            assert isinstance(result["score"], (int, float))


class TestRAGAssertionContext:
    """Tests for RAG assertion context creation."""

    def test_create_rag_assertion_context_basic(self) -> None:
        """Test creating basic RAG assertion context."""
        retrieved_docs = [
            mock.Mock(page_content="Tax law section 1"),
            mock.Mock(page_content="Tax law section 2"),
        ]

        context = create_rag_assertion_context(
            query="What is tax?",
            retrieved_docs=retrieved_docs,
            answer="Tax is a financial obligation",
        )

        assert context["query"] == "What is tax?"
        assert context["answer"] == "Tax is a financial obligation"
        assert "context" in context
        assert "Tax law section 1" in context["context"]

    def test_create_rag_assertion_context_with_metadata(self) -> None:
        """Test creating RAG context with document metadata."""
        retrieved_docs = [
            mock.Mock(page_content="Tax content", metadata={"source": "tax_law.txt", "page": 1}),
        ]

        context = create_rag_assertion_context(
            query="Tax question", retrieved_docs=retrieved_docs, answer="Tax answer"
        )

        assert "documents" in context
        assert len(context["documents"]) == 1
        # Check metadata exists (doesn't have to have specific key)
        assert "metadata" in context["documents"][0]

    def test_create_rag_assertion_context_empty_docs(self) -> None:
        """Test creating RAG context with no documents."""
        context = create_rag_assertion_context(
            query="Test query", retrieved_docs=[], answer="No context answer"
        )

        assert context["context"] == ""
        assert context["documents"] == []
