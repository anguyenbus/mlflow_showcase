# MLflow Intermediate Examples

This directory contains intermediate-level examples that demonstrate more advanced MLflow capabilities, including manual span tracing, nested spans, distributed tracing, and evaluation metrics.

## Prerequisites

Before running these examples, ensure you have:

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

2. **Start MLflow UI** (if not already running):
   ```bash
   uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
   ```

   Then open: http://localhost:5000

3. **Install dependencies** (if needed):
   ```bash
   uv sync --all-extras --dev
   ```

---

## Examples

### 1. Manual Span Tracing (`tracing_manual_spans.py`)

**Overview:** Demonstrates fine-grained control over tracing using `mlflow.start_span()` context manager, giving you complete control over what gets traced and when.

**What it demonstrates:**
- Manual span creation with `mlflow.start_span()`
- Building nested span hierarchies (parent-child relationships)
- Capturing inputs and outputs at each span level
- Document processing pipeline with multi-step tracing

**Key MLflow APIs:**

```python
import mlflow

# Manual span creation with full control
with mlflow.start_run():
    # Create parent span for document processing
    with mlflow.start_span(name="process_document") as parent_span:
        parent_span.set_inputs({"file_path": "document.pdf"})

        # Child span for text extraction
        with mlflow.start_span(name="extract_text") as extract_span:
            extract_span.set_inputs({"file_path": "document.pdf"})
            text = extract_text_from_pdf("document.pdf")
            extract_span.set_outputs({
                "text_length": len(text),
                "num_pages": 10
            })

        # Child span for sentiment analysis
        with mlflow.start_span(name="analyze_sentiment") as sentiment_span:
            sentiment_span.set_inputs({"text": text[:100]})
            sentiment = analyze_sentiment(text)
            sentiment_span.set_outputs({
                "sentiment": sentiment,
                "confidence": 0.95
            })

        # Complete parent span
        parent_span.set_outputs({
            "status": "completed",
            "sentiment": sentiment
        })

# Span hierarchy:
# process_document (parent)
# ├── extract_text (child)
# └── analyze_sentiment (child)
```

**Conditional Tracing:**

```python
# Trace only specific conditions
def process_document(file_path: str, enable_tracing: bool = False):
    if not enable_tracing:
        return simple_process(file_path)

    with mlflow.start_span(name="process_document") as span:
        span.set_inputs({"file_path": file_path})

        # Only trace if file size > threshold
        file_size = os.path.getsize(file_path)
        if file_size > 10_000_000:  # 10MB
            span.set_attribute("large_file", True)
            # Detailed tracing for large files
            with mlflow.start_span(name="detailed_processing"):
                result = detailed_process(file_path)
        else:
            result = simple_process(file_path)

        span.set_outputs({"status": "done"})
        return result
```

**How it works:**

Instead of using `@mlflow.trace` decorators, you explicitly create spans:

```python
with mlflow.start_span(name="extract_text") as span:
    span.set_inputs({"file_path": file_path})
    # ... do work ...
    span.set_outputs({"text_length": len(text)})
```

**The example creates a nested span structure:**
```
process_document (parent span)
├── extract_text (child span)
└── analyze_sentiment (child span)
```

**Manual vs Decorator-Based Tracing:**

| Aspect | Decorator (`@mlflow.trace`) | Manual (`mlflow.start_span()`) |
|--------|----------------------------|--------------------------------|
| **Control** | Automatic, less control | Full control over what/when to trace |
| **Use case** | Quick tracing of functions | Complex workflows, conditional logic |
| **Setup** | Just add decorator | Explicitly wrap code sections |
| **Best for** | Simple function calls | Multi-step pipelines, async work |

**Run the example:**
```bash
uv run python src/intermediate/tracing_manual_spans.py
```

**Expected output:**
```
Processing document: test.txt
✓ Extracted text: 175 characters
✓ Analyzed sentiment: positive
Document processing completed

Trace ID: tr-96cda33f1e63e318c8e8b2d26ff55c76
View in MLflow UI to see span hierarchy!
```

**Result in MLflow UI:**

![Manual Spans Tracing](./screenshots/tracing_manual_spans.png)
*Screenshot showing the parent-child span hierarchy*

