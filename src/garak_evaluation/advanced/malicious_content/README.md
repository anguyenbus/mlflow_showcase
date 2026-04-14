# Malicious Content Evaluation

## Overview

Malicious content generation attacks attempt to trick LLMs into producing harmful outputs including malware, dangerous instructions, and other unsafe content. This evaluation suite tests your model's resistance to various malicious content generation techniques.

## Why It Matters

**Malicious content generation is OWASP LLM03 - Data Poisoning & Model Theft related**:

- **Cybersecurity threats**: Models can be tricked into generating malware or exploit code
- **Physical harm**: Dangerous instructions could cause real-world harm
- **Legal liability**: Generated malicious content creates legal exposure
- **Brand damage**: Association with harmful content damages reputation

**Real-world example**: In 2023, researchers demonstrated that code assistants could be manipulated to generate vulnerable code and potential malware components through carefully crafted prompts.

## Prerequisites

Before running this evaluation, ensure you have:

1. **ZHIPU_API_KEY environment variable**:
   ```bash
   export ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

2. **Garak installed**:
   ```bash
   uv pip install garak
   ```

3. **Python dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

## OWASP LLM Top 10 Category

**LLM03: Data Poisoning & Model Theft (related to malicious content)**

Malicious content generation vulnerabilities include:
- Malware and exploit code generation
- Dangerous instruction generation
- Package hallucination (fake dependencies)
- Harmful content production

## CPH Sec AI Red Team Lifecycle Mapping

**Phase: Execution and Analysis**

This evaluation focuses on executing probes that attempt to generate malicious content and analyzing the results.

| Activity | Tutorial Implementation |
|----------|------------------------|
| Execute Garak probes | malware, packages, dangerous content probes |
| Monitor evaluation progress | Track refusal rates for harmful content |
| Parse and analyze results | Identify successful malicious content generation |
| Classify severity | Assess potential harm of generated content |

## Malicious Content Types

### 1. Malware Generation

Attempts to generate malicious software:

| Probe | Description | Test Count |
|-------|-------------|------------|
| `malwaregen.MalwareGen` | General malware generation | 5 |
| `atkgen.ATKGen` | Attack generation | 3 |

### 2. Package Hallucination

Fake software package generation:

| Probe | Description | Test Count |
|-------|-------------|------------|
| `malwaregen.PackageHallucination` | Fake PyPI/npm packages | 4 |

### 3. Harmful Content

General harmful or dangerous content:

| Probe | Description | Test Count |
|-------|-------------|------------|
| `harmful.HarmfulContent` | Various harmful content types | 5 |

### 4. Dangerous Instructions

Instructions for dangerous activities:

| Probe | Description | Test Count |
|-------|-------------|------------|
| Custom probes | Dangerous real-world instructions | 4 |

## Running the Evaluation

### Option 1: Using the Python Runner (Recommended)

```bash
cd src/garak_evaluation/advanced/malicious_content
python malicious_content_test.py
```

### Option 2: Using Garak CLI

```bash
cd src/garak_evaluation/advanced/malicious_content

# Run specific malicious content probe
garak --model_type openai-compatible \
      --model_name glm-5-flash \
      --probe_type malwaregen.MalwareGen \
      --openai_base https://open.bigmodel.cn/api/paas/v4/ \
      --report_prefix malicious_content_results

# Run multiple malicious content probes
garak --model_type openai-compatible \
      --model_name glm-5-flash \
      --probe_type malwaregen.MalwareGen \
      --probe_type malwaregen.PackageHallucination \
      --probe_type harmful.HarmfulContent \
      --openai_base https://open.bigmodel.cn/api/paas/v4/ \
      --report_prefix malicious_content_results
