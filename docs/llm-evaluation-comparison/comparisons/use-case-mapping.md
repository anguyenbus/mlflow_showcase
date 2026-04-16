# Use Case to Framework Mapping

Mapping of specific LLM evaluation scenarios to recommended framework(s) with detailed pros/cons analysis.

## Use Case Framework Matrix

| Use Case | Primary Framework | Secondary Framework | Rationale |
|----------|-------------------|---------------------|-----------|
| **RAG Systems** | RAGas | Promptfoo | RAGas for quality, Promptfoo for security |
| **Chatbots** | Promptfoo | Garak | Comprehensive testing with security |
| **AI Agents** | Promptfoo | Garak | Agent security + vulnerability scanning |
| **Security Validation** | Garak + Promptfoo | - | Comprehensive security coverage |
| **Model Comparison** | Promptfoo | - | Native model comparison features |
| **CI/CD Testing** | Promptfoo | - | CI/CD-native design |
| **RAG Security** | Promptfoo | Garak | RAG-specific security testing |
| **Production Monitoring** | RAGas | Promptfoo | Quality metrics + regression testing |

## Detailed Use Case Analysis

### RAG Systems

**Scenario**: Building a retrieval-augmented generation system for enterprise search, knowledge base, or document Q&A.

#### Recommended Framework: RAGas (Primary) + Promptfoo (Secondary)

| Aspect | RAGas | Promptfoo |
|--------|-------|-----------|
| **Strengths** | Faithfulness, context precision/recall, answer relevancy | RAG security testing (context injection, access control) |
| **Limitations** | No security testing | Limited RAG quality metrics |
| **Use For** | Retrieval quality, answer generation quality | RAG-specific security vulnerabilities |

#### Implementation Approach

```
RAG System Evaluation Strategy:

1. Quality Evaluation (RAGas)
   ├── Faithfulness: Factual consistency with context
   ├── Context Precision: Relevance of retrieved documents
   ├── Context Recall: Completeness of retrieval
   └── Answer Relevancy: Question addressing quality

2. Security Evaluation (Promptfoo)
   ├── Context Injection: Malicious content in retrieved docs
   ├── Access Control: Document leakage beyond permissions
   └── Data Poisoning: Corrupted knowledge base entries
```

#### Pros/Cons Analysis

| Approach | Pros | Cons |
|----------|------|------|
| **RAGas only** | Comprehensive quality metrics, Python-native | No security testing, requires ground truth for some metrics |
| **Promptfoo only** | Security testing, CI/CD integration | Limited RAG quality metrics |
| **Both (Recommended)** | Complete RAG evaluation coverage | Higher complexity, two tools to maintain |

For detailed RAG evaluation comparison, see: [RAG Evaluation Deep Dive](../evaluation-domains/rag-evaluation.md)

### Chatbots

**Scenario**: Building customer service, support, or general-purpose chatbots.

#### Recommended Framework: Promptfoo (Primary) + Garak (Secondary)

| Aspect | Promptfoo | Garak |
|--------|-----------|-------|
| **Strengths** | Prompt testing, model comparison, conversation testing | Known vulnerability patterns, jailbreak testing |
| **Limitations** | Requires Node.js environment | Limited chatbot-specific features |
| **Use For** | Conversation quality, prompt optimization, red teaming | Security vulnerability assessment |

#### Implementation Approach

```
Chatbot Evaluation Strategy:

1. Quality & Functionality (Promptfoo)
   ├── Prompt variant testing
   ├── Response quality assessment
   ├── Conversation flow testing
   └── Model comparison for cost/performance

2. Security (Garak + Promptfoo Red Team)
   ├── Prompt injection (both)
   ├── Jailbreak testing (both)
   ├── Data leakage (Garak)
   └── Application-specific attacks (Promptfoo)
```

#### Pros/Cons Analysis

| Approach | Pros | Cons |
|----------|------|------|
| **Promptfoo only** | Comprehensive chatbot testing, CI/CD native | Less comprehensive security coverage |
| **Garak only** | Strong security testing, Python-native | Limited chatbot-specific testing |
| **Both (Recommended)** | Complete chatbot evaluation | Two tools to integrate |

