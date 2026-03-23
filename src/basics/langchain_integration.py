"""LangChain integration with Zhipu AI via OpenAI-compatible interface.

This module provides LangChain integration for Zhipu AI GLM-5 models
using the OpenAI-compatible API endpoint.
"""

import os
from typing import Final

from beartype import beartype
from langchain_openai import ChatOpenAI
from rich.console import Console

from config import get_config

# Initialize rich console
console: Final[Console] = Console()

# Zhipu AI OpenAI-compatible endpoint
ZHIPU_BASE_URL: Final[str] = "https://open.bigmodel.cn/api/paas/v4/"
DEFAULT_MODEL: Final[str] = "glm-5"


@beartype
def create_zhipu_langchain_llm(
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> ChatOpenAI:
    """Create a LangChain ChatOpenAI instance configured for Zhipu AI.

    Args:
        model: Model identifier (default: glm-5-flash)
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Configured ChatOpenAI instance for Zhipu AI
    """
    config = get_config()

    # NOTE: Zhipu AI provides OpenAI-compatible API
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        openai_api_key=config.zhipu_api_key,
        openai_api_base=ZHIPU_BASE_URL,
    )

    console.print(
        f"[green]✓[/green] Created LangChain LLM for Zhipu AI model: {model}"
    )

    return llm


@beartype
def create_streaming_llm(
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
) -> ChatOpenAI:
    """Create a streaming-enabled LangChain LLM for Zhipu AI.

    Args:
        model: Model identifier (default: glm-5-flash)
        temperature: Sampling temperature (0.0 to 1.0)

    Returns:
        Configured ChatOpenAI instance with streaming enabled
    """
    config = get_config()

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        streaming=True,
        openai_api_key=config.zhipu_api_key,
        openai_api_base=ZHIPU_BASE_URL,
    )

    console.print(
        f"[green]✓[/green] Created streaming LangChain LLM for Zhipu AI model: {model}"
    )

    return llm
