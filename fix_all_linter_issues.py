#!/usr/bin/env python3
"""
Comprehensive Linter Fix Script
==============================

Automatically fixes common flake8 issues across the entire codebase.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


def fix_whitespace_after_colons(content: str) -> str:
    """Fix missing whitespace after colons in type hints and dicts."""
    # Fix type hints like Dict[str,Any] -> Dict[str, Any]
    content = re.sub(
        r'(\w+)\[([^]]+)\]',
        lambda m: m.group(1) + '[' +
        re.sub(r'([^,\s]):([^,\s])', r'\1: \2', m.group(2)) + ']',
        content
    )

    # Fix dict literals like {a: b,c: d} -> {a: b, c: d}
    content = re.sub(
        r'\{([^}]+)\}',
        lambda m: '{' + re.sub(r'([^,\s]): ([^,\s])', r'\1: \2', m.group(1)) +
    '}',
        content
    )

    # Fix function calls like func(a: b,c: d) -> func(a: b, c: d)
    content = re.sub(
        r'\(([^)]+)\)',
        lambda m: '(' + re.sub(r'([^,\s]):([^,\s])', r'\1: \2', m.group(1)) +
    ')',
        content
    )

    return content


def fix_long_lines(content: str, max_length: int = 79) -> str:
    """Break long lines at appropriate points."""
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        if len(line) <= max_length:
            fixed_lines.append(line)
            continue

        # Try to break at common points
        if 'import ' in line and len(line) > max_length:
            # Handle long imports
            parts = line.split('import ')
            if len(parts) == 2:
                import_part = parts[1]
                if len(import_part) > max_length - 10:
                    # Break long import lists
                    imports = import_part.split(', ')
                    if len(imports) > 1:
                        fixed_lines.append(parts[0] + 'import (')
                        for imp in imports:
                            fixed_lines.append('    ' + imp.strip() + ',')
                        fixed_lines.append(')')
                        continue

        # Try to break at operators
        if any(op in line for op in [' + ', ' - ', ' * ', ' / ', ' = ', ' == ', ' != ']):
            # Find the last operator before max_length
            for i in range(max_length, 0, -1):
                if line[i] in '+-*/=!':
                    if (i > 0 and line[i-1] == ' ' and
                            i < len(line)-1 and line[i+1] == ' '):
                        fixed_lines.append(line[: i+1])
                        fixed_lines.append('    ' + line[i+2: ])
                        break
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_string_formatting(content: str) -> str:
    """Fix f-string formatting issues."""
    # Fix f-strings with long expressions
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        if 'f"' in line and len(line) > 79:
            # Try to break f-strings at logical points
            if '{' in line and '}' in line:
                # Find the longest expression in braces
                brace_pattern = r'\{[^}]*\}'
                matches = re.findall(brace_pattern, line)

                if matches:
                    longest_match = max(matches, key=len)
                    if len(longest_match) > 30:  # If expression is long
                        # Break the line before the long expression
                        parts = line.split(longest_match)
                        if len(parts) == 2:
                            fixed_lines.append(parts[0] + '(')
                            fixed_lines.append('    ' + longest_match + parts[1])
                            fixed_lines.append(')')
                            continue

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_dictionary_formatting(content: str) -> str:
    """Fix long dictionary assignments."""
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        if len(line) > 79 and '": ' in line and line.strip().startswith('"'):
            # This looks like a dictionary key assignment
            if ':' in line and not line.strip().startswith('#'):
                # Try to break at the colon
                colon_pos = line.find(': ')
                if colon_pos > 0:
                    key_part = line[:colon_pos]
                    value_part = line[colon_pos + 2:]

                    if len(key_part) < 40:  # If key is reasonable length
                        fixed_lines.append(key_part + ': (')
                        fixed_lines.append('    ' + value_part)
                        fixed_lines.append(')')
                        continue

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_function_calls(content: str) -> str:
    """Fix long function calls by breaking them."""
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        if len(line) > 79 and '(' in line and ')' in line:
            # Try to break function calls
            if line.count('(') == 1 and line.count(')') == 1:
                # Simple function call
                open_paren = line.find('(')
                close_paren = line.rfind(')')

                if open_paren > 0 and close_paren > open_paren:
                    func_name = line[:open_paren].strip()
                    args = line[open_paren + 1: close_paren]

                    if len(func_name) < 30:  # If function name is reasonable
                        fixed_lines.append(func_name + '(')
                        # Split arguments by comma
                        arg_parts = [arg.strip() for arg in args.split(',')]
                        for j, arg in enumerate(arg_parts):
                            if j == len(arg_parts) - 1:
                                fixed_lines.append('    ' + arg + ')')
                            else:
                                fixed_lines.append('    ' + arg + ',')
                        continue

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_file(filepath: str) -> bool:
    """Fix linter errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply fixes in order
        content = fix_whitespace_after_colons(content)
        content = fix_long_lines(content)
        content = fix_string_formatting(content)
        content = fix_dictionary_formatting(content)
        content = fix_function_calls(content)

        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
            return True
        else:
            print(f"No changes needed: {filepath}")
            return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def find_python_files(directory: str = '.') -> List[str]:
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.venv']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files


def main():
    """Main function to fix all linter errors."""
    print("🔧 Comprehensive Linter Fix Script")
    print("=" * 40)

    # Find all Python files
    python_files = find_python_files()
    print(f"Found {len(python_files)} Python files")

    # Fix each file
    fixed_count = 0
    for filepath in python_files:
        if fix_file(filepath):
            fixed_count += 1

    print(f"\n✅ Fixed {fixed_count} files")
    print("\n🎉 Linter fix complete!")

    # Run flake8 to check remaining issues
    print("\n🔍 Checking remaining issues...")
    os.system("python -m flake8 . --max-line-length=79 --count")


if __name__ == "__main__":
    main()
