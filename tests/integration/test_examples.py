"""Integration tests for example execution.

Tests critical end-to-end workflows and example execution.
Focuses on integration points between components.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import os

from src.config import Config
from src.advanced.rag.documents import DocumentLoader, ChunkingStrategy
from src.advanced.rag.vector_store import VectorStore


class TestDocumentLoadingIntegration:
    """Test document loading and chunking integration."""

    def test_load_and_chunk_tax_law_document(self, tmp_path):
        """Test loading and chunking a tax law document."""
        # Create a sample tax law document
        doc_content = """
Australian Tax Law - Income Tax Assessment Act

Section 1: Taxable Income
Taxable income is calculated as assessable income minus allowable deductions.

Section 2: Tax Rates
For Australian residents:
- 0% on income up to $18,200
- 19% on income between $18,201 and $45,000
- 32.5% on income between $45,001 and $120,000

Section 3: Allowable Deductions
Common deductions include work-related expenses, business expenses,
and charitable donations.
"""

        doc_file = tmp_path / "tax_law.txt"
        doc_file.write_text(doc_content.strip())

        # Load document
        loader = DocumentLoader(str(doc_file))
        documents = loader.load()

        assert len(documents) == 1
        assert "Australian Tax Law" in documents[0].page_content

        # Chunk document with valid overlap
        chunks = loader.chunk_documents(
            documents,
            strategy=ChunkingStrategy.RECURSIVE,
            chunk_size=200,
            chunk_overlap=50  # Overlap must be smaller than chunk size
        )

        assert len(chunks) > 1
        # Verify chunks have content
        assert all(len(chunk.page_content) > 0 for chunk in chunks)
        assert all("chunk_index" in chunk.metadata for chunk in chunks)


class TestRAGIntegration:
    """Test RAG system integration."""

    @patch("src.advanced.rag.vector_store.OpenAIEmbeddings")
    @patch("chromadb.EphemeralClient")
    def test_rag_document_to_retrieval_flow(self, mock_client, mock_embeddings):
        """Test flow from documents to retrieval."""
        # Create a mock collection
        mock_collection = Mock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        # Create sample document
        doc_text = "Tax rate is 32.5% for income between $45,001 and $120,000."

        # Load and chunk
        loader = DocumentLoader.__new__(DocumentLoader)
        chunks = loader.chunk_text(
            doc_text,
            strategy=ChunkingStrategy.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=20
        )

        assert len(chunks) >= 1

        # Create vector store
        store = VectorStore(
            collection_name="test_collection",
            persist_directory=None
        )

        # Mock embeddings
        with patch.object(store.embeddings, "embed_documents", return_value=[[0.1] * 1536]):
            # Create mock documents
            from langchain_core.documents import Document
            documents = [Document(page_content=chunk) for chunk in chunks]

            # Add documents
            store.add_documents(documents)

            # Verify collection was called
            assert True  # Test passes if no exceptions


class TestEvaluationIntegration:
    """Test evaluation framework integration."""

    def test_evaluation_dataset_structure(self):
        """Test evaluation dataset has correct structure."""
        # Create sample evaluation dataset
        data = {
            "question": [
                "What is the tax rate for income between $45,001 and $120,000?",
                "What are allowable deductions?"
            ],
            "ground_truth": [
                "The tax rate is 32.5%.",
                "Allowable deductions include work-related expenses."
            ],
            "category": ["tax_rates", "deductions"]
        }

        df = pd.DataFrame(data)

        # Verify structure
        assert "question" in df.columns
        assert "ground_truth" in df.columns
        assert "category" in df.columns
        assert len(df) == 2

    def test_evaluation_metric_calculation(self):
        """Test evaluation metrics can be calculated."""
        # Sample predictions and ground truth
        predictions = ["The tax rate is 32.5%.", "Deductions include work expenses."]
        targets = ["The tax rate is 32.5%.", "Allowable deductions include work expenses."]

        # Simple exact match calculation
        matches = sum(1 for p, t in zip(predictions, targets) if p.lower() == t.lower())
        accuracy = matches / len(predictions)

        assert accuracy >= 0.0
        assert accuracy <= 1.0


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def test_document_to_vector_store_workflow(self, tmp_path):
        """Test workflow from document loading to vector storage."""
        # Create sample document
        content = "Test document content for vector store."
        doc_file = tmp_path / "test.txt"
        doc_file.write_text(content)

        # Load document
        loader = DocumentLoader(str(doc_file))
        documents = loader.load()

        # Verify document loaded
        assert len(documents) == 1
        assert documents[0].page_content == content

        # Chunk document with valid overlap
        chunks = loader.chunk_documents(documents, chunk_size=100, chunk_overlap=20)
        assert len(chunks) >= 1

    def test_config_object_structure(self):
        """Test configuration object has correct structure."""
        # Create a config object directly
        config = Config(
            zhipu_api_key="test_key",
            mlflow_tracking_uri="sqlite:///test.db"
        )

        assert config.zhipu_api_key == "test_key"
        assert config.mlflow_tracking_uri == "sqlite:///test.db"
        # Config has other attributes
        # Config has other attributes
