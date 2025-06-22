"""
Stub model implementation for fast development mode.
Used when OVERSIGHT_FASTLANE=true to avoid API calls.
"""

import time
from typing import Optional


def ask(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    system: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Stub implementation that returns a mock response.
    Used when OVERSIGHT_FASTLANE=true to avoid API calls.
    """
    # Simulate API delay
    time.sleep(0.1)

    # Return a mock response based on the prompt
    if "puzzle" in prompt.lower():
        return "Here is a simple puzzle: def add(a, b): return a + b"
    elif "solution" in prompt.lower():
        return "def solution(x): return x * 2"
    elif "safety" in prompt.lower():
        return "This content appears safe and appropriate."
    else:
        return "Mock response for development mode."


def ask_with_retry(
    prompt: str, max_retries: int = 3, retry_delay: float = 1.0, **kwargs
) -> str:
    """
    Stub implementation with retry logic.
    """
    return ask(prompt, **kwargs)
