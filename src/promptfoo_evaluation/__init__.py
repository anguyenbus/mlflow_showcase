"""
Promptfoo Evaluation Module for LLM Applications.

This module provides comprehensive promptfoo evaluation examples for LLM applications,
demonstrating systematic prompt testing, model comparison, RAG evaluation, and MLflow
integration using Zhipu AI GLM models.

Example:
    >>> from promptfoo_evaluation.shared.config import get_zhipu_api_key
    >>> api_key = get_zhipu_api_key()

The module is organized into:
- basics/: Simple prompt testing examples
- intermediate/: Advanced assertions and custom providers
- advanced/: RAG evaluation and MLflow integration
- shared/: Reusable utilities and configurations

"""

__version__ = "0.1.0"

# Re-export key utilities for convenience
from promptfoo_evaluation.shared.config import (
    get_promptfoo_config_path,
    get_promptfoo_output_dir,
    get_zhipu_api_key,
    validate_promptfoo_installation,
)

__all__ = [
    "get_zhipu_api_key",
    "get_promptfoo_output_dir",
    "get_promptfoo_config_path",
    "validate_promptfoo_installation",
]
