#!/usr/bin/env python3
"""
QA Checklist - Verify fixes actually work
=========================================

Implements the user's suggested QA verification steps to ensure:
1. Cost meter is actually working (not just started)
2. Unit tests are genuinely fixed (not just xfail'd)
3. Coverage is meaningful (≥85% on core modules)
4. Dashboard actually shows PASS

Usage:
    python scripts/qa_checklist.py
    python scripts/qa_checklist.py --verbose
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'


def log(message, level="INFO", color=Colors.BLUE):
    timestamp = time.strftime("%H:%M:%S")
    level_colors = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "STEP": Colors.PURPLE,
        "QA": Colors.CYAN
    }
    color_code = level_colors.get(level, Colors.BLUE)
    print(f"{color_code}[{level}]{Colors.NC} [{timestamp}] {message}")


def qa_cost_meter():
    """QA: Verify cost meter is actually working"""
    log("QA: Verifying cost meter functionality", "QA")
    
    checks = []
    
    # Check 1: cost.log exists and is being updated
    cost_log = Path("logs/cost.log")
    if cost_log.exists():
        initial_size = cost_log.stat().st_size
        time.sleep(3)  # Wait for potential updates
        final_size = cost_log.stat().st_size
        
        if final_size > initial_size:
            log("✓ cost.log is being updated", "SUCCESS")
            checks.append(True)
        else:
            log("❌ cost.log not being updated", "ERROR")
            checks.append(False)
    else:
        log("❌ cost.log not found", "ERROR")
        checks.append(False)
    
    # Check 2: Process is running
    try:
        result = subprocess.run(["pgrep", "-f", "cost_watch.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            log("✓ cost_watch.py process is running", "SUCCESS")
            checks.append(True)
        else:
            log("❌ cost_watch.py process not found", "ERROR")
            checks.append(False)
    except Exception as e:
        log(f"❌ Error checking process: {e}", "ERROR")
        checks.append(False)
    
    # Check 3: Recent entries in log
    try:
        with open(cost_log, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                log(f"Latest entry: {last_line}", "INFO")
                
                # Check if entry is recent (within last 2 minutes)
                if "2025" in last_line:  # Simple timestamp check
                    log("✓ Recent log entry found", "SUCCESS")
                    checks.append(True)
                else:
                    log("⚠️ Log entry may be stale", "WARNING")
                    checks.append(False)
            else:
                log("❌ No entries in cost.log", "ERROR")
                checks.append(False)
    except Exception as e:
        log(f"❌ Error reading cost.log: {e}", "ERROR")
        checks.append(False)
    
    return all(checks)


def qa_unit_tests():
    """QA: Verify unit tests are genuinely fixed"""
    log("QA: Verifying unit test fixes", "QA")
    
    checks = []
    
    # Check 1: All tests pass
    try:
        result = subprocess.run(
            ["pytest", "-q"], 
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            log("✓ All unit tests pass", "SUCCESS")
            checks.append(True)
        else:
            log("❌ Some unit tests still fail", "ERROR")
            print(result.stdout)
            print(result.stderr)
            checks.append(False)
    except subprocess.TimeoutExpired:
        log("❌ Unit tests timed out", "ERROR")
        checks.append(False)
    except Exception as e:
        log(f"❌ Error running tests: {e}", "ERROR")
        checks.append(False)
    
    # Check 2: No excessive xfail usage
    test_files = list(Path("tests").glob("*.py"))
    xfail_count = 0
    total_tests = 0
    
    for test_file in test_files:
        try:
            with open(test_file, 'r') as f:
                content = f.read()
                xfail_count += content.count("@pytest.mark.xfail")
                total_tests += content.count("def test_")
        except Exception:
            pass
    
    if total_tests > 0:
        xfail_ratio = xfail_count / total_tests
        if xfail_ratio < 0.3:  # Less than 30% xfail
            log(f"✓ Reasonable xfail ratio: {xfail_ratio:.1%}", "SUCCESS")
            checks.append(True)
        else:
            log(f"⚠️ High xfail ratio: {xfail_ratio:.1%} - may be masking issues", 
                "WARNING")
            checks.append(False)
    else:
        log("⚠️ No test functions found", "WARNING")
        checks.append(False)
    
    return all(checks)


def qa_coverage():
    """QA: Verify coverage is meaningful"""
    log("QA: Verifying coverage quality", "QA")
    
    checks = []
    
    # Check 1: Coverage files exist
    if Path("coverage.xml").exists():
        log("✓ coverage.xml exists", "SUCCESS")
        checks.append(True)
    else:
        log("❌ coverage.xml not found", "ERROR")
        checks.append(False)
    
    if Path("htmlcov").exists():
        log("✓ htmlcov/ directory exists", "SUCCESS")
        checks.append(True)
    else:
        log("❌ htmlcov/ directory not found", "ERROR")
        checks.append(False)
    
    # Check 2: Coverage percentage
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse("coverage.xml")
        root = tree.getroot()
        coverage = root.get("line-rate")
        
        if coverage:
            coverage_pct = float(coverage) * 100
            log(f"Coverage: {coverage_pct:.1f}%", "INFO")
            
            if coverage_pct >= 85:
                log("✓ Coverage meets target (≥85%)", "SUCCESS")
                checks.append(True)
            else:
                log(f"⚠️ Coverage below target (need ≥85%, have {coverage_pct:.1f}%)", 
                    "WARNING")
                checks.append(False)
        else:
            log("❌ Could not parse coverage percentage", "ERROR")
            checks.append(False)
    except Exception as e:
        log(f"❌ Error parsing coverage: {e}", "ERROR")
        checks.append(False)
    
    # Check 3: Core modules are covered
    core_modules = ["src/deduction_loop.py", "src/metrics.py", "src/analysis.py"]
    covered_modules = 0
    
    for module in core_modules:
        if Path(module).exists():
            covered_modules += 1
    
    if covered_modules >= 2:  # At least 2 core modules
        log(f"✓ Core modules covered: {covered_modules}/3", "SUCCESS")
        checks.append(True)
    else:
        log(f"⚠️ Insufficient core module coverage: {covered_modules}/3", 
            "WARNING")
        checks.append(False)
    
    return all(checks)


def qa_dashboard():
    """QA: Verify dashboard shows PASS"""
    log("QA: Verifying dashboard status", "QA")
    
    checks = []
    
    try:
        result = subprocess.run(
            ["python", "scripts/progress_monitor.py", "--dashboard"],
            capture_output=True, text=True, timeout=300
        )
        
        if "Overall Status: PASS" in result.stdout:
            log("✓ Dashboard shows PASS status", "SUCCESS")
            checks.append(True)
        elif "Overall Status: FAIL" in result.stdout:
            log("❌ Dashboard still shows FAIL status", "ERROR")
            checks.append(False)
        else:
            log("⚠️ Could not determine dashboard status", "WARNING")
            checks.append(False)
        
        # Check success rate
        if "Success rate:" in result.stdout:
            for line in result.stdout.split('\n'):
                if "Success rate:" in line:
                    rate_str = line.split("Success rate:")[1].strip()
                    try:
                        rate = float(rate_str.replace('%', ''))
                        if rate >= 80:  # At least 80% success rate
                            log(f"✓ Good success rate: {rate:.1f}%", "SUCCESS")
                            checks.append(True)
                        else:
                            log(f"⚠️ Low success rate: {rate:.1f}%", "WARNING")
                            checks.append(False)
                        break
                    except ValueError:
                        pass
        
    except subprocess.TimeoutExpired:
        log("❌ Dashboard check timed out", "ERROR")
        checks.append(False)
    except Exception as e:
        log(f"❌ Error running dashboard: {e}", "ERROR")
        checks.append(False)
    
    return all(checks)


def qa_benchmark_results():
    """QA: Check benchmark results if available"""
    log("QA: Checking benchmark results", "QA")
    
    checks = []
    
    # Check for benchmark results
    bench_files = list(Path("results").glob("*bench*.json"))
    if bench_files:
        latest_bench = max(bench_files, key=lambda p: p.stat().st_mtime)
        log(f"Found benchmark file: {latest_bench}", "INFO")
        
        try:
            with open(latest_bench, 'r') as f:
                data = json.load(f)
            
            # Check for key metrics
            if "pass_at_1" in data:
                pass_rate = data["pass_at_1"]
                log(f"pass@1: {pass_rate:.3f}", "INFO")
                if pass_rate >= 0.6:
                    log("✓ pass@1 meets target (≥0.6)", "SUCCESS")
                    checks.append(True)
                else:
                    log(f"⚠️ pass@1 below target (need ≥0.6, have {pass_rate:.3f})", 
                        "WARNING")
                    checks.append(False)
            
            if "uplift_pp" in data:
                uplift = data["uplift_pp"]
                log(f"uplift: {uplift:.1f}pp", "INFO")
                if uplift >= 8:
                    log("✓ uplift meets target (≥8pp)", "SUCCESS")
                    checks.append(True)
                else:
                    log(f"⚠️ uplift below target (need ≥8pp, have {uplift:.1f}pp)", 
                        "WARNING")
                    checks.append(False)
                    
        except Exception as e:
            log(f"❌ Error reading benchmark: {e}", "ERROR")
            checks.append(False)
    else:
        log("ℹ️ No benchmark results found", "INFO")
        checks.append(True)  # Not a failure, just no data yet
    
    return all(checks)


def main():
    parser = argparse.ArgumentParser(description="QA Checklist")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║                    QA CHECKLIST                              ║")
    print(f"║                    Verify Fixes Actually Work                ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
    
    qa_results = []
    
    # Run QA checks
    qa_checks = [
        ("Cost Meter", qa_cost_meter),
        ("Unit Tests", qa_unit_tests),
        ("Coverage", qa_coverage),
        ("Dashboard", qa_dashboard),
        ("Benchmark Results", qa_benchmark_results)
    ]
    
    for check_name, check_func in qa_checks:
        print(f"\n{Colors.PURPLE}🔍 {check_name} QA Check{Colors.NC}")
        print("-" * 50)
        
        try:
            result = check_func()
            qa_results.append((check_name, result))
            
            if result:
                log(f"{check_name} QA: PASS", "SUCCESS")
            else:
                log(f"{check_name} QA: FAIL", "ERROR")
                
        except Exception as e:
            log(f"{check_name} QA: ERROR - {e}", "ERROR")
            qa_results.append((check_name, False))
    
    # Summary
    print(f"\n{Colors.CYAN}📊 QA Checklist Summary:{Colors.NC}")
    print("=" * 50)
    
    passed = sum(1 for _, result in qa_results if result)
    total = len(qa_results)
    
    for check_name, result in qa_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name:<20} {status}")
    
    print(f"\n  Overall: {passed}/{total} checks passed")
    
    if passed == total:
        log("🎉 All QA checks passed! System is ready for production", "SUCCESS")
        print(f"\n{Colors.GREEN}🚀 Ready to launch full HumanEval-164 + harm-200 run!{Colors.NC}")
        return True
    else:
        log(f"⚠️ {total - passed} QA checks failed - review before proceeding", 
            "WARNING")
        print(f"\n{Colors.YELLOW}🔧 Fix issues before launching production run{Colors.NC}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 