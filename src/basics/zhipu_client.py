"""Zhipu AI GLM-5 model integration.

This module provides a client for interacting with Zhipu AI's GLM-5 models
via the zhipuai SDK with retry logic and error handling.
"""

import time
from typing import Final

from beartype import beartype
from rich.console import Console
from zhipuai import ZhipuAI as ZhipuaiSDK

from config import get_config

# Initialize rich console
console: Final[Console] = Console()

# Default configuration
DEFAULT_MODEL: Final[str] = "glm-5"
MAX_RETRIES: Final[int] = 3
RETRY_DELAY: Final[float] = 1.0


class ZhipuAIError(Exception):
    """Exception raised for Zhipu AI API errors."""

    pass


@beartype
class ZhipuAIClient:
    """Client for Zhipu AI GLM-5 model API.

    This client provides methods for text completion with automatic
    retry logic and error handling.

    Attributes:
        api_key: Zhipu AI API key
        model: Model identifier (default: glm-5-flash)
    """

    __slots__ = ("api_key", "model", "_client")

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        """Initialize Zhipu AI client.

        Args:
            model: Model identifier (default: glm-5-flash)
        """
        config = get_config()
        self.api_key = config.zhipu_api_key
        self.model = model

        # Initialize zhipuai SDK client
        self._client = ZhipuaiSDK(api_key=self.api_key)

        console.print(
            f"[green]✓[/green] Initialized Zhipu AI client with model: {model}"
        )

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text completion for the given prompt.

        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response

        Raises:
            ZhipuAIError: If API call fails after retries
        """
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                # NOTE: Use exponential backoff for retries
                if attempt > 0:
                    delay = RETRY_DELAY * (2**attempt)
                    console.print(
                        f"[yellow]Retrying attempt {attempt + 1}/{MAX_RETRIES} "
                        f"after {delay:.1f}s delay[/yellow]"
                    )
                    time.sleep(delay)

                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Extract response text
                content = response.choices[0].message.content
                return content

            except Exception as e:
                last_error = e
                console.print(
                    f"[red]✗[/red] API call failed (attempt {attempt + 1}): {e}"
                )

        # All retries exhausted
        raise ZhipuAIError(
            f"Zhipu AI API call failed after {MAX_RETRIES} attempts"
        ) from last_error


def create_zhipu_client(model: str = DEFAULT_MODEL) -> ZhipuAIClient:
    """Factory function to create a Zhipu AI client.

    Args:
        model: Model identifier (default: glm-5-flash)

    Returns:
        Configured ZhipuAIClient instance
    """
    return ZhipuAIClient(model=model)
