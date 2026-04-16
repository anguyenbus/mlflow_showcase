# Quick Reference Guide

Scannable tables and rapid comparison materials for framework selection.

## Framework Selection by Use Case

| Use Case | Primary Framework | Secondary Framework | One-Line Summary |
|----------|-------------------|---------------------|------------------|
| **RAG Systems** | RAGas | Promptfoo | RAGas for quality, Promptfoo for security |
| **RAG Security** | Promptfoo | Garak | RAG-specific security testing |
| **Chatbots** | Promptfoo | Garak | Comprehensive testing with CI/CD |
| **AI Agents** | Promptfoo | - | Agent security suite |
| **Security Audit** | Garak | Promptfoo | Known vulnerabilities + dynamic attacks |
| **Model Comparison** | Promptfoo | - | Native side-by-side comparison |
| **CI/CD Testing** | Promptfoo | Garak | CI/CD-native design |
| **Production Monitoring** | RAGas | Promptfoo | Quality tracking + regression |

## Framework Selection by Team Expertise

| Team Expertise | Recommended Framework | Considerations |
|----------------|----------------------|----------------|
| **Python-only** | Garak, RAGas | Both Python-native |
| **JavaScript/TypeScript** | Promptfoo | Native Node.js ecosystem |
| **Multi-language** | Promptfoo + RAGas | Best of both ecosystems |
| **ML/Data Science** | RAGas | Aligns with Python ML stack |
| **Security** | Garak + Promptfoo | Comprehensive security |
| **DevOps/SRE** | Promptfoo | CI/CD native |

## Feature Scoring Matrix

| Feature | Promptfoo | Garak | RAGas |
|---------|-----------|-------|-------|
| **Ease of Setup** | 8/10 | 9/10 | 7/10 |
| **CI/CD Integration** | 10/10 | 7/10 | 6/10 |
| **Security Testing** | 9/10 | 10/10 | 0/10 |
| **RAG Quality** | 4/10 | 0/10 | 10/10 |
| **Model Comparison** | 10/10 | 6/10 | 0/10 |
| **Documentation** | 9/10 | 7/10 | 7/10 |
| **Community** | 9/10 | 8/10 | 8/10 |
| **Extensibility** | 9/10 | 8/10 | 7/10 |

## Technical Requirements Summary

| Requirement | Promptfoo | Garak | RAGas |
|-------------|-----------|-------|-------|
| **Language** | TypeScript/Node.js | Python | Python |
| **Runtime** | Node.js 20+ | Python 3.10-3.12 | Python 3.9+ |
| **Package Manager** | npm/pnpm/yarn | pip | pip |
| **Installation** | `npm install -g promptfoo` | `pip install garak` | `pip install ragas` |
| **CLI** | Yes | Yes | No (Python API) |
| **Web UI** | Yes | No | No |
| **Config Format** | YAML | YAML + CLI | Python code |

## Security Coverage Summary

| OWASP Category | Promptfoo | Garak | Combined |
|----------------|-----------|-------|----------|
| **LLM01: Prompt Injection** | Excellent | Excellent | Comprehensive |
| **LLM02: Insecure Output** | Good | Good | Good |
| **LLM03: Data Poisoning** | Limited | Limited | Limited |
| **LLM04: DoS** | Limited | Limited | Limited |
| **LLM05: Supply Chain** | Good | Good | Good |
| **LLM06: Data Disclosure** | Excellent | Excellent | Comprehensive |
| **LLM07: Plugin Security** | Good | Limited | Good |
| **LLM08: Excessive Agency** | Excellent | Moderate | Excellent |
| **LLM09: Overreliance** | Good | Good | Good |
| **LLM10: Model Theft** | Limited | Limited | Limited |

## RAG Evaluation Coverage

| Metric | Promptfoo | Garak | RAGas |
|--------|-----------|-------|-------|
| **Faithfulness** | Via assertions | No | Yes (native) |
| **Context Precision** | No | No | Yes |
| **Context Recall** | No | No | Yes |
| **Answer Relevancy** | Via assertions | No | Yes |
| **Retrieval Quality** | No | No | Yes |
| **RAG Security** | Yes | Limited | No |