**Real-World Use Cases:**
- Document processing pipelines
- Data ETL jobs
- Multi-step workflows where you want to see exactly what happens at each stage
- Identifying bottlenecks in complex operations
- Conditional tracing based on runtime logic

**Key concepts learned:**
- **Manual span creation**: Using `mlflow.start_span()` for explicit control
- **Span hierarchies**: Parent-child relationships in trace visualization
- **Input/output tracking**: Recording data flow through each operation
- **Fine-grained tracing**: Tracing only what matters, not entire functions

---

### 2. Nested Spans (`tracing_nested.py`)

**Overview:** Demonstrates deep span hierarchies in a data pipeline, showing how parent-child relationships represent the call flow and timing information for each stage.

**What it demonstrates:**
- Creating multi-level nested span hierarchies
- Automatic parent-child relationships from function calls
- Timing information for each span and total execution time
- Data pipeline visualization with sequential operations

**Key MLflow APIs:**

```python
import mlflow
import time

# Nested span hierarchies with decorators
@mlflow.trace
def fetch_data(source: str) -> dict:
    """Fetches data from external source."""
    time.sleep(0.5)  # Simulate API call
    return {"records": 1000, "source": source}

@mlflow.trace
def process_data(data: dict) -> dict:
    """Processes the fetched data."""
    time.sleep(0.3)  # Simulate processing
    return {"processed": data["records"], "errors": 0}

@mlflow.trace
def generate_report(data: dict) -> str:
    """Generates final report."""
    time.sleep(0.2)  # Simulate report generation
    return f"Report: {data['processed']} records processed"

@mlflow.trace
def run_data_pipeline(source: str) -> str:
    """Orchestrates the entire data pipeline."""
    # These calls automatically create nested spans
    data = fetch_data(source)
    processed = process_data(data)
    report = generate_report(processed)
    return report

# Run pipeline - creates automatic hierarchy
with mlflow.start_run():
    result = run_data_pipeline("api.example.com")

# Span hierarchy:
# run_data_pipeline (root span)
# ├── fetch_data (child span, ~500ms)
# ├── process_data (child span, ~300ms)
# └── generate_report (child span, ~200ms)
```

**Deep Nesting with Manual Spans:**

```python
# Complex nested structure with manual spans
with mlflow.start_run():
    with mlflow.start_span(name="data_pipeline") as root:
        with mlflow.start_span(name="fetch") as span1:
            data = fetch_from_api()
            span1.set_outputs({"count": len(data)})

        with mlflow.start_span(name="transform") as span2:
            with mlflow.start_span(name="clean") as child1:
                clean_data = clean(data)

            with mlflow.start_span(name="validate") as child2:
                valid_data = validate(clean_data)

            span2.set_outputs({"valid": len(valid_data)})

        with mlflow.start_span(name="load") as span3:
            load_to_database(valid_data)
```

**The example creates a sequential pipeline hierarchy:**
```
run_data_pipeline (root span)
├── fetch_data (child span, ~500ms)
├── process_data (child span, ~300ms)
└── generate_report (child span, ~200ms)
```

**Run the example:**
```bash
uv run python src/intermediate/tracing_nested.py
```

**Expected output:**
```
Fetching data from API...
Processing data: 1000 records
Generating report...
Pipeline completed successfully

Total execution time: 1.32s
```

**Result in MLflow UI:**

![Nested Spans Tracing](./screenshots/tracing_nested.png)

**Real-World Use Cases:**
- Data ETL pipelines: Extract → Transform → Load workflows
- API request chains: Multiple sequential service calls
- Batch processing jobs: Multi-stage data processing
- Performance profiling: Identifying slow stages in pipelines
- ML pipelines: Data preprocessing → Training → Evaluation

**Key concepts learned:**
- **Automatic parent-child relationships**: Spans inherit context from calling code
- **Timing hierarchy**: Total time vs individual span times
- **Sequential workflows**: Visualizing execution flow
- **Pipeline debugging**: Pinpoint slow stages in complex workflows

---

### 3. Distributed Tracing (`tracing_distributed.py`)

