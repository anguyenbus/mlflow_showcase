"""
MLflow-integrated advanced examples for RAGas evaluation.

This package provides MLflow integration for advanced RAGas evaluation patterns,
including chunking strategy comparison, model comparison, custom metrics, and
test data generation with comprehensive tracking.
"""

from ragas_evaluation.examples.advanced.with_mlflows.compare_chunking_strategies_with_mlflow import (  # noqa: F401
    compare_chunking_strategies_with_mlflow,
)
from ragas_evaluation.examples.advanced.with_mlflows.compare_models_enhanced_with_mlflow import (  # noqa: F401
    compare_models_with_mlflow,
)
from ragas_evaluation.examples.advanced.with_mlflows.custom_metrics_with_mlflow import (  # noqa: F401
    demonstrate_custom_metrics_with_mlflow,
)
from ragas_evaluation.examples.advanced.with_mlflows.test_data_generation_with_mlflow import (  # noqa: F401
    generate_test_data_with_mlflow,
)

__all__ = [
    "compare_chunking_strategies_with_mlflow",
    "compare_models_with_mlflow",
    "demonstrate_custom_metrics_with_mlflow",
    "generate_test_data_with_mlflow",
]