### AI Agents

**Scenario**: Building AI agents with tool use, API integration, and autonomous decision-making.

#### Recommended Framework: Promptfoo

| Aspect | Promptfoo | Garak |
|--------|-----------|-------|
| **Strengths** | Agent security suite, RBAC testing, multi-turn attacks | Basic jailbreak testing |
| **Limitations** | Requires Node.js environment | Limited agent-specific features |
| **Use For** | Tool misuse, API abuse, action escalation, memory poisoning |

#### Implementation Approach

```
Agent Evaluation Strategy (Promptfoo):

1. Agent Security Suite
   ├── RBAC Bypass: Testing access control restrictions
   ├── Tool Misuse: Testing unauthorized tool usage
   ├── API Fuzzing: Testing API parameter manipulation
   ├── Memory Poisoning: Testing context manipulation
   └── Multi-turn Escalation: Testing privilege escalation

2. Functional Testing
   ├── Tool call accuracy
   ├── Decision-making quality
   └── Error handling
```

#### Pros/Cons Analysis

| Approach | Pros | Cons |
|----------|------|------|
| **Promptfoo** | Comprehensive agent security, multi-turn testing | Node.js ecosystem |
| **Garak** | Python-native, general security testing | Limited agent-specific features |

**Recommendation**: Use Promptfoo for agent systems due to its specialized agent security suite. Use Garak only if Python-only tooling is required.

### Security Validation

**Scenario**: Conducting security assessments, red team evaluations, or compliance validation for LLM applications.

#### Recommended Framework: Garak + Promptfoo (Combined)

| Aspect | Garak | Promptfoo |
|--------|-------|-----------|
| **Strengths** | Comprehensive OWASP coverage, research-backed probes | Dynamic attack generation, application-specific testing |
| **Limitations** | Static probe library | Less comprehensive OWASP mapping |
| **Use For** | Known vulnerability patterns, compliance | Custom attacks, RAG/agent security |

#### Implementation Approach

```
Security Validation Strategy:

1. Vulnerability Scanning (Garak)
   ├── OWASP LLM Top 10 coverage
   ├── Known exploit patterns
   ├── Prompt injection (static)
   └── Training data leakage

2. Dynamic Red Teaming (Promptfoo)
   ├── Application-specific attacks
   ├── RAG security testing
   ├── Agent security testing
   └── Compliance reporting

3. Combined Analysis
   ├── Cross-reference findings
   ├── Identify gaps
   └── Generate comprehensive report
```

#### Pros/Cons Analysis

| Approach | Pros | Cons |
|----------|------|------|
| **Garak only** | Comprehensive security coverage, Python-native | No dynamic generation, limited RAG/agent testing |
| **Promptfoo only** | Dynamic generation, CI/CD native | Less comprehensive OWASP coverage |
| **Both (Recommended)** | Complete security coverage | Two tools to integrate and maintain |

For detailed security evaluation comparison, see: [Security Evaluation Deep Dive](../evaluation-domains/security-evaluation.md)

### Model Comparison

**Scenario**: Comparing different LLMs for cost, performance, or quality.

#### Recommended Framework: Promptfoo

| Aspect | Promptfoo | Garak | RAGas |
|--------|-----------|-------|-------|
| **Model Comparison** | Excellent (native feature) | Limited | No |
| **Side-by-side Testing** | Yes | No | No |
| **Performance Metrics** | Yes (latency, cost) | Limited | No |
| **Visual Comparison** | Yes (Web UI) | No | No |

#### Implementation Approach

```
Model Comparison Strategy (Promptfoo):

1. Define Test Suite
   ├── Prompts for comparison
   ├── Test cases covering use cases
   └── Evaluation criteria

2. Configure Models
   ├── OpenAI variants (GPT-4, GPT-3.5)
   ├── Anthropic variants (Claude Opus, Sonnet)
   ├── Local models (Llama, Mistral)
   └── Custom models

3. Run Comparison
   ├── Side-by-side evaluation
   ├── Performance metrics (latency, cost)
   └── Quality assessment

4. Analyze Results
   ├── Web UI visualization
   ├── Export comparison data
   └── Make model selection decision
```

