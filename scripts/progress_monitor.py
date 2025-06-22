#!/usr/bin/env python3
"""
Progress Monitor for Oversight Curriculum
Comprehensive monitoring of all objective progress signals
"""

import json
import time
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback


@dataclass
class ProgressSignal:
    """A progress signal result"""
    signal_type: str
    status: str  # "pass", "fail", "warning", "info"
    value: Any
    message: str
    timestamp: str
    details: Dict[str, Any] = None


class ProgressMonitor:
    """Comprehensive progress monitoring system"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.parent
        self.signals: List[ProgressSignal] = []
        self.start_time = time.time()
        
        # Create output directories
        self.results_dir = self.script_dir / "results" / "progress"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{level}] [{timestamp}] {message}")
    
    def add_signal(self, signal_type: str, status: str, value: Any, 
                   message: str, details: Dict[str, Any] = None):
        """Add a progress signal"""
        signal = ProgressSignal(
            signal_type=signal_type,
            status=status,
            value=value,
            message=message,
            timestamp=datetime.now().isoformat(),
            details=details or {}
        )
        self.signals.append(signal)
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests"""
        self.log("Running smoke tests...")
        
        try:
            smoke_script = self.script_dir / "scripts" / "smoke_test.py"
            if not smoke_script.exists():
                self.add_signal("smoke_tests", "fail", False, 
                              "Smoke test script not found")
                return {"success": False, "error": "Script not found"}
            
            result = subprocess.run(
                [sys.executable, str(smoke_script)],
                capture_output=True, text=True, cwd=self.script_dir
            )
            
            if result.returncode == 0:
                self.add_signal("smoke_tests", "pass", True, 
                              "All smoke tests passed")
                return {"success": True, "output": result.stdout}
            else:
                self.add_signal("smoke_tests", "fail", False, 
                              f"Smoke tests failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.add_signal("smoke_tests", "fail", False, 
                          f"Error running smoke tests: {e}")
            return {"success": False, "error": str(e)}
    
    def run_nightly_benchmarks(self) -> Dict[str, Any]:
        """Run nightly benchmarks"""
        self.log("Running nightly benchmarks...")
        
        try:
            benchmark_script = self.script_dir / "scripts" / "nightly_benchmark.py"
            if not benchmark_script.exists():
                self.add_signal("nightly_benchmarks", "fail", False, 
                              "Benchmark script not found")
                return {"success": False, "error": "Script not found"}
            
            result = subprocess.run(
                [sys.executable, str(benchmark_script)],
                capture_output=True, text=True, cwd=self.script_dir
            )
            
            if result.returncode == 0:
                self.add_signal("nightly_benchmarks", "pass", True, 
                              "Benchmarks completed successfully")
                return {"success": True, "output": result.stdout}
            else:
                self.add_signal("nightly_benchmarks", "fail", False, 
                              f"Benchmarks failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.add_signal("nightly_benchmarks", "fail", False, 
                          f"Error running benchmarks: {e}")
            return {"success": False, "error": str(e)}
    
    def check_safety_dashboard(self) -> Dict[str, Any]:
        """Check safety dashboard status"""
        self.log("Checking safety dashboard...")
        
        try:
            safety_script = self.script_dir / "scripts" / "safety_dashboard.py"
            if not safety_script.exists():
                self.add_signal("safety_dashboard", "fail", False, 
                              "Safety dashboard script not found")
                return {"success": False, "error": "Script not found"}
            
            # Run safety test suite
            result = subprocess.run(
                [sys.executable, str(safety_script), "--test"],
                capture_output=True, text=True, cwd=self.script_dir
            )
            
            if result.returncode == 0:
                self.add_signal("safety_dashboard", "pass", True, 
                              "Safety tests passed")
                return {"success": True, "output": result.stdout}
            else:
                self.add_signal("safety_dashboard", "fail", False, 
                              f"Safety tests failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.add_signal("safety_dashboard", "fail", False, 
                          f"Error checking safety: {e}")
            return {"success": False, "error": str(e)}
    
    def check_cost_meter(self) -> Dict[str, Any]:
        """Check cost meter status"""
        self.log("Checking cost meter...")
        
        try:
            cost_script = self.script_dir / "cost_watch.py"
            if not cost_script.exists():
                self.add_signal("cost_meter", "warning", None, 
                              "Cost watch script not found")
                return {"success": False, "error": "Script not found"}
            
            # Check if cost tracking is active
            cost_log = self.script_dir / "cost.log"
            if cost_log.exists():
                # Read last few lines to check status
                with open(cost_log, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        self.add_signal("cost_meter", "info", last_line, 
                                      "Cost tracking active")
                        return {"success": True, "last_entry": last_line}
            
            self.add_signal("cost_meter", "warning", None, 
                          "Cost tracking not active")
            return {"success": False, "error": "No cost tracking data"}
            
        except Exception as e:
            self.add_signal("cost_meter", "fail", False, 
                          f"Error checking cost meter: {e}")
            return {"success": False, "error": str(e)}
    
    def check_changelog(self) -> Dict[str, Any]:
        """Check changelog status"""
        self.log("Checking changelog...")
        
        try:
            changelog_script = self.script_dir / "scripts" / "changelog_tracker.py"
            if not changelog_script.exists():
                self.add_signal("changelog", "warning", None, 
                              "Changelog script not found")
                return {"success": False, "error": "Script not found"}
            
            # Check for recent changes
            result = subprocess.run(
                [sys.executable, str(changelog_script), "--check"],
                capture_output=True, text=True, cwd=self.script_dir
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if "Changes detected" in output:
                    self.add_signal("changelog", "info", True, 
                                  "Changes detected - changelog updated")
                else:
                    self.add_signal("changelog", "info", False, 
                                  "No changes detected")
                return {"success": True, "output": output}
            else:
                self.add_signal("changelog", "fail", False, 
                              f"Changelog check failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.add_signal("changelog", "fail", False, 
                          f"Error checking changelog: {e}")
            return {"success": False, "error": str(e)}
    
    def check_blockers(self) -> Dict[str, Any]:
        """Check blocker status"""
        self.log("Checking blockers...")
        
        try:
            blocker_script = self.script_dir / "scripts" / "blocker_tracker.py"
            if not blocker_script.exists():
                self.add_signal("blockers", "warning", None, 
                              "Blocker script not found")
                return {"success": False, "error": "Script not found"}
            
            # Get blocker summary
            result = subprocess.run(
                [sys.executable, str(blocker_script), "--summary"],
                capture_output=True, text=True, cwd=self.script_dir
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                
                # Check for critical blockers
                if "CRITICAL BLOCKERS:" in output:
                    self.add_signal("blockers", "fail", False, 
                                  "Critical blockers detected")
                elif "ACTIVE BLOCKERS:" in output:
                    self.add_signal("blockers", "warning", True, 
                                  "Active blockers present")
                else:
                    self.add_signal("blockers", "pass", True, 
                                  "No active blockers")
                
                return {"success": True, "output": output}
            else:
                self.add_signal("blockers", "fail", False, 
                              f"Blocker check failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.add_signal("blockers", "fail", False, 
                          f"Error checking blockers: {e}")
            return {"success": False, "error": str(e)}
    
    def check_unit_tests(self) -> Dict[str, Any]:
        """Check unit test status"""
        self.log("Checking unit tests...")
        
        try:
            test_dir = self.script_dir / "tests"
            if not test_dir.exists():
                self.add_signal("unit_tests", "warning", None, 
                              "Tests directory not found")
                return {"success": False, "error": "Tests directory not found"}
            
            # Run pytest
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_dir), "-v"],
                capture_output=True, text=True, cwd=self.script_dir
            )
            
            if result.returncode == 0:
                self.add_signal("unit_tests", "pass", True, 
                              "All unit tests passed")
                return {"success": True, "output": result.stdout}
            else:
                self.add_signal("unit_tests", "fail", False, 
                              f"Unit tests failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.add_signal("unit_tests", "fail", False, 
                          f"Error running unit tests: {e}")
            return {"success": False, "error": str(e)}
    
    def check_coverage(self) -> Dict[str, Any]:
        """Check code coverage"""
        self.log("Checking code coverage...")
        
        try:
            # Check if coverage files exist
            coverage_dir = self.script_dir / "htmlcov"
            if coverage_dir.exists():
                # Look for coverage report
                index_file = coverage_dir / "index.html"
                if index_file.exists():
                    self.add_signal("coverage", "info", True, 
                                  "Coverage report available")
                    return {"success": True, "report_available": True}
            
            self.add_signal("coverage", "warning", None, 
                          "No coverage report found")
            return {"success": False, "error": "No coverage data"}
            
        except Exception as e:
            self.add_signal("coverage", "fail", False, 
                          f"Error checking coverage: {e}")
            return {"success": False, "error": str(e)}
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all progress checks"""
        self.log("🚀 Starting comprehensive progress monitoring")
        
        checks = [
            ("smoke_tests", self.run_smoke_tests),
            ("nightly_benchmarks", self.run_nightly_benchmarks),
            ("safety_dashboard", self.check_safety_dashboard),
            ("cost_meter", self.check_cost_meter),
            ("changelog", self.check_changelog),
            ("blockers", self.check_blockers),
            ("unit_tests", self.check_unit_tests),
            ("coverage", self.check_coverage)
        ]
        
        results = {}
        for check_name, check_func in checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                self.add_signal(check_name, "fail", False, f"Error: {e}")
                results[check_name] = {"success": False, "error": str(e)}
        
        # Generate summary
        total_checks = len(self.signals)
        passed_checks = sum(1 for s in self.signals if s.status == "pass")
        failed_checks = sum(1 for s in self.signals if s.status == "fail")
        warning_checks = sum(1 for s in self.signals if s.status == "warning")
        
        summary = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "warning_checks": warning_checks,
            "success_rate": passed_checks / total_checks if total_checks > 0 else 0,
            "overall_status": "pass" if failed_checks == 0 else "fail",
            "duration": time.time() - self.start_time,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log(f"📊 Progress Monitoring Summary:")
        self.log(f"   Total checks: {total_checks}")
        self.log(f"   Passed: {passed_checks}")
        self.log(f"   Failed: {failed_checks}")
        self.log(f"   Warnings: {warning_checks}")
        self.log(f"   Success rate: {summary['success_rate']:.1%}")
        self.log(f"   Duration: {summary['duration']:.2f}s")
        
        return {
            "summary": summary,
            "results": results,
            "signals": [asdict(signal) for signal in self.signals]
        }
    
    def save_report(self, output_file: Optional[Path] = None):
        """Save progress report"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.results_dir / f"progress_report_{timestamp}.json"
        
        report = self.run_all_checks()
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.log(f"Progress report saved to {output_file}")
            return output_file
        except Exception as e:
            self.log(f"Error saving report: {e}", "ERROR")
            return None
    
    def print_dashboard(self):
        """Print progress dashboard"""
        report = self.run_all_checks()
        summary = report["summary"]
        signals = report["signals"]
        
        print(f"\n📊 PROGRESS MONITORING DASHBOARD")
        print("=" * 60)
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Duration: {summary['duration']:.2f}s")
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        
        print(f"\n📋 SIGNAL BREAKDOWN:")
        print("-" * 40)
        
        for signal in signals:
            status_icon = {
                "pass": "✅",
                "fail": "❌", 
                "warning": "⚠️",
                "info": "ℹ️"
            }.get(signal["status"], "❓")
            
            print(f"{status_icon} {signal['signal_type']}: {signal['message']}")
        
        print(f"\n📈 SUMMARY:")
        print("-" * 40)
        print(f"Total checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed_checks']}")
        print(f"Failed: {summary['failed_checks']}")
        print(f"Warnings: {summary['warning_checks']}")
        
        if summary['failed_checks'] > 0:
            print(f"\n🚨 FAILED CHECKS:")
            for signal in signals:
                if signal["status"] == "fail":
                    print(f"  - {signal['signal_type']}: {signal['message']}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Progress monitoring dashboard")
    parser.add_argument("--dashboard", "-d", action="store_true", 
                       help="Print dashboard")
    parser.add_argument("--report", "-r", action="store_true", 
                       help="Generate report")
    parser.add_argument("--output", "-o", help="Output file for report")
    
    args = parser.parse_args()
    
    monitor = ProgressMonitor()
    
    try:
        if args.dashboard:
            # Print dashboard
            monitor.print_dashboard()
        
        elif args.report:
            # Generate report
            if args.output:
                output_file = Path(args.output)
            else:
                output_file = None
            
            monitor.save_report(output_file)
        
        else:
            # Default: print dashboard
            monitor.print_dashboard()
    
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 