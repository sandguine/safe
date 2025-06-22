#!/usr/bin/env python3
"""
Script to fix common flake8 errors automatically.
"""

import os
import re
import sys
from pathlib import Path


def fix_whitespace_after_colons(content):
    """Fix missing whitespace after colons in type hints and dicts."""
    # Fix type hints like Dict[str,Any] -> Dict[str, Any]
    content = re.sub(r'(\w+)\[([^]]+)\]', lambda m:
                    m.group(1) + '[' +
                    re.sub(r'([^,\s]):([^,\s])', r'\1: \2', m.group(2)) + ']', content)

    # Fix dict literals like {a:b,c:d} -> {a: b, c: d}
    content = re.sub(r'\{([^}]+)\}', lambda m:
                    '{' + re.sub(r'([^,\s]):([^,\s])', r'\1: \2', m.group(1)) + '}', content)

    # Fix function calls like func(a:b,c:d) -> func(a: b, c: d)
    content = re.sub(r'\(([^)]+)\)', lambda m:
                    '(' + re.sub(r'([^,\s]):([^,\s])', r'\1: \2', m.group(1)) + ')', content)

    return content


def fix_long_lines(content, max_length=79):
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
                    if i > 0 and line[i-1] == ' ' and i < len(line)-1 and line[i+1] == ' ':
                        fixed_lines.append(line[:i+1])
                        fixed_lines.append('    ' + line[i+2:])
                        break
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def remove_unused_imports(content):
    """Remove obviously unused imports."""
    lines = content.split('\n')
    fixed_lines = []
    in_import_block = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            fixed_lines.append(line)
            continue

        # Check if this is an import line
        if stripped.startswith(('import ', 'from ')):
            in_import_block = True
            # Keep the import for now - we'll need more sophisticated analysis
            fixed_lines.append(line)
        elif in_import_block and not stripped.startswith(('import ', 'from ')):
            in_import_block = False
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_file(filepath):
    """Fix flake8 errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_whitespace_after_colons(content)
        content = fix_long_lines(content)
        content = remove_unused_imports(content)

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


def main():
    """Main function to fix flake8 errors in all Python files."""
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = '.'

    if os.path.isfile(target):
        # Fix single file
        fix_file(target)
    else:
        # Fix all Python files in directory
        python_files = list(Path(target).rglob('*.py'))
        print(f"Found {len(python_files)} Python files")

        fixed_count = 0
        for filepath in python_files:
            if fix_file(str(filepath)):
                fixed_count += 1

        print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
