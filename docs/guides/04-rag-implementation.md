# RAG Implementation: Retrieval-Augmented Generation

This guide covers building production-ready RAG systems with MLflow tracing and evaluation. You'll learn document loading, vector stores, retrieval chains, and RAG evaluation.

## Prerequisites

- Completed [02-tracing-deep-dive.md](02-tracing-deep-dive.md)
- Completed [03-evaluation-framework.md](03-evaluation-framework.md)
- MLflow UI running at http://localhost:5000
- Zhipu AI API key configured

## What is RAG?

**RAG (Retrieval-Augmented Generation)** combines:

1. **Retrieval**: Find relevant documents from a knowledge base
2. **Generation**: Use retrieved context to generate accurate responses

**Benefits:**

- Reduces hallucinations by grounding responses in facts
- Updates knowledge without retraining models
- Provides source attribution for answers
- Handles domain-specific knowledge effectively

## Exercise 1: Document Loading and Chunking

Load documents and split them into searchable chunks.

1. **Run the document loading example:**

```bash
uv run python src/advanced/rag/documents.py
```

2. **Expected output:**

```
Loading tax law documents...
Document loaded: 1250 characters
Chunking with recursive strategy...
Created 3 chunks:
- Chunk 0: 500 characters
- Chunk 1: 500 characters
- Chunk 2: 250 characters
```

### Understanding Chunking Strategies

**Fixed-Size Chunking:**

```python
# Splits text into equal-sized chunks with overlap
chunks = loader.chunk_text(
    text,
    strategy="fixed_size",
    chunk_size=1000,
    chunk_overlap=200
)
```

**When to use:**

- Simple documents with uniform content
- Predictable chunk sizes needed
- Fast processing required

**Recursive Chunking:**

```python
# Splits on paragraph boundaries, then sentences, then words
chunks = loader.chunk_text(
    text,
    strategy="recursive",
    chunk_size=1000,
    chunk_overlap=200
)
```

**When to use:**

- Documents with clear structure (paragraphs, sections)
- Better context preservation needed
- More natural splits desired

**Chunk Size Guidelines:**

- **Small chunks (200-500)**: Better for precise retrieval
- **Medium chunks (500-1000)**: Balance precision and context
- **Large chunks (1000-2000)**: More context, less precise

**Overlap Guidelines:**

- **No overlap (0)**: May miss context at boundaries
- **Small overlap (10-20%)**: Minimal redundancy
- **Large overlap (20-50%)**: Better context, more storage

## Exercise 2: Vector Store with ChromaDB

Create a vector database for semantic search.

1. **Run the vector store example:**

```bash
uv run python src/advanced/rag/vector_store.py
```

2. **Expected output:**

```
Creating vector store...
Adding documents to vector store...
Embedded 3 documents
Searching for similar documents...
Found 2 relevant documents:
- Doc 1 (score: 0.15)
- Doc 2 (score: 0.28)
```

### Understanding Vector Stores

**How they work:**

1. **Embedding**: Convert text to numerical vectors
2. **Storage**: Store vectors with metadata
3. **Search**: Find similar vectors by cosine similarity

**ChromaDB features:**

- In-memory or persistent storage
- Metadata filtering
- Similarity search with scores
- Easy integration with LangChain

**Configuration:**

```python
from src.advanced.rag.vector_store import VectorStore

# Create persistent vector store
store = VectorStore(
    collection_name="tax_law_docs",
    persist_directory="./data/chroma_db"
)

# Add documents
store.add_documents(chunked_documents)

# Search
results = store.search("tax question", k=3)
```

## Exercise 3: Building a Retrieval Chain

Combine retrieval with LLM generation using LangChain.

1. **Run the retrieval chain example:**

```bash
uv run python src/advanced/rag/retrieval_chain.py
```

2. **Expected output:**

```
Creating retrieval chain...
Querying: What is the tax rate for income between $45,001 and $120,000?
Retrieved 2 relevant documents
Generating answer...
Answer: According to Australian tax law, the tax rate for income between
$45,001 and $120,000 is 32.5% for Australian residents.
```

### Understanding Retrieval Chains

**Chain components:**

```python
from src.advanced.rag.retrieval_chain import RetrievalChain

# Create chain
chain = RetrievalChain(
    retriever=retriever,
    llm=llm
)

# Invoke
answer = chain.invoke("Your question here")
```

**LCEL Syntax (LangChain Expression Language):**

```python
# The chain uses LCEL for composition
chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

**What happens:**

1. User provides question
2. Retriever finds relevant documents
3. Documents formatted into context
4. Context + question passed to LLM
5. LLM generates answer using context

## Exercise 4: RAG with Tracing

Add comprehensive observability to your RAG system.

1. **Run the RAG tracing example:**

```bash
uv run python src/advanced/rag/rag_tracing.py
```

2. **Expected output:**

```
RAG System Tracing Demo
==================================================
Loading documents...
Chunking documents...
Created 3 chunks
Creating vector store...
Initializing LLM...
Building RAG chain...

Running sample queries...

Query 1:
Q: What is the tax rate for income between $45,001 and $120,000?
A: According to the tax documents, the rate is 32.5%.

