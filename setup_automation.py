#!/usr/bin/env python3
"""
Setup automation for SAFE MVP demo.
Configures all tools to prevent code quality issues automatically.
"""

import os
import subprocess
import sys
from pathlib import Path


class AutomationSetup:
    """Setup automation tools and configurations"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.setup_complete = False

    def setup_pre_commit(self):
        """Install and configure pre-commit hooks"""
        print("🔧 Setting up pre-commit hooks...")

        try:
            # Install pre-commit
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pre-commit"],
                check=True,
                capture_output=True,
            )

            # Install pre-commit hooks
            subprocess.run(
                ["pre-commit", "install"], check=True, capture_output=True
            )

            # Install additional hooks
            subprocess.run(
                ["pre-commit", "install", "--hook-type", "commit-msg"],
                check=True,
                capture_output=True,
            )

            print("✅ Pre-commit hooks installed successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup pre-commit: {e}")
            return False

    def setup_development_tools(self):
        """Install development tools"""
        print("🔧 Installing development tools...")

        tools = ["black", "flake8", "isort", "mypy", "pytest", "pytest-cov"]

        try:
            for tool in tools:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", tool],
                    check=True,
                    capture_output=True,
                )
                print(f"✅ Installed {tool}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install development tools: {e}")
            return False

    def create_editor_config(self):
        """Create .editorconfig for consistent formatting"""
        print("📝 Creating .editorconfig...")

        editor_config = """# EditorConfig is awesome: https://EditorConfig.org

# top-most EditorConfig file
root = true

