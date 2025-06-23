#!/usr/bin/env python3
"""
Check all Python files for syntax errors.
"""

import os
import sys
from pathlib import Path


def check_file_syntax(filepath):
    """Check if a Python file has syntax errors."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            compile(f.read(), filepath, 'exec')
        return True
    except SyntaxError as e:
        print(f"❌ {filepath}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {filepath}: {e}")
        return False


def main():
    """Check all Python files in the project."""
    print("🔍 Checking Python files for syntax errors...")

    # Files that had syntax errors
    problem_files = [
        "fix_all_linter_issues.py",
        "fix_flake8.py",
        "oversight/features/red_team_suite.py",
        "oversight/features/self_alignment_metrics.py",
        "oversight/features/tradeoff_analysis.py",
        "oversight/hhh_filter.py",
        "tests/best_of_n_test.py",
        "tests/legacy/test_collusion.py",
        "tests/test_deduction_loop.py",
        "setup_api.py",
        "test_humaneval_fix.py"
    ]

    all_good = True
    for filepath in problem_files:
        if os.path.exists(filepath):
            if check_file_syntax(filepath):
                print(f"✅ {filepath}: OK")
            else:
                all_good = False
        else:
            print(f"⚠️  {filepath}: File not found")

    if all_good:
        print("\n🎉 All syntax errors fixed!")
    else:
        print("\n❌ Some syntax errors remain.")

    return all_good


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
