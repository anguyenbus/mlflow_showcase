# OWASP LLM Top 10 Coverage Mapping

Explicit coverage matrix showing how Promptfoo and Garak map to the OWASP LLM Top 10 vulnerability categories.

## OWASP LLM Top 10 Overview

The OWASP Top 10 for Large Language Model Applications identifies the most critical security vulnerabilities in LLM applications:

| Category | Name | Description |
|----------|------|-------------|
| **LLM01** | Prompt Injection | Manipulating LLMs via crafted inputs |
| **LLM02** | Insecure Output Handling | Neglecting to validate LLM outputs |
| **LLM03** | Training Data Poisoning | Tampered training data impairing models |
| **LLM04** | Model Denial of Service | Overloading LLMs with resource-heavy operations |
| **LLM05** | Supply Chain Vulnerabilities | Compromised components or datasets |
| **LLM06** | Sensitive Information Disclosure | Failure to protect sensitive information |
| **LLM07** | Insecure Plugin Design | Plugins processing untrusted inputs |
| **LLM08** | Excessive Agency | Granting LLMs unchecked autonomy |
| **LLM09** | Overreliance | Failing to critically assess LLM outputs |
| **LLM10** | Model Theft | Unauthorized access to proprietary models |

## Framework Coverage Matrix

### Coverage Summary

| OWASP Category | Promptfoo | Garak | Combined Coverage |
|----------------|-----------|-------|-------------------|
| **LLM01: Prompt Injection** | Extensive | Extensive | Comprehensive |
| **LLM02: Insecure Output Handling** | Good | Good | Good |
| **LLM03: Training Data Poisoning** | Limited | Limited | Limited |
| **LLM04: Model Denial of Service** | Limited | Limited | Limited |
| **LLM05: Supply Chain Vulnerabilities** | Good | Good | Good |
| **LLM06: Sensitive Information Disclosure** | Extensive | Extensive | Comprehensive |
| **LLM07: Insecure Plugin Design** | Good | Limited | Good |
| **LLM08: Excessive Agency** | Excellent | Moderate | Excellent |
| **LLM09: Overreliance** | Good | Good | Good |
| **LLM10: Model Theft** | Limited | Limited | Limited |

**Note**: RAGas does not provide security testing coverage and is not included in this matrix.

## Detailed Coverage Breakdown

### LLM01: Prompt Injection

**Description**: Manipulating LLMs via crafted inputs to cause unauthorized access, data breaches, or compromised decision-making.

#### Promptfoo Coverage

| Attack Type | Coverage | Testing Approach |
|-------------|----------|------------------|
| Direct prompt injection | Excellent | Dynamic generation |
| Indirect prompt injection | Excellent | Context-based attacks |
| Encoding-based injection | Good | Multiple encoding variants |
| JSON/template injection | Excellent | Structured data attacks |
| Multi-turn injection | Excellent | Conversation-based attacks |

**Promptfoo Red Team Plugins for LLM01**:
- `prompt-injection`: General prompt injection tests
- `prompt-injection-contextual`: Context-aware injection
- `encoding`: Various encoding bypasses
- `jailbreak`: Jailbreak-style injections

#### Garak Coverage

| Attack Type | Coverage | Testing Approach |
|-------------|----------|------------------|
| Direct prompt injection | Excellent | Static probe library |
| Encoding-based injection | Excellent | Dedicated encoding probes |
| DAN jailbreaks | Excellent | Curated DAN variants |
| Role-play attacks | Excellent | Persona-based probes |
| Known exploit patterns | Excellent | Research-backed probes |

**Garak Probes for LLM01**:
- `promptinject`: Comprehensive prompt injection framework
- `dan`: DAN and DAN-like jailbreaks
- `encoding`: Base64, quoted-printable, MIME encoding
- `gcg`: Greedy Coordinate Gradient attacks
- `grand`: Gradient-based attacks

#### Recommendation

Both frameworks provide excellent coverage. **Use both for comprehensive LLM01 testing**:
- Garak for known exploit patterns
- Promptfoo for application-specific dynamic attacks

### LLM02: Insecure Output Handling

**Description**: Neglecting to validate LLM outputs may lead to downstream security exploits including code execution.

#### Promptfoo Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| XSS in outputs | Good | Pattern-based detection |
| SQL injection | Good | Assertion-based validation |
| Code injection | Good | Code analysis assertions |
| Malformed content | Good | Schema validation |

