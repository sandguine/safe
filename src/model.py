"""
Claude API wrapper for oversight curriculum.
"""

import os
import time
from pathlib import Path

# Try to load from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root (oversight_curriculum directory)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # dotenv not installed, continue without it
    pass

import anthropic


def get_api_key() -> str:
    """Get Claude API key from .env file or environment variable"""
    # First try to get from .env file
    api_key = os.getenv("CLAUDE_API_KEY")
    
    if not api_key:
        # Try alternative environment variable names
        api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Claude API key not found. Please set CLAUDE_API_KEY in your .env file:\n"
            "CLAUDE_API_KEY=your-api-key-here"
        )
    
    return api_key


def ask(prompt: str, 
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 512,
        temperature: float = 0.7) -> str:
    """
    Ask Claude a question and get the response.
    
    Args:
        prompt: The prompt to send to Claude
        model: The model to use
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Claude's response as a string
    """
    
    try:
        # Get API key
        api_key = get_api_key()
        
        # Initialize client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Create message
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract response
        response = message.content[0].text
        return response
        
    except anthropic.RateLimitError:
        # Handle rate limiting
        print("Rate limit hit, waiting 60 seconds...")
        time.sleep(60)
        return ask(prompt, model, max_tokens, temperature)  # Retry
        
    except anthropic.APIError as e:
        print(f"API error: {e}")
        raise
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