Query 2:
Q: What can be claimed as allowable deductions?
A: Allowable deductions include work-related expenses...
```

3. **View the trace in MLflow UI:**

- Navigate to the "advanced_rag_tracing" experiment
- Click on the trace to see detailed spans
- You should see:
  - Document loading span
  - Chunking span
  - Vector store creation span
  - Embedding generation span
  - Retrieval span
  - LLM generation span

### Trace Analysis

**Key spans to examine:**

- **Document loading**: Check file size and load time
- **Chunking**: Verify chunk count and sizes
- **Embeddings**: Monitor embedding generation time
- **Retrieval**: Check retrieval quality and scores
- **Generation**: Review LLM response time

**Performance optimization:**

```python
# Check span timings in traces
# - Slow embeddings? Consider caching
# - Slow retrieval? Reduce chunk count or k
# - Slow generation? Use faster model
```

## Exercise 5: RAG Evaluation

Evaluate retrieval quality and answer relevance.

1. **Run the RAG evaluation example:**

```bash
uv run python src/advanced/rag/evaluate_rag.py
```

2. **Expected output:**

```
RAG System Evaluation
==================================================
Setting up RAG system...
Loading evaluation dataset...
Evaluating retrieval quality...
Average documents retrieved: 3.00
Evaluating answer relevance...
Average relevance score: 0.75

Comparing chunking strategies...
Testing: small_chunks (size=200, overlap=25)
  Chunks: 6
  Answer: According to tax law...

Testing: medium_chunks (size=500, overlap=50)
  Chunks: 3
  Answer: The tax rate is 32.5%...

Testing: large_chunks (size=1000, overlap=100)
  Chunks: 2
  Answer: For income between $45,001 and $120,000...
```

3. **View evaluation results:**

- Check metrics in MLflow UI
- Compare chunking strategies
- Review evaluation dataset

### Evaluation Metrics

**Retrieval Quality:**

```python
# Average documents retrieved
avg_retrieved = 3.0

# Retrieval relevance scores
relevance_scores = [0.85, 0.72, 0.90, 0.68, 0.88]
avg_relevance = sum(relevance_scores) / len(relevance_scores)
```

**Answer Relevance:**

```python
# Keyword overlap metric
def calculate_relevance(generated, ground_truth):
    keywords = set(ground_truth.lower().split())
    answer_words = set(generated.lower().split())
    overlap = len(keywords & answer_words)
    return overlap / len(keywords) if keywords else 0
```

**Chunking Strategy Comparison:**

| Strategy | Chunks | Pros | Cons |
|----------|--------|------|------|
| Small (200) | Many | Precise retrieval | May miss context |
| Medium (500) | Balanced | Good balance | Some boundary issues |
| Large (1000) | Few | More context | Less precise |

## Production Considerations

### Scaling RAG Systems

**Document management:**

```python
# Incremental updates
def add_documents(new_docs):
    """Add new documents without rebuilding."""
    vector_store.add_documents(new_docs)

# Document versioning
def update_document(doc_id, new_content):
    """Update existing document."""
    delete_by_metadata(doc_id)
    add_documents([new_content])
```

**Performance optimization:**

```python
# Use persistent storage
store = VectorStore(
    collection_name="docs",
    persist_directory="./chroma_db"  # Persistent
)

# Configure retrieval
retriever = store.as_retriever(
    search_kwargs={"k": 3}  # Top-k documents
)

# Cache embeddings
@lru_cache(maxsize=1000)
def get_embedding(text):
    return embeddings.embed_query(text)
```

### Monitoring RAG Systems

**Key metrics to track:**

- **Retrieval latency**: Time to find documents
- **Generation latency**: Time to generate answer
- **Retrieval quality**: Average relevance scores
- **Answer quality**: User feedback or automated metrics
- **Resource usage**: Memory, CPU, storage

**MLflow dashboards:**

```python
# Log RAG-specific metrics
mlflow.log_metric("retrieval_latency_ms", retrieval_time)
mlflow.log_metric("generation_latency_ms", generation_time)
mlflow.log_metric("avg_relevance_score", avg_relevance)
mlflow.log_metric("documents_retrieved", len(docs))
```

## Best Practices

### Document Preparation

- **Clean text**: Remove formatting, special characters
- **Structure**: Use clear headings and sections
- **Metadata**: Add source, date, category tags
- **Quality**: Ensure accurate, up-to-date content

### Chunking Strategy

- **Start with medium chunks** (500-1000 chars)
- **Add overlap** (10-20%) for context
- **Test different strategies** on your data
- **Monitor retrieval quality** metrics

### Retrieval Configuration

- **Start with k=3-5** documents
- **Increase k** for complex queries
- **Decrease k** for precise answers
- **Use metadata filters** when applicable

### Prompt Engineering

```python
# Good RAG prompt
template = """Answer the question based only on the following context:

Context:
{context}

Question: {question}

If the context doesn't contain the answer, say "I don't have enough information
to answer this question."

Answer:"""
```

## Verification Checklist

Before completing this guide, verify:

- [ ] Documents load and chunk correctly
- [ ] Vector store stores and retrieves documents
- [ ] Retrieval chain generates answers using context
- [ ] Tracing captures all RAG components
- [ ] Evaluation metrics measure retrieval and answer quality
- [ ] Chunking strategies compare successfully

## Troubleshooting

**Issue: Poor retrieval quality**

- Solution: Try different chunk sizes or overlap amounts

**Issue: Answers ignore context**

- Solution: Improve prompt template to emphasize context usage

**Issue: Slow retrieval**

- Solution: Reduce k (number of documents) or chunk count

**Issue: Low relevance scores**

- Solution: Improve document quality or use better embeddings

**Issue: Tracing not working**

- Solution: Ensure MLflow autologging is enabled

## Next Steps

- Review all guides in the @docs/guides/ directory
- Check architecture decisions in @docs/adr/
- Read security practices in @docs/security/

## Additional Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- RAG examples: @src/advanced/rag/
