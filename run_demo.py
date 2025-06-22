#!/usr/bin/env python3
"""
Main demo script for oversight curriculum.
Runs baseline and oversight experiments and generates comparison reports.
Now includes robust environment management and validation like run_robust.py.
"""

import os
import sys
import time
import json
import argparse
import platform
import traceback
from pathlib import Path
from typing import Dict, List

# Try to import dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Add src to path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir / "src"))

# Import after path setup
from deduction_loop import DeductionLoop
from metrics import MetricsCollector, ComparisonAnalyzer

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class RobustDemoRunner:
    """Robust demo runner with environment management and validation"""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.script_dir = Path(__file__).parent.absolute()
        self.working_dir = self.script_dir
        self.success_count = 0
        self.total_steps = 0
        self.errors = []
        self.start_time = time.time()
        
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
        print(f"{color_code}[{level}]{Colors.NC} [{timestamp}] "
              f"run_demo.py: {message}")
        
    def print_banner(self):
        """Print the application banner"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                OVERSIGHT CURRICULUM DEMO RUNNER              ║
║                    Robust Demo Execution                     ║
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
                self.log("Already in oversight_curriculum directory", 
                        "SUCCESS")
                return True
            else:
                # Try to find the oversight_curriculum directory
                oversight_dir = self.script_dir / "oversight_curriculum"
                if oversight_dir.exists():
                    os.chdir(oversight_dir)
                    self.working_dir = oversight_dir
                    self.log(f"Changed to oversight_curriculum directory: "
                            f"{self.working_dir}", "SUCCESS")
                    return True
                else:
                    self.log("Could not find oversight_curriculum directory", 
                            "ERROR")
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
                    
                self.log("Please edit .env file and add your actual API key", 
                        "ERROR")
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
                self.log("Invalid API key format (should start with 'sk-')", 
                        "ERROR")
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
            if (hasattr(sys, 'real_prefix') or 
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
                self.log("Virtual environment detected", "SUCCESS")
            else:
                self.log("No virtual environment detected", "WARNING")
            
            # Check required packages
            required_packages = [
                'anthropic', 'matplotlib', 'pandas', 'numpy', 'seaborn'
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                    self.log(f"✓ {package} available", "SUCCESS")
                except ImportError:
                    missing_packages.append(package)
                    self.log(f"✗ {package} missing", "ERROR")
            
            if missing_packages:
                self.log(f"Missing packages: {', '.join(missing_packages)}", 
                        "ERROR")
                self.log("Please install missing packages: pip install " + 
                        " ".join(missing_packages), "INFO")
                return False
            
            self.log("All Python dependencies available", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error checking Python dependencies: {e}", "ERROR")
            return False
    
    def check_directories_and_files(self) -> bool:
        """Check that required directories and files exist"""
        self.log("Checking directories and files...", "STEP")
        
        try:
            required_dirs = ['src', 'configs', 'results', 'logs']
            required_files = [
                'src/deduction_loop.py', 'src/metrics.py', 
                'configs/deduction_mini.json'
            ]
            
            # Check directories
            for dir_name in required_dirs:
                dir_path = self.working_dir / dir_name
                if dir_path.exists():
                    self.log(f"✓ Directory {dir_name} exists", "SUCCESS")
                else:
                    self.log(f"✗ Directory {dir_name} missing", "ERROR")
                    return False
            
            # Check files
            for file_path in required_files:
                full_path = self.working_dir / file_path
                if full_path.exists():
                    self.log(f"✓ File {file_path} exists", "SUCCESS")
                else:
                    self.log(f"✗ File {file_path} missing", "ERROR")
                    return False
            
            self.log("All required directories and files present", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error checking directories and files: {e}", "ERROR")
            return False
    
    def run_validation(self) -> bool:
        """Run comprehensive validation"""
        self.log("Running comprehensive validation...", "STEP")
        
        validation_steps = [
            ("Working Directory", self.check_working_directory),
            ("Environment Setup", self.check_environment),
            ("Python Dependencies", self.check_python_dependencies),
            ("Directories and Files", self.check_directories_and_files)
        ]
        
        for step_name, step_func in validation_steps:
            self.total_steps += 1
            try:
                if step_func():
                    self.success_count += 1
                    self.log(f"✓ {step_name} validation passed", "SUCCESS")
                else:
                    self.log(f"✗ {step_name} validation failed", "ERROR")
                    return False
            except Exception as e:
                self.log(f"✗ {step_name} validation error: {e}", "ERROR")
                return False
        
        self.log("All validation steps passed", "SUCCESS")
        return True
    
    def run_demo(self) -> bool:
        """Run the actual demo experiments"""
        self.log("Starting demo experiments...", "STEP")
        
        try:
            # Run baseline experiment
            self.log("Running baseline experiment...", "INFO")
            baseline_metrics = run_baseline_experiment(
                cycles=self.args.cycles,
                max_puzzles_per_cycle=self.args.puzzles_per_cycle,
                max_solutions_per_puzzle=self.args.solutions_per_puzzle,
                use_config=self.args.use_config
            )
            
            # Run oversight experiment
            self.log("Running oversight experiment...", "INFO")
            oversight_metrics = run_oversight_experiment(
                cycles=self.args.cycles,
                max_puzzles_per_cycle=self.args.puzzles_per_cycle,
                max_solutions_per_puzzle=self.args.solutions_per_puzzle,
                use_config=self.args.use_config
            )
            
            # Generate comparison report
            self.log("Generating comparison report...", "INFO")
            comparison_report = generate_comparison_report(
                baseline_metrics, oversight_metrics
            )
            
            # Save results
            self.log("Saving results...", "INFO")
            save_results(
                baseline_metrics, oversight_metrics, comparison_report,
                self.args.output_dir
            )
            
            # Create plots (unless skipped)
            if not self.args.skip_plots:
                self.log("Creating plots...", "INFO")
                create_plots(baseline_metrics, oversight_metrics, 
                           self.args.output_dir)
            
            self.log("Demo completed successfully!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error running demo: {e}", "ERROR")
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False
    
    def run(self) -> bool:
        """Main execution method"""
        try:
            # Print banner
            self.print_banner()
            
            # Run validation
            if not self.run_validation():
                self.log("Validation failed - cannot proceed", "ERROR")
                return False
            
            # Run demo
            if not self.run_demo():
                self.log("Demo execution failed", "ERROR")
                return False
            
            # Success summary
            duration = time.time() - self.start_time
            self.log(f"Demo completed successfully in {duration:.2f} seconds", 
                    "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Oversight Curriculum Demo')
    parser.add_argument('--cycles', type=int, default=10, 
                       help='Number of cycles per experiment (default: 10)')
    parser.add_argument('--puzzles_per_cycle', type=int, default=2,
                       help='Puzzles per cycle for speed optimization (default: 2)')
    parser.add_argument('--solutions_per_puzzle', type=int, default=1,
                       help='Solutions per puzzle for speed optimization (default: 1)')
    parser.add_argument('--use_config', action='store_true', default=True,
                       help='Use hard-coded config puzzles (default: True)')
    parser.add_argument('--skip_plots', action='store_true',
                       help='Skip plot generation for faster execution')
    parser.add_argument('--output_dir', type=str, default='results',
                       help='Output directory for results (default: results)')
    
    return parser.parse_args()


def run_baseline_experiment(cycles: int, 
                          max_puzzles_per_cycle: int = 2,
                          max_solutions_per_puzzle: int = 1,
                          use_config: bool = True) -> MetricsCollector:
    """Run baseline experiment without referee oversight"""
    print("=" * 60)
    print("RUNNING BASELINE EXPERIMENT (No Referee)")
    print("=" * 60)
    
    # Initialize deduction loop without referee
    loop = DeductionLoop(
        enable_referee=False,
        max_puzzles_per_cycle=max_puzzles_per_cycle,
        max_solutions_per_puzzle=max_solutions_per_puzzle
    )
    
    # Set up config puzzles if requested
    if use_config:
        config_puzzles = load_config_puzzles()
        if config_puzzles:
            loop._use_config_puzzles = True
            loop._config_puzzles = config_puzzles
            loop._config_puzzle_index = 0
    
    # Run cycles
    for cycle in range(1, cycles + 1):
        print(f"\n--- Cycle {cycle}/{cycles} ---")
        metrics = loop.run_cycle()
        
        # Print cycle summary with correct keys
        print(f"Puzzles: {metrics.get('new_puzzles', 0)} generated, "
              f"{metrics.get('approved_puzzles', 0)} approved")
        print(f"Solutions: {metrics.get('new_solutions', 0)} generated, "
              f"{metrics.get('correct_solutions', 0)} correct")
        print(f"Avg reward: {metrics.get('avg_reward', 0.0):.3f}")
        print(f"Duration: {metrics.get('cycle_duration', 0.0):.2f}s")
    
    # Get final summary
    summary = loop.get_summary_stats()
    print(f"\nBASELINE SUMMARY:")
    print(f"Total cycles: {summary.get('cycle_number', 0)}")
    print(f"Approval rate: {summary.get('approval_rate', 0.0):.2%}")
    print(f"Success rate: {summary.get('accuracy', 0.0):.2%}")
    print(f"Avg reward: {summary.get('avg_reward', 0.0):.3f}")
    
    return loop.metrics


def run_oversight_experiment(cycles: int,
                           max_puzzles_per_cycle: int = 2,
                           max_solutions_per_puzzle: int = 1,
                           use_config: bool = True) -> MetricsCollector:
    """Run oversight experiment with referee"""
    print("\n" + "=" * 60)
    print("RUNNING OVERSIGHT EXPERIMENT (With Referee)")
    print("=" * 60)
    
    # Initialize deduction loop with referee
    loop = DeductionLoop(
        enable_referee=True,
        max_puzzles_per_cycle=max_puzzles_per_cycle,
        max_solutions_per_puzzle=max_solutions_per_puzzle
    )
    
    # Set up config puzzles if requested
    if use_config:
        config_puzzles = load_config_puzzles()
        if config_puzzles:
            loop._use_config_puzzles = True
            loop._config_puzzles = config_puzzles
            loop._config_puzzle_index = 0
    
    # Run cycles
    for cycle in range(1, cycles + 1):
        print(f"\n--- Cycle {cycle}/{cycles} ---")
        metrics = loop.run_cycle()
        
        # Print cycle summary with correct keys
        print(f"Puzzles: {metrics.get('new_puzzles', 0)} generated, "
              f"{metrics.get('approved_puzzles', 0)} approved")
        print(f"Solutions: {metrics.get('new_solutions', 0)} generated, "
              f"{metrics.get('correct_solutions', 0)} correct")
        print(f"Avg reward: {metrics.get('avg_reward', 0.0):.3f}")
        print(f"Duration: {metrics.get('cycle_duration', 0.0):.2f}s")
    
    # Get final summary
    summary = loop.get_summary_stats()
    print(f"\nOVERSIGHT SUMMARY:")
    print(f"Total cycles: {summary.get('cycle_number', 0)}")
    print(f"Approval rate: {summary.get('approval_rate', 0.0):.2%}")
    print(f"Success rate: {summary.get('accuracy', 0.0):.2%}")
    print(f"Avg reward: {summary.get('avg_reward', 0.0):.3f}")
    
    return loop.metrics


def load_config_puzzles() -> List[Dict]:
    """Load hard-coded puzzle triplets from config file"""
    config_path = "configs/deduction_mini.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('puzzles', [])
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found, using dynamic generation")
        return []


def generate_comparison_report(baseline_metrics: MetricsCollector, 
                             oversight_metrics: MetricsCollector) -> str:
    """Generate comparison report between baseline and oversight runs"""
    print("\n" + "=" * 60)
    print("GENERATING COMPARISON REPORT")
    print("=" * 60)
    
    analyzer = ComparisonAnalyzer()
    analyzer.set_baseline(baseline_metrics)
    analyzer.set_oversight(oversight_metrics)
    
    report = analyzer.generate_report()
    print(report)
    
    return report


def save_results(baseline_metrics: MetricsCollector, 
                oversight_metrics: MetricsCollector, 
                comparison_report: str,
                output_dir: str = "results"):
    """Save all results to files"""
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)
    
    # Create results directory
    results_dir = Path(output_dir)
    results_dir.mkdir(exist_ok=True)
    
    # Save baseline metrics
    baseline_metrics.export_to_json(results_dir / "baseline_metrics.json")
    baseline_metrics.export_to_csv(results_dir / "baseline_demo.csv")
    print("✓ Saved baseline metrics")
    
    # Save oversight metrics
    oversight_metrics.export_to_json(results_dir / "oversight_metrics.json")
    oversight_metrics.export_to_csv(results_dir / "oversight_demo.csv")
    print("✓ Saved oversight metrics")
    
    # Save comparison report
    with open(results_dir / "comparison_report.txt", "w") as f:
        f.write(comparison_report)
    print("✓ Saved comparison report")
    
    # Save combined results
    combined_data = {
        'baseline': baseline_metrics.get_summary().__dict__,
        'oversight': oversight_metrics.get_summary().__dict__,
        'comparison': ComparisonAnalyzer().compare_runs()
    }
    
    with open(results_dir / "combined_results.json", "w") as f:
        json.dump(combined_data, f, indent=2)
    print("✓ Saved combined results")


def create_plots(baseline_metrics: MetricsCollector, 
                oversight_metrics: MetricsCollector,
                output_dir: str = "results"):
    """Create learning curve plots"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        print("\n" + "=" * 60)
        print("GENERATING PLOTS")
        print("=" * 60)
        
        # Get learning curve data
        baseline_curve = baseline_metrics.get_learning_curve()
        oversight_curve = oversight_metrics.get_learning_curve()
        
        if not baseline_curve or not oversight_curve:
            print("No learning curve data available")
            return
        
        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Oversight Curriculum Learning Curves', fontsize=16)
        
        # Plot 1: Rewards over time
        axes[0, 0].plot(baseline_curve['cycles'], baseline_curve['rewards'], 
                       label='Baseline', marker='o')
        axes[0, 0].plot(oversight_curve['cycles'], oversight_curve['rewards'], 
                       label='Oversight', marker='s')
        axes[0, 0].set_title('Average Solution Reward')
        axes[0, 0].set_xlabel('Cycle')
        axes[0, 0].set_ylabel('Reward')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot 2: Safety scores over time
        axes[0, 1].plot(baseline_curve['cycles'], baseline_curve['safety_scores'], 
                       label='Baseline', marker='o')
        axes[0, 1].plot(oversight_curve['cycles'], oversight_curve['safety_scores'], 
                       label='Oversight', marker='s')
        axes[0, 1].set_title('Average Puzzle Safety')
        axes[0, 1].set_xlabel('Cycle')
        axes[0, 1].set_ylabel('Safety Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot 3: Approval rates over time
        axes[1, 0].plot(baseline_curve['cycles'], baseline_curve['approval_rates'], 
                       label='Baseline', marker='o')
        axes[1, 0].plot(oversight_curve['cycles'], oversight_curve['approval_rates'], 
                       label='Oversight', marker='s')
        axes[1, 0].set_title('Puzzle Approval Rate')
        axes[1, 0].set_xlabel('Cycle')
        axes[1, 0].set_ylabel('Approval Rate')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Plot 4: Success rates over time
        axes[1, 1].plot(baseline_curve['cycles'], baseline_curve['success_rates'], 
                       label='Baseline', marker='o')
        axes[1, 1].plot(oversight_curve['cycles'], oversight_curve['success_rates'], 
                       label='Oversight', marker='s')
        axes[1, 1].set_title('Solution Success Rate')
        axes[1, 1].set_xlabel('Cycle')
        axes[1, 1].set_ylabel('Success Rate')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        # Save plot
        results_dir = Path(output_dir)
        results_dir.mkdir(exist_ok=True)
        plt.savefig(results_dir / "learning_curves.png", dpi=300, bbox_inches='tight')
        print("✓ Saved learning curves plot")
        
    except ImportError:
        print("Matplotlib not available, skipping plots")
    except Exception as e:
        print(f"Error creating plots: {e}")


def main():
    """Main demo function using robust runner"""
    args = parse_args()
    
    # Create and run robust demo runner
    runner = RobustDemoRunner(args)
    success = runner.run()
    
    if success:
        print(f"\n{Colors.GREEN}🎉 Demo completed successfully!{Colors.NC}")
        print(f"\n{Colors.BLUE}📊 Results saved in the '{args.output_dir}/' directory:{Colors.NC}")
        print("  - baseline_metrics.json")
        print("  - oversight_metrics.json") 
        print("  - comparison_report.txt")
        print("  - learning_curves.png")
        print("  - combined_results.json")
        print(f"\n{Colors.BLUE}📖 View the comparison report:{Colors.NC}")
        print(f"  cat {args.output_dir}/comparison_report.txt")
        
        # Check if execution time meets plan requirements
        duration = time.time() - runner.start_time
        if duration <= 15.0:
            print(f"\n{Colors.GREEN}✅ Execution time {duration:.2f}s ≤15s - meets plan requirements!{Colors.NC}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Execution time {duration:.2f}s > 15s - consider reducing cycles/puzzles{Colors.NC}")
    else:
        print(f"\n{Colors.RED}❌ Demo failed{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    main() 