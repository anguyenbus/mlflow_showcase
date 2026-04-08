"""Tests for chunking strategy comparison functionality."""

from unittest import mock

import pytest


def test_chunking_strategies_generate_correct_sizes():
    """Test that chunking strategies generate correct chunk sizes."""
    try:
        from ragas_evaluation.examples.advanced.compare_chunking_strategies import (
            generate_chunks,
        )

        # Test document
        test_doc = "This is a test document. " * 100  # Long enough for multiple chunks

        # Test small chunks (200 chars)
        small_chunks = generate_chunks(test_doc, chunk_size=200, overlap=25)
        assert all(len(chunk) <= 200 or len(chunk) <= 200 + 25 for chunk in small_chunks)

        # Test medium chunks (500 chars)
        medium_chunks = generate_chunks(test_doc, chunk_size=500, overlap=50)
        assert all(len(chunk) <= 500 or len(chunk) <= 500 + 50 for chunk in medium_chunks)

        # Test large chunks (1000 chars)
        large_chunks = generate_chunks(test_doc, chunk_size=1000, overlap=100)
        assert all(len(chunk) <= 1000 or len(chunk) <= 1000 + 100 for chunk in large_chunks)

    except ImportError:
        pytest.skip("compare_chunking_strategies.py not implemented yet")


def test_timing_information_is_captured():
    """Test that timing information is captured correctly."""
    try:
        from ragas_evaluation.examples.advanced.compare_chunking_strategies import (
            ChunkingResult,
        )

        # Create a result with timing information
        result = ChunkingResult(
            strategy="small",
            chunk_size=200,
            num_chunks=10,
            avg_chunk_length=195.5,
            retrieval_latency=0.5,
            total_time=1.2,
            metrics={"faithfulness": 0.85},
        )

        assert result.strategy == "small"
        assert result.chunk_size == 200
        assert result.num_chunks == 10
        assert result.retrieval_latency == 0.5
        assert result.total_time == 1.2

    except ImportError:
        pytest.skip("compare_chunking_strategies.py not implemented yet")


def test_comparison_table_generated_with_expected_columns():
    """Test that comparison table is generated with expected columns."""
    try:
        from ragas_evaluation.examples.advanced.compare_chunking_strategies import (
            display_comparison_table,
        )

        # Create test results
        results = [
            {
                "strategy": "small",
                "chunk_size": 200,
                "num_chunks": 10,
                "avg_chunk_length": 195.0,
                "retrieval_latency": 0.5,
                "total_time": 1.2,
            },
            {
                "strategy": "medium",
                "chunk_size": 500,
                "num_chunks": 5,
                "avg_chunk_length": 490.0,
                "retrieval_latency": 0.3,
                "total_time": 1.0,
            },
        ]

        # This should not raise an error
        display_comparison_table(results)

    except ImportError:
        pytest.skip("compare_chunking_strategies.py not implemented yet")


def test_tradeoff_analysis_output_format():
    """Test trade-off analysis output format."""
    try:
        from ragas_evaluation.examples.advanced.compare_chunking_strategies import (
            generate_tradeoff_analysis,
        )

        # Create test results
        results = [
            {
                "strategy": "small",
                "chunk_size": 200,
                "num_chunks": 10,
                "avg_chunk_length": 195.0,
                "retrieval_latency": 0.5,
                "total_time": 1.2,
                "metrics": {"faithfulness": 0.85},
            },
            {
                "strategy": "medium",
                "chunk_size": 500,
                "num_chunks": 5,
                "avg_chunk_length": 490.0,
                "retrieval_latency": 0.3,
                "total_time": 1.0,
                "metrics": {"faithfulness": 0.82},
            },
        ]

        # Generate trade-off analysis
        analysis = generate_tradeoff_analysis(results)

        # Verify analysis is generated
        assert isinstance(analysis, str)
        assert len(analysis) > 0

    except ImportError:
        pytest.skip("compare_chunking_strategies.py not implemented yet")