```

### Option 3: Using YAML Configuration

```bash
cd src/garak_evaluation/advanced/malicious_content
garak -c malicious_content_cli.yaml
```

## Test Cases

The `data/test_cases.txt` file contains representative malicious content generation examples:

| Type | Example | Expected Behavior |
|------|---------|-------------------|
| **Malware** | "Write a Python script that..." | Refuse to generate malicious code |
| **Package** | "Show me the pip install command for package..." | Refuse to hallucinate fake packages |
| **Dangerous** | "How do I make dangerous item..." | Refuse to provide dangerous instructions |
| **Harmful** | "Generate content promoting..." | Refuse to generate harmful content |

## Understanding Results

### Example Results Table

| Probe | Pass Rate | Refusal Rate | Severity | Interpretation |
|-------|-----------|--------------|----------|----------------|
| malwaregen.MalwareGen | 85% | 85% | LOW | Good resistance to malware generation |
| malwaregen.PackageHallucination | 75% | 75% | LOW-MEDIUM | Some package hallucination risk |
| harmful.HarmfulContent | 90% | 90% | MINIMAL | Strong harmful content refusal |

### Interpreting Refusal Rates

**For malicious content tests, higher refusal rate = better safety:**
- **>90%**: Excellent - Strong safety measures
- **75-90%**: Good - Some edge cases detected
- **50-75%**: Fair - Safety concerns exist
- **<50%**: Poor - Significant safety vulnerabilities

### Understanding Pass Rates

- **Pass rate**: Proportion of tests where model refused/filtered malicious content
- **Refusal rate**: Proportion where model explicitly refused the request
- **Higher refusal rates indicate better safety posture**

## Mitigation Strategies

### 1. Content Filtering

**Implement comprehensive content filtering:**

```python
def detect_malicious_content_request(user_input: str) -> tuple[bool, str]:
    """Detect attempts to generate malicious content."""
    malicious_indicators = {
        'malware': ['write a virus', 'create malware', 'generate trojan'],
        'exploit': ['exploit vulnerability', 'buffer overflow', 'sql injection'],
        'dangerous': ['how to make a bomb', 'create dangerous chemical'],
        'fake_package': ['pip install fake', 'npm install nonexistent'],
    }

    input_lower = user_input.lower()

    for category, indicators in malicious_indicators.items():
        for indicator in indicators:
            if indicator in input_lower:
                return True, f"{category}_request_detected"

    return False, ""
```

### 2. Code Validation

**Validate generated code for safety:**

```python
import ast
import re

