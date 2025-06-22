#!/usr/bin/env python3
"""
Documentation validation script for SAFE MVP Demo.
Checks for common issues and ensures accuracy of documentation.
"""

import subprocess
import sys
from pathlib import Path


class DocValidator:
    """Validates documentation files for common issues"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = Path.cwd()

    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("🔍 Validating documentation...")

        # Check files exist
        self.check_files_exist()

        # Validate commands
        self.validate_commands()

        # Check for common issues
        self.check_common_issues()

        # Validate file references
        self.validate_file_references()

        # Check for overselling language
        self.check_language()

        # Print results
        self.print_results()

        return len(self.errors) == 0

    def check_files_exist(self):
        """Check that all referenced files exist"""
        required_files = [
            "demo.sh",
            "evaluate_results.py",
            "requirements.txt",
            "oversight/features/humaneval_integration.py",
            "oversight/features/red_team_suite.py",
            "oversight/model.py",
            "oversight/hhh_filter.py",
        ]

        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                self.errors.append(f"Referenced file does not exist: {file_path}")

    def validate_commands(self):
        """Validate that commands in documentation work"""
        commands_to_test = [
            "python -m oversight.features.humaneval_integration --help",
            "python -m oversight.features.red_team_suite --help",
        ]

        for cmd in commands_to_test:
            try:
                result = subprocess.run(
                    cmd.split(), capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    self.errors.append(f"Command failed: {cmd}")
            except Exception as e:
                self.errors.append(f"Command error: {cmd} - {e}")

        # Check dependencies separately with better error handling
        try:
            import importlib

            importlib.import_module("anthropic")
            importlib.import_module("human_eval")
            print("  ✅ Dependencies available")
        except ImportError as e:
            self.warnings.append(f"Dependencies not installed: {e}")
            print(
                "  ⚠️  Dependencies not installed "
                "(run: pip install -r requirements.txt)"
            )

    def check_common_issues(self):
        """Check for common documentation issues"""
        doc_files = ["README.md", "MVP_DEMO.md"]

        for doc_file in doc_files:
            if not (self.project_root / doc_file).exists():
                self.errors.append(f"Documentation file missing: {doc_file}")
                continue

            content = (self.project_root / doc_file).read_text()

            # Check for broken links
            if "README_ENHANCED.md" in content:
                self.errors.append(f"Reference to deleted file in {doc_file}")

            # Check for inconsistent paths
            if "results/" in content and "demo/" in content:
                self.warnings.append(f"Mixed output directories in {doc_file}")

            # Check for missing code blocks
            if "```bash" in content and "```" not in content:
                self.errors.append(f"Unclosed code block in {doc_file}")

    def validate_file_references(self):
        """Validate that file references are consistent"""
        doc_files = ["README.md", "MVP_DEMO.md"]

        for doc_file in doc_files:
            if not (self.project_root / doc_file).exists():
                continue

            content = (self.project_root / doc_file).read_text()

            # Check for consistent output paths
            if "demo/baseline.json" in content and "results/baseline.json" in content:
                self.errors.append(f"Inconsistent output paths in {doc_file}")

    def check_language(self):
        """Check for overselling or inaccurate language"""
        doc_files = ["README.md", "MVP_DEMO.md"]

        problematic_phrases = [
            "zero false positives",
            "perfect",
            "revolutionary",
            "breakthrough",
            "state of the art",
            "best in class",
            "unprecedented",
        ]

        for doc_file in doc_files:
            if not (self.project_root / doc_file).exists():
                continue

            content = (self.project_root / doc_file).read_text().lower()

            for phrase in problematic_phrases:
                if phrase in content:
                    self.warnings.append(
                        f"Potentially overselling language in {doc_file}: '{phrase}'"
                    )

    def print_results(self):
        """Print validation results"""
        print("\n📊 Validation Results:")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All checks passed!")
        elif not self.errors:
            print("\n✅ No errors found, but check warnings above.")
        else:
            print(f"\n❌ Found {len(self.errors)} errors that need to be fixed.")


def main():
    """Main validation function"""
    validator = DocValidator()
    success = validator.validate_all()

    if not success:
        print("\n💡 To fix issues:")
        print("  1. Check that all referenced files exist")
        print("  2. Ensure commands work as documented")
        print("  3. Fix inconsistent file paths")
        print("  4. Review language for accuracy")
        sys.exit(1)

    print("\n🎉 Documentation validation completed successfully!")


if __name__ == "__main__":
    main()