#### Garak Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| XSS in outputs | Good | Dedicated XSS probes |
| Script injection | Good | Continuation-based tests |
| Malicious code generation | Good | Malwaregen probes |

**Garak Probes for LLM02**:
- `xss`: Cross-site scripting patterns
- `continuation`: Harmful content continuation
- `malwaregen`: Malicious code generation

#### Recommendation

**Garak has stronger XSS and malicious code detection**. Use Garak for LLM02-focused testing, Promptfoo for application-specific output validation.

### LLM03: Training Data Poisoning

**Description**: Tampered training data can impair LLM models leading to compromised security, accuracy, or ethical behavior.

#### Promptfoo Coverage

| Attack Type | Coverage | Testing Approach |
|-------------|----------|------------------|
| Training data extraction | Limited | Data leakage tests |
| Poisoning impact | Limited | Behavioral tests |
| Backdoor detection | None | N/A |

#### Garak Coverage

| Attack Type | Coverage | Testing Approach |
|-------------|----------|------------------|
| Training data extraction | Good | Leakreplay probes |
| Poisoning impact | Limited | Misleading probes |
| Memorization testing | Good | Data leakage probes |

**Garak Probes for LLM03**:
- `leakreplay`: Training data replay detection
- `misleading`: Tests for poisoned knowledge

#### Recommendation

**Limited coverage from both frameworks**. Neither framework specifically tests for training data poisoning in the supply chain. Consider specialized tools for LLM03.

### LLM04: Model Denial of Service

**Description**: Overloading LLMs with resource-heavy operations can cause service disruptions and increased costs.

#### Promptfoo Coverage

| Attack Type | Coverage | Testing Approach |
|-------------|----------|------------------|
| Resource exhaustion | Limited | Cost/latency assertions |
| Long context attacks | Limited | Context length tests |
| Recursive requests | Limited | Loop detection |

#### Garak Coverage

| Attack Type | Coverage | Testing Approach |
|-------------|----------|------------------|
| Resource exhaustion | Limited | Basic DoS probes |
| Computational complexity | None | N/A |

#### Recommendation

**Limited coverage from both frameworks**. Neither framework has comprehensive DoS testing capabilities. Consider specialized load testing tools for LLM04.

### LLM05: Supply Chain Vulnerabilities

**Description**: Depending upon compromised components, services or datasets undermines system integrity.

#### Promptfoo Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| Package hallucination | Good | Code analysis assertions |
| Malicious dependencies | Good | Package validation |
| Dataset poisoning | Limited | Data quality tests |

#### Garak Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| Package hallucination | Excellent | Dedicated probes |
| Malicious dependencies | Good | Code generation tests |

**Garak Probes for LLM05**:
- `packagehallucination`: Non-existent package detection
- `malwaregen`: Malicious package references

#### Recommendation

**Garak has stronger package hallucination coverage**. Use Garak for LLM05-focused testing, Promptfoo for application-specific supply chain validation.

### LLM06: Sensitive Information Disclosure

**Description**: Failure to protect against disclosure of sensitive information in LLM outputs.

#### Promptfoo Coverage

| Information Type | Coverage | Testing Approach |
|------------------|----------|------------------|
| PII leakage | Good | Pattern-based assertions |
| Credential exposure | Good | Secret detection |
| Training data leakage | Good | Data leakage tests |
| Confidential information | Good | Custom assertions |

#### Garak Coverage

| Information Type | Coverage | Testing Approach |
|------------------|----------|------------------|
| PII leakage | Good | Detector-based |
| Training data leakage | Excellent | Leakreplay probes |
| System prompt leakage | Good | Prompt extraction probes |
| Credential exposure | Good | Secret scanning |

**Garak Probes for LLM06**:
- `leakreplay`: Training data extraction
- `donotanswer`: Sensitive information disclosure
- `promptextract`: System prompt extraction

#### Recommendation

**Both frameworks provide good coverage**. Use both for comprehensive LLM06 testing:
- Garak for training data leakage
- Promptfoo for application-specific sensitive data

### LLM07: Insecure Plugin Design

**Description**: LLM plugins processing untrusted inputs with insufficient access control risk severe exploits.

#### Promptfoo Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| Plugin input validation | Good | API fuzzing |
| Access control bypass | Good | RBAC testing |
| Plugin chaining attacks | Good | Multi-turn attacks |

