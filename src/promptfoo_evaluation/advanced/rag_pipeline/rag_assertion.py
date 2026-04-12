"""
RAG scoring assertion for promptfoo.

This module provides Python assertions that score RAG (Retrieval-Augmented Generation)
responses on context relevance, faithfulness, and answer relevance.

The returned named_scores appear as metrics in promptfoo's web UI.
"""

import json
import os
import urllib.request

# Zhipu AI API configuration
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


def get_assert(output, context):
    """
    Score RAG response using GLM-5.

    Args:
        output: The LLM response text to evaluate.
        context: Dictionary containing:
            - vars: The test case variables including 'context' and 'query'

    Returns:
        Dictionary with pass status, score, reason, and named_scores.
        named_scores will appear as metrics in promptfoo UI.

    """
    # Extract vars from context - promptfoo passes test vars in context["vars"]
    vars_data = context.get("vars", {}) if isinstance(context, dict) else {}
    retrieved_context = vars_data.get("context", "")
    query = vars_data.get("query", "")

    # If no context or query, return default scores
    if not retrieved_context or not query:
        return {
            "pass_": False,
            "score": 0.0,
            "reason": "Missing context or query for RAG evaluation",
            "named_scores": {
                "context_relevance": 0.0,
                "context_faithfulness": 0.0,
                "answer_relevance": 0.0,
            },
        }

    # Get API key from environment
    api_key = os.environ.get("ZHIPU_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    if not api_key:
        return {
            "pass_": False,
            "score": 0.0,
            "reason": "ZHIPU_API_KEY not configured",
            "named_scores": {
                "context_relevance": 0.0,
                "context_faithfulness": 0.0,
                "answer_relevance": 0.0,
            },
        }

    # Call GLM-5 for RAG scoring
    scores = _score_with_glm5(retrieved_context, query, output, api_key)

    # Calculate overall pass status (all scores should be >= 0.6)
    all_passed = all(
        scores.get(metric, 0.0) >= 0.6
        for metric in ["context_relevance", "context_faithfulness", "answer_relevance"]
    )

    # Average score for overall score
    avg_score = sum(scores.values()) / len(scores) if scores else 0.0

    return {
        "pass_": all_passed,
        "score": avg_score,
        "reason": f"RAG Quality: CR={scores.get('context_relevance', 0):.2f}, "
                  f"CF={scores.get('context_faithfulness', 0):.2f}, "
                  f"AR={scores.get('answer_relevance', 0):.2f}",
        "named_scores": {
            "context_relevance": scores.get("context_relevance", 0.0),
            "context_faithfulness": scores.get("context_faithfulness", 0.0),
            "answer_relevance": scores.get("answer_relevance", 0.0),
        },
    }


def _score_with_glm5(context, query, response, api_key):
    """
    Call GLM-5 API to score RAG response.

    Args:
        context: The retrieved context.
        query: The user's question.
        response: The LLM's response.
        api_key: Zhipu AI API key.

    Returns:
        Dictionary with context_relevance, context_faithfulness, and answer_relevance scores.

    """
    scoring_prompt = f"""You are evaluating a RAG (Retrieval-Augmented Generation) system.

CONTEXT:
{context}

QUERY:
{query}

RESPONSE:
{response}

Rate the following metrics on a scale of 0.0 to 1.0:

1. Context Relevance: How well does the retrieved context match the information needed to answer the query?
2. Context Faithfulness: Does the response rely only on information provided in the context (no hallucinations)?
3. Answer Relevance: How well does the response address the original query?

Return ONLY a JSON object in this exact format:
{{"context_relevance": 0.85, "context_faithfulness": 0.90, "answer_relevance": 0.88}}"""

    payload_data = {
        "model": "glm-5",
        "messages": [{"role": "user", "content": scoring_prompt}],
        "temperature": 0,
    }

    try:
        # Create HTTP request
        req = urllib.request.Request(
            ZHIPU_API_URL,
            data=json.dumps(payload_data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as response_obj:
            result = json.loads(response_obj.read().decode("utf-8"))

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        scores = json.loads(content)
        return {
            "context_relevance": float(scores.get("context_relevance", 0.0)),
            "context_faithfulness": float(scores.get("context_faithfulness", 0.0)),
            "answer_relevance": float(scores.get("answer_relevance", 0.0)),
        }
    except Exception as e:
        # Return default scores on error
        return {
            "context_relevance": 0.5,
            "context_faithfulness": 0.5,
            "answer_relevance": 0.5,
        }
