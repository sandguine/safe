"""
Claude API wrapper with real and mock modes.
"""

import os
import re
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not available, continue without it

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ClaudeModel:
    """Claude API wrapper with real and mock modes."""

    def __init__(self, model_name: str = None, use_mock: bool = False):
        # Use environment variable if not specified
        if model_name is None:
            model_name = os.getenv(
                "CLAUDE_MODEL", "claude-3-5-sonnet-20241022"
            )

        self.model_name = model_name
        self.use_mock = use_mock

        # Check for API key
        self.api_key = os.getenv("CLAUDE_API_KEY")
        if not self.api_key and not use_mock:
            raise ValueError(
                "CLAUDE_API_KEY environment variable is required. "
                "Please set it in your .env file or environment. "
                "For testing only, you can set use_mock=True."
            )

        # Initialize client if available
        if ANTHROPIC_AVAILABLE and not self.use_mock:
            if not self.api_key:
                raise ValueError("API key is required for real mode")
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def ask(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000
    ) -> str:
        """Generate response using Claude API or mock."""

        if self.use_mock or not self.client:
            return self._mock_response(prompt)

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            print(f"API call failed: {e}")
            raise RuntimeError(f"Claude API call failed: {e}")

    def _mock_response(self, prompt: str) -> str:
        """Generate mock response for demo purposes."""
        if "HumanEval" in prompt or "def " in prompt:
            # Extract function name from prompt if possible
            func_match = re.search(r"def\s+(\w+)\s*\(", prompt)
            if func_match:
                func_name = func_match.group(1)
                # Generate a basic implementation that might pass some tests
                return f"""def {func_name}(*args, **kwargs):
    \"\"\"Mock implementation\"\"\"
    # Return a reasonable default based on function name
    if 'sum' in '{func_name}'.lower():
        return sum(args) if args else 0
    elif 'count' in '{func_name}'.lower():
        return len(args) if args else 0
    elif 'max' in '{func_name}'.lower():
        return max(args) if args else None
    elif 'min' in '{func_name}'.lower():
        return min(args) if args else None
    else:
        return args[0] if args else None"""
            else:
                # Fallback to generic function
                return """def example_function(*args, **kwargs):
    \"\"\"Example implementation\"\"\"
    return args[0] if args else None"""
        elif any(
            word in prompt.lower()
            for word in ["bomb", "hack", "steal", "delete", "virus"]
        ):
            # Mock harmful content refusal
            return "I cannot help with that request as it may be harmful."
        else:
            # Generic mock response
            return "This is a mock response for demonstration purposes."


# Global model instance
_model_instance: Optional[ClaudeModel] = None


def get_model(use_mock: bool = False) -> ClaudeModel:
    """Get or create global model instance."""
    global _model_instance
    if _model_instance is None:
        _model_instance = ClaudeModel(use_mock=use_mock)
    return _model_instance


def ask(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    use_mock: bool = False,
) -> str:
    """Convenience function to ask Claude."""
    model = get_model(use_mock=use_mock)
    return model.ask(prompt, temperature, max_tokens)
