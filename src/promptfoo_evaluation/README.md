# Promptfoo Evaluation for LLM Applications

This module demonstrates systematic prompt testing, model comparison, RAG evaluation, and MLflow integration using [promptfoo](https://promptfoo.dev/) with Zhipu AI GLM models.

## Overview

Promptfoo is a CLI-based evaluation framework for LLM applications that enables:
- Systematic prompt testing with assertions
- A/B testing of prompt variants
- Model comparison across different LLMs
- RAG system evaluation with retrieval quality metrics
- Integration with MLflow for experiment tracking

## Prerequisites

### 1. Zhipu AI API Key

Set your Zhipu AI API key in the `.env` file:

```bash
ZHIPU_API_KEY=your_zhipu_api_key_here
```

Get your API key from: https://open.bigmodel.cn/

### 2. Install promptfoo

**Option 1 - Global installation (recommended for repeated use):**

```bash
npm install -g promptfoo
```

**Option 2 - Use npx (no installation required):**

```bash
npx promptfoo eval
```

See [promptfoo documentation](https://promptfoo.dev/docs/quick-start/) for more details.

### 3. Install Python Dependencies

```bash
uv sync --all-extras --dev
```

## Directory Structure

```
src/promptfoo_evaluation/
├── basics/           # Simple prompt testing examples
├── intermediate/     # Advanced assertions and custom providers
├── advanced/         # RAG evaluation and MLflow integration
└── shared/           # Reusable utilities and configurations
```

## Quick Start

### Basic Prompt Testing

```bash
# Navigate to basics directory
cd src/promptfoo_evaluation/basics

# Set environment variable and run
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval simple_test.yaml

# View results in web UI
npx promptfoo view
```

### Model Comparison

```bash
# Compare different GLM models
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval model_comparison.yaml
```

### RAG Evaluation

```bash
# Run RAG evaluation with custom provider
cd src/promptfoo_evaluation/advanced
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval rag_evaluation.yaml
```

**Note:** Or use the Python runners which handle environment variables automatically:
```bash
python simple_test.py
```

## Zhipu AI Models

This module uses Zhipu AI GLM models via OpenAI-compatible API:

| Model | Description | Use Case |
|-------|-------------|----------|
| `glm-5-flash` | Fast inference | Quick iterations, high-volume testing |
| `glm-5-plus` | Balanced performance | General-purpose evaluation |
| `glm-5-std` | Standard quality | Production-grade comparisons |

The models are accessed through the OpenAI-compatible endpoint:
```
https://open.bigmodel.cn/api/paas/v4/
```

## Configuration

All promptfoo configurations use the following base URL for Zhipu AI:

```yaml
openai:
  baseURL: https://open.bigmodel.cn/api/paas/v4/
```

**Environment Variables:**

Since promptfoo's OpenAI-compatible provider expects `OPENAI_API_KEY`, you have two options:

1. **Set it when running promptfoo:**
   ```bash
   OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval config.yaml
   ```

2. **Use the Python runners** which handle the mapping automatically:
   ```bash
   python simple_test.py
   ```

This design allows the YAML configurations to remain clean and portable while keeping your actual Zhipu AI API key secure in your `.env` file.

## Learning Path

1. **Basics** - Start with simple prompt testing and assertions
2. **Intermediate** - Learn LLM-graded assertions and custom providers
3. **Advanced** - RAG evaluation and MLflow integration

## Documentation

- [Basics Examples](./basics/README.md) - Simple prompt testing
- [Intermediate Examples](./intermediate/README.md) - Advanced assertions
- [Advanced Examples](./advanced/README.md) - RAG and MLflow integration

## Standards Compliance

This module follows project coding standards:
- **Type safety**: `beartype` decorators on all public functions
- **Filesystem**: `pathlib.Path` for all file operations
- **Output**: `rich` library for console formatting
- **Testing**: `pytest` with >=80% coverage target
- **Formatting**: `ruff` for linting and formatting

## License

MIT
