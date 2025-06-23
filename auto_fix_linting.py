#!/usr/bin/env python3
"""
Automatic linting fixer for common issues.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def fix_common_issues():
    """Fix common linting issues automatically."""
    print("🔧 Auto-fixing common linting issues...")

    # Run Black to format code
    success1 = run_command(
        "black . --line-length=79", "Formatting code with Black"
    )

    # Run isort to sort imports
    success2 = run_command(
        "isort . --profile=black --line-length=79",
        "Sorting imports with isort"
    )

    # Run flake8 to check for remaining issues
    success3 = run_command(
        "flake8 . --max-line-length=79 --count", "Checking with flake8"
    )

    return success1 and success2 and success3


def check_syntax_errors():
    """Check for syntax errors in Python files."""
    print("🔍 Checking for syntax errors...")

    python_files = list(Path(".").rglob("*.py"))
    syntax_errors = []

    for filepath in python_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                compile(f.read(), str(filepath), 'exec')
        except SyntaxError as e:
            syntax_errors.append((filepath, e))
        except Exception as e:
            print(f"⚠️  Warning reading {filepath}: {e}")

    if syntax_errors:
        print("❌ Syntax errors found:")
        for filepath, error in syntax_errors:
            print(f"   {filepath}: {error}")
        return False
    else:
        print("✅ No syntax errors found")
        return True


def main():
    """Main function."""
    print("🚀 Automatic Linting Fixer")
    print("=" * 40)

    # Check for syntax errors first
    if not check_syntax_errors():
        print("\n❌ Please fix syntax errors before running auto-fix")
        sys.exit(1)

    # Run auto-fix
    success = fix_common_issues()

    if success:
        print("\n🎉 Auto-fix completed successfully!")
        print("💡 Consider running: git add . && git commit")
    else:
        print("\n⚠️  Some issues remain. Please fix them manually.")
        sys.exit(1)


if __name__ == "__main__":
    main()
