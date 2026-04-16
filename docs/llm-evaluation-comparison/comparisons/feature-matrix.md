# Feature Comparison Matrix

Side-by-side comparison of Promptfoo, Garak, and RAGas across all major evaluation dimensions.

## Complete Feature Comparison

| Feature | Promptfoo | Garak | RAGas |
|---------|-----------|-------|-------|
| **Primary Focus** | Prompt testing, red teaming | Security vulnerability scanning | RAG quality evaluation |
| **Language** | TypeScript/Node.js | Python | Python |
| **Configuration** | YAML/JSON | CLI + YAML | Python API |
| **License** | MIT | Apache 2.0 | MIT |
| **Installation** | npm, brew, pip, npx | pip | pip |
| **CLI Available** | Yes | Yes | No (Python API only) |
| **Web UI** | Yes | No | No |
| **CI/CD Native** | Yes | Yes | Via Python scripts |
| **Model Support** | Extensive | Extensive | Via backends |

## Testing Capabilities Comparison

| Capability | Promptfoo | Garak | RAGas |
|------------|-----------|-------|-------|
| **Prompt Testing** | Excellent | Limited | No |
| **Model Comparison** | Excellent | Yes | No |
| **A/B Testing** | Excellent | No | No |
| **Red Teaming** | Excellent | Excellent | No |
| **RAG Security** | Excellent | Limited | No |
| **RAG Quality** | Limited | No | Excellent |
| **Agent Security** | Excellent | Limited | No |

## Security Testing Comparison

| Security Feature | Promptfoo | Garak | RAGas |
|-----------------|-----------|-------|-------|
| **Prompt Injection** | Dynamic generation | Curated probes | No |
| **Jailbreaking** | Dynamic generation | Curated probes | No |
| **Data Leakage** | Yes | Yes | No |
| **OWASP Coverage** | Mapped to categories | Mapped to categories | No |
| **Compliance Reporting** | Yes | Via AVIDB | No |
| **Attack Strategy** | AI-powered generation | Static library | N/A |

For detailed OWASP LLM Top 10 coverage mapping, see: [OWASP Coverage](owasp-coverage.md)

## RAG Evaluation Comparison

| RAG Metric | Promptfoo | Garak | RAGas |
|------------|-----------|-------|-------|
| **Faithfulness** | No | No | Yes |
| **Context Precision** | No | No | Yes |
| **Context Recall** | No | No | Yes |
| **Answer Relevancy** | No | No | Yes |
| **RAG Security** | Yes (via red team) | Limited | No |
| **Retrieval Testing** | No | No | Yes |
| **Hallucination Detection** | Via assertions | No | Via faithfulness |

## Quality Metrics Comparison

| Quality Metric | Promptfoo | Garak | RAGas |
|----------------|-----------|-------|-------|
| **LLM-graded Evaluation** | Yes | No | Yes |
| **Exact Match** | Yes | No | No |
| **Similarity Matching** | Yes | No | Yes |
| **Regex Validation** | Yes | No | No |
| **JSON Schema** | Yes | No | No |
| **Custom Assertions** | Yes (JS, Python) | Via detectors | Via Python |

## Integration Capabilities

| Integration | Promptfoo | Garak | RAGas |
|-------------|-----------|-------|-------|
| **CI/CD** | Native (GitHub Actions, etc.) | CLI-based | Python scripts |
| **MLflow** | Via export | Via logging | Native integration |
| **LangChain** | Via providers | No | Yes |
| **LlamaIndex** | Via providers | No | Yes |
| **Observability** | Export + webhooks | Logging | Custom |

## Provider Support

| Provider Type | Promptfoo | Garak | RAGas |
|---------------|-----------|-------|-------|
| **OpenAI** | Yes | Yes | Yes |
| **Anthropic** | Yes | Yes | Yes |
| **Azure OpenAI** | Yes | Yes | Yes |
| **Google** | Yes | No | Via backend |
| **AWS Bedrock** | Yes | Yes | Via backend |
| **Hugging Face** | Yes | Yes | Via backend |
| **Local Models** | Yes (Ollama, vLLM) | Yes | Via backend |
| **Custom API** | Yes | REST generator | Yes |

