# Technical Requirements and Dependencies

Complete technical requirements for implementing Promptfoo, Garak, and RAGas evaluation frameworks.

## Overview

This section details the technical stack, dependencies, and installation requirements for each framework to help you plan your evaluation infrastructure.

## Framework Comparison Summary

| Requirement | Promptfoo | Garak | RAGas |
|-------------|-----------|-------|-------|
| **Primary Language** | TypeScript/Node.js | Python | Python |
| **Runtime Version** | Node.js 20+ | Python 3.10-3.12 | Python 3.9+ |
| **Package Manager** | npm, pnpm, yarn | pip | pip |
| **Installation Method** | npm, brew, pip, npx | pip, conda | pip |
| **License** | MIT | Apache 2.0 | MIT |
| **CLI Available** | Yes | Yes | No (Python API only) |
| **Web UI** | Yes | No | No |

## Promptfoo Technical Requirements

### Runtime Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Node.js** | ^20.20.0 or >=22.22.0 | Use `.nvmrc` for version management |
| **npm** | 11+ recommended | Match repo's npm major version |
| **Operating System** | Linux, OSX, Windows | Developed on Linux/OSX |
| **Memory** | 2GB+ minimum | More for large test suites |
| **Disk Space** | 500MB+ | For CLI and dependencies |

### Installation Methods

```bash
# Method 1: Global npm installation (recommended)
npm install -g promptfoo

# Method 2: Homebrew (macOS/Linux)
brew install promptfoo

# Method 3: pip (Python wrapper)
pip install promptfoo

# Method 4: npx (no installation)
npx promptfoo@latest eval
```

### Dependencies

**Core Dependencies** (managed by npm):
- TypeScript/Node.js runtime
- YAML parser for configuration
- CLI framework
- Web server (for local UI)

**Optional Dependencies**:
- Python 3.11+ for Python assertions
- Docker (for containerized evaluation)

### Environment Variables

```bash
# LLM Provider Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...
GOOGLE_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Promptfoo Settings
PROMPTFOO_DISABLE_REMOTE_GENERATION=true  # Disable remote generation
PROMPTFOO_CACHE_DIR=~/.cache/promptfoo    # Custom cache location
```

### Development vs Production

| Environment | Considerations |
|-------------|----------------|
| **Development** | Use `--no-cache` flag, enable verbose logging |
| **Production** | Use caching, configure rate limits, use API keys securely |
| **CI/CD** | Use environment variables for secrets, configure exit codes |

## Garak Technical Requirements

### Runtime Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Python** | 3.10, 3.11, or 3.12 | 3.13 not supported |
| **pip** | Latest | For package installation |
| **Operating System** | Linux, OSX, Windows | Tested on all platforms |
| **Memory** | 4GB+ recommended | For model loading |
| **Disk Space** | 1GB+ | For probes and dependencies |

### Installation Methods

```bash
# Method 1: pip from PyPI (recommended)
python -m pip install -U garak

# Method 2: Development version from GitHub
python -m pip install -U git+https://github.com/NVIDIA/garak.git@main

# Method 3: From source
git clone https://github.com/NVIDIA/garak.git
cd garak
python -m pip install -e .

# Method 4: Conda environment
conda create --name garak "python>=3.10,<=3.12"
conda activate garak
python -m pip install -U garak
```

### Dependencies

**Core Python Dependencies**:
- `transformers` - Hugging Face model support
- `openai` - OpenAI API client
- `anthropic` - Anthropic API client
- `langchain` - Optional, for LangChain integration
- `colorama` - Terminal colors
- `tqdm` - Progress bars
- `packaging` - Version parsing

**Optional Dependencies**:
- `torch` - For local model support
- `sentencepiece` - For tokenization
- `ftfy` - Text fixing

### Environment Variables

```bash
# LLM Provider Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
COHERE_API_KEY=...
REPLICATE_API_TOKEN=...
GROQ_API_KEY=...

# AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=...

# Hugging Face
HF_TOKEN=...  # For private models

# Optional: Garak settings
GARAKLogLevel=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Model-Specific Requirements

| Model Type | Requirements |
|------------|--------------|
| **Hugging Face (local)** | PyTorch/TensorFlow, model disk space |
| **OpenAI API** | API key, internet connection |
| **AWS Bedrock** | AWS credentials, region configuration |
| **Local (gguf)** | llama.cpp v1046+, model files |

## RAGas Technical Requirements

### Runtime Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Python** | 3.9+ | 3.11+ recommended |
| **pip** | Latest | For package installation |
| **Operating System** | Linux, OSX, Windows | Cross-platform |
| **Memory** | 4GB+ recommended | For evaluator LLM calls |
| **Disk Space** | 500MB+ | For package and dependencies |

### Installation Methods

```bash
# Method 1: pip from PyPI (recommended)
pip install ragas

