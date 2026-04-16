# RAGas Framework Profile

Comprehensive profile of RAGas, a Python-based evaluation framework for Retrieval-Augmented Generation systems.

## Architecture Overview

RAGas is a **Python-based RAG evaluation framework** designed specifically for measuring the quality of Retrieval-Augmented Generation systems. It provides metrics for faithfulness, context precision, answer relevancy, and other RAG-specific quality measures.

### Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAGAS FRAMEWORK                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   METRICS    │      │   BACKENDS   │      │  DATASETS    │  │
│  │              │      │              │      │              │  │
│  │ Faithfulness │      │ OpenAI, Anth│ropic│ Eloquence    │  │
│  │ Context Prec.│      │ Local LLMs   │ │ WikiEval, etc │  │
│  │ Answer Rel.  │      │ Custom       │ │ Synthetic gen.│  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                       │                    │          │
│         └───────────────────────┴────────────────────┘          │
│                                 ↓                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    EVALUATION ENGINE                     │  │
│  │  • Metric calculation  • LLM-as-judge  • Traditional    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                 ↓                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    INTEGRATION LAYER                     │  │
│  │  • LangChain  • LlamaIndex  • MLflow  • Custom          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Design Philosophy

- **RAG-focused**: Purpose-built for RAG system evaluation
- **LLM-based metrics**: Uses LLMs to judge subjective quality aspects
- **Hybrid approach**: Combines LLM-based and traditional metrics
- **Framework integration**: Works seamlessly with LangChain and LlamaIndex

## Core Features

### RAG-Specific Metrics

RAGas provides comprehensive metrics for evaluating RAG systems:

| Metric | Description | Requires Ground Truth |
|--------|-------------|----------------------|
| **Faithfulness** | Factual consistency of answer with retrieved context | No |
| **Answer Relevancy** | How well the answer addresses the question | No |
| **Context Precision** | Relevance of retrieved context to the question | Yes |
| **Context Recall** | Whether all relevant information was retrieved | Yes |
| **Context Entity Recall** | Entity-level retrieval completeness | Yes |
| **Answer Correctness** | Factual accuracy compared to ground truth | Yes |
| **Answer Similarity** | Semantic similarity to ground truth | Yes |

### Metric Categories

1. **Retrieval Metrics**: Evaluate the quality of retrieved documents
   - Context Precision
   - Context Recall
   - Context Entity Recall

2. **Generation Metrics**: Evaluate the quality of generated answers
   - Faithfulness
   - Answer Relevancy
   - Answer Correctness
   - Answer Similarity

3. **Composite Metrics**: Overall RAG system performance
   - Combines retrieval and generation metrics

### Test Data Generation

RAGas can **automatically generate synthetic test data** for RAG evaluation:

- **Question generation**: Create relevant questions from documents
- **Context generation**: Generate synthetic context passages
- **Answer generation**: Create ground truth answers
- **Variation generation**: Create multiple question variants

### Backend Support

RAGas supports various LLM backends for metric calculation:

- **OpenAI**: GPT models for metric calculation
- **Anthropic**: Claude models
- **Azure OpenAI**: Enterprise deployment
- **Local models**: Via LiteLLM and Hugging Face
- **Custom backends**: Any OpenAI-compatible API

## Configuration Options

### Basic Evaluation

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

# Prepare your dataset
dataset = [
    {
        "question": "What is the capital of France?",
        "answer": "Paris is the capital of France.",
        "contexts": ["France is a country in Europe. Its capital is Paris."],
        "ground_truth": "Paris"
    }
]

# Run evaluation
result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy]
)

# View results
print(result)
```

### Backend Configuration

```python
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

# Configure evaluator LLM
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o"))

# Use custom backend for metrics
from ragas.metrics import Faithfulness
metric = Faithfulness(llm=evaluator_llm)

# Run evaluation with custom backend
result = evaluate(
    dataset=dataset,
    metrics=[metric]
)
```

### Advanced Configuration

```python
from ragas import RunConfig
from ragas.metrics import ContextPrecision, ContextRecall

# Configure run settings
run_config = RunConfig(
    timeout=10,
    max_retries=3,
    max_wait=60
)

# Run with custom config
result = evaluate(
    dataset=dataset,
    metrics=[context_precision, context_recall],
    run_config=run_config
)
```

## Integration Capabilities

### LangChain Integration

```python
from langchainchain import RagEvaluator
from ragas.metrics import faithfulness

# Create RAG chain
rag_chain = create_retrieval_chain(retriever, llm)

