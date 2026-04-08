# RAGas Evaluation Basics

This directory contains fundamental examples demonstrating RAGas (RAG Assessment) package capabilities for evaluating Retrieval-Augmented Generation (RAG) systems using Zhipu AI backend integration.

## 📚 Complete Guide

For comprehensive tutorials with screenshots, see: **[RAGAS_COMPLETE_GUIDE.md](../../examples/advanced/RAGAS_COMPLETE_GUIDE.md)**

## Overview

RAGas is a framework that helps you evaluate your RAG pipelines using a variety of metrics that measure:
- **Faithfulness**: Factual consistency of generated answers with retrieved context
- **Answer Relevancy**: How well the answer addresses the question
- **Context Precision**: Quality and relevance of retrieved contexts
- **Context Recall**: Completeness of retrieved contexts (requires ground truth)
- **Answer Correctness**: Accuracy compared to ground truth (requires ground truth)

## Prerequisites

Before running these examples, ensure you have:

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

2. **Install dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

---

## Quick Start: Minimal Working Example

```python
# minimal_ragas_evaluation.py
import os
import pandas as pd
from datasets import Dataset as HFDataset
from ragas import evaluate
from ragas.metrics._faithfulness import faithfulness
from ragas.metrics._context_precision import context_precision
from ragas.llms.base import llm_factory
from openai import OpenAI as OpenAIClient
from ragas.run_config import RunConfig

# 1. Configure Zhipu AI backend
api_key = os.getenv("ZHIPU_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_BASE_URL"] = "https://open.bigmodel.cn/api/paas/v4/"

# 2. Prepare your evaluation data
data = [{
    "user_input": "What is the GST rate in Australia?",
    "retrieved_contexts": ["GST is a broad-based tax of 10% on most goods in Australia."],
    "response": "The GST rate in Australia is 10%.",
    "reference": "The GST rate is 10%."  # optional
}]
hf_dataset = HFDataset.from_pandas(pd.DataFrame(data))

# 3. Configure RAGAS with Zhipu AI
client = OpenAIClient(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
ragas_llm = llm_factory(model="glm-5", client=client, max_tokens=4096)
faithfulness.llm = ragas_llm
context_precision.llm = ragas_llm

# 4. Run evaluation
results = evaluate(
    dataset=hf_dataset,
    metrics=[faithfulness, context_precision],
    run_config=RunConfig(max_retries=3, max_wait=60, timeout=60),
)

# 5. View results
print(results.to_pandas())
```

**Expected output:**
```
   user_input                                        retrieved_contexts  ...  faithfulness  context_precision
0  What is the GST rate in Australia?  [GST is a broad-based tax of 10% ...]  ...         1.000               1.0

[1 rows x 5 columns]
```

---

## Examples

### 1. Simple Evaluation (`simple_evaluation_new.py`)

Complete RAGAS evaluation workflow with Zhipu AI backend integration.

**Run the example:**
```bash
export $(grep -v '^#' .env | xargs) && uv run python src/ragas_evaluation/basics/simple_evaluation_new.py
```

**Step-by-Step Code Breakdown:**

#### Step 1: Load Configuration and Setup Environment
```python
from ragas_evaluation.shared.config import get_ragas_config
import os

config = get_ragas_config()

# Configure RAGAS to use Zhipu AI (OpenAI-compatible API)
os.environ["OPENAI_API_KEY"] = config.zhipu_api_key
os.environ["OPENAI_BASE_URL"] = "https://open.bigmodel.cn/api/paas/v4/"
```

#### Step 2: Prepare Your Dataset
```python
from ragas_evaluation.shared.data_loader import load_evaluation_dataset
import pandas as pd
from datasets import Dataset as HFDataset

# Load your evaluation data
dataset = load_evaluation_dataset()

# RAGAS expects specific column names - rename accordingly
df = pd.DataFrame(dataset)
df_renamed = df.rename(columns={
    "question": "user_input",           # Required: user's question
    "contexts": "retrieved_contexts",   # Required: list of retrieved passages
    "response": "response",              # Required: your RAG system's answer
    "reference_answer": "reference"      # Optional: ground truth answer
})

# Convert to HuggingFace Dataset format
hf_dataset = HFDataset.from_pandas(df_renamed)
```