## Technical Requirements

| Requirement | Promptfoo | Garak | RAGas |
|-------------|-----------|-------|-------|
| **Runtime** | Node.js 20+ | Python 3.10-3.12 | Python 3.9+ |
| **Package Manager** | npm, pnpm, yarn | pip | pip |
| **Learning Curve** | Medium | Low | Medium |
| **Setup Time** | Fast | Fast | Medium |
| **Config Complexity** | Medium | Low | Medium (code) |

## Extensibility

| Extension Point | Promptfoo | Garak | RAGas |
|-----------------|-----------|-------|-------|
| **Custom Tests** | Yes (YAML) | Custom probes | Custom metrics |
| **Custom Assertions** | Yes (JS, Python) | Custom detectors | Yes (Python) |
| **Custom Providers** | Yes | Yes | Yes (backends) |
| **Plugin System** | Yes | Yes | No |

## Reporting and Output

| Output Feature | Promptfoo | Garak | RAGas |
|----------------|-----------|-------|-------|
| **CLI Output** | Yes | Yes | No |
| **Web UI** | Yes | No | No |
| **JSON Export** | Yes | Yes | Yes |
| **Markdown Report** | Yes | No | No |
| **HTML Report** | Yes | No | No |
| **Compliance Reports** | Yes | Via AVIDB | No |
| **Screenshot Capture** | Yes | No | No |

## Cost and Performance

| Factor | Promptfoo | Garak | RAGas |
|--------|-----------|-------|-------|
| **API Cost** | Medium (model-graded) | Low (mostly static) | High (LLM-based metrics) |
| **Execution Speed** | Fast | Medium | Slow (LLM calls) |
| **Caching** | Yes | No | No |
| **Parallel Execution** | Yes | Limited | Limited |

## Community and Support

| Support Aspect | Promptfoo | Garak | RAGas |
|----------------|-----------|-------|-------|
| **GitHub Stars** | High | High | High |
| **Active Development** | Yes | Yes | Yes |
| **Documentation** | Excellent | Good | Good |
| **Community** | Discord | Discord | Discord |
| **Enterprise Support** | Yes | No | Available |

## Use Case Alignment

| Use Case | Promptfoo | Garak | RAGas |
|----------|-----------|-------|-------|
| **RAG Systems** | Security only | Limited | Excellent |
| **Chatbots** | Excellent | Good | Limited |
| **Agents** | Excellent | Limited | No |
| **Security Validation** | Excellent | Excellent | No |
| **General Quality Testing** | Excellent | No | Limited |
| **Model Comparison** | Excellent | Yes | No |
| **Production Monitoring** | Good | Limited | Good |

For detailed use case mapping, see: [Use Case Mapping](use-case-mapping.md)

## Summary Table

| Dimension | Promptfoo | Garak | RAGas |
|-----------|-----------|-------|-------|
| **Best For** | Application-specific testing, CI/CD | Security audits, OWASP compliance | RAG quality measurement |
| **Team Expertise** | JavaScript/TypeScript | Python | Python |
| **Integration Effort** | Low | Low | Medium |
| **Comprehensive Coverage** | Yes (with plugins) | Security only | RAG only |
| **Enterprise Ready** | Yes (with Enterprise edition) | Open-source only | Yes |

## Quick Decision Guide

| If you need... | Use... |
|----------------|--------|
| CI/CD-integrated testing | Promptfoo |
| OWASP LLM Top 10 coverage | Garak (+ Promptfoo) |
| RAG quality metrics | RAGas |
| RAG security testing | Promptfoo |
| Model comparison | Promptfoo |
| Agent security testing | Promptfoo |
| Python-only tooling | Garak or RAGas |
| Web-based results viewer | Promptfoo |
| Compliance reporting | Promptfoo |

## Related Comparisons

- **OWASP Coverage**: Detailed [OWASP LLM Top 10 mapping](owasp-coverage.md)
- **Use Case Mapping**: Specific [use case recommendations](use-case-mapping.md)
- **Framework Profiles**: Detailed profiles for [Promptfoo](../frameworks/promptfoo.md), [Garak](../frameworks/garak.md), [RAGas](../frameworks/ragas.md)
