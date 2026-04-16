# LLM Evaluation Framework Comparison Table

Side-by-side comparison of Promptfoo, RAGas, and Garak across key dimensions.

| Dimension | Promptfoo | RAGas | Garak |
|-----------|-----------|-------|-------|
| **Primary positioning** | General-purpose LLM testing framework for prompt engineering, model comparison, and red teaming | RAG-specific evaluation framework measuring retrieval and generation quality | Security vulnerability scanner for LLM red teaming and assessment |
| **Provider coverage** | OpenAI, Anthropic, Azure, Google, AWS Bedrock, Ollama, vLLM, LocalAI, LM Studio, custom REST APIs, Python scripts | OpenAI, Anthropic, Azure OpenAI, local models via LiteLLM/Hugging Face, custom OpenAI-compatible APIs | OpenAI, Hugging Face, AWS Bedrock (Anthropic, Meta, Amazon, AI21, Cohere, Mistral), Replicate, Cohere, Groq, NVIDIA NIM, REST APIs, local gguf models |
| **Governance & Security** | OWASP LLM Top 10, NIST AI RMF, MITRE ATLAS, EU AI Act compliance mapping; dynamic attack generation for RAG and agent security; red team plugins | No security testing capabilities; focuses on quality metrics (faithfulness, relevancy, precision/recall) | OWASP LLM Top 10 focused; probe-based vulnerability testing; detector system for analyzing attack success; JSONL logging for audits |
| **Observability** | Web UI for result visualization; JSON/CSV/HTML export; CLI output; MLflow integration; webhook notifications; custom reporters | MLflow integration; structured result objects; pandas DataFrame export; LLM-as-judge metrics with detailed scoring | JSONL reports; hit logs for vulnerabilities; garak.log for debugging; optional AI Vulnerability Database push; pass/fail rates with severity classification |
| **Routing** | N/A - testing framework, not a routing layer. Tests models side-by-side for comparison. | N/A - evaluation framework, not a routing layer. Evaluates existing RAG pipelines. | N/A - security scanner, not a routing layer. Connects directly to target models for testing. |
| **Admin/user experience** | CLI-first with YAML/JSON config; Web UI for comparing outputs; declarative tests; supports JavaScript/Python assertions; CI/CD native | Python-native API; programmatic evaluation; integrates with LangChain/LlamaIndex workflows; requires Python expertise | CLI-based with Python backend; YAML config support; probe selection via CLI; security-focused reporting |
| **Deployment** | Node.js ^20.20.0 || >=22.22.0 (npm install); optional Python wrapper (pip); runs in CI/CD pipelines; no server required | Python 3.9+ (pip install); integrates into existing Python RAG pipelines; MLflow tracking; no server required | Python 3.10-3.12 (pip install); CLI tool; CI/CD integration via exit codes; no server required |
| **Performance notes** | Parallel test execution; caching support; tracks latency, token usage, and cost per test; model-graded assertions add API overhead | LLM-based metrics require API calls (cost/latency); synthetic test generation adds overhead; supports timeout/retry configuration | Probe execution can be time-intensive for comprehensive scans; detector analysis adds latency; configurable timeouts and retries |
| **Best fit** | CI/CD automated testing; application-specific red teaming; model comparison/A-B testing; teams with JavaScript/TypeScript expertise; RAG/agent security validation | RAG system quality measurement; Python teams using LangChain/LlamaIndex; production RAG monitoring; retrieval and generation metric analysis | Security teams conducting vulnerability assessments; regulatory compliance (OWASP); red team operations; Python-first teams needing comprehensive security scanning |

## Usage Notes

- **None of these frameworks are routing layers** - they are testing/evaluation tools that connect to your existing LLM deployments
- **Hybrid approaches are common**: Promptfoo + RAGas for complete RAG testing (security + quality), or Promptfoo + Garak for comprehensive security coverage
- **Team expertise matters**: Promptfoo favors Node.js/JS skills, RAGas and Garak favor Python skills
- **CI/CD integration**: All three support automated pipelines, but Promptfoo is most CI/CD-native by design