# Evaluate with Ragas
evaluator = RagEvaluator(metrics=[faithfulness])
results = evaluator.evaluate(rag_chain, test_dataset)
```

### LlamaIndex Integration

```python
from llama_index.core.evaluation import RagEvaluator
from ragas.metrics import answer_relevancy

# Create query engine
query_engine = index.as_query_engine()

# Evaluate
evaluator = RagEvaluator(metrics=[answer_relevancy])
results = evaluator.evaluate(query_engine, test_dataset)
```

### MLflow Integration

RAGas integrates with MLflow for experiment tracking:

```python
import mlflow
from ragas import evaluate

# Start MLflow run
with mlflow.start_run():
    # Run evaluation
    result = evaluate(dataset=dataset, metrics=metrics)

    # Log metrics to MLflow
    mlflow.log_metrics(result.to_dict())

    # Log parameters
    mlflow.log_params({"model": "gpt-4", "retriever": "chromadb"})
```

For detailed MLflow integration patterns, see: [@src/ragas_evaluation/](../../src/ragas_evaluation/)

## Current Version Capabilities

### Key Strengths

1. **RAG-specialized**: Purpose-built for RAG system evaluation
2. **Comprehensive metrics**: Covers all major RAG quality dimensions
3. **LLM-based evaluation**: Uses LLMs to judge subjective quality
4. **Framework integration**: Works with LangChain and LlamaIndex
5. **Test generation**: Can generate synthetic test data
6. **Python-native**: Pure Python implementation

### Limitations

1. **RAG-focused**: Not suitable for general LLM evaluation
2. **No security testing**: Doesn't assess security vulnerabilities
3. **Cost**: LLM-based metrics require API calls
4. **Ground truth**: Some metrics require ground truth data
5. **No red teaming**: No adversarial testing capabilities

## When to Use RAGas

### Ideal For

- **RAG system developers** measuring retrieval and generation quality
- **Production RAG systems** requiring quality monitoring
- **Python-first teams** building RAG applications
- **LangChain/LlamaIndex users** needing evaluation
- **A/B testing** different RAG configurations
- **Enterprise search** and knowledge base applications

### Less Ideal For

- Non-RAG LLM applications
- Security testing (use Garak or Promptfoo)
- General prompt testing (use Promptfoo)
- Teams without Python expertise
- Projects requiring minimal configuration

## Technical Requirements

### Installation

```bash
# Standard installation
pip install ragas

# With extras for additional features
pip install ragas[evaluator]

# From source
pip install git+https://github.com/explodinggradients/ragas
```

### Dependencies

- **Python**: 3.9+
- **Package manager**: pip
- **Key dependencies**:
  - langchain (for framework integration)
  - openai/anthropic (for LLM-based metrics)
  - numpy, pandas (for data handling)

### Environment Variables

```bash
# LLM Provider API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...

# Optional: Disable telemetry
RAGAS_DO_NOT_TRACK=true
```

## RAG Evaluation Workflow

### Typical RAGas Evaluation Flow

```
1. Prepare Test Data
   ├── Questions
   ├── Retrieved Contexts
   ├── Generated Answers
   └── Ground Truth (optional)

2. Select Metrics
   ├── Faithfulness (always recommended)
   ├── Answer Relevancy (always recommended)
   ├── Context Precision (requires ground truth)
   └── Context Recall (requires ground truth)

3. Configure Backend
   ├── Select evaluator LLM
   ├── Set temperature (low = more consistent)
   └── Configure rate limits

4. Run Evaluation
   ├── Execute metrics
   ├── Aggregate results
   └── Generate report

5. Analyze Results
   ├── Identify weak components
   ├── Compare configurations
   └── Track improvements over time
```

## Related Resources

### Official Documentation

- **Main Docs**: https://docs.ragas.io/
- **GitHub**: https://github.com/explodinggradients/ragas
- **Examples**: https://docs.ragas.io/en/stable/getstarted/rag_evaluation/

### Project Tutorials

- **RAGas Tutorial**: [@src/ragas_evaluation/](../../src/ragas_evaluation/)
  - MLflow integration patterns
  - Working examples with Zhipu AI
  - Shared utilities pattern

### Related Comparisons

- **RAG Evaluation**: [RAG Evaluation Comparison](../evaluation-domains/rag-evaluation.md)
- **Feature Matrix**: [Feature Comparison Matrix](../comparisons/feature-matrix.md)
- **Hybrid Solutions**: [RAGas + Promptfoo Integration](../integration/hybrid-solutions.md)
