#!/usr/bin/env python3
"""
Setup verification script for Oversight Curriculum
Validates all prerequisites and configuration before execution
"""

import importlib
import os
import sys
from pathlib import Path


# Colors for output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def print_step(message):
    print(f"{Colors.PURPLE}[STEP]{Colors.NC} {message}")


def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def check_python_version():
    """Check if Python version is 3.7+"""
    print_step("Checking Python version...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error(
            f"Python 3.7+ required, found {version.major}.{version.minor}.{version.micro}"
        )
        return False

    print_success(f"Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_working_directory():
    """Check if we're in the oversight_curriculum directory"""
    print_step("Checking working directory...")

    current_dir = Path.cwd()
    required_files = ["demo.sh", "requirements.txt", "README.md"]

    missing_files = [f for f in required_files if not (current_dir / f).exists()]

    if missing_files:
        print_error(f"Missing required files: {missing_files}")
        print_error(f"Current directory: {current_dir}")
        print_error("Please run this script from the oversight_curriculum directory")
        return False

    print_success(f"Working directory: {current_dir}")
    return True


def check_dependencies():
    """Check if all required dependencies are installed"""
    print_step("Checking dependencies...")

    required_packages = {
        "anthropic": "anthropic",
        "human_eval": "human-eval",
        "dotenv": "python-dotenv",
        "requests": "requests",
        "pandas": "pandas",
        "matplotlib": "matplotlib",
    }

    missing_packages = []
    optional_missing = []

    for package, pip_name in required_packages.items():
        try:
            importlib.import_module(package)
            print_success(f"✓ {package}")
        except ImportError:
            if package in ["anthropic", "human_eval"]:
                missing_packages.append(pip_name)
                print_error(f"✗ {package} (required)")
            else:
                optional_missing.append(pip_name)
                print_warning(f"✗ {package} (optional)")

    if missing_packages:
        print_error(f"Missing required packages: {missing_packages}")
        print_error("Run: pip install -r requirements.txt")
        return False

    if optional_missing:
        print_warning(f"Missing optional packages: {optional_missing}")
        print_warning(
            "For enhanced functionality, run: pip install python-dotenv requests pandas matplotlib"
        )

    return True


def check_environment_file():
    """Check .env file configuration"""
    print_step("Checking environment configuration...")

    env_file = Path(".env")

    if not env_file.exists():
        print_warning(".env file not found")
        print_warning("Demo will run with mock responses")
        return True

    # Load and check environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.getenv("CLAUDE_API_KEY")
        model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

        if api_key and api_key != "sk-your-actual-api-key-here":
            # Basic format validation
            if api_key.startswith("sk-") and len(api_key) == 51:
                print_success("Valid API key format detected")
            else:
                print_warning("API key format appears invalid")
        else:
            print_warning("No valid API key found - demo will use mock responses")

        print_success(f"Model configured: {model}")
        return True

    except ImportError:
        print_warning("python-dotenv not available - cannot load .env file")
        return True


def check_directories():
    """Check and create necessary directories"""
    print_step("Checking output directories...")

    required_dirs = ["demo", "results", "logs", "temp"]

    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {dir_name}/")
        else:
            print_success(f"Directory exists: {dir_name}/")

    return True


def check_executable_permissions():
    """Check if demo.sh is executable"""
    print_step("Checking script permissions...")

    demo_script = Path("demo.sh")
    if not demo_script.exists():
        print_error("demo.sh not found")
        return False

    if not os.access(demo_script, os.X_OK):
        print_warning("demo.sh is not executable")
        print_warning("Run: chmod +x demo.sh")
        return False

    print_success("demo.sh is executable")
    return True


def run_quick_test():
    """Run a quick test to verify the setup works"""
    print_step("Running quick setup test...")

    try:
        # Test basic imports
        import anthropic
        import human_eval

        # Test that we can create basic objects
        print_success("Core modules import successfully")

        # Test directory structure
        if Path("oversight").exists():
            print_success("Oversight module structure found")
        else:
            print_warning("Oversight module structure not found")

        return True

    except Exception as e:
        print_error(f"Quick test failed: {e}")
        return False


def main():
    """Main verification function"""
    print(
        f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗"
    )
    print("║                OVERSIGHT CURRICULUM SETUP VERIFICATION    ║")
    print("╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()

    checks = [
        check_python_version,
        check_working_directory,
        check_dependencies,
        check_environment_file,
        check_directories,
        check_executable_permissions,
        run_quick_test,
    ]

    passed = 0
    total = len(checks)

    for check in checks:
        try:
            if check():
                passed += 1
        except Exception as e:
            print_error(f"Check failed with exception: {e}")

    print()
    print(
        f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗"
    )
    print(f"║                    VERIFICATION SUMMARY                        ║")
    print("╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()

    if passed == total:
        print_success(f"All {total} checks passed! Setup is ready.")
        print_success("You can now run: ./run_robust.sh")
        return 0
    else:
        print_error(f"{total - passed} of {total} checks failed.")
        print_error("Please fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
