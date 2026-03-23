# Tracing Deep Dive: LLM Observability

This guide explores MLflow's tracing capabilities for LLM applications. You'll learn different tracing approaches, from simple decorators to advanced distributed tracing.

## Prerequisites

- Completed [01-basics-tracking.md](01-basics-tracking.md)
- MLflow UI running at http://localhost:5000
- Zhipu AI API key configured

## What is Tracing?

Tracing captures the execution flow of your LLM applications, showing:

- Function calls and their relationships
- Input/output data for each call
- Timing information and latency
- Error handling and exceptions

MLflow tracing provides end-to-end observability for debugging and optimization.

## Exercise 1: Decorator-Based Tracing

The simplest way to add tracing to your functions.

1. **Run the decorator tracing example:**

```bash
uv run python src/basics/tracing_decorators.py
```

2. **Expected output:**

```
Running traced function...
Function executed successfully
Trace ID: <trace_id>
View trace at: http://localhost:5000/#/traces/<trace_id>
```

3. **View the trace in MLflow UI:**

- Go to http://localhost:5000
- Navigate to "Traces" in the left sidebar
- Click on the latest trace
- You should see:
  - Function name and timing
  - Input arguments
  - Output/return value
  - Execution time

### Key Concepts

**@mlflow.trace decorator:**

```python
import mlflow

@mlflow.trace
def my_function(arg1, arg2):
    """This function is automatically traced."""
    result = arg1 + arg2
    return result
```

**What gets captured:**

- Function name and module
- Arguments passed to the function
- Return value
- Execution time
- Any exceptions raised

## Exercise 2: Manual Span Creation

For fine-grained control over what gets traced.

1. **Run the manual spans example:**

```bash
uv run python src/intermediate/tracing_manual_spans.py
```

2. **Expected output:**

```
Starting manual span example...
Processing data...
Span 'data_processing' completed
Transforming data...
Span 'data_transformation' completed
Trace complete
```

3. **View the trace in MLflow UI:**

- Look for the trace with multiple spans
- You should see:
  - Parent span: `data_processing`
  - Child span: `data_transformation`
  - Timing information for each

### Key Concepts

**Manual span creation:**

```python
import mlflow

def process_data(data):
    with mlflow.start_span(name="data_processing") as span:
        # Your processing logic
        result = transform(data)

        # Set custom attributes
        span.set_attribute("data_size", len(data))
        span.set_attribute("processing_method", "batch")

        return result
```

**Span attributes:**

```python
# Add custom metadata to spans
span.set_attribute("user_id", "12345")
span.set_attribute("model_version", "v1.0")
span.set_attribute("input_length", 150)
```

## Exercise 3: Nested Spans

Understanding parent-child relationships in traces.

1. **Run the nested spans example:**

```bash
uv run python src/intermediate/tracing_nested.py
```

2. **Expected output:**

```
Starting nested spans example...
  Calling function A...
    Calling function B...
      Calling function C...
  All nested functions completed
Trace ID: <trace_id>
```

3. **View the trace hierarchy:**

- In MLflow UI, expand the trace to see the hierarchy
- You should see:
  - `function_a` (parent)
    - `function_b` (child of A)
      - `function_c` (child of B)
  - Timing information showing execution order

### Key Concepts

**Automatic parent-child relationships:**

```python
@mlflow.trace
def parent_function():
    """This creates a parent span."""
    result1 = child_function_1()
    result2 = child_function_2()
    return result1 + result2

@mlflow.trace
def child_function_1():
    """This creates a child span."""
    return "data"

@mlflow.trace
def child_function_2():
    """This creates another child span."""
    return "more data"
```

**Understanding span hierarchy:**

- Parent spans encompass their children
- Timing shows both total and individual execution time
- Errors in children propagate to parents

## Exercise 4: Distributed Tracing

Tracing across multiple function calls and modules.

1. **Run the distributed tracing example:**

```bash
uv run python src/intermediate/tracing_distributed.py
```

2. **Expected output:**

```
Starting distributed tracing...
Fetching data from API...
Processing data...
Storing results...
Distributed trace complete
Trace ID: <trace_id>
```

3. **View the distributed trace:**

- The trace shows functions from different modules
- All related spans are linked in a single trace
- You can see the complete execution flow

### Key Concepts