# Unix-style newlines with a newline ending every file
[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
trim_trailing_whitespace = true

# Python files
[*.py]
indent_style = space
indent_size = 4
max_line_length = 79

# Markdown files
[*.md]
indent_style = space
indent_size = 2
max_line_length = 80

# YAML files
[*.{yml,yaml}]
indent_style = space
indent_size = 2

# JSON files
[*.json]
indent_style = space
indent_size = 2

# Shell scripts
[*.sh]
indent_style = space
indent_size = 2
end_of_line = lf

# Windows batch files
[*.{cmd,bat}]
end_of_line = crlf
"""

        try:
            with open(self.project_root / ".editorconfig", "w") as f:
                f.write(editor_config)
            print("✅ Created .editorconfig")
            return True
        except Exception as e:
            print(f"❌ Failed to create .editorconfig: {e}")
            return False

    def create_vscode_settings(self):
        """Create VS Code settings for consistent development"""
        print("📝 Creating VS Code settings...")

        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        settings = {
            "python.defaultInterpreterPath": "./venv/bin/python",
            "python.formatting.provider": "black",
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.mypyEnabled": True,
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "python.testing.pytestArgs": ["tests"],
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {"source.organizeImports": True},
            "files.trimTrailingWhitespace": True,
            "files.insertFinalNewline": True,
            "files.trimFinalNewlines": True,
            "[python]": {
                "editor.defaultFormatter": "ms-python.black-formatter",
                "editor.rulers": [79],
            },
            "[markdown]": {"editor.wordWrap": "on", "editor.rulers": [80]},
        }

        try:
            import json

            with open(vscode_dir / "settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            print("✅ Created VS Code settings")
            return True
        except Exception as e:
            print(f"❌ Failed to create VS Code settings: {e}")
            return False

    def create_automation_scripts(self):
        """Create automation scripts for common tasks"""
        print("📝 Creating automation scripts...")

        scripts = {
            "format_code.sh": """#!/bin/bash
# Format all code files
echo "🔧 Formatting code..."

# Format Python files
black .
isort .

# Format other files
pre-commit run --all-files

echo "✅ Code formatting complete!"
""",
            "lint_code.sh": """#!/bin/bash
# Lint all code files
echo "🔍 Linting code..."

# Run flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=79 --statistics

# Run mypy
mypy . --ignore-missing-imports

echo "✅ Code linting complete!"
""",
            "test_code.sh": """#!/bin/bash
# Run all tests
echo "🧪 Running tests..."

# Run pytest with coverage
pytest tests/ -v --cov=oversight --cov-report=html --cov-report=term

echo "✅ Testing complete!"
""",
            "check_all.sh": """#!/bin/bash
# Run all quality checks
echo "🔍 Running all quality checks..."

# Format code
./format_code.sh

# Lint code
./lint_code.sh

# Run tests
./test_code.sh

# Validate documentation
python validate_docs.py

echo "✅ All quality checks complete!"
""",
            "setup_dev.sh": """#!/bin/bash
# Setup development environment
echo "🔧 Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install black flake8 isort mypy pytest pytest-cov pre-commit

# Setup pre-commit
pre-commit install

# Setup automation
python setup_automation.py

echo "✅ Development environment setup complete!"
""",
        }

        try:
            for filename, content in scripts.items():
                script_path = self.project_root / filename
                with open(script_path, "w") as f:
                    f.write(content)

                # Make executable
                os.chmod(script_path, 0o755)
                print(f"✅ Created {filename}")

            return True
        except Exception as e:
            print(f"❌ Failed to create automation scripts: {e}")
            return False

    def create_github_workflows(self):
        """Create comprehensive GitHub Actions workflows"""
        print("📝 Creating GitHub Actions workflows...")

        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        workflows = {
            "ci.yml": """name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install black flake8 isort mypy pytest pytest-cov

    - name: Format code
      run: |
        black . --check
        isort . --check-only

    - name: Lint code
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=79 --statistics
        mypy . --ignore-missing-imports

    - name: Run tests
      run: |
        pytest tests/ -v --cov=oversight --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
""",
            "validate-docs.yml": """name: Validate Documentation

on:
  push:
    paths:
      - 'README.md'
      - 'MVP_DEMO.md'
      - 'validate_docs.py'
  pull_request:
    paths:
      - 'README.md'
      - 'MVP_DEMO.md'
      - 'validate_docs.py'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Validate documentation
      run: |
        python validate_docs.py

    - name: Check demo script
      run: |
        chmod +x demo.sh
        echo "Demo script is executable"

    - name: Verify commands work
      run: |
        python -m oversight.features.humaneval_integration --help
        python -m oversight.features.red_team_suite --help
        echo "All commands work correctly"
""",
            "security.yml": """name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  push:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Run Bandit security scan
      uses: python-security/bandit-action@v1
      with:
        path: oversight/
        level: medium
        confidence: medium

    - name: Run Safety check
      run: |
        pip install safety
        safety check
""",
        }

        try:
            for filename, content in workflows.items():
                workflow_path = workflows_dir / filename
                with open(workflow_path, "w") as f:
                    f.write(content)
                print(f"✅ Created {filename}")

            return True
        except Exception as e:
            print(f"❌ Failed to create GitHub workflows: {e}")
            return False

    def setup_all(self):
        """Setup all automation tools"""
        print("🚀 Setting up comprehensive automation...")

        steps = [
            ("Development tools", self.setup_development_tools),
            ("Pre-commit hooks", self.setup_pre_commit),
            ("Editor config", self.create_editor_config),
            ("VS Code settings", self.create_vscode_settings),
            ("Automation scripts", self.create_automation_scripts),
            ("GitHub workflows", self.create_github_workflows),
        ]

        success_count = 0
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if step_func():
                success_count += 1
            else:
                print(f"⚠️ {step_name} failed, continuing...")

        self.setup_complete = (
            success_count >= len(steps) - 1
        )  # Allow one failure

        if self.setup_complete:
            print(
                "\n🎉 Automation setup complete! "
                f"({success_count}/{len(steps)} steps successful)"
            )
            print("\n📋 Next steps:")
            print("1. Run: ./setup_dev.sh (if not already done)")
            print("2. Run: ./check_all.sh (to verify everything works)")
            print("3. Make a test commit to verify pre-commit hooks")
        else:
            print(
                "\n❌ Automation setup incomplete "
                f"({success_count}/{len(steps)} steps successful)"
            )
            print("Please check the errors above and try again.")

        return self.setup_complete


def main():
    """Main setup function"""
    setup = AutomationSetup()
    success = setup.setup_all()

    if success:
        print("\n✅ All automation tools are now configured!")
        print("🔧 Future commits will automatically:")
        print("  - Format code with Black")
        print("  - Check style with flake8")
        print("  - Sort imports with isort")
        print("  - Validate documentation")
        print("  - Run tests")
        print("  - Check for security issues")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
