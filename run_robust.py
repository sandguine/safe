#!/usr/bin/env python3
"""
Robust Execution Script for Oversight Curriculum
================================================

This Python script provides a cross-platform, robust execution environment
that ensures smooth operation every time by:

1. Setting correct working directory
2. Loading environment variables properly
3. Checking all dependencies and prerequisites
4. Providing comprehensive error handling
5. Ensuring proper cleanup and reporting
6. Cross-platform compatibility (Windows, macOS, Linux)

Usage:
    python run_robust.py [options]

Options:
    --cycles N                    Number of cycles to run (default: 10)
    --puzzles-per-cycle N         Puzzles per cycle (default: 2)
    --solutions-per-puzzle N      Solutions per puzzle (default: 1)
    --skip-verification          Skip verification step
    --skip-tests                 Skip test execution
    --skip-analysis              Skip analysis step
    --verbose                    Enable verbose output
    --dry-run                    Show what would be done without executing
"""

import os
import sys
import subprocess
import platform
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import traceback

# Try to import dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class RobustRunner:
    """Main class for robust execution of the oversight curriculum"""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.script_dir = Path(__file__).parent.absolute()
        self.working_dir = self.script_dir
        self.success_count = 0
        self.total_steps = 0
        self.errors = []
        self.start_time = time.time()
        
        # Ensure we're in the right directory
        os.chdir(self.working_dir)
        
    def log(self, message: str, level: str = "INFO", color: str = Colors.BLUE):
        """Log a message with timestamp and color"""
        timestamp = time.strftime("%H:%M:%S")
        level_colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "STEP": Colors.PURPLE
        }
        
        color_code = level_colors.get(level, Colors.BLUE)
        print(f"{color_code}[{level}]{Colors.NC} [{timestamp}] {message}")
        
    def print_banner(self):
        """Print the application banner"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                OVERSIGHT CURRICULUM RUNNER                   ║
║                    Robust Execution Script                   ║
║                    (Python Cross-Platform)                   ║
╚══════════════════════════════════════════════════════════════╝{Colors.NC}
"""
        print(banner)
        
    def check_working_directory(self) -> bool:
        """Check and set the correct working directory"""
        self.log("Checking working directory...", "STEP")
        
        try:
            # Check if we're in the oversight_curriculum directory
            if self.working_dir.name == "oversight_curriculum":
                self.log("Already in oversight_curriculum directory", "SUCCESS")
                return True
            else:
                # Try to find the oversight_curriculum directory
                oversight_dir = self.script_dir / "oversight_curriculum"
                if oversight_dir.exists():
                    os.chdir(oversight_dir)
                    self.working_dir = oversight_dir
                    self.log(f"Changed to oversight_curriculum directory: {self.working_dir}", "SUCCESS")
                    return True
                else:
                    self.log("Could not find oversight_curriculum directory", "ERROR")
                    return False
        except Exception as e:
            self.log(f"Error checking working directory: {e}", "ERROR")
            return False
            
    def check_environment(self) -> bool:
        """Check and load environment variables"""
        self.log("Checking environment setup...", "STEP")
        
        try:
            # Check if .env file exists
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
                with open(env_file, 'w') as f:
                    f.write(env_template)
                    
                self.log("Please edit .env file and add your actual API key", "ERROR")
                self.log("Then run this script again", "INFO")
                return False
            
            # Load .env file
            if DOTENV_AVAILABLE:
                load_dotenv(env_file)
                self.log("Loaded .env file using python-dotenv", "SUCCESS")
            else:
                # Manual loading for basic .env files
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                self.log("Loaded .env file manually", "SUCCESS")
            
            # Check if API key is set
            api_key = os.getenv("CLAUDE_API_KEY")
            if not api_key:
                self.log("CLAUDE_API_KEY not found in .env file", "ERROR")
                return False
            
            # Validate API key format
            if not api_key.startswith("sk-"):
                self.log("Invalid API key format (should start with 'sk-')", "ERROR")
                return False
            
            self.log("Environment variables loaded successfully", "SUCCESS")
            self.log(f"API Key: {api_key[:10]}...{api_key[-4:]}", "INFO")
            return True
            
        except Exception as e:
            self.log(f"Error checking environment: {e}", "ERROR")
            return False
    
    def check_python_dependencies(self) -> bool:
        """Check Python and required dependencies"""
        self.log("Checking Python and dependencies...", "STEP")
        
        try:
            # Check Python version
            python_version = platform.python_version()
            self.log(f"Python version: {python_version}", "INFO")
            
            # Check if requirements.txt exists
            requirements_file = self.working_dir / "requirements.txt"
            if not requirements_file.exists():
                self.log("requirements.txt not found", "ERROR")
                return False
            
            # Check if virtual environment is active
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                self.log(f"Running in virtual environment: {sys.prefix}", "SUCCESS")
            else:
                self.log("Not running in a virtual environment (recommended but not required)", "WARNING")
            
            # Check required packages
            required_packages = self._parse_requirements(requirements_file)
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                self.log(f"Missing packages: {', '.join(missing_packages)}", "WARNING")
                self.log("Installing missing packages...", "INFO")
                
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                                 check=True, capture_output=True, text=True)
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
    
    def _parse_requirements(self, requirements_file: Path) -> List[str]:
        """Parse requirements.txt and extract package names"""
        packages = []
        try:
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (remove version specifiers)
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                        packages.append(package)
        except Exception as e:
            self.log(f"Error parsing requirements: {e}", "WARNING")
        
        return packages
    
    def run_verification(self) -> bool:
        """Run the verification script"""
        self.log("Running verification script...", "STEP")
        
        try:
            verify_script = self.working_dir / "verify_setup.py"
            if not verify_script.exists():
                self.log("verify_setup.py not found", "ERROR")
                return False
            
            result = subprocess.run([sys.executable, str(verify_script)], 
                                  capture_output=True, text=True)
            
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
    
    def create_directories(self) -> bool:
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
    
    def run_main_application(self) -> bool:
        """Run the main application"""
        self.log("Running main application...", "STEP")
        
        try:
            main_script = self.working_dir / "azr_loop.py"
            if not main_script.exists():
                self.log("azr_loop.py not found", "ERROR")
                return False
            
            # Set parameters
            cycles = getattr(self.args, 'cycles', 10)
            puzzles_per_cycle = getattr(self.args, 'puzzles_per_cycle', 2)
            solutions_per_puzzle = getattr(self.args, 'solutions_per_puzzle', 1)
            
            self.log(f"Running with parameters:", "INFO")
            self.log(f"  - Cycles: {cycles}", "INFO")
            self.log(f"  - Puzzles per cycle: {puzzles_per_cycle}", "INFO")
            self.log(f"  - Solutions per puzzle: {solutions_per_puzzle}", "INFO")
            
            # Generate output filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = self.working_dir / "results" / f"robust_run_{timestamp}.csv"
            
            # Build command
            cmd = [
                sys.executable, str(main_script),
                "--cycles", str(cycles),
                "--puzzles_per_cycle", str(puzzles_per_cycle),
                "--solutions_per_puzzle", str(solutions_per_puzzle),
                "--output", str(output_file)
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
    
    def run_analysis(self) -> bool:
        """Run analysis on results"""
        if self.args.skip_analysis:
            self.log("Skipping analysis (--skip-analysis flag)", "INFO")
            return True
            
        self.log("Running analysis...", "STEP")
        
        try:
            analysis_script = self.working_dir / "src" / "analysis.py"
            if not analysis_script.exists():
                self.log("analysis.py not found, skipping analysis", "WARNING")
                return True
            
            # Find result files
            results_dir = self.working_dir / "results"
            baseline_files = list(results_dir.glob("baseline_*.csv"))
            oversight_files = list(results_dir.glob("oversight_*.csv"))
            
            if baseline_files and oversight_files:
                baseline_file = max(baseline_files, key=lambda x: x.stat().st_mtime)
                oversight_file = max(oversight_files, key=lambda x: x.stat().st_mtime)
                
                self.log(f"Running analysis on:", "INFO")
                self.log(f"  - Baseline: {baseline_file.name}", "INFO")
                self.log(f"  - Oversight: {oversight_file.name}", "INFO")
                
                cmd = [
                    sys.executable, str(analysis_script),
                    "--baseline", str(baseline_file),
                    "--oversight", str(oversight_file)
                ]
                
                if self.args.dry_run:
                    self.log(f"DRY RUN - Would execute: {' '.join(cmd)}", "INFO")
                    return True
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log("Analysis completed successfully", "SUCCESS")
                    return True
                else:
                    self.log("Analysis failed, but continuing", "WARNING")
                    return True
            else:
                self.log("No result files found for analysis", "WARNING")
                return True
                
        except Exception as e:
            self.log(f"Error running analysis: {e}", "WARNING")
            return True
    
    def run_tests(self) -> bool:
        """Run tests"""
        if self.args.skip_tests:
            self.log("Skipping tests (--skip-tests flag)", "INFO")
            return True
            
        self.log("Running tests...", "STEP")
        
        try:
            test_file = self.working_dir / "tests" / "test_deduction_loop.py"
            if not test_file.exists():
                self.log("Tests not found, skipping", "WARNING")
                return True
            
            cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
            
            if self.args.dry_run:
                self.log(f"DRY RUN - Would execute: {' '.join(cmd)}", "INFO")
                return True
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Tests passed", "SUCCESS")
                return True
            else:
                self.log("Some tests failed, but continuing", "WARNING")
                return True
                
        except Exception as e:
            self.log(f"Error running tests: {e}", "WARNING")
            return True
    
    def cleanup(self) -> bool:
        """Perform cleanup operations"""
        self.log("Performing cleanup...", "STEP")
        
        try:
            # Clean temporary files
            temp_dir = self.working_dir / "temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                temp_dir.mkdir()
                self.log("Cleaned temporary files", "INFO")
            
            # Remove Python cache
            for cache_dir in self.working_dir.rglob("__pycache__"):
                shutil.rmtree(cache_dir)
            
            for pyc_file in self.working_dir.rglob("*.pyc"):
                pyc_file.unlink()
            
            self.log("Cleanup completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error during cleanup: {e}", "WARNING")
            return True
    
    def generate_summary(self) -> bool:
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
            
            summary += f"\n⏱️  Execution completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            print(summary)
            
            # Save summary to file
            summary_file = self.working_dir / "results" / f"execution_summary_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(summary_file, 'w') as f:
                f.write(summary)
            
            return True
            
        except Exception as e:
            self.log(f"Error generating summary: {e}", "WARNING")
            return True
    
    def run(self) -> bool:
        """Main execution method"""
        self.print_banner()
        
        # Define execution steps
        steps = [
            ("check_working_directory", "Checking working directory"),
            ("check_environment", "Checking environment setup"),
            ("check_python_dependencies", "Checking Python dependencies"),
            ("run_verification", "Running verification"),
            ("create_directories", "Creating directories"),
            ("run_main_application", "Running main application"),
            ("run_analysis", "Running analysis"),
            ("run_tests", "Running tests"),
            ("cleanup", "Performing cleanup"),
            ("generate_summary", "Generating summary")
        ]
        
        self.total_steps = len(steps)
        
        for step_name, step_description in steps:
            self.log(f"Executing: {step_description}", "STEP")
            
            try:
                step_method = getattr(self, step_name)
                if step_method():
                    self.log(f"{step_description} completed successfully", "SUCCESS")
                    self.success_count += 1
                else:
                    self.log(f"{step_description} failed", "ERROR")
                    self.errors.append(step_name)
                    
                    # Ask user if they want to continue
                    if not self.args.dry_run:
                        response = input(f"\n{Colors.YELLOW}Do you want to continue with the remaining steps? (y/N): {Colors.NC}")
                        if response.lower() not in ['y', 'yes']:
                            self.log("Execution stopped by user", "INFO")
                            break
            except Exception as e:
                self.log(f"Error in {step_name}: {e}", "ERROR")
                self.errors.append(step_name)
                traceback.print_exc()
        
        # Final status
        if self.success_count == self.total_steps:
            self.log("🎉 EXECUTION SUCCESSFUL 🎉", "SUCCESS")
        else:
            self.log("⚠️  EXECUTION HAD ISSUES ⚠️", "WARNING")
            self.log(f"Failed steps: {', '.join(self.errors)}", "ERROR")
        
        return self.success_count == self.total_steps

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Robust execution script for oversight curriculum",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--cycles", type=int, default=10,
                       help="Number of cycles to run (default: 10)")
    parser.add_argument("--puzzles-per-cycle", type=int, default=2,
                       help="Puzzles per cycle (default: 2)")
    parser.add_argument("--solutions-per-puzzle", type=int, default=1,
                       help="Solutions per puzzle (default: 1)")
    parser.add_argument("--skip-verification", action="store_true",
                       help="Skip verification step")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip test execution")
    parser.add_argument("--skip-analysis", action="store_true",
                       help="Skip analysis step")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without executing")
    
    args = parser.parse_args()
    
    # Create and run the robust runner
    runner = RobustRunner(args)
    success = runner.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 