**Trace correlation:**

```python
import mlflow

# All spans in the same context are correlated
with mlflow.start_run():
    data = fetch_data()  # Creates span 1
    processed = process(data)  # Creates span 2
    store(processed)  # Creates span 3
```

**Retrieving traces:**

```python
# Get a specific trace by ID
trace = mlflow.get_trace(trace_id)

# Search for traces
traces = mlflow.search_traces(
    filter_string="params.model_name = 'glm-5-flash'"
)
```

## Exercise 5: LangChain Auto-Tracing

Automatic tracing for LangChain chains.

1. **Run the LangChain tracing example:**

```bash
uv run python src/intermediate/tracing_langchain.py
```

2. **Expected output:**

```
Enabling LangChain autologging...
Creating LangChain chain...
Invoking chain...
Response: <LLM response>
LangChain autologging complete
```

3. **View the LangChain trace:**

- The trace shows all LangChain components:
  - Prompt template
  - LLM invocation
  - Output parser
  - Chain composition

### Key Concepts

**LangChain autologging:**

```python
import mlflow

# Enable automatic LangChain tracing
mlflow.langchain.autolog(
    log_input_examples=True,
    log_model_signatures=True,
    log_models=True
)

# Now all LangChain chains are automatically traced
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="glm-5-flash")
response = llm.invoke("Hello")  # Automatically traced
```

**What gets captured:**

- Chain structure and components
- Prompt templates and inputs
- LLM calls and responses
- Intermediate outputs
- Timing for each component

## Exercise 6: Trace Search and Inspection

Finding and analyzing traces.

1. **Run the trace search example:**

```bash
uv run python src/intermediate/tracing_search.py
```

2. **Expected output:**

```
Searching for traces...
Found 5 traces
Trace 1: <trace_id> - Duration: 1.2s
Trace 2: <trace_id> - Duration: 0.8s
...
```

### Key Concepts

**Searching traces:**

```python
# Search by experiment
traces = mlflow.search_traces(
    experiment_ids=["experiment_id"]
)

# Search by filter
traces = mlflow.search_traces(
    filter_string="attributes.model_name = 'glm-5-flash'"
)

# Search with pagination
traces = mlflow.search_traces(
    max_results=10,
    page_token="next_page_token"
)
```

**Analyzing traces:**

```python
# Get trace details
trace = mlflow.get_trace(trace_id)

# Access span data
for span in trace.data.spans:
    print(f"Span: {span.name}")
    print(f"Duration: {span.duration_ms}ms")
    print(f"Inputs: {span.inputs}")
    print(f"Outputs: {span.outputs}")
```

## Best Practices

### When to Use Decorator Tracing

- Simple functions with clear inputs/outputs
- Quick instrumentation without code changes
- Functions with stable interfaces

### When to Use Manual Spans

- Complex logic with multiple steps
- Need for custom attributes
- Performance-critical code paths
- Asynchronous operations

### Organizing Traces

- Use descriptive span names
- Add relevant attributes for filtering
- Group related operations in parent spans
- Keep spans focused on single responsibilities

## Verification Checklist

Before moving to the next guide, verify:

- [ ] You can view traces in MLflow UI
- [ ] Decorator tracing captures function calls
- [ ] Manual spans provide fine-grained control
- [ ] Nested spans show correct hierarchy
- [ ] Distributed tracing correlates related calls
- [ ] LangChain autologging captures chain execution
- [ ] You can search and filter traces

## Troubleshooting

**Issue: Traces not appearing in UI**

- Solution: Ensure MLflow UI is running and you're using the correct tracking URI

**Issue: Spans not linked**

- Solution: Make sure span creation happens within the same run context

**Issue: Missing span attributes**

- Solution: Use `span.set_attribute()` to add custom metadata

**Issue: LangChain autologging not working**

- Solution: Call `mlflow.langchain.autolog()` before creating chains

## Next Steps

- **[03-evaluation-framework.md](03-evaluation-framework.md)** - Learn evaluation metrics and frameworks
- **[04-rag-implementation.md](04-rag-implementation.md)** - Build RAG systems with tracing

## Additional Resources

- [MLflow Tracing Documentation](https://mlflow.org/docs/latest/llms/tracing.html)
- Tracing examples: @src/basics/tracing_decorators.py, @src/intermediate/
