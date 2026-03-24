# MLflow LLM Show Case Repository

An Show Case repository demonstrating MLflow's LLM observability capabilities with Zhipu AI GLM-5 models. This repository provides progressive examples from basic tracing to advanced RAG systems with comprehensive evaluation.

## Overview

This repository teaches you how to:

- Track LLM experiments with MLflow
- Trace LangChain chains and custom functions
- Evaluate LLM applications with MLflow's evaluation framework
- Build and monitor RAG systems with full observability
- Integrate Zhipu AI GLM-5 models via OpenAI-compatible interface

## Prerequisites

- Python 3.10 or higher
- Zhipu AI account and API key ([Sign up](https://open.bigmodel.cn/))
- Basic familiarity with Python and LangChain

## Quick Start

### 1. Install Dependencies

```bash
# Install all dependencies with uv
uv sync --all-extras --dev

# Install pre-commit hooks
uv run pre-commit install
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Zhipu AI API key
# ZHIPU_API_KEY=your_actual_api_key_here
```

### 3. Run Examples

```bash
# Run basic tracking example
uv run python src/basics/mlflow_tracking.py

# Run tracing example
uv run python src/basics/tracing_decorators.py

# Run evaluation example
uv run python src/intermediate/evaluate_qa.py

# Run RAG example
uv run python src/advanced/rag/rag_tracing.py
```

### 4. View Results in MLflow UI

```bash
# Start MLflow tracking server
uv run mlflow ui

# Open browser to http://localhost:5000
```

## Project Organization

Examples are organized by complexity level:

```
.
├── src/
│   ├── basics/           # Fundamental MLflow concepts
│   │   ├── README.md     # Basics guide with screenshots
│   │   ├── screenshots/  # Example outputs in MLflow UI
│   │   ├── zhipu_completions.py
│   │   ├── mlflow_tracking.py
│   │   ├── model_logging.py
│   │   └── tracing_decorators.py
│   ├── intermediate/     # Tracing and evaluation
│   │   ├── README.md     # Intermediate guide with screenshots
│   │   ├── screenshots/  # Example outputs in MLflow UI
│   │   ├── tracing_manual_spans.py
│   │   ├── tracing_nested.py
│   │   ├── tracing_distributed.py
│   │   ├── tracing_langchain.py
│   │   ├── tracing_search.py
│   │   ├── evaluate_custom_metrics.py
│   │   ├── evaluate_qa.py
│   │   └── evaluate_summarization.py
│   └── advanced/         # RAG systems and evaluation
│       ├── README.md     # Advanced guide with screenshots
│       ├── screenshots/  # Example outputs in MLflow UI
│       ├── evaluate_baselines.py
│       ├── evaluate_llm_judge.py
│       └── rag/
│           ├── documents.py
│           ├── vector_store.py
│           ├── retrieval_chain.py
│           ├── rag_tracing.py
│           └── evaluate_rag.py
├── tests/                # Test suite mirroring src structure
├── docs/
│   ├── guides/          # Step-by-step tutorials
│   └── adr/             # Architecture decision records
└── data/                # Evaluation datasets
```

### Detailed Example Guides

Each directory has its own README with detailed explanations and screenshots:

- [Basics Guide](src/basics/README.md) - MLflow tracking, decorators, Zhipu AI integration
- [Intermediate Guide](src/intermediate/README.md) - Manual spans, nested spans, distributed tracing, LangChain autologging
- [Advanced Guide](src/advanced/README.md) - Baseline comparison, LLM judge evaluation, RAG systems

## Learning Path

### Level 1: Basics (Start Here)

1. **Zhipu AI Completions** - Learn GLM-5 model integration
2. **MLflow Tracking** - Understand experiment tracking
3. **Model Logging** - Save and load LangChain chains
4. **Tracing Decorators** - Automatic function tracing

### Level 2: Intermediate

1. **Manual Spans** - Fine-grained tracing control
2. **Nested Spans** - Trace call hierarchies
3. **Distributed Tracing** - Correlate traces across functions
4. **LangChain Autologging** - Automatic chain instrumentation
5. **Evaluation** - Assess LLM quality with metrics

### Level 3: Advanced

1. **Document Loading** - Process tax law documents
2. **Vector Stores** - Semantic search with ChromaDB
3. **RAG Pipeline** - Build retrieval-augmented generation
4. **RAG Tracing** - Observe entire RAG workflow
5. **RAG Evaluation** - Measure retrieval quality

## Expected Outputs

Each example includes expected output in its docstring. For example:

```python
"""
Expected Output:
--------------
Experiment ID: 1234567890123456789
Run ID: 9876543210987654321
Parameters logged: {'model': 'glm-5-flash', 'temperature': 0.7}
Metrics logged: {'accuracy': 0.85, 'latency': 1.23}
"""
```

## Documentation

- [Basics Tutorial](docs/guides/01-basics-tracking.md) - Getting started with MLflow tracking
- [Tracing Deep Dive](docs/guides/02-tracing-deep-dive.md) - Master observability
- [Evaluation Framework](docs/guides/03-evaluation-framework.md) - Assess LLM quality
- [RAG Implementation](docs/guides/04-rag-implementation.md) - Build production RAG

## Development

### Running Tests

```bash
# Run all tests
uv run pytest -q

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_config.py -v
```

### Code Quality

```bash
# Format code
uv run ruff format .
uv run black .

# Lint code
uv run ruff check --fix .

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Troubleshooting

### MLflow UI Not Showing Experiments

```bash
# Check MLflow tracking URI
echo $MLFLOW_TRACKING_URI

# Verify database exists
ls -la mlflow.db
```

### Zhipu AI API Errors

```bash
# Verify API key is set
echo $ZHIPU_API_KEY

# Test API connection
uv run python -c "from src.config import validate_environment; validate_environment()"
```

### Import Errors

```bash
# Reinstall dependencies
uv sync --all-extras --dev

# Verify installation
uv run pip list | grep mlflow
```