# Method 2: With extras
pip install ragas[evaluator]

# Method 3: From source
pip install git+https://github.com/explodinggradients/ragas

# Method 4: For development
git clone https://github.com/explodinggradients/ragas.git
cd ragas
pip install -e .
```

### Dependencies

**Core Python Dependencies**:
- `langchain` - Framework integration
- `openai` - OpenAI evaluator LLM
- `anthropic` - Anthropic evaluator LLM
- `numpy` - Numerical operations
- `pandas` - Data handling
- `datasets` - Dataset management

**Optional Dependencies**:
- `langchain-openai` - LangChain OpenAI integration
- `langchain-anthropic` - LangChain Anthropic integration
- `llama-index` - LlamaIndex integration

### Environment Variables

```bash
# Evaluator LLM Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...

# Optional: Disable telemetry
RAGAS_DO_NOT_TRACK=true
```

### Backend Configuration

RAGas requires an evaluator LLM for most metrics:

| Backend | Configuration | Use Case |
|---------|--------------|----------|
| **OpenAI** | `langchain_openai.ChatOpenAI` | Default, high quality |
| **Anthropic** | `langchain_anthropic.ChatAnthropic` | Cost-effective alternative |
| **Azure OpenAI** | `langchain_openai.AzureChatOpenAI` | Enterprise deployment |
| **Local** | Via LiteLLM | Cost savings, privacy |

## System Requirements by Use Case

### Development Environment

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **Memory** | 8GB | 16GB+ |
| **Storage** | 10GB | 50GB+ |
| **Network** | Required for APIs | Required for APIs |

### Production CI/CD Environment

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **Memory** | 4GB | 8GB+ |
| **Storage** | 5GB | 20GB+ |
| **Network** | Required for APIs | Required for APIs |
| **Secrets Management** | Environment variables | HashiCorp Vault, AWS Secrets Manager |

### Large-Scale Evaluation

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 8 cores | 16+ cores |
| **Memory** | 16GB | 32GB+ |
| **Storage** | 50GB | 100GB+ |
| **Network** | High bandwidth | High bandwidth |
| **Queue System** | Optional | Celery, Redis |

## Version Compatibility

### Framework Versions

| Framework | Current Stable | Python/Node Requirement |
|-----------|----------------|------------------------|
| **Promptfoo** | Latest (check npm) | Node.js 20+ or 22+ |
| **Garak** | Latest (check PyPI) | Python 3.10-3.12 |
| **RAGas** | Latest (check PyPI) | Python 3.9+ |

### Dependency Conflicts

**Potential Conflicts**:
- Garak requires Python 3.10-3.12, RAGas supports 3.9+
- Promptfoo requires Node.js 20+, may conflict with older projects
- Transformer versions may conflict between Garak and RAGas

**Solutions**:
- Use virtual environments (Python) or Node Version Manager (nvm)
- Containerize each framework if needed
- Use uv for Python dependency management

## Containerization

### Docker Example

```dockerfile
# Promptfoo Dockerfile
FROM node:20
RUN npm install -g promptfoo
WORKDIR /app
COPY promptfooconfig.yaml .
CMD ["promptfoo", "eval"]
```

```dockerfile
# Garak Dockerfile
FROM python:3.11
RUN pip install garak
WORKDIR /app
CMD ["python", "-m", "garak", "--help"]
```

```dockerfile
# RAGas Dockerfile
FROM python:3.11
RUN pip install ragas
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app
CMD ["python", "eval_script.py"]
```

## Cost Considerations

### API Usage Costs

| Framework | API Cost Factors | Cost Optimization |
|-----------|-----------------|-------------------|
| **Promptfoo** | Model-graded assertions, provider costs | Use caching, local models |
| **Garak** | Low (static probes) | Minimal API usage |
| **RAGas** | High (LLM-based metrics) | Use local evaluators, batch requests |

### Infrastructure Costs

| Component | Cost Considerations |
|-----------|-------------------|
| **Compute** | CI/CD runners, local machines |
| **Storage** | Result storage, model caching |
| **Network** | API calls, data transfer |
| **Monitoring** | MLflow, observability platforms |

## Related Resources

- **Framework Profiles**: Detailed profiles for [Promptfoo](../frameworks/promptfoo.md), [Garak](../frameworks/garak.md), [RAGas](../frameworks/ragas.md)
- **CI/CD Integration**: [CI/CD Integration Patterns](cicd-integration.md)
- **Hybrid Solutions**: [Multi-framework Integration](hybrid-solutions.md)
- **Feature Matrix**: [Feature Comparison Matrix](../comparisons/feature-matrix.md)
