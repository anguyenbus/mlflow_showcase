"""
Shared utilities for RAGas evaluation.

This module contains shared configuration, data loading, metrics,
and MLflow handling utilities used across all RAGas evaluation examples.
"""

from ragas_evaluation.shared.config import (
    RagasConfig,
    get_evaluation_dataset_path,
    get_ragas_config,
    get_ragas_data_dir,
)
from ragas_evaluation.shared.data_loader import load_evaluation_dataset
from ragas_evaluation.shared.metrics import (
    configure_zhipu_backend,
    create_ragas_evaluation,
)
from ragas_evaluation.shared.mlflow_handler import (
    get_mlflow_ui_url,
    log_ragas_results,
    setup_mlflow_experiment,
)

__all__ = [
    # Config
    "RagasConfig",
    "get_ragas_config",
    "get_ragas_data_dir",
    "get_evaluation_dataset_path",
    # Data loader
    "load_evaluation_dataset",
    # Metrics
    "configure_zhipu_backend",
    "create_ragas_evaluation",
    # MLflow
    "setup_mlflow_experiment",
    "log_ragas_results",
    "get_mlflow_ui_url",
]
