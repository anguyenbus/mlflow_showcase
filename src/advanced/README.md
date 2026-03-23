# MLflow Advanced Examples

This directory contains advanced examples demonstrating MLflow's capabilities for model evaluation, LLM judge evaluation, RAG (Retrieval-Augmented Generation) tracing and evaluation.

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

### 1. Baseline Comparison (`evaluate_baselines.py`)

**Overview:** Demonstrates comparing multiple model variants and tracking their performance metrics in MLflow for model selection and improvement analysis.

**What it demonstrates:**
- Creating evaluation datasets
- Running multiple model variants
- Logging metrics for comparison
- Calculating improvements between baselines

**Run the example:**
```bash
uv run python src/advanced/evaluate_baselines.py
```

**Expected output:**
```
✓ Experiment 'mlflow-baseline-comparison' (ID: 9)
✓ Created evaluation dataset: 5 questions

Evaluating model: glm-5
✓ Evaluated model: glm-5
  Accuracy: 0.20
  Avg Latency: 46.07s

Baseline Comparison Results:
glm-5:
  Accuracy: 0.20
  Latency: 46.07s
```

**Result in MLflow UI:**

![Baseline Comparison](./screenshots/evaluate_baselines.png)

**Real-World Use Cases:**
- **A/B testing models**: Comparing new models against production baselines
- **Hyperparameter tuning**: Tracking different configurations
- **Model selection**: Choosing best model based on metrics
- **Performance regression testing**: Ensuring new models don't degrade performance
- **Cost-benefit analysis**: Trading off accuracy vs latency/cost

**Key concepts learned:**
- **Baseline metrics**: Establishing performance benchmarks
- **Comparative evaluation**: Running multiple variants under same conditions
- **Metric tracking**: Logging accuracy, latency, custom metrics
- **Improvement analysis**: Calculating relative improvements

---

### 2. LLM Judge Evaluation (`evaluate_llm_judge.py`)

Coming soon...

---

## RAG Examples

The `rag/` subdirectory contains examples for Retrieval-Augmented Generation applications:

### 2. RAG Tracing (`rag/rag_tracing.py`)

**Overview:** Demonstrates end-to-end tracing of a RAG system with MLflow, showing how to observe document loading, chunking, vector store operations, and the complete retrieval-generation pipeline.

**What it demonstrates:**
- Document loading and chunking
- Vector store creation and embeddings
- RAG chain assembly with LangChain
- Complete trace visualization of the RAG pipeline
- Multiple query execution with trace capture

**NOTE:** This example uses deterministic embeddings for Show Case purposes. The embeddings are generated using hash functions, not semantic understanding. For production RAG systems, use proper embedding models like:
- OpenAI embeddings (`text-embedding-ada-002`)
- HuggingFace sentence transformers (`all-MiniLM-L6-v2`)
- Cohere embeddings

**Run the example:**
```bash
uv run python src/advanced/rag/rag_tracing.py
```

**Expected output:**
```
RAG System Tracing Demo
==================================================
Loading documents...
Chunking documents...
Creating vector store...
Initializing LLM...
✓ Created LangChain LLM for Zhipu AI model: glm-5
Building RAG chain...

Running sample queries...

Query 1: What is the tax rate for income between $45,001 and $120,000?

Retrieved 3 chunks:
  1. Tax File Number (TFN)
A TFN is a unique identifier issued by...
  2. Tax File Number (TFN)
A TFN is a unique identifier issued by...
  3. Tax File Number (TFN)
A TFN is a unique identifier issued by...

Answer: Based on the provided context, there is no information...
```

**Result in MLflow UI:**

![RAG Tracing Demo](./screenshots/rag_tracing_demo.png)
*Screenshot showing the trace view with retrieved chunks visible in the `retrieve_documents` span*

**What you see in the screenshot:**
- Trace list showing all RAG queries
- Span tree with `retrieve_documents` and `generate_answer` spans
- Retrieved chunks with content preview and metadata
- Query inputs and generated outputs

**How to Find Chunks in MLflow UI:**

1. **Navigate to the run:**
   - Open http://localhost:5000/#/experiments/10
   - Click on the latest `rag_tracing_demo` run

2. **Open Traces section:**
   - Scroll down to "Traces"
   - Click on any trace with your query text

3. **View the span tree:**
   - You'll see: `query_rag` → `retrieve_documents` + `generate_answer`
   - Click on `retrieve_documents` span

4. **See retrieved chunks:**
   - In the span's "Outputs" section
   - Look for `chunks` array with:
     - `content`: The actual chunk text
     - `metadata`: Source file, chunk index, total chunks

This gives you **full visibility** into which documents were retrieved for each query!

