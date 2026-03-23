# ADR 001: MLflow for LLM Observability

## Status

Accepted

## Context

We need an observability solution for LLM applications that provides:

- **Experiment tracking**: Log parameters, metrics, and artifacts
- **Tracing**: Capture execution flows and latency
- **Evaluation**: Assess model performance with standard metrics
- **Model management**: Version, store, and deploy models
- **UI**: Visualize and analyze results

### Requirements

1. **Python-native**: Must integrate seamlessly with Python ML workflows
2. **Open-source**: No vendor lock-in or expensive licensing
3. **LLM-focused**: Support for LLM-specific features (tracing, evaluation)
4. **Easy integration**: Work with LangChain and popular LLM providers
5. **Local deployment**: Run on-premises without cloud dependencies

### Alternatives Considered

#### Option 1: MLflow

**Description**: Open-source ML platform with experiment tracking, model registry, and LLM observability.

**Pros:**

- Comprehensive LLM observability (tracing, evaluation, logging)
- Strong LangChain integration
- Active community and development
- Local deployment with SQLite backend
- Python-native API
- Rich UI for experiment comparison
- Supports multiple model frameworks

**Cons:**

- UI can be slow with large numbers of experiments
- Documentation for LLM features is evolving
- Some features still in beta
- Resource-intensive for very large deployments

**Evaluation**: Meets all requirements with strong LLM support.

#### Option 2: Weights & Biases (W&B)

**Description**: Cloud-based MLOps platform with experiment tracking and visualization.

**Pros:**

- Excellent UI and visualization
- Strong community and integrations
- Good for team collaboration
- Automated hyperparameter logging

**Cons:**

- Cloud-based with privacy concerns
- Requires paid plan for advanced features
- Limited LLM-specific features
- Vendor lock-in risk
- Not suitable for local-only deployment

**Evaluation**: Rejected due to cloud requirement and cost.

#### Option 3: LangSmith

**Description**: LangChain's observability platform for LLM applications.

**Pros:**

- Deep LangChain integration
- Purpose-built for LLM applications
- Excellent tracing and debugging
- LLM-as-a-judge evaluation

**Cons:**

- Relatively new, evolving quickly
- Limited to LangChain ecosystem
- Cloud-based (Self-hosted in beta)
- Less mature than MLflow
- Vendor lock-in risk

**Evaluation**: Good for LangChain-specific apps, but MLflow provides broader framework support.

#### Option 4: Custom Solution

**Description**: Build custom observability using Prometheus, Grafana, and Elasticsearch.

**Pros:**

- Full control over features
- No vendor lock-in
- Can tailor to specific needs

**Cons:**

- High development cost
- Maintenance burden
- Re-inventing existing solutions
- Limited LLM-specific features
- Integration complexity

**Evaluation**: Rejected due to development cost and maintenance burden.

## Decision

**Use MLflow for LLM observability.**

### Rationale

1. **Comprehensive feature set**: Tracing, evaluation, and model management in one platform
2. **Open-source**: No licensing costs or vendor lock-in
3. **LLM-focused**: Dedicated LLM observability features
4. **LangChain integration**: Excellent support for LangChain chains and agents
5. **Local deployment**: Runs on-premises with SQLite or PostgreSQL
6. **Python-native**: Fits naturally into Python ML workflows
7. **Active development**: Regular updates and growing LLM feature set
8. **UI visualization**: Compare experiments and trace executions visually

### Implementation Approach

```python
# Enable MLflow tracking
import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("llm_applications")

# Enable LangChain autologging
mlflow.langchain.autolog()

# Trace functions
@mlflow.trace
def my_llm_function():
    pass

# Evaluate models
results = mlflow.evaluate(
    model=model,
    data=eval_data,
    metrics=[rouge1, exact_match]
)
```

## Consequences

### Positive

1. **Unified observability**: Single platform for tracking, tracing, and evaluation
2. **Easy integration**: Minimal code changes to add observability
3. **Cost-effective**: Open-source with local deployment
4. **Scalable**: Can start with SQLite and migrate to PostgreSQL
5. **Reproducible**: All experiments logged with full context
6. **Debuggable**: Tracing shows execution flow for debugging
7. **Collaborative**: Team can share experiments and results

### Negative

1. **Learning curve**: Team must learn MLflow API and concepts
2. **Resource usage**: MLflow server requires resources for large deployments
3. **UI performance**: Can be slow with thousands of experiments
4. **Evolving features**: Some LLM features still in beta
5. **Maintenance**: Need to manage MLflow server and database

### Mitigation

1. **Training**: Provide documentation and examples for team
2. **Resource planning**: Allocate sufficient resources for MLflow server
3. **Organization**: Use experiments and runs to organize work
4. **Version pinning**: Pin MLflow version to avoid breaking changes
5. **Monitoring**: Monitor MLflow server health and performance

## Implementation Details

### Architecture

```
MLflow UI (Port 5000)
    ↓
MLflow Server
    ↓
SQLite Backend (mlflow.db)
    ↓
Artifacts Storage (mlflow-artifacts/)
```

### Configuration

```python
# config.py
import os
from pathlib import Path

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "sqlite:///mlflow.db"
)

ARTIFACT_ROOT = Path("./mlflow-artifacts")
```

### Usage Patterns

**Experiment tracking:**

```python
with mlflow.start_run():
    mlflow.log_param("model", "glm-5-flash")
    mlflow.log_metric("accuracy", 0.85)
    mlflow.log_artifact("predictions.csv")
```

**Tracing:**

```python
@mlflow.trace
def process_query(query):
    result = llm.invoke(query)
    return result
```

**Evaluation:**

```python
results = mlflow.evaluate(
    model=model,
    data=eval_data,
    metrics=["rouge1", "rouge2", "exact_match"]
)
```

## Alternatives Revisited

If MLflow doesn't meet needs in the future, consider:

1. **LangSmith**: If project becomes LangChain-exclusive
2. **W&B**: If budget allows and cloud deployment is acceptable
3. **Prometheus + Grafana**: For metrics-only monitoring
4. **Hybrid approach**: MLflow for experiments, Prometheus for metrics

## References

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow LLM Evaluation](https://mlflow.org/docs/latest/llms/llm-evaluation/index.html)
- [MLflow Tracing](https://mlflow.org/docs/latest/llms/tracing.html)
- [MLflow LangChain Integration](https://mlflow.org/docs/latest/langchain/index.html)

## Related Decisions

- ADR 002: Zhipu AI GLM-5 Model Selection (if applicable)
- ADR 003: ChromaDB for Vector Storage (if applicable)

## History

- 2026-03-20: Initial decision to use MLflow