#### Step 3: Configure Metrics with LLM
```python
from ragas.metrics._faithfulness import faithfulness
from ragas.metrics._context_precision import context_precision
from ragas.llms.base import llm_factory
from openai import OpenAI as OpenAIClient
from ragas.run_config import RunConfig

# Create Zhipu AI client
client = OpenAIClient(
    api_key=config.zhipu_api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

# Create RAGAS LLM wrapper with increased max_tokens
ragas_llm = llm_factory(model="glm-5", client=client, max_tokens=4096)

# Inject LLM into metrics
faithfulness.llm = ragas_llm
context_precision.llm = ragas_llm
```

#### Step 4: Run Evaluation
```python
from ragas import evaluate

run_config = RunConfig(max_retries=3, max_wait=60, timeout=60)
results = evaluate(
    dataset=hf_dataset,
    metrics=[faithfulness, context_precision],
    run_config=run_config,
)

# Access results
results_df = results.to_pandas()
print(results_df[["faithfulness", "context_precision"]].mean())
```

**Expected output:**
```
Step 1: Loading configuration...
MLflow tracking URI: http://localhost:5000
Configured RAGAS to use Zhipu AI backend

Step 2: Loading evaluation dataset...
Loaded 7 evaluation examples

Step 3: Preparing data for RAGAS...
Data prepared for RAGAS evaluation

Step 4: Creating RAGAS metrics...
Created RAGAS evaluation with metrics:
  - faithfulness
  - context_precision

Step 5: Running RAGAS evaluation...
Evaluating: 100%|██████████| 14/14 [06:40<00:00, 28.61s/it]
Evaluation complete!

      Evaluation Results
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric            ┃ Score  ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ faithfulness      │ 0.9286 │
│ context_precision │ 1.0000 │
└───────────────────┴────────┘

Evaluation Summary
• Dataset size: 7 examples
• Metrics evaluated: 2
• Average score: 0.9643
• Backend: Zhipu AI (glm-5)
```

---

### 2. Metric Demonstration (`metric_demonstration.py`)

Individual demonstrations of each RAGAS metric with explanations.

**Run the example:**
```bash
uv run python src/ragas_evaluation/basics/metric_demonstration.py
```

**Expected output:**
```
RAGas Metrics Demonstration

Faithfulness
 Measures the factual consistency of the generated answer against the retrieved context.
 Score range: 0.0-1.0 (higher is better)

Example Scenario:
  Question: What is the GST rate in Australia?
  Context: 'GST is a broad-based tax of 10% on most goods in Australia.'
  Response (High Faithfulness): 'The GST rate in Australia is 10%.'
  Response (Low Faithfulness): 'The GST rate in Australia is 15%.'

Answer Relevancy
 Measures how well the generated answer addresses the given question.
 Score range: 0.0-1.0 (higher is better)

Context Precision
 Measures how relevant the retrieved contexts are to the given question.
 Score range: 0.0-1.0 (higher is better)

Context Recall
 Measures the ability of the retriever to retrieve all relevant information.
 Score range: 0.0-1.0 (higher is better)
 Requires: Ground truth reference answers

Answer Correctness
 Measures the accuracy of the generated answer compared to the ground truth.
 Score range: 0.0-1.0 (higher is better)
 Requires: Ground truth reference answers

All Metrics Demonstrated:
• Faithfulness: Factual consistency with context
• Answer Relevancy: How well answer addresses question
• Context Precision: Quality of retrieved contexts
• Context Recall: Completeness of retrieved contexts (requires ground truth)
• Answer Correctness: Accuracy compared to ground truth (requires ground truth)
```

**Available metrics:**

| Metric | Purpose | Score Range | Ground Truth Required |
|--------|---------|-------------|---------------------|
| **Faithfulness** | Factual consistency with context | 0.0-1.0 (higher is better) | No |
| **Answer Relevancy** | How well answer addresses question | 0.0-1.0 (higher is better) | No |
| **Context Precision** | Quality of retrieved contexts | 0.0-1.0 (higher is better) | Yes |
| **Context Recall** | Completeness of retrieved contexts | 0.0-1.0 (higher is better) | Yes |
| **Answer Correctness** | Accuracy compared to ground truth | 0.0-1.0 (higher is better) | Yes |

---

## Dataset Format

RAGAS requires evaluation data in the following format:

```python
# Required columns
{
    "user_input": "What is the GST rate in Australia?",
    "retrieved_contexts": [
        "GST is a broad-based tax of 10% on most goods in Australia."
    ],
    "response": "The GST rate in Australia is 10%.",
}

# Optional column (for metrics requiring ground truth)
{
    "user_input": "...",
    "retrieved_contexts": [...],
    "response": "...",
    "reference": "The GST rate is 10%."  # Ground truth answer
}
```

