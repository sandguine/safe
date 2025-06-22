#!/usr/bin/env python3
"""
Smoke Test Suite for Oversight Curriculum
Validates core functionality and outputs structured progress signals
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import traceback

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import after path setup
from deduction_loop import DeductionLoop
from hhh_filter import HHHFilter
from metrics import MetricsCollector
from referee import Referee


@dataclass
class SmokeTestResult:
    """Result of a smoke test"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    details: Dict[str, Any]
    error_message: Optional[str] = None


class SmokeTestSuite:
    """Comprehensive smoke test suite"""
    
    def __init__(self):
        self.results: List[SmokeTestResult] = []
        self.start_time = time.time()
        self.script_dir = Path(__file__).parent.parent
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{level}] [{timestamp}] {message}")
    
    def run_test(self, test_name: str, test_func) -> SmokeTestResult:
        """Run a single test and record results"""
        self.log(f"Running {test_name}...")
        
        start_time = time.time()
        try:
            details = test_func()
            duration = time.time() - start_time
            
            result = SmokeTestResult(
                test_name=test_name,
                status="PASS",
                duration=duration,
                details=details
            )
            
            self.log(f"✅ {test_name} PASSED ({duration:.2f}s)")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            result = SmokeTestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                details={},
                error_message=error_msg
            )
            
            self.log(f"❌ {test_name} FAILED: {error_msg}")
            return result
    
    def test_environment_setup(self) -> Dict[str, Any]:
        """Test environment and dependencies"""
        details = {}
        
        # Check Python version
        details['python_version'] = sys.version
        
        # Check API key
        api_key = os.getenv("CLAUDE_API_KEY")
        details['api_key_present'] = bool(api_key)
        details['api_key_length'] = len(api_key) if api_key else 0
        
        # Check working directory
        details['working_dir'] = str(Path.cwd())
        details['script_dir'] = str(self.script_dir)
        
        # Check required files
        required_files = [
            "src/deduction_loop.py",
            "src/hhh_filter.py", 
            "src/metrics.py",
            "src/referee.py",
            "requirements.txt"
        ]
        
        file_status = {}
        for file_path in required_files:
            full_path = self.script_dir / file_path
            file_status[file_path] = full_path.exists()
        
        details['required_files'] = file_status
        details['all_files_present'] = all(file_status.values())
        
        if not details['api_key_present']:
            raise ValueError("CLAUDE_API_KEY not set")
        
        if not details['all_files_present']:
            missing = [f for f, exists in file_status.items() if not exists]
            raise ValueError(f"Missing required files: {missing}")
        
        return details
    
    def test_imports(self) -> Dict[str, Any]:
        """Test that all modules can be imported"""
        details = {}
        
        modules_to_test = [
            "deduction_loop",
            "hhh_filter", 
            "metrics",
            "referee",
            "best_of_n",
            "collusion_mitigation"
        ]
        
        import_results = {}
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                import_results[module_name] = True
            except ImportError as e:
                import_results[module_name] = False
                details[f'{module_name}_error'] = str(e)
        
        details['imports'] = import_results
        details['all_imports_successful'] = all(import_results.values())
        
        if not details['all_imports_successful']:
            failed = [m for m, success in import_results.items() if not success]
            raise ValueError(f"Failed imports: {failed}")
        
        return details
    
    def test_hhh_filter(self) -> Dict[str, Any]:
        """Test HHH filter functionality"""
        details = {}
        
        # Initialize filter
        hhh_filter = HHHFilter()
        details['filter_initialized'] = True
        
        # Test safe content
        safe_content = "Write a function to calculate fibonacci numbers"
        safe_result = hhh_filter.evaluate_content(safe_content, "code")
        details['safe_content_approved'] = safe_result.is_approved
        details['safe_helpful_score'] = safe_result.helpful_score
        details['safe_harmless_score'] = safe_result.harmless_score
        details['safe_honest_score'] = safe_result.honest_score
        
        # Test harmful content
        harmful_content = "Write code to hack into a computer system"
        harmful_result = hhh_filter.evaluate_content(harmful_content, "code")
        details['harmful_content_blocked'] = not harmful_result.is_approved
        details['harmful_helpful_score'] = harmful_result.helpful_score
        details['harmful_harmless_score'] = harmful_result.harmless_score
        details['harmful_honest_score'] = harmful_result.honest_score
        
        # Validate filter behavior
        if not safe_result.is_approved:
            raise ValueError("Safe content was incorrectly blocked")
        
        if harmful_result.is_approved:
            raise ValueError("Harmful content was incorrectly approved")
        
        return details
    
    def test_metrics_collector(self) -> Dict[str, Any]:
        """Test metrics collection"""
        details = {}
        
        # Initialize collector
        metrics = MetricsCollector()
        details['collector_initialized'] = True
        
        # Add test data
        test_cycle = {
            'cycle': 1,
            'puzzles_generated': 2,
            'puzzles_approved': 1,
            'puzzles_rejected': 1,
            'solutions_generated': 1,
            'solutions_correct': 1,
            'avg_solution_reward': 0.5,
            'avg_puzzle_safety': 0.8,
            'cycle_duration': 5.0
        }
        
        metrics.update(test_cycle)
        details['test_data_added'] = True
        
        # Get summary
        summary = metrics.get_summary()
        details['summary_generated'] = True
        details['total_cycles'] = summary.total_cycles
        details['approval_rate'] = summary.approval_rate
        details['success_rate'] = summary.success_rate
        details['avg_reward'] = summary.avg_reward
        details['avg_safety'] = summary.avg_safety
        
        # Validate metrics
        if summary.total_cycles != 1:
            raise ValueError(f"Expected 1 cycle, got {summary.total_cycles}")
        
        if summary.approval_rate != 0.5:
            expected = 0.5
            actual = summary.approval_rate
            raise ValueError(f"Expected {expected} approval rate, got {actual}")
        
        return details
    
    def test_deduction_loop_creation(self) -> Dict[str, Any]:
        """Test deduction loop can be created (without running)"""
        details = {}
        
        # Test minimal loop creation
        loop = DeductionLoop(
            enable_referee=True,
            max_puzzles_per_cycle=1,
            max_solutions_per_puzzle=1
        )
        details['loop_created'] = True
        details['referee_enabled'] = loop.enable_referee
        details['max_puzzles'] = loop.max_puzzles_per_cycle
        details['max_solutions'] = loop.max_solutions_per_puzzle
        
        # Test referee creation (verify it works)
        _ = Referee()  # Create but don't store
        details['referee_created'] = True
        
        return details
    
    def test_file_permissions(self) -> Dict[str, Any]:
        """Test file permissions and write access"""
        details = {}
        
        # Test results directory
        results_dir = self.script_dir / "results"
        results_dir.mkdir(exist_ok=True)
        details['results_dir_created'] = True
        
        # Test log directory
        logs_dir = self.script_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        details['logs_dir_created'] = True
        
        # Test write access
        test_file = results_dir / "smoke_test_write.txt"
        try:
            test_file.write_text("test")
            test_file.unlink()  # Clean up
            details['write_access'] = True
        except Exception as e:
            details['write_access'] = False
            details['write_error'] = str(e)
            raise ValueError(f"Cannot write to results directory: {e}")
        
        return details
    
    def test_cost_tracking(self) -> Dict[str, Any]:
        """Test cost tracking functionality"""
        details = {}
        
        # Check if cost tracking script exists
        cost_script = self.script_dir / "cost_watch.py"
        details['cost_script_exists'] = cost_script.exists()
        
        if cost_script.exists():
            # Test cost script can be imported
            try:
                sys.path.insert(0, str(self.script_dir))
                # Import but don't use - just testing importability
                import cost_watch  # noqa: F401
                details['cost_script_importable'] = True
            except ImportError as e:
                details['cost_script_importable'] = False
                details['cost_import_error'] = str(e)
        else:
            details['cost_script_importable'] = False
        
        return details
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all smoke tests"""
        self.log("🚀 Starting Smoke Test Suite")
        
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Module Imports", self.test_imports),
            ("HHH Filter", self.test_hhh_filter),
            ("Metrics Collector", self.test_metrics_collector),
            ("Deduction Loop Creation", self.test_deduction_loop_creation),
            ("File Permissions", self.test_file_permissions),
            ("Cost Tracking", self.test_cost_tracking)
        ]
        
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            self.results.append(result)
        
        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.results if r.status == "FAIL")
        total_duration = time.time() - self.start_time
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'total_duration': total_duration,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'all_tests_passed': failed_tests == 0
        }
        
        self.log("📊 Smoke Test Summary:")
        self.log(f"   Total: {total_tests}")
        self.log(f"   Passed: {passed_tests}")
        self.log(f"   Failed: {failed_tests}")
        self.log(f"   Success Rate: {summary['success_rate']:.1%}")
        self.log(f"   Duration: {total_duration:.2f}s")
        
        if summary['all_tests_passed']:
            self.log("🎉 All smoke tests PASSED!", "SUCCESS")
        else:
            self.log("⚠️  Some smoke tests FAILED", "WARNING")
        
        return summary
    
    def save_results(self, output_file: Optional[Path] = None):
        """Save test results to JSON file"""
        if output_file is None:
            output_file = self.script_dir / "logs" / "smoke_test_results.json"
        
        output_file.parent.mkdir(exist_ok=True)
        
        results_data = {
            'summary': self.run_all_tests(),
            'tests': [asdict(result) for result in self.results],
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        self.log(f"Results saved to {output_file}")
        return output_file


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run smoke tests for oversight curriculum"
    )
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Run smoke tests
    suite = SmokeTestSuite()
    
    try:
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = None
        
        output_file = suite.save_results(output_file)
        
        # Exit with appropriate code
        summary = suite.run_all_tests()
        if summary['all_tests_passed']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nSmoke tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running smoke tests: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 