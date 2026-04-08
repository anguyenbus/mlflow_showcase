# RAGas Evaluation Examples

Comprehensive examples demonstrating RAGas (RAG Assessment) evaluation framework for Retrieval-Augmented Generation (RAG) systems using Zhipu AI backend integration.

## 📚 Complete Guide

For a comprehensive guide covering all RAGAS evaluation patterns from basics to advanced, see: **[RAGAS_COMPLETE_GUIDE.md](examples/advanced/RAGAS_COMPLETE_GUIDE.md)**

This complete guide includes:
- Step-by-step tutorials for each evaluation pattern
- MLflow integration examples with screenshots
- Advanced production-level patterns
- Real-world use cases and best practices
- 10 MLflow UI screenshots demonstrating experiment tracking

This complete guide includes:
- Step-by-step tutorials for each evaluation pattern
- MLflow integration examples with screenshots
- Advanced production-level patterns
- Real-world use cases and best practices

## Overview

This directory contains practical examples for evaluating RAG systems using the RAGas framework. Examples are organized by complexity level from basic fundamentals to advanced production patterns.

### What is RAGas?

RAGas is a framework that helps you evaluate your RAG pipelines using metrics that measure:
- **Faithfulness**: Factual consistency of generated answers with retrieved context
- **Answer Relevancy**: How well the answer addresses the question
- **Context Precision**: Quality and relevance of retrieved contexts
- **Context Recall**: Completeness of retrieved contexts
- **Answer Correctness**: Accuracy compared to ground truth

## Example Levels

| Level | Directory | Description | Prerequisites |
|-------|-----------|-------------|---------------|
| **Basics** | `basics/` | Fundamental RAGas evaluation concepts | Python, RAG basics |
| **MLflow Integration** | `with_mlflows/` | MLflow tracking for experiments | Basics completed |
| **Advanced** | `examples/advanced/` | Production-level patterns | Basics + MLflow |

## Quick Start

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

2. **Install dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

3. **Run a basic example**:
   ```bash
   uv run python src/ragas_evaluation/basics/simple_evaluation.py
   ```

## Examples

### Basics (`basics/`)

**Target Audience:** Users new to RAGas evaluation

**Examples:**
- **Simple Evaluation**: Complete RAGas evaluation workflow
- **Metric Demonstration**: Understanding each RAGas metric

**Learn:** RAGas fundamentals, metric interpretation, evaluation workflow

**Run:** `uv run python src/ragas_evaluation/basics/simple_evaluation.py`

**Documentation:** `@src/ragas_evaluation/basics/README.md`

---

### MLflow Integration (`with_mlflows/`)

**Target Audience:** Users who want to track experiments over time

**Examples:**
- **Manual Logging**: Explicit MLflow parameter and metric logging
- **Auto Logging**: Automatic MLflow evaluation tracking

**Learn:** MLflow experiment tracking, run comparison, artifact management

**Run:** `uv run python src/ragas_evaluation/with_mlflows/manual_logging.py`

**Documentation:** `@src/ragas_evaluation/with_mlflows/README.md`

---

### Advanced (`examples/advanced/`)

**Target Audience:** Users ready for production-level evaluation patterns

**Examples:**
- **Chunking Strategy Comparison**: Compare different document chunk sizes
- **Model Comparison**: Evaluate multiple LLM models with identical metrics
- **Custom Metrics**: Create domain-specific evaluation metrics
- **Test Data Generation**: Generate synthetic and golden datasets

**Learn:** Production optimization, A/B testing, domain-specific evaluation, data generation

**Run:** `uv run python src/ragas_evaluation/examples/advanced/compare_chunking_strategies.py`

**Documentation:** `@src/ragas_evaluation/examples/advanced/README.md`

## Quick Reference

### Choosing the Right Example

| Your Goal | Start With | Then Explore |
|-----------|------------|--------------|
| Learn RAGas basics | `basics/simple_evaluation.py` | `basics/metric_demonstration.py` |
| Track experiments | `with_mlflows/manual_logging.py` | `with_mlflows/auto_logging.py` |
| Optimize chunking | `examples/advanced/compare_chunking_strategies.py` | `examples/advanced/compare_models.py` |
| Create custom metrics | `examples/advanced/custom_metrics.py` | `examples/advanced/test_data_generation.py` |
| Prepare for production | All basics → All MLflow → All advanced | - |

### Expected Time to Complete

| Example Level | Estimated Time |
|---------------|----------------|
| Simple Evaluation | 15-20 minutes |
| Metric Demonstration | 10-15 minutes |
| MLflow Manual Logging | 20-25 minutes |
| MLflow Auto Logging | 15-20 minutes |
| Chunking Comparison | 20-30 minutes |
| Model Comparison | 25-35 minutes |
| Custom Metrics | 30-40 minutes |
| Data Generation | 25-35 minutes |

## Shared Utilities

All examples leverage shared utilities for consistency:

- **Configuration** (`@src/ragas_evaluation/shared/config.py`): Environment-based config loading
- **MLflow Handler** (`@src/ragas_evaluation/shared/mlflow_handler.py`): MLflow setup and logging
- **Data Loader** (`@src/ragas_evaluation/shared/data_loader.py`): Dataset loading and validation
- **Metrics** (`@src/ragas_evaluation/shared/metrics.py`): Zhipu AI backend configuration

## Prerequisites

### Required

- Python 3.10 or higher
- Zhipu AI API key
- Dependencies installed via `uv sync`

### Recommended Knowledge

- Familiarity with RAG (Retrieval-Augmented Generation) concepts
- Understanding of LLM evaluation challenges
- Basic MLflow knowledge (for MLflow examples)

## Common Workflows

### Development Workflow

1. Start with `basics/simple_evaluation.py` to understand RAGas
2. Explore `basics/metric_demonstration.py` for detailed metric understanding
3. Use `with_mlflows/` examples to track your experiments
4. Apply `examples/advanced/` patterns for production optimization

### Production Evaluation Workflow

1. Create evaluation dataset from production queries
2. Run baseline evaluation with `basics/simple_evaluation.py`
3. Track metrics in MLflow using `with_mlflows/` patterns
4. Optimize using `examples/advanced/` comparison techniques
5. Set up continuous monitoring with custom metrics

### A/B Testing Workflow

1. Use `examples/advanced/compare_chunking_strategies.py` to test chunking
2. Use `examples/advanced/compare_models.py` to test models
3. Track all experiments in MLflow
4. Compare results using MLflow UI
5. Deploy based on data-driven decisions

## Troubleshooting

### Common Issues

**Problem**: Missing API key error
```bash
ERROR: ZHIPU_API_KEY environment variable is not set
```
**Solution**: Set up `.env` file with your Zhipu AI API key

**Problem**: Dataset not found error
```bash
ERROR: Evaluation dataset not found
```
**Solution**: Create `data/ragas_evaluation/evaluation_dataset.json` with test data

**Problem**: MLflow tracking server not accessible
```bash
ERROR: Cannot connect to MLflow tracking server
```
**Solution**: Start MLflow UI with `uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000`

## Additional Resources

- **RAGas Documentation**: https://docs.ragas.io/
- **Zhipu AI**: https://open.bigmodel.cn/
- **MLflow Documentation**: https://mlflow.org/docs/
- **Project README**: `@README.md`

## Contributing

When adding new examples:

1. Follow existing code style and patterns
2. Include comprehensive docstrings
3. Add tests for new functionality
4. Update relevant README documentation
5. Use shared utilities where applicable

## License

See project root for license information.
