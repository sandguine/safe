#!/usr/bin/env python3
"""
Cross-platform robust execution script for Oversight Curriculum
Provides the same functionality as run_robust.sh but works on Windows, macOS, and Linux
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


# Colors for output (works on most terminals)
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


def run_command(cmd, capture_output=False, check=True):
    """Run a command and handle errors"""
    try:
        if capture_output:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=check
            )
            return result
        else:
            subprocess.run(cmd, shell=True, check=check)
            return None
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {cmd}")
            print_error(f"Error: {e}")
            raise
        return e


def validate_setup():
    """Validate the setup using verify_setup.py"""
    print_step("Validating setup...")

    if Path("verify_setup.py").exists():
        result = run_command(
            "python verify_setup.py", capture_output=True, check=False
        )
        if result and result.returncode != 0:
            print_error("Setup validation failed")
            return False
        print_success("Setup validation passed")
        return True
    else:
        print_warning("verify_setup.py not found, skipping validation")
        return True


def setup_environment():
    """Set up environment variables and directories"""
    print_step("Setting up environment...")

    # Create necessary directories
    for dir_name in ["results", "logs", "temp"]:
        Path(dir_name).mkdir(exist_ok=True)

    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print_warning(".env file not found, creating template...")
        env_content = """# Oversight Curriculum Environment Configuration
CLAUDE_API_KEY=sk-your-actual-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
"""
        env_file.write_text(env_content)
        print_warning(
            "Please edit .env file and add your actual Claude API key"
        )

    print_success("Environment setup complete")
    return True


def install_dependencies():
    """Install required dependencies"""
    print_step("Checking dependencies...")

    try:
        # Check if core dependencies are installed
        import anthropic
        import human_eval

        print_success("Core dependencies already installed")
    except ImportError:
        print_warning("Installing core dependencies...")
        run_command("pip install -r requirements.txt")

    # Check for enhanced dependencies
    enhanced_deps = ["dotenv", "requests", "pandas", "matplotlib"]
    missing_deps = []

    for dep in enhanced_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)

    if missing_deps:
        print_warning(f"Installing enhanced dependencies: {missing_deps}")
        run_command("pip install python-dotenv requests pandas matplotlib")

    print_success("All dependencies verified")
    return True


def run_demo():
    """Run the main demo script"""
    print_step("Executing oversight curriculum demo...")

    start_time = time.time()

    # Run the demo
    try:
        run_command("./demo.sh")
        print_success("Demo execution completed successfully")
    except subprocess.CalledProcessError:
        print_error("Demo execution failed")
        return False

    execution_time = time.time() - start_time
    print_success(f"Execution time: {execution_time: .1f} seconds")
    return True


def generate_summary(timestamp, execution_time):
    """Generate execution summary"""
    print_step("Generating execution summary...")

    summary_file = f"results/execution_summary_{timestamp}.txt"

    summary_content = """OVERSIGHT CURRICULUM EXECUTION SUMMARY
=====================================
Timestamp: {datetime.now()}
Execution Time: {execution_time: .1f} seconds

ENVIRONMENT:
- Working Directory: {Path.cwd()}
- Python Version: {sys.version.split()[0]}
- Platform: {sys.platform}

FILES GENERATED:
- demo/baseline.json - Baseline capability results
- demo/oversight.json - Oversight capability results
- demo/safety.json - Safety filtering results
- demo/harm_prompts.json - Sample harmful prompts
- evaluation_report_*.txt - Comprehensive analysis
- evaluation_data_*.json - Structured data

LOGS:
- logs/execution_{timestamp}.log - Detailed execution log

COMPLETION: {datetime.now()}
"""

    Path(summary_file).write_text(summary_content)
    print_success(f"Execution summary saved to {summary_file}")


def cleanup():
    """Clean up temporary files"""
    print_step("Performing cleanup...")

    # Remove temporary files
    temp_dir = Path("temp")
    if temp_dir.exists():
        for file in temp_dir.glob("*"):
            try:
                file.unlink()
            except Exception:
                pass

    # Remove __pycache__ directories
    for cache_dir in Path(".").rglob("__pycache__"):
        try:
            import shutil

            shutil.rmtree(cache_dir)
        except Exception:
            pass

    print_success("Cleanup completed")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Robust Oversight Curriculum Runner"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )
    parser.add_argument(
        "--skip-validation", action="store_true", help="Skip setup validation"
    )
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(
        f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗"
    )
    print("║                OVERSIGHT CURRICULUM ROBUST RUN               ║")
    print("║                    Cross-Platform Python Version             ║")
    print(
        "╚══════════════════════════════════════════════════════════════╝{Colors.NC}"
    )
    print()

    if args.dry_run:
        print_warning("DRY RUN MODE - No actual execution will occur")
        print_step("Would validate setup...")
        print_step("Would set up environment...")
        print_step("Would install dependencies...")
        print_step("Would run demo...")
        print_step("Would generate summary...")
        print_step("Would perform cleanup...")
        print_success("Dry run completed")
        return 0

    try:
        # Validate setup
        if not args.skip_validation:
            if not validate_setup():
                return 1

        # Setup environment
        if not setup_environment():
            return 1

        # Install dependencies
        if not install_dependencies():
            return 1

        # Run demo
        start_time = time.time()
        if not run_demo():
            return 1
        execution_time = time.time() - start_time

        # Generate summary
        generate_summary(timestamp, execution_time)

        # Cleanup
        cleanup()

        # Final summary
        print()
        print(
            f"{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗"
        )
        print(
            "║                    EXECUTION COMPLETE                        ║"
        )
        print(
            "╚══════════════════════════════════════════════════════════════╝{Colors.NC}"
        )
        print()
        print(f"{Colors.CYAN}📊 Results available in: {Colors.NC}")
        print("  • demo/ directory - Raw results")
        print("  • results/ directory - Analysis and summaries")
        print("  • logs/ directory - Execution logs")
        print()
        print(f"{Colors.CYAN}📋 Next steps: {Colors.NC}")
        print("  • Review evaluation_report_*.txt for detailed analysis")
        print("  • Check demo/ directory for raw results")
        print("  • Run 'python evaluate_results.py' for additional analysis")
        print()
        print_success("Oversight curriculum execution completed successfully!")

        return 0

    except KeyboardInterrupt:
        print_error("Execution interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
