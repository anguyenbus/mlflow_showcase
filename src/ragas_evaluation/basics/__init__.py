"""
Basic RAGas evaluation examples.

This module contains standalone RAGas evaluation examples
without MLflow integration.
"""

from ragas_evaluation.basics.metric_demonstration import (
    demonstrate_answer_correctness,
    demonstrate_answer_relevancy,
    demonstrate_context_precision,
    demonstrate_context_recall,
    demonstrate_faithfulness,
)
from ragas_evaluation.basics.simple_evaluation import main as simple_evaluation_main

__all__ = [
    "simple_evaluation_main",
    "demonstrate_faithfulness",
    "demonstrate_answer_relevancy",
    "demonstrate_context_precision",
    "demonstrate_context_recall",
    "demonstrate_answer_correctness",
]