**RAG Pipeline Architecture:**
```
┌─────────────┐
│ Documents   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Chunking   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Embeddings  │ ← Deterministic (Show Case)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Vector Store│
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│    RAG Chain            │
│  ┌─────────┐  ┌──────┐  │
│  │Retriever│→ │ LLM  │  │
│  └─────────┘  └──────┘  │
└─────────────────────────┘
```

**Real-World Use Cases:**
- **Knowledge base Q&A**: Company documentation, technical manuals
- **Customer support**: Automated responses from knowledge base
- **Research assistance**: Query scientific papers, legal documents
- **Show Case tools**: Textbook Q&A, course material assistance
- **Compliance**: Policy document queries, regulatory guidance

**Key concepts learned:**
- **RAG architecture**: Retrieval + Generation pattern
- **Document chunking**: Strategies for splitting large documents
- **Vector stores**: Semantic similarity search with embeddings
- **Trace visualization**: Observing the complete RAG pipeline
- **LangChain LCEL**: Composable chains for RAG systems

**Show Case Simplifications:**
- Uses deterministic hash-based embeddings (not semantic)
- Small in-memory vector store (not persistent)
- Simple chunking strategy (not domain-specific)
- Basic prompt template (not optimized)

**Production considerations:**
- Use real embedding models for semantic search
- Implement persistent vector stores (ChromaDB, Pinecone, Weaviate)
- Add re-ranking for improved retrieval quality
- Implement caching for frequently asked questions
- Add guardrails and safety filters

---

### 3. LLM Judge Evaluation (`evaluate_llm_judge.py`)

Coming soon...

### 4. RAG Evaluation (`rag/evaluate_rag.py`)

**Overview:** Demonstrates evaluating RAG system quality with MLflow metrics, measuring retrieval quality, answer relevance, and comparing different chunking strategies.

**What it demonstrates:**
- Evaluation dataset creation with ground truth answers
- Retrieval quality metrics (documents retrieved, relevance)
- Answer relevance evaluation using keyword overlap
- Chunking strategy comparison (small vs medium vs large chunks)
- MLflow metrics logging for evaluation results
- Artifact logging for detailed results

**Run the example:**
```bash
uv run python src/advanced/rag/evaluate_rag.py
```

**NOTE:** This example takes 2-3 minutes to complete as it evaluates multiple questions with the LLM.

**Expected output:**
```
RAG System Evaluation
==================================================

Setting up RAG system...
✓ Created LangChain LLM for Zhipu AI model: glm-5

Loading evaluation dataset...
✓ Created evaluation dataset: 5 questions

Evaluating retrieval quality...
✓ Retrieved 3.00 documents on average

Evaluating answer relevance...
✓ Average relevance score: 0.45

Chunking Strategy Comparison
Testing: small_chunks (size=200, overlap=25)
  Answer: Based on the provided context...

Testing: medium_chunks (size=500, overlap=50)
  Answer: According to the tax law documents...

Testing: large_chunks (size=1000, overlap=100)
  Answer: The documents indicate that...

RAG evaluation complete!
View results in MLflow UI: http://localhost:5000

Average relevance score: 0.45
Average documents retrieved: 3.00
```

**Result in MLflow UI:**

![RAG Evaluation Metrics](./screenshots/rag_evaluation_metrics.png)
*Screenshot showing evaluation metrics: avg_documents_retrieved (3.0) and avg_relevance_score (0.31)*

![RAG Evaluation Traces](./screenshots/rag_evaluation_traces.png)
*Screenshot showing trace view with retrieval_eval and answer_eval spans for each question*

![RAG Evaluation Artifacts](./screenshots/rag_evaluation_artifacts.png)
*Screenshot showing artifacts: evaluation results CSV and chunking strategy comparison files*

**What the Metrics Mean:**

- **avg_documents_retrieved: 3.0** - The system consistently retrieves 3 documents (as configured with `retrieval_k=3`)

- **avg_relevance_score: 0.31** - This indicates the keyword overlap between generated answers and ground truth. In this Show Case example with deterministic embeddings, the relevance is lower because:
  - Deterministic embeddings don't capture semantic meaning
  - Simple keyword matching is used for evaluation
  - Production systems would use semantic similarity or LLM-based evaluation

**Chunking Strategy Insights:**

From the run output and artifacts, you can compare answers across different chunk sizes:
- **small_chunks (200 chars)**: 11 chunks, more precise but may miss context
- **medium_chunks (500 chars)**: 5 chunks, balanced approach
- **large_chunks (1000 chars)**: 2 chunks, **best performance** - found the correct tax rate answer!

The evaluation revealed that **larger chunks performed better** for this specific use case, demonstrating how RAG evaluation helps optimize system configuration.

**Real-World Use Cases:**
- **RAG system optimization**: Find optimal chunk size and overlap
- **Quality assurance**: Monitor RAG system performance over time
- **A/B testing**: Compare different retrieval strategies or embedding models
- **Regression testing**: Ensure RAG quality doesn't degrade with changes
- **Production monitoring**: Track retrieval and generation metrics in production

