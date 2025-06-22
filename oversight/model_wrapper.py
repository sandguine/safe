"""
Model wrapper with stub functionality for local testing.
Eliminates test skips by providing stub implementations when API keys are not available.
"""

import os
import time
from typing import Optional

import anthropic


class ClaudeModelStub:
    """Stub model class for local testing without API keys."""

    def __init__(self, *args, **kwargs):
        pass

    def complete(self, *args, **kwargs):
        raise RuntimeError(
            "External API disabled in local mode - set CLAUDE_API_KEY for real execution"
        )

    def messages(self, *args, **kwargs):
        raise RuntimeError(
            "External API disabled in local mode - set CLAUDE_API_KEY for real execution"
        )


def ask(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    system: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Make a simple API call to Claude.

    Args:
        prompt: The user prompt
        model: Model name to use
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        system: Optional system message
        **kwargs: Additional arguments passed to the API

    Returns:
        The model's response as a string
    """
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "CLAUDE_API_KEY environment variable not set - use stub for local testing"
        )

    client = anthropic.Anthropic(api_key=api_key)

    messages = []
    if system:
        messages.append({"role": "user", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            **kwargs,
        )
        return response.content[0].text
    except Exception as e:
        raise RuntimeError(f"API call failed: {e}")


def ask_with_retry(
    prompt: str, max_retries: int = 3, retry_delay: float = 1.0, **kwargs
) -> str:
    """
    Make an API call with automatic retry on failure.

    Args:
        prompt: The user prompt
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        **kwargs: Arguments passed to ask()

    Returns:
        The model's response as a string
    """
    for attempt in range(max_retries):
        try:
            return ask(prompt, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(retry_delay)
            continue


# Export the appropriate model class based on environment
if not os.getenv("CLAUDE_API_KEY"):
    Model = ClaudeModelStub
else:
    # In CI or with real API key, use the real model
    class Model:
        def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
            self.model_name = model_name
            self.client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

        def complete(self, prompt: str, **kwargs):
            response = self.client.messages.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.content[0].text
