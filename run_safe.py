#!/usr/bin/env python3
"""
Safe Execution Script for Oversight Curriculum
=============================================

This Python script ensures smooth execution every time by:
1. Setting correct working directory
2. Loading environment variables properly
3. Checking all dependencies and prerequisites
4. Providing comprehensive error handling
5. Ensuring proper cleanup and reporting

Usage:
    python run_safe.py [options]
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

# Try to import dotenv
try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class Colors:
    """ANSI color codes for terminal output"""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"


class SafeRunner:
    """Main class for safe execution"""

    def __init__(self, args):
        self.args = args
        self.script_dir = Path(__file__).parent.absolute()
        self.working_dir = self.script_dir
        self.success_count = 0
        self.total_steps = 0
        self.errors = []
        self.start_time = time.time()

        # Ensure we're in the right directory
        os.chdir(self.working_dir)

    def log(self, message, level="INFO"):
        """Log a message with timestamp and color"""
        timestamp = time.strftime("%H:%M:%S")
        level_colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "STEP": Colors.PURPLE,
        }

        color_code = level_colors.get(level, Colors.BLUE)
        print(f"{color_code}[{level}]{Colors.NC} [{timestamp}] {message}")

    def print_banner(self):
        """Print the application banner"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                OVERSIGHT CURRICULUM RUNNER                   ║
║                    Safe Execution Script                     ║
╚══════════════════════════════════════════════════════════════╝{Colors.NC}
"""
        print(banner)

    def check_working_directory(self):
        """Check and set the correct working directory"""
        self.log("Checking working directory...", "STEP")

        try:
            if self.working_dir.name == "oversight_curriculum":
                self.log(
                    "Already in oversight_curriculum directory", "SUCCESS"
                )
                return True
            else:
                oversight_dir = self.script_dir / "oversight_curriculum"
                if oversight_dir.exists():
                    os.chdir(oversight_dir)
                    self.working_dir = oversight_dir
                    self.log(
                        f"Changed to oversight_curriculum directory: "
                        f"{self.working_dir}",
                        "SUCCESS",
                    )
                    return True
                else:
                    self.log(
                        "Could not find oversight_curriculum directory",
                        "ERROR",
                    )
                    return False
        except Exception as e:
            self.log(f"Error checking working directory: {e}", "ERROR")
            return False

    def check_environment(self):
        """Check and load environment variables"""
        self.log("Checking environment setup...", "STEP")

        try:
            env_file = self.working_dir / ".env"

            if not env_file.exists():
                self.log(".env file not found", "WARNING")
                self.log("Creating .env file template...", "INFO")

                env_template = """# Claude API Configuration
CLAUDE_API_KEY=your-api-key-here