## Cost Comparison

| Framework | API Cost Factors | Cost Optimization |
|-----------|-----------------|-------------------|
| **Promptfoo** | Medium (model-graded assertions) | Use caching, local models |
| **Garak** | Low (static probes) | Minimal API usage |
| **RAGas** | High (LLM-based metrics) | Use local evaluators |

## Integration Capabilities

| Integration | Promptfoo | Garak | RAGas |
|-------------|-----------|-------|-------|
| **GitHub Actions** | Native | Via CLI | Custom |
| **MLflow** | Via export | Via logging | Native |
| **LangChain** | Via providers | No | Yes |
| **LlamaIndex** | Via providers | No | Yes |
| **Docker** | Yes | Yes | Yes |
| **Observability** | Export + webhooks | Logging | Custom |

## Decision Checklist

Use this checklist to validate your framework selection:

### Use Case Validation
- [ ] Framework supports my primary use case
- [ ] Framework covers my evaluation requirements
- [ ] Framework integrates with my tech stack

### Team Validation
- [ ] Team has required language expertise
- [ ] Team can maintain the framework
- [ ] Team has capacity for learning curve

### Integration Validation
- [ ] Framework integrates with CI/CD
- [ ] Framework integrates with monitoring
- [ ] Framework supports required providers

### Cost Validation
- [ ] API costs are acceptable
- [ ] Infrastructure costs are acceptable
- [ ] Maintenance costs are acceptable

### Coverage Validation
- [ ] Framework provides adequate coverage
- [ ] Gaps are identified and addressed
- [ ] Complementary tools considered if needed

## One-Line Framework Summaries

| Framework | One-Line Summary |
|-----------|------------------|
| **Promptfoo** | CLI-based LLM testing framework with native CI/CD integration and dynamic red teaming |
| **Garak** | Python-based security vulnerability scanner with comprehensive OWASP LLM Top 10 coverage |
| **RAGas** | Python-based RAG evaluation framework with purpose-built quality metrics |

## Quick Decision Table

| If you need... | Use... | Why... |
|----------------|--------|--------|
| RAG quality metrics | RAGas | Purpose-built for RAG |
| RAG security testing | Promptfoo | RAG-specific security suite |
| OWASP compliance | Garak + Promptfoo | Comprehensive coverage |
| Model comparison | Promptfoo | Native comparison features |
| Agent security | Promptfoo | Agent security suite |
| Python-only tooling | Garak or RAGas | Python-native |
| CI/CD integration | Promptfoo | CI/CD-native design |
| Lowest API costs | Garak | Static probes |
| Web-based results | Promptfoo | Built-in web UI |
| Compliance reporting | Promptfoo | Native compliance mapping |

## Common Combinations

| Combination | Best For | Coverage |
|------------|----------|----------|
| **RAGas + Promptfoo** | RAG systems | Quality + security |
| **Garak + Promptfoo** | Security | Known + dynamic attacks |
| **All Three** | Production systems | Complete coverage |

## Framework Limitations

| Framework | Key Limitations | Workaround |
|-----------|-----------------|------------|
| **Promptfoo** | Node.js ecosystem | Use Python wrappers |
| **Garak** | No quality metrics | Pair with RAGas |
| **RAGas** | No security testing | Pair with Promptfoo |

## Verification Checklist

Before committing to a framework:

- [ ] Reviewed framework profile documentation
- [ ] Tested framework with sample data
- [ ] Validated integration requirements
- [ ] Confirmed team expertise alignment
- [ ] Estimated costs and validated budget
- [ ] Reviewed existing project tutorials
- [ ] Checked community support availability
- [ ] Validated license requirements

## Related Resources

- **Decision Framework**: [Decision Flowchart](decision-framework.md)
- **Use Case Mapping**: [Detailed Use Case Analysis](../comparisons/use-case-mapping.md)
- **Feature Matrix**: [Complete Feature Comparison](../comparisons/feature-matrix.md)
- **Framework Profiles**: [Promptfoo](../frameworks/promptfoo.md) | [Garak](../frameworks/garak.md) | [RAGas](../frameworks/ragas.md)
