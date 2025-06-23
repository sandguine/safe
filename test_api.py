#!/usr/bin/env python3
"""
Simple test to verify Claude API is working and see generated solutions.
"""

import os
import sys

# Add the oversight directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "oversight"))

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from oversight.model import ask


def test_api():
    """Test the Claude API with a simple prompt."""
    print("Testing Claude API...")

    # Check if API key is loaded
    api_key = os.getenv("CLAUDE_API_KEY")
    if api_key:
        print(f"✓ API key found: {api_key[: 20]}...")
    else:
        print("✗ No API key found")
        return

    # Test with a simple HumanEval-style prompt
    prompt = """Complete the following Python function:

def has_close_elements(numbers, threshold):
    \"\"\"Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    \"\"\"
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True

    return False

Provide only the function implementation, no explanations:"""

    try:
        print("\nGenerating solution...")
        response = ask(prompt, temperature=0.7)
        print(f"\nGenerated solution: \n{response}")

        # Check if it looks like valid Python code
        if "def " in response and "return" in response:
            print("\n✓ Response looks like valid Python code")
        else:
            print("\n✗ Response doesn't look like valid Python code")

    except Exception as e:
        print(f"\n✗ Error calling API: {e}")


if __name__ == "__main__":
    test_api()