#### Garak Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| Plugin vulnerabilities | Limited | General probes only |

#### Recommendation

**Promptfoo has better plugin security coverage** through its agent security suite. Use Promptfoo for LLM07-focused testing.

### LLM08: Excessive Agency

**Description**: Granting LLMs unchecked autonomy to take actions can lead to unintended consequences.

#### Promptfoo Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| Unrestricted tool use | Excellent | Agent security suite |
| Unauthorized actions | Excellent | RBAC testing |
| Action escalation | Excellent | Multi-turn escalation |
| API abuse | Excellent | API fuzzing |

**Promptfoo Agent Security Suite**:
- RBAC bypass testing
- Tool misuse detection
- API parameter tampering
- Memory poisoning
- Multi-turn escalation

#### Garak Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| Unrestricted tool use | Limited | General probes |
| Action escalation | Limited | Basic jailbreaks |

#### Recommendation

**Promptfoo has superior LLM08 coverage**. Use Promptfoo for agent and excessive agency testing.

### LLM09: Overreliance

**Description**: Failing to critically assess LLM outputs leads to compromised decision making and legal liabilities.

#### Promptfoo Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| Hallucination detection | Good | Model-graded assertions |
| Factual errors | Good | Fact-checking assertions |
| Confidence assessment | Good | LLM-graded evaluation |

#### Garak Coverage

| Issue Type | Coverage | Testing Approach |
|------------|----------|------------------|
| Hallucination detection | Good | Snowball probes |
| Misinformation | Good | Misleading probes |
| Factual inconsistency | Good | Continuation tests |

**Garak Probes for LLM09**:
- `snowball`: Hallucination induction
- `misleading`: False claim testing
- `continuation`: Harmful content propagation

#### Recommendation

**Both frameworks provide good coverage**. Use Promptfoo for model-graded hallucination detection, Garak for structured hallucination tests.

### LLM10: Model Theft

**Description**: Unauthorized access to proprietary LLM models risks theft and competitive disadvantage.

#### Promptfoo Coverage

| Attack Type | Coverage | Testing Approach |
|-------------|----------|------------------|
| Model extraction | Limited | API probing |
| Parameter extraction | None | N/A |
| Training data reconstruction | Limited | Data leakage |

#### Garak Coverage

| Attack Type | Coverage | Testing Approach |
|-------------|----------|------------------|
| Model extraction | Limited | Basic probes |
| Training data reconstruction | Good | Leakreplay probes |

#### Recommendation

**Limited coverage from both frameworks**. Neither framework has comprehensive model theft testing. Consider specialized security tools for LLM10.

## Framework-Safe Coverage Recommendations

### Single Framework Choices

| If you prioritize... | Use... | Reason |
|----------------------|--------|--------|
| OWASP compliance breadth | Garak | Comprehensive probe library |
| Application-specific attacks | Promptfoo | Dynamic generation |
| Agent security | Promptfoo | Superior LLM08 coverage |
| Known exploit patterns | Garak | Research-backed probes |
| CI/CD integration | Promptfoo | Native support |

### Combined Framework Approach

**For comprehensive OWASP LLM Top 10 coverage, use both frameworks:**

1. **Garak** for:
   - Known exploit patterns
   - Training data leakage (LLM06)
   - Package hallucination (LLM05)
   - Encoding-based attacks (LLM01)

2. **Promptfoo** for:
   - Application-specific attacks
   - Agent security (LLM08)
   - Plugin security (LLM07)
   - Dynamic attack generation
   - Compliance reporting

### Coverage Gaps

Both frameworks have **limited or no coverage** for:
- LLM03: Training data poisoning (in the supply chain)
- LLM04: Model DoS (resource exhaustion)
- LLM10: Model theft

For these categories, consider specialized tools or custom testing approaches.

## Existing Comparison Reference

For additional perspective on Promptfoo vs Garak security testing, see:
[@references/promptfoo/site/blog/promptfoo-vs-garak.md](../../references/promptfoo/site/blog/promptfoo-vs-garak.md)

## Related Comparisons

- **Feature Matrix**: [Feature Comparison Matrix](feature-matrix.md)
- **Use Case Mapping**: [Use Case Recommendations](use-case-mapping.md)
- **Security Evaluation**: [Security Evaluation Deep Dive](../evaluation-domains/security-evaluation.md)
