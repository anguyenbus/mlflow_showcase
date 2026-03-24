"""
RAGas evaluation with MLflow integration.

This module contains RAGas evaluation examples with MLflow tracking,
including both automatic and manual logging approaches.
"""

from ragas_evaluation.with_mlflows.auto_logging import main as auto_logging_main
from ragas_evaluation.with_mlflows.manual_logging import main as manual_logging_main

__all__ = [
    "auto_logging_main",
    "manual_logging_main",
]