**Key concepts learned:**
- **Evaluation datasets**: Creating ground truth for testing
- **Retrieval metrics**: Measuring document retrieval quality
- **Answer relevance**: Simple keyword overlap vs LLM-based evaluation
- **Chunking strategies**: Impact of chunk size on RAG performance
- **MLflow artifacts**: Saving detailed results for analysis

**Show Case Simplifications:**
- Uses keyword overlap for relevance (production: use LLM judge or semantic similarity)
- Small evaluation dataset (5 questions vs 100+ in production)
- Simple retrieval metrics (production: add precision@k, recall, MRR)
- Basic chunking comparison (production: test more parameters)

**Production considerations:**
- Use LLM-as-a-judge for answer quality evaluation
- Implement semantic similarity metrics with embeddings
- Add faithfulness metrics (does answer cite retrieved context?)
- Test with larger, diverse evaluation datasets
- Include edge cases and adversarial examples
- Track latency and cost metrics alongside quality

---

## Conversation Examples

The `conversation/` subdirectory contains examples for multi-turn conversation tracing:

### 5. Multi-Turn Conversation Tracing (`conversation/conversation_tracing.py`)

**Overview:** Demonstrates tracing multi-turn conversations with LangChain and MLflow, showing how to observe conversation history, context management, and message state across multiple exchanges.

**What it demonstrates:**
- Conversation memory management with ConversationBufferMemory
- Message history tracking across turns
- Context-aware responses using conversation history
- MLflow span tracing for each conversation turn
- Memory state visualization in traces

**Run the example:**
```bash
uv run python src/advanced/conversation/conversation_tracing.py
```

**Expected output:**
```
Multi-Turn Conversation Tracing Demo
==================================================

Turn 1: Hello! What's your name?
AI: I'm an AI assistant. I don't have a personal name, but you can call me Assistant!

Messages in history: 2

Turn 2: What did I just ask you?
AI: You asked me what my name is.

Messages in history: 4

Turn 3: Can you help me calculate 15 * 23?
AI: 15 multiplied by 23 equals 345.

Messages in history: 6

Turn 4: What was the result of that calculation?
AI: The result of the calculation was 345.

Conversation complete!
Total exchanges: 4
Total messages: 8
```

**Result in MLflow UI:**

![Conversation Turn 1](./screenshots/conversation_tracing_1.png)
*Screenshot showing Turn 1 trace with initial greeting*

![Conversation Turn 2](./screenshots/conversation_tracing_2.png)
*Screenshot showing Turn 2 with context from previous message*

![Conversation Turn 3](./screenshots/conversation_tracing_3.png)
*Screenshot showing Turn 3 with calculation request*

![Conversation Turn 4](./screenshots/conversation_tracing_4.png)
*Screenshot showing Turn 4 referencing previous calculation*

**What you see in the traces:**
- **Turn-level spans**: Each conversation turn is traced with `@mlflow.trace`
- **User input spans**: Log user messages with history context
- **Response generation spans**: Show LLM inputs (including history) and outputs
- **Memory metrics**: Total messages, user messages, AI messages logged as metrics
- **Conversation flow**: Click through each turn to see how history builds up

**Real-World Use Cases:**
- **Customer support chatbots**: Track conversation context across multiple turns
- **Virtual assistants**: Maintain conversation history for contextual responses
- **Dialogue systems**: Debug conversation flow and context handling
- **Chat analytics**: Analyze conversation patterns and user behavior
- **Memory optimization**: Monitor memory usage and history truncation

**Key concepts learned:**
- **ConversationBufferMemory**: LangChain's in-memory conversation history
- **Message types**: HumanMessage, AIMessage, and their roles
- **History injection**: Including conversation context in prompts
- **Memory management**: Controlling history length and token limits
- **Span relationships**: Parent-child spans in conversation turns

**Architecture:**
```
┌─────────────────────────────────────────────────────┐
│            Conversation Turn                        │
│  ┌──────────────┐      ┌──────────────────┐        │
│  │ User Input   │─────▶│ Add to Memory    │        │
│  └──────────────┘      └──────────────────┘        │
│                               │                     │
│                               ▼                     │
│  ┌──────────────┐      ┌──────────────────┐        │
│  │ Get History  │─────▶│ LLM with Context │        │
│  └──────────────┘      └──────────────────┘        │
│                               │                     │
│                               ▼                     │
│  ┌──────────────┐      ┌──────────────────┐        │
│  │ AI Response  │─────▶│ Add to Memory    │        │
│  └──────────────┘      └──────────────────┘        │
└─────────────────────────────────────────────────────┘
```

---

## Tool Calling Examples

