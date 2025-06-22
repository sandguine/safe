"""
Minimal model interface for MVP demo.
"""

import os

try:
    import anthropic
except ImportError:
    print("Warning: anthropic not installed. Run: pip install anthropic")
    anthropic = None


def ask(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> str:
    """
    Ask Claude a question and return the response.

    Args:
        prompt: The input prompt
        model: Model name to use
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        The model's response as a string
    """
    if not anthropic:
        return f"# Mock response for: {prompt[:100]}..."

    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        return f"# Mock response (no API key): {prompt[:100]}..."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"# Error: {str(e)}"