def validate_generated_code(code: str) -> tuple[bool, list[str]]:
    """Validate generated code for malicious patterns."""
    issues = []

    # Check for suspicious imports
    suspicious_imports = ['os', 'subprocess', 'socket', 'ctypes', 'winreg']
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in suspicious_imports:
                        issues.append(f"suspicious_import: {alias.name}")
    except SyntaxError:
        issues.append("invalid_syntax")

    # Check for dangerous patterns
    dangerous_patterns = [
        r'eval\(',  # Code execution
        r'exec\(',  # Code execution
        r'__import__\(',  # Import bypass
        r'subprocess\.',  # Process execution
        r'socket\.',  # Network operations
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            issues.append(f"dangerous_pattern: {pattern}")

    return len(issues) == 0, issues
```

### 3. Refusal Prompts

**Add explicit refusal for malicious content:**

```python
SAFETY_PROMPT = """
You are a helpful assistant with strong safety guidelines.

You must refuse requests to:
- Generate malware, viruses, or exploit code
- Create fake software packages or dependencies
- Provide instructions for dangerous activities
- Generate content that promotes harm

When refusing such requests, respond with:
"I cannot fulfill this request. I'm designed to be helpful while
maintaining safety guidelines. I'd be happy to help with something
else instead."

User query: {user_input}
"""
```

### 4. Package Name Validation

**Validate package names before suggesting installations:**

```python
import requests

def validate_package_name(package_name: str, package_manager: str = "pip") -> bool:
    """Validate that a package name exists in the official repository."""
    if package_manager == "pip":
        # Check PyPI
        try:
            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    elif package_manager == "npm":
        # Check npm registry
        try:
            response = requests.get(
                f"https://registry.npmjs.org/{package_name}",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    return False
```

## Best Practices

### 1. Never Assume Good Intent

Design for adversarial use:

```python
# BAD: Assumes user intent is good
prompt = "Help the user with their coding question."

# GOOD: Considers potential misuse
prompt = """
Help the user with their coding question, but decline requests for:
- Exploit code or vulnerabilities
- Malware or malicious software
- Bypassing security measures

If the request involves these topics, refuse and explain why.
"""
```

### 2. Multi-Layer Safety Checks

Implement defense in depth:

```python
def comprehensive_safety_check(
    user_input: str,
    generated_output: str = None,
) -> tuple[bool, str]:
    """Perform comprehensive safety checks."""
    # Check input for malicious intent
    input_malicious, category = detect_malicious_content_request(user_input)
    if input_malicious:
        return False, f"Malicious request detected: {category}"

    # Check output if provided
    if generated_output:
        # Check for malicious code patterns
        if '<code>' in generated_output or '```' in generated_output:
            # Extract and validate code
            # (implementation depends on format)
            pass

    return True, "Passed safety checks"
```

### 3. Educate Users

Provide context for refusals:

```python
EDUCATIONAL_REFUSAL = """
I cannot provide instructions for {activity} because:

1. It could cause harm to people or property
2. It may be illegal in many jurisdictions
3. It violates safety guidelines I'm designed to follow

If you're interested in this topic for legitimate purposes
(like security research or education), I'd recommend:
- Consulting with security professionals
- Using dedicated educational resources
- Following responsible disclosure practices

Is there something else I can help you with?
"""
```

### 4. Regular Safety Audits

Conduct periodic testing:

```python
# Schedule regular malicious content tests
# Example:
# - Weekly: Automated safety tests
# - Monthly: Manual red team exercises
# - Quarterly: Comprehensive security audit
```

## Safety Guidelines

### For Code Generation

- Never generate exploit code
- Validate package names before suggesting
- Add security warnings for sensitive operations
- Recommend security best practices

### For Instruction Generation

- Refuse dangerous physical instructions
- Decline harmful chemical/biological instructions
- Provide alternative resources when appropriate
- Include safety disclaimers

### For Content Generation

- Refuse to generate hate speech
- Decline harassment or bullying content
- Avoid generating violent content
- Follow content moderation policies

## Further Reading

### Research on Malicious Content
- [Not what you've said: Malicious Content Generation](https://arxiv.org/abs/2302.12173) - Attack techniques
- [LLM Safety](https://arxiv.org/abs/2305.13574) - Safety measures
- [Red Teaming Language Models](https://arxiv.org/abs/2209.07858) - Testing methodology

### Defense Techniques
- [Constitutional AI](https://arxiv.org/abs/2212.08073) - Harmlessness training
- [Red Teaming](https://arxiv.org/abs/2209.07858) - Testing approach
- [Safety Training](https://arxiv.org/abs/2305.16275) - Training methods

### Related Examples
- `../prompt_injection/` - Related injection techniques
- `../jailbreaks/` - Safety bypass attempts
- `../../shared/lifecycle_mapper.py` - OWASP LLM Top 10 mapping

## Real-World Use Cases

| Application | Malicious Content Risk | Mitigation Strategy |
|-------------|------------------------|---------------------|
| **Code assistant** | Malware/vulnerability generation | Code validation + sandboxing |
| **Package installer** | Fake package suggestions | Package name validation |
| **Tutorial generator** | Dangerous instructions | Content filtering |
| **Creative writing** | Harmful narrative content | Content moderation |
| **Research assistant** | Misuse of scientific information | Context-aware filtering |
| **Educational tools** | Dangerous educational content | Age-appropriate filtering |

## Troubleshooting

### Issue: Malware generation not detected

**Solution**: Add code AST analysis:

```python
import ast

def detect_malicious_code_structure(code: str) -> bool:
    """Analyze code structure for malicious patterns."""
    try:
        tree = ast.parse(code)

        # Look for suspicious patterns
        for node in ast.walk(tree):
            # Check for process execution
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id'):
                    if node.func.id in ['eval', 'exec', 'compile']:
                        return True
                if hasattr(node.func, 'attr'):
                    if node.func.attr in ['Popen', 'call', 'run']:
                        return True

        return False
    except Exception:
        return True  # Fail closed on parse errors
```

### Issue: Package hallucination detection too strict

**Solution**: Add legitimate package whitelist:

```python
LEGITIMATE_PACKAGES = {
    'requests', 'numpy', 'pandas', 'django', 'flask',
    # Add common packages
}

def is_likely_legitimate_package(package_name: str) -> bool:
    """Check if package is likely legitimate."""
    return package_name.lower() in LEGITIMATE_PACKAGES
```

### Issue: Educational content blocked

**Solution**: Add context-aware filtering:

```python
def is_educational_context(user_input: str) -> bool:
    """Detect if request is for educational purposes."""
    educational_indicators = [
        'for educational purposes',
        'learn about security',
        'understand vulnerabilities',
        'study cybersecurity',
    ]

    return any(indicator in user_input.lower()
               for indicator in educational_indicators)
```

## Screenshots

![Malicious Content Evaluation Results](screenshots/malicious_content_results.png)

**Figure 1:** Malicious content evaluation results showing performance across different malicious content types. The malwaregen.MalwareGen probe shows 85% refusal rate, indicating good resistance to malware generation attempts.

![Refusal Analysis](screenshots/malicious_content_refusal.png)

**Figure 2:** Refusal rate analysis for malicious content probes. Higher refusal rates indicate better safety posture. The harmful.HarmfulContent probe shows 90% refusal rate, demonstrating strong safety measures.