**Overview:** Demonstrates trace correlation across multiple distributed function calls and trace retrieval with MLflow's search capabilities.

**What it demonstrates:**
- Correlating spans across distributed function calls
- Trace retrieval using `mlflow.get_trace()`
- Searching traces with `mlflow.search_traces()`
- Understanding span counts and trace metadata

**Key MLflow APIs:**

```python
import mlflow
import uuid

# Distributed workflow with trace correlation
@mlflow.trace
def query_database(user_id: str) -> dict:
    """Simulates database query."""
    return {"user_id": user_id, "name": "John Doe"}

@mlflow.trace
def fetch_external_profile(user_id: str) -> dict:
    """Simulates external API call."""
    return {"profile": "complete"}

@mlflow.trace
def calculate_recommendations(user: dict) -> list:
    """Calculates recommendations."""
    return ["item1", "item2", "item3"]

@mlflow.trace
def update_statistics(user_id: str) -> bool:
    """Updates user statistics."""
    return True

@mlflow.trace
def user_workflow(user_id: str) -> dict:
    """Orchestrates distributed user workflow."""
    # All these calls are correlated in one trace
    user_data = query_database(user_id)
    profile = fetch_external_profile(user_id)
    recommendations = calculate_recommendations(user_data)
    update_statistics(user_id)

    return {
        "user": user_data,
        "profile": profile,
        "recommendations": recommendations
    }

# Run workflow
with mlflow.start_run():
    result = user_workflow("user_123")

# Retrieve trace information
trace = mlflow.get_trace(trace_id)
print(f"Trace ID: {trace.info.trace_id}")
print(f"Total spans: {len(trace.data.spans)}")

# Search traces with filters
traces = mlflow.search_traces(
    experiment_ids=[experiment_id],
    filter_string="user_workflow"
)

# Correlate across services with custom context
@mlflow.trace
def process_request(request_id: str):
    """Process request with correlation ID."""
    span = mlflow.get_current_span()
    span.set_attribute("request_id", request_id)
    span.set_attribute("correlation_id", str(uuid.uuid4()))

    # Call other services - all correlated
    result = service_a(request_id)
    result = service_b(result)

    return result
```

**Cross-Service Tracing:**

```python
# Service A
@mlflow.trace
def service_a(request_id: str) -> dict:
    """Service A - Business logic."""
    mlflow.get_current_span().set_attribute("service", "service-a")
    return {"data": "from_service_a"}

# Service B
@mlflow.trace
def service_b(data: dict) -> dict:
    """Service B - Processing."""
    mlflow.get_current_span().set_attribute("service", "service-b")
    return {"result": "processed"}
```

**The example creates a distributed workflow hierarchy:**
```
user_workflow (root span)
├── query_database (span 1)
├── fetch_external_profile (span 2)
├── calculate_recommendations (span 3)
└── update_statistics (span 4)
```

**Run the example:**
```bash
uv run python src/intermediate/tracing_distributed.py
```

**Expected output:**
```
Querying database for user: user_123
Fetching user profile from external service
Calculating user recommendations
Updating user statistics
User workflow completed

Trace ID: tr-e1f82d072ad54fc4520c1adb38407d42
Trace spans: 5
Found 1 traces for this workflow
```

**Result in MLflow UI:**

![Distributed Tracing](./screenshots/tracing_distributed.png)

**Real-World Use Cases:**
- **Microservices**: Tracing requests across multiple services
- **Workflow orchestration**: Complex multi-step business processes
- **API gateways**: Request routing and aggregation
- **Event-driven systems**: Async message processing
- **Debugging distributed systems**: Finding where failures occur

**Key concepts learned:**
- **Trace correlation**: Linking related operations across functions
- **Trace retrieval**: Fetching complete trace data by ID
- **Trace search**: Querying traces with filters
- **Span counting**: Understanding trace complexity

---

### 4. LangChain Autologging (`tracing_langchain.py`)

**Overview:** Demonstrates automatic LangChain chain tracing using `mlflow.langchain.autolog()`, which automatically instruments all LangChain operations without manual decorators.

