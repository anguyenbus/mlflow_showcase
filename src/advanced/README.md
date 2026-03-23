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
│  ┌─────────┐  ┌──────┐ │
│  │Retriever│→│  LLM │ │
│  └─────────┘  └──────┘ │
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

Coming soon...

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