# Optional: Model configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Optional: Logging level
LOG_LEVEL=INFO
"""
                with open(env_file, "w") as f:
                    f.write(env_template)

                self.log(
                    "Please edit .env file and add your actual API key",
                    "ERROR",
                )
                self.log("Then run this script again", "INFO")
                return False

            # Load .env file
            if DOTENV_AVAILABLE:
                load_dotenv(env_file)
                self.log("Loaded .env file using python-dotenv", "SUCCESS")
            else:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key.strip()] = value.strip()
                self.log("Loaded .env file manually", "SUCCESS")

            # Check if API key is set
            api_key = os.getenv("CLAUDE_API_KEY")
            if not api_key:
                self.log("CLAUDE_API_KEY not found in .env file", "ERROR")
                return False

            if not api_key.startswith("sk-"):
                self.log(
                    "Invalid API key format (should start with 'sk-')", "ERROR"
                )
                return False

            self.log("Environment variables loaded successfully", "SUCCESS")
            self.log(f"API Key: {api_key[:10]}...{api_key[-4:]}", "INFO")
            return True

        except Exception as e:
            self.log(f"Error checking environment: {e}", "ERROR")
            return False

    def check_python_dependencies(self):
        """Check Python and required dependencies"""
        self.log("Checking Python and dependencies...", "STEP")

        try:
            python_version = platform.python_version()
            self.log(f"Python version: {python_version}", "INFO")

            requirements_file = self.working_dir / "requirements.txt"
            if not requirements_file.exists():
                self.log("requirements.txt not found", "ERROR")
                return False

            if hasattr(sys, "real_prefix") or (
                hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
            ):
                self.log(
                    f"Running in virtual environment: {sys.prefix}", "SUCCESS"
                )
            else:
                self.log(
                    "Not running in a virtual environment "
                    "(recommended but not required)",
                    "WARNING",
                )

            # Check required packages
            required_packages = self._parse_requirements(requirements_file)
            missing_packages = []

            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)

            if missing_packages:
                self.log(
                    f"Missing packages: {', '.join(missing_packages)}",
                    "WARNING",
                )
                self.log("Installing missing packages...", "INFO")

                try:
                    subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "-r",
                            str(requirements_file),
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    self.log("All packages installed successfully", "SUCCESS")
                except subprocess.CalledProcessError as e:
                    self.log(f"Failed to install packages: {e}", "ERROR")
                    return False
            else:
                self.log("All required packages are installed", "SUCCESS")

            return True

        except Exception as e:
            self.log(f"Error checking dependencies: {e}", "ERROR")
            return False

    def _parse_requirements(self, requirements_file):
        """Parse requirements.txt and extract package names"""
        packages = []
        try:
            with open(requirements_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        package = (
                            line.split("==")[0]
                            .split(">=")[0]
                            .split("<=")[0]
                            .split("~=")[0]
                            .strip()
                        )
                        packages.append(package)
        except Exception as e:
            self.log(f"Error parsing requirements: {e}", "WARNING")

        return packages

    def run_verification(self):
        """Run the verification script"""
        self.log("Running verification script...", "STEP")

        try:
            verify_script = self.working_dir / "verify_setup.py"
            if not verify_script.exists():
                self.log("verify_setup.py not found", "ERROR")
                return False

            result = subprocess.run(
                [sys.executable, str(verify_script)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.log("Verification passed", "SUCCESS")
                return True
            else:
                self.log("Verification failed", "ERROR")
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                return False

        except Exception as e:
            self.log(f"Error running verification: {e}", "ERROR")
            return False

    def create_directories(self):
        """Create necessary directories"""
        self.log("Creating necessary directories...", "STEP")

        try:
            directories = ["results", "logs", "temp"]

            for dir_name in directories:
                dir_path = self.working_dir / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.log(f"Created directory: {dir_name}", "INFO")
                else:
                    self.log(f"Directory exists: {dir_name}", "INFO")

            return True

        except Exception as e:
            self.log(f"Error creating directories: {e}", "ERROR")
            return False

    def run_main_application(self):
        """Run the main application"""
        self.log("Running main application...", "STEP")

        try:
            main_script = self.working_dir / "azr_loop.py"
            if not main_script.exists():
                self.log("azr_loop.py not found", "ERROR")
                return False

            # Set parameters
            cycles = getattr(self.args, "cycles", 10)

            self.log("Running with parameters:", "INFO")
            self.log(f"  - Cycles: {cycles}", "INFO")
            self.log("  - Referee: ON (with oversight)", "INFO")
            self.log("  - Config puzzles: ON", "INFO")

            # Generate output filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = (
                self.working_dir / "results" / f"safe_run_{timestamp}.csv"
            )

            # Build command with correct arguments
            cmd = [
                sys.executable,
                str(main_script),
                "--with_ref",
                "--cycles",
                str(cycles),
                "--config",
                "--output",
                str(output_file),
            ]

            if self.args.dry_run:
                self.log(f"DRY RUN - Would execute: {' '.join(cmd)}", "INFO")
                return True

            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.log("Main application completed successfully", "SUCCESS")
                return True
            else:
                self.log("Main application failed", "ERROR")
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                return False

        except Exception as e:
            self.log(f"Error running main application: {e}", "ERROR")
            return False

    def cleanup(self):
        """Perform cleanup operations"""
        self.log("Performing cleanup...", "STEP")

        try:
            temp_dir = self.working_dir / "temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                temp_dir.mkdir()
                self.log("Cleaned temporary files", "INFO")

            for cache_dir in self.working_dir.rglob("__pycache__"):
                shutil.rmtree(cache_dir)

            for pyc_file in self.working_dir.rglob("*.pyc"):
                pyc_file.unlink()

            self.log("Cleanup completed", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Error during cleanup: {e}", "WARNING")
            return True

    def generate_summary(self):
        """Generate execution summary"""
        self.log("Generating summary...", "STEP")

        try:
            end_time = time.time()
            duration = end_time - self.start_time

            summary = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                        EXECUTION SUMMARY                     ║
╚══════════════════════════════════════════════════════════════╝{Colors.NC}

📁 Working Directory: {self.working_dir}
🐍 Python Version: {platform.python_version()}
🔑 API Key: {os.getenv('CLAUDE_API_KEY', 'Not set')[:10]}...{os.getenv('CLAUDE_API_KEY', 'Not set')[-4:] if os.getenv('CLAUDE_API_KEY') else 'N/A'}
⏱️  Execution Time: {duration:.2f} seconds
📊 Steps Completed: {self.success_count}/{self.total_steps}

📊 Generated Files:
"""

            results_dir = self.working_dir / "results"
            if results_dir.exists():
                for file in results_dir.iterdir():
                    if file.is_file():
                        summary += f"  - {file.name}\n"
            else:
                summary += "  No result files found\n"

            summary += (
                f"\n⏱️  Execution completed at: "
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            print(summary)

            summary_file = (
                self.working_dir
                / "results"
                / f"execution_summary_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            )
            with open(summary_file, "w") as f:
                f.write(summary)

            return True

        except Exception as e:
            self.log(f"Error generating summary: {e}", "WARNING")
            return True

    def run(self):
        """Main execution method"""
        self.print_banner()

        steps = [
            ("check_working_directory", "Checking working directory"),
            ("check_environment", "Checking environment setup"),
            ("check_python_dependencies", "Checking Python dependencies"),
            ("run_verification", "Running verification"),
            ("create_directories", "Creating directories"),
            ("run_main_application", "Running main application"),
            ("cleanup", "Performing cleanup"),
            ("generate_summary", "Generating summary"),
        ]

        self.total_steps = len(steps)

        for step_name, step_description in steps:
            self.log(f"Executing: {step_description}", "STEP")

            try:
                step_method = getattr(self, step_name)
                if step_method():
                    self.log(
                        f"{step_description} completed successfully", "SUCCESS"
                    )
                    self.success_count += 1
                else:
                    self.log(f"{step_description} failed", "ERROR")
                    self.errors.append(step_name)

                    if not self.args.dry_run:
                        response = input(
                            f"\n{Colors.YELLOW}Do you want to continue with "
                            f"the remaining steps? (y/N): {Colors.NC}"
                        )
                        if response.lower() not in ["y", "yes"]:
                            self.log("Execution stopped by user", "INFO")
                            break
            except Exception as e:
                self.log(f"Error in {step_name}: {e}", "ERROR")
                self.errors.append(step_name)
                traceback.print_exc()

        if self.success_count == self.total_steps:
            self.log("🎉 EXECUTION SUCCESSFUL 🎉", "SUCCESS")
        else:
            self.log("⚠️  EXECUTION HAD ISSUES ⚠️", "WARNING")
            self.log(f"Failed steps: {', '.join(self.errors)}", "ERROR")

        return self.success_count == self.total_steps


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Safe execution script for oversight curriculum"
    )

    parser.add_argument(
        "--cycles",
        type=int,
        default=10,
        help="Number of cycles to run (default: 10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )

    args = parser.parse_args()

    runner = SafeRunner(args)
    success = runner.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
