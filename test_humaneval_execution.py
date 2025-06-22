#!/usr/bin/env python3
"""
Test HumanEval test execution to understand the output format.
"""

import os
import subprocess
import sys
import tempfile

# Add the oversight directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "oversight"))

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def test_humaneval_execution():
    """Test how HumanEval test execution works."""
    print("Testing HumanEval test execution...")

    # Create a simple test case
    test_code = '''
def has_close_elements(numbers, threshold):
    """Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True
    return False

# Test cases
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
'''

    # Write to temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(test_code)
        temp_file = f.name

    try:
        # Execute the test
        print(f"Executing test file: {temp_file}")
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10,
        )

        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    finally:
        # Clean up
        try:
            os.unlink(temp_file)
        except OSError:
            pass


if __name__ == "__main__":
    test_humaneval_execution()