**Field descriptions:**
- `user_input`: The user query to evaluate (previously named `question`)
- `retrieved_contexts`: List of retrieved document passages (previously named `contexts`)
- `response`: Your RAG system's generated answer
- `reference`: Ground truth answer (optional, needed for some metrics)

**Creating a dataset from scratch:**
```python
import pandas as pd
from datasets import Dataset as HFDataset

evaluation_data = [
    {
        "user_input": "What is the GST rate in Australia?",
        "retrieved_contexts": ["GST is a broad-based tax of 10% on most goods, services and other items in Australia."],
        "response": "The GST rate in Australia is 10%.",
        "reference": "The GST rate is 10%."
    },
    {
        "user_input": "When was GST introduced in Australia?",
        "retrieved_contexts": ["GST was introduced in Australia on 1 July 2000."],
        "response": "GST was introduced in Australia on July 1, 2000.",
        "reference": "GST was introduced on 1 July 2000."
    }
]

hf_dataset = HFDataset.from_pandas(pd.DataFrame(evaluation_data))
```

---

## Quick Reference

### Common Evaluation Patterns

**Pattern 1: Metrics without ground truth**
```python
from ragas.metrics._faithfulness import faithfulness
from ragas.metrics._context_precision import context_precision

metrics_no_gt = [faithfulness, context_precision]
```

**Pattern 2: Metrics with ground truth**
```python
from ragas.metrics._context_recall import context_recall
from ragas.metrics._answer_correctness import answer_correctness

metrics_with_gt = [
    faithfulness,
    context_precision,
    context_recall,
    answer_correctness
]
```

**Pattern 3: Extracting results**
```python
# Get results as pandas DataFrame
results_df = results.to_pandas()

# Calculate average scores
avg_faithfulness = results_df["faithfulness"].mean()
avg_context_precision = results_df["context_precision"].mean()

# Get individual sample scores
for idx, row in results_df.iterrows():
    print(f"Sample {idx}: Faithfulness={row['faithfulness']:.3f}")
```

**Expected output:**
```
Sample 0: Faithfulness=1.000
Sample 1: Faithfulness=0.850
Sample 2: Faithfulness=0.920
...
Average faithfulness: 0.9286
Average context_precision: 1.0000
```

**Pattern 4: Custom run configuration**
```python
from ragas.run_config import RunConfig

# For slower/more reliable evaluation
run_config = RunConfig(
    max_retries=5,      # More retries for unstable connections
    max_wait=90,        # Longer wait between retries
    timeout=120         # Longer timeout for complex evaluations
)

# For faster evaluation (development)
run_config = RunConfig(
    max_retries=1,
    max_wait=30,
    timeout=30
)
```

---

## Key Configuration

### Zhipu AI Backend Configuration
```python
import os

# Required environment variables
os.environ["OPENAI_API_KEY"] = config.zhipu_api_key
os.environ["OPENAI_BASE_URL"] = "https://open.bigmodel.cn/api/paas/v4/"

# Available models
# - glm-5: Most capable, recommended for evaluation
# - glm-4: Faster, good for simple metrics
```

### LLM Factory Options
```python
from ragas.llms.base import llm_factory
from openai import OpenAI as OpenAIClient

client = OpenAIClient(
    api_key=config.zhipu_api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

# Standard configuration
ragas_llm = llm_factory(
    model="glm-5",
    client=client,
    max_tokens=4096  # Important: Set high enough for evaluation responses
)

# With temperature (for reproducible results)
ragas_llm = llm_factory(
    model="glm-5",
    client=client,
    max_tokens=4096,
    temperature=0.1  # Low temperature for consistent evaluation
)
```

---

## Next Steps

After mastering these basics:

1. **MLflow Integration**: See `../with_mlflows/` for experiment tracking
2. **Advanced Patterns**: See `../examples/advanced/` for production-level patterns
3. **Complete Guide**: See [RAGAS_COMPLETE_GUIDE.md](../../examples/advanced/RAGAS_COMPLETE_GUIDE.md) for comprehensive tutorials

---

## Additional Resources

- **RAGas Documentation**: https://docs.ragas.io/
- **Zhipu AI**: https://open.bigmodel.cn/
- **MLflow Documentation**: https://mlflow.org/docs/
- **Complete Guide**: [RAGAS_COMPLETE_GUIDE.md](../../examples/advanced/RAGAS_COMPLETE_GUIDE.md)