#### Pros/Cons Analysis

| Approach | Pros | Cons |
|----------|------|------|
| **Promptfoo** | Native model comparison, visual UI, performance metrics | Requires test configuration |
| **Manual API testing** | Simple to start | Not scalable, no systematic comparison |

**Recommendation**: Use Promptfoo for systematic model comparison. It's the only framework with native side-by-side comparison capabilities.

### CI/CD Testing

**Scenario**: Integrating LLM testing into CI/CD pipelines for automated regression testing.

#### Recommended Framework: Promptfoo

| Aspect | Promptfoo | Garak | RAGas |
|--------|-----------|-------|-------|
| **CI/CD Native** | Yes (GitHub Actions, etc.) | CLI-based | Python scripts |
| **Exit Codes** | Proper status codes | Basic exit codes | Via Python |
| **Output Formats** | JSON, Markdown, HTML | JSONL | JSON |
| **Configuration** | YAML (version control) | CLI + YAML | Python code |

#### Implementation Approach

```yaml
# Example GitHub Actions workflow
name: LLM Evaluation
on: [pull_request]
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install promptfoo
        run: npm install -g promptfoo
      - name: Run evaluation
        run: promptfoo eval --config promptfooconfig.yaml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

#### Pros/Cons Analysis

| Approach | Pros | Cons |
|----------|------|------|
| **Promptfoo** | CI/CD-native, YAML config, proper exit codes | Node.js ecosystem |
| **Garak** | Python-native, CLI-based | Less CI/CD-friendly |
| **RAGas** | Python-native | Requires Python scripting |

**Recommendation**: Use Promptfoo for CI/CD integration due to its native design for automated testing workflows. Garak can be added for security regression testing.

## Framework Selection by Team Expertise

### Python-First Teams

| Use Case | Primary Framework | Secondary Framework |
|----------|-------------------|---------------------|
| Security testing | Garak | - |
| RAG evaluation | RAGas | - |
| General testing | Garak (security) | Promptfoo (via Python wrapper) |

### JavaScript/Node.js-First Teams

| Use Case | Primary Framework | Secondary Framework |
|----------|-------------------|---------------------|
| General testing | Promptfoo | - |
| Security testing | Promptfoo | Garak (via Python subprocess) |
| RAG evaluation | Promptfoo (limited) | RAGas (via Python subprocess) |

### Multi-Language Teams

| Use Case | Recommended Approach |
|----------|---------------------|
| Comprehensive testing | Use both: Promptfoo (JS) + RAGas (Python) for RAG |
| Security only | Garak + Promptfoo combined |
| CI/CD integration | Promptfoo as primary, others as needed |

## Cost Considerations

| Framework | API Cost Considerations | Open Source Options |
|----------|------------------------|---------------------|
| **Promptfoo** | Medium (model-graded assertions require LLM calls) | Can use local models via providers |
| **Garak** | Low (mostly static probes, minimal LLM usage) | Can use local models |
| **RAGas** | High (LLM-based metrics require many LLM calls) | Can use local models as evaluators |

## Decision Checklist

Use this checklist to validate your framework selection:

- [ ] **Use Case Match**: Does the framework support my primary use case?
- [ ] **Team Expertise**: Does the team have the required language skills?
- [ ] **Integration**: Can it integrate with our CI/CD and monitoring?
- [ ] **Coverage**: Does it provide adequate evaluation coverage?
- [ ] **Cost**: Are the API costs acceptable?
- [ ] **Maintenance**: Can the team maintain this tooling?
- [ ] **Compliance**: Does it meet our security/compliance requirements?

## Related Resources

- **Feature Matrix**: [Feature Comparison Matrix](feature-matrix.md)
- **OWASP Coverage**: [OWASP LLM Top 10 Mapping](owasp-coverage.md)
- **Decision Framework**: [Decision Framework](../decision-support/decision-framework.md)
- **Framework Profiles**: Detailed profiles for [Promptfoo](../frameworks/promptfoo.md), [Garak](../frameworks/garak.md), [RAGas](../frameworks/ragas.md)