**What it demonstrates:**
- Automatic LangChain chain tracing
- No manual span creation needed
- Multiple trace capture from sequential invocations
- Trace search and retrieval for LangChain operations

**Key MLflow APIs:**

```python
import mlflow
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Enable autologging - one line enables automatic tracing
mlflow.langchain.autolog()

# All LangChain operations are now automatically traced
llm = ChatOpenAI(model="glm-5")
prompt = ChatPromptTemplate.from_template(
    "You are a helpful assistant. Answer: {question}"
)

# Build chain - automatically traced
chain = prompt | llm

# Invoke chain - all steps automatically logged
with mlflow.start_run():
    response1 = chain.invoke({"question": "What is the capital of Japan?"})
    response2 = chain.invoke({"question": "How many animals are there?"})

# All traces are automatically captured and searchable
traces = mlflow.search_traces(experiment_names=["langchain_autolog"])
for trace in traces:
    print(f"Trace ID: {trace.info.trace_id}")
    print(f"Spans: {len(trace.data.spans)}")
```

**Autologging with Complex Chains:**

```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Enable autologging
mlflow.langchain.autolog()

# Complex chain with memory - automatically traced
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# All conversation turns automatically traced
response1 = conversation.predict(input="Hi, I'm John")
response2 = conversation.predict(input="What's my name?")

# Trace shows:
# - ConversationChain invocation
# - Prompt construction with history
# - LLM call
# - Response parsing
# - Memory update
```

**Autologging Configuration:**

```python
# Configure autologging behavior
mlflow.langchain.autolog(
    log_input_examples=True,  # Log sample inputs
    log_model_signatures=True,  # Log model signatures
    log_models=True,  # Log model artifacts
    disable=False,  # Enable autologging
    exclusive=False,  # Allow other instrumentation
    disable_for_unsupported_versions=False,
    silent=False  # Print confirmation
)
```

**How it works:**

Instead of manually adding `@mlflow.trace` decorators, enable autologging once:

```python
mlflow.langchain.autolog()  # Enable automatic tracing

# All LangChain chains are now automatically traced
chain.invoke({"question": "What is the capital of Japan?"})
chain.invoke({"question": "How many animals are there?"})
```

**Run the example:**
```bash
uv run python src/intermediate/tracing_langchain.py
```

**Expected output:**
```
✓ Enabled LangChain autologging
Invoking chain with question: What is the capital of Japan?
Response: The capital of Japan is Tokyo.

Invoking chain with question: How many animals are there?
Response: Scientists estimate there are approximately 8.7 million animal species...

✓ Retrieved 3 traces

Trace ID: tr-4bfc1bfa4f71eec18ed26d78ecf25c2c
Spans: 4
```

**Result in MLflow UI:**

![LangChain Autologging](./screenshots/tracing_langchain.png)

**Autologging vs Manual Tracing:**

| Aspect | Autologging | Manual Tracing |
|--------|------------|----------------|
| **Setup** | One line: `mlflow.langchain.autolog()` | Add `@mlflow.trace` to each function |
| **Coverage** | All LangChain operations automatically | Only explicitly traced functions |
| **Control** | Automatic, less control | Full control over what's traced |
| **Best for** | Quick instrumentation of LangChain apps | Custom tracing logic, non-LangChain code |

**Real-World Use Cases:**
- **RAG applications**: Automatically trace retrieval + generation
- **Chain workflows**: Multi-step LangChain chains
- **Agent systems**: Complex agent decision-making
- **Quick debugging**: No code changes needed for tracing

**Key concepts learned:**
- **Automatic instrumentation**: Enable tracing with one line
- **Framework integration**: MLflow integrates with LangChain
- **Zero-code tracing**: No decorators needed for LangChain
- **Production-ready**: Drop-in observability for LangChain apps

---

### 5. Trace Search (`tracing_search.py`)

**Overview:** Demonstrates programmatic trace retrieval and filtering using MLflow's search API, enabling you to find and analyze traces matching specific criteria.

**What it demonstrates:**
- Searching traces by experiment name
- Filtering traces by run ID
- Retrieving trace details and span information
- Batch trace analysis
- Trace metadata extraction

**Key MLflow APIs:**

