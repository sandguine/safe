"""
Model API wrapper for oversight curriculum.
Provides a simple interface for making API calls to language models.
"""

import os
import time
from typing import Optional
import anthropic


def ask(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    system: Optional[str] = None,
    **kwargs
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
        raise ValueError("CLAUDE_API_KEY environment variable not set")
    
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
            **kwargs
        )
        return response.content[0].text
    except Exception as e:
        raise RuntimeError(f"API call failed: {e}")


def ask_with_retry(
    prompt: str,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    **kwargs
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