The `tools/` subdirectory contains examples for LangChain tool calling with MLflow tracing:

### 6. Tool Calling Tracing (`tools/tool_tracing.py`)

**Overview:** Demonstrates tracing LangChain tool calling with MLflow, showing how to observe tool selection, execution, inputs/outputs, and multi-tool workflows.

**What it demonstrates:**
- Tool definitions with `@tool` decorator
- Tool binding to LLM with `bind_tools()`
- Tool selection and invocation tracing
- Multi-step tool workflows
- Tool input/output logging in spans

**Built-in Tools:**
- `get_current_time`: Get current date/time with custom formatting
- `get_current_date`: Get today's date
- `calculate`: Evaluate mathematical expressions (e.g., "15 * 23")
- `add_numbers`: Add two numbers
- `multiply_numbers`: Multiply two numbers

**Run the example:**
```bash
uv run python src/advanced/tools/tool_tracing.py
```

**Expected output:**
```
Tool Calling Tracing Demo
╔════════════════════════════════════════════════════════╗
║       Tool Calling Tracing Demo                         ║
╚════════════════════════════════════════════════════════╝

┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Tool            ┃ Description                           ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ get_current_time│ Get current date/time with custom...  │
│ get_current_date│ Get current date in YYYY-MM-DD format  │
│ calculate       │ Evaluate mathematical expressions      │
│ add_numbers     │ Add two numbers together               │
│ multiply_numbers│ Multiply two numbers                   │
└────────────────┴────────────────────────────────────────┘

Query 1: What is 15 * 23?
Response: 15 * 23 = 345

Query 2: What time is it right now?
Response: The current time is 2026-03-23 14:30:45

Query 3: What's 10 * 5 and what's today's date?
Response: 10 * 5 = 50 and today's date is 2026-03-23
```

**Result in MLflow UI:**

![Tool Calling Tracing](./screenshots/tool_tracing.png)
*Screenshot showing tool selection and execution with multiple tool calls*

**What you see in the traces:**
- **Query processing span**: Logs query and available tools
- **LLM tool execution span**: Shows LLM decision-making for tool selection
- **Tool call spans**: Individual spans for each tool invoked with:
  - Tool name and arguments
  - Tool execution results
  - Timing information
- **Response generation**: Final answer after tool execution
- **Multi-tool workflows**: See how multiple tools are called in sequence (Query 3 shows both `multiply_numbers` and `get_current_date`)

**Real-World Use Cases:**
- **Function calling**: Build agents that can interact with external systems
- **Data analysis**: Tools for querying databases, running calculations
- **API integration**: Tools for calling external APIs (weather, stock prices)
- **Workflow automation**: Multi-step processes requiring different tools
- **Debugging**: Understand which tools are selected and why

**Key concepts learned:**
- **`@tool` decorator**: Convert Python functions to LangChain tools
- **`bind_tools()`**: Attach tool schemas to LLM for tool calling
- **Tool schemas**: Automatic generation from function signatures
- **Tool selection**: LLM decides which tools to use based on query
- **Span hierarchy**: Organize tool calls within query spans

**Tool Calling Flow:**
```
┌──────────────────────────────────────────────────────┐
│              Tool Query Processing                   │
│  ┌──────────────┐      ┌──────────────────┐         │
│  │ User Query   │─────▶│ LLM with Tools   │         │
│  └──────────────┘      │ (bind_tools)     │         │
│                        └────────┬─────────┘         │
│                                 │                    │
│                                 ▼                    │
│                        ┌──────────────────┐         │
│                        │ Tool Selection   │         │
│                        │ (LLM Decision)   │         │
│                        └────────┬─────────┘         │
│                                 │                    │
│                    ┌────────────┴────────────┐      │
│                    ▼                         ▼      │
│           ┌──────────────┐          ┌────────────┐ │
│           │ Tool 1:      │          │ Tool 2:    │ │
│           │ calculate    │          │ get_time   │ │
│           └──────┬───────┘          └──────┬─────┘ │
│                  │                        │        │
│                  └────────────┬───────────┘        │
│                               ▼                    │
│                  ┌──────────────────┐             │
│                  │ Response         │             │
│                  │ Generation       │             │
│                  └──────────────────┘             │
└──────────────────────────────────────────────────────┘
```

---

## Common Issues

**Q: Model evaluation takes too long**
- A: Reduce your evaluation dataset size for faster iteration

**Q: Accuracy scores seem low**
- A: The example uses simple substring matching. In production, use semantic similarity or LLM-based evaluation

**Q: How do I compare runs in MLflow UI?**
- A: Select multiple runs in the experiment view and click "Compare" to see side-by-side metrics

**Q: Can I evaluate models that aren't LangChain?**
- A: Yes! MLflow supports evaluating any Python function. See MLflow docs for custom evaluation logic