```python
import mlflow

# Search traces by experiment name
traces = mlflow.search_traces(
    experiment_names=["my_experiment"],
    max_results=10
)

# Filter traces by run ID
traces = mlflow.search_traces(
    run_ids=["abc123", "def456"]
)

# Search with experiment ID
traces = mlflow.search_traces(
    experiment_ids=[1, 2, 3],
    max_results=50
)

# Analyze traces in batch
for trace in traces:
    print(f"Trace ID: {trace.info.trace_id}")
    print(f"Execution time: {trace.info.execution_time_ms}ms")
    print(f"Span count: {len(trace.data.spans)}")
    print(f"Request: {trace.data.request}")

    # Access individual spans
    for span in trace.data.spans:
        print(f"  {span.name}: {span.inputs} → {span.outputs}")

# Get specific trace by ID
trace = mlflow.get_trace(trace_id="tr-abc123")
print(f"Trace: {trace.info.trace_id}")
print(f"Status: {trace.info.status}")
```

**Advanced Trace Search:**

```python
# Search with time range
from datetime import datetime, timedelta

# Search traces from last hour
cutoff_time = datetime.now() - timedelta(hours=1)
traces = mlflow.search_traces(
    experiment_names=["production"],
    max_results=100
)

# Filter by time in Python
recent_traces = [
    t for t in traces
    if datetime.fromtimestamp(t.info.timestamp_ms / 1000) > cutoff_time
]

# Analyze performance metrics
slow_traces = []
for trace in traces:
    if trace.info.execution_time_ms > 5000:  # > 5 seconds
        slow_traces.append({
            "trace_id": trace.info.trace_id,
            "duration": trace.info.execution_time_ms,
            "span_count": len(trace.data.spans)
        })

print(f"Found {len(slow_traces)} slow traces")
```

**Trace Metadata Extraction:**

```python
# Extract metadata for analysis
def extract_trace_metadata(trace):
    """Extract key metadata from trace."""
    return {
        "trace_id": trace.info.trace_id,
        "execution_time_ms": trace.info.execution_time_ms,
        "span_count": len(trace.data.spans),
        "status": trace.info.status,
        "request": trace.data.request,
        "response": trace.data.response,
    }

# Batch analyze traces
traces = mlflow.search_traces(experiment_names=["rag_production"])
metadata_list = [extract_trace_metadata(t) for t in traces]

# Calculate statistics
import statistics
execution_times = [m["execution_time_ms"] for m in metadata_list]
print(f"Average execution time: {statistics.mean(execution_times):.2f}ms")
print(f"Median execution time: {statistics.median(execution_times):.2f}ms")
print(f"Max execution time: {max(execution_times)}ms")
```

**Run the example:**
```bash
uv run python src/intermediate/tracing_search.py
```

**Expected output:**
```
Running traced functions...
✓ Traced 10 function calls

Searching for traces...
Found 10 traces

Filtering traces by experiment: 8
Found 10 traces in experiment

Sample trace:
  ID: tr-99abde0bebc2cefc3a1cf9355f97ca6f
  Span Count: 4
  Execution Time: 1.23s

View in MLflow UI: http://localhost:5000/#/experiments/8
```

**Real-World Use Cases:**
- **Debugging**: Find traces for specific runs or time periods
- **Performance analysis**: Filter slow traces for investigation
- **Batch processing**: Analyze multiple traces programmatically
- **Monitoring**: Build custom dashboards with trace data
- **Compliance**: Export traces for auditing

**Key concepts learned:**
- **mlflow.search_traces()**: Search and filter traces
- **Trace filtering**: By experiment, run ID, time range
- **Trace metadata**: Extract span counts, execution times
- **Batch analysis**: Process multiple traces efficiently

---

## Common Issues

**Q: Manual spans don't appear in MLflow UI**
- A: Ensure you're inside an active MLflow run (`with mlflow.start_run():`)

**Q: Spans are not nested properly**
- A: Make sure child spans are created within the parent span's context manager scope

**Q: How is this different from decorator tracing?**
- A: Manual spans give you control over WHEN to create spans (useful for conditional logic, loops, async operations), while decorators trace entire functions automatically
