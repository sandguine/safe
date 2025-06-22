#!/usr/bin/env python3
"""
Quick Fix Monitor - Addresses specific monitoring issues
=======================================================

This script fixes the three main issues identified:
1. Cost meter not running
2. Unit tests failing
3. Coverage reports missing

Usage:
    python scripts/quick_fix_monitor.py --fix-all
    python scripts/quick_fix_monitor.py --fix-all --dry-run
    python scripts/quick_fix_monitor.py --start-cost
    python scripts/quick_fix_monitor.py --fix-tests
    python scripts/quick_fix_monitor.py --generate-coverage
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
        "DRY_RUN": Colors.CYAN
    }
    color_code = level_colors.get(level, Colors.BLUE)
    print(f"{color_code}[{level}]{Colors.NC} [{timestamp}] {message}")

def check_cost_meter():
    """Check if cost meter is running"""
    try:
        # Check for cost.log file
        cost_log = Path("logs/cost.log")
        if cost_log.exists():
            # Check if it's been updated recently (within last 5 minutes)
            if time.time() - cost_log.stat().st_mtime < 300:
                return True
        
        # Check for running cost_watch.py process
        result = subprocess.run(["pgrep", "-f", "cost_watch.py"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def start_cost_meter(dry_run=False):
    """Start the cost meter in background"""
    if dry_run:
        log("DRY RUN: Would start cost meter with max-cost 110, interval 60s", 
            "DRY_RUN")
        log("DRY RUN: Would create logs/cost.log", "DRY_RUN")
        log("DRY RUN: Would lock PID in tmp/cost.pid", "DRY_RUN")
        return True
    
    log("Starting cost meter...", "STEP")
    
    try:
        # Create directories
        Path("logs").mkdir(exist_ok=True)
        Path("tmp").mkdir(exist_ok=True)
        
        # Check for existing cost watcher and kill if stale
        pid_file = Path("tmp/cost.pid")
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # Check if process is still running
                result = subprocess.run(["kill", "-0", str(old_pid)], 
                                      capture_output=True)
                if result.returncode == 0:
                    log(f"Killing existing cost watcher (PID {old_pid})", "INFO")
                    subprocess.run(["kill", str(old_pid)], capture_output=True)
                    time.sleep(1)
                else:
                    log("Stale PID file found, removing", "INFO")
                
                pid_file.unlink()
            except Exception as e:
                log(f"Error handling existing PID: {e}", "WARNING")
                if pid_file.exists():
                    pid_file.unlink()
        
        # Start cost meter in background
        cmd = [
            "python", "scripts/cost_watch.py", 
            "--max-cost", "110", 
            "--interval", "60",
            "--log-file", "logs/cost.log"
        ]
        
        # Use nohup to keep it running
        process = subprocess.Popen(
            cmd,
            stdout=open("logs/cost_watch.out", "w"),
            stderr=open("logs/cost_watch.err", "w"),
            preexec_fn=os.setsid  # Detach from parent
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        if process.poll() is None:
            # Write PID to file
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            log("Cost meter started successfully", "SUCCESS")
            log(f"PID locked: {process.pid}", "INFO")
            
            # Verify cost.log is being written to
            time.sleep(3)
            if Path("logs/cost.log").exists():
                log("✓ cost.log is being written to", "SUCCESS")
            else:
                log("⚠️ cost.log not found - check cost_watch.py", "WARNING")
            
            return True
        else:
            log("Cost meter failed to start", "ERROR")
            return False
            
    except Exception as e:
        log(f"Error starting cost meter: {e}", "ERROR")
        return False

def verify_cost_meter():
    """Verify cost meter is working properly"""
    log("Verifying cost meter...", "STEP")
    
    try:
        cost_log = Path("logs/cost.log")
        if not cost_log.exists():
            log("❌ cost.log not found", "ERROR")
            return False
        
        # Check if log is being updated
        initial_size = cost_log.stat().st_size
        time.sleep(2)
        final_size = cost_log.stat().st_size
        
        if final_size > initial_size:
            log("✓ cost.log is being updated", "SUCCESS")
            
            # Show last few lines
            with open(cost_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    log(f"Latest entry: {lines[-1].strip()}", "INFO")
            
            return True
        else:
            log("⚠️ cost.log not being updated", "WARNING")
            return False
            
    except Exception as e:
        log(f"Error verifying cost meter: {e}", "ERROR")
        return False

def fix_unit_tests(dry_run=False):
    """Fix or run unit tests"""
    if dry_run:
        log("DRY RUN: Would run pytest -v --tb=short", "DRY_RUN")
        log("DRY RUN: Would analyze failures and suggest fixes", "DRY_RUN")
        return True
    
    log("Checking unit tests...", "STEP")
    
    try:
        # First, try to run tests to see what's failing
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"], 
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            log("All unit tests passed!", "SUCCESS")
            return True
        
        # Tests failed, let's see what's wrong
        log("Unit tests failed. Analyzing failures...", "WARNING")
        print(result.stdout)
        print(result.stderr)
        
        # Check if we have placeholder tests that should be marked xfail
        test_files = list(Path("tests").glob("*.py"))
        if test_files:
            log("Found test files. Consider marking placeholder tests as xfail", 
                "INFO")
            for test_file in test_files:
                log(f"  - {test_file}", "INFO")
                
                # Check if test file contains placeholder content
                try:
                    with open(test_file, 'r') as f:
                        content = f.read()
                        if "TODO" in content or "placeholder" in content.lower():
                            log(f"    ⚠️ Contains placeholder content - consider xfail", 
                                "WARNING")
                except Exception:
                    pass
        
        log("⚠️ Please fix real test failures before marking as xfail", "WARNING")
        return False
        
    except subprocess.TimeoutExpired:
        log("Unit tests timed out", "ERROR")
        return False
    except Exception as e:
        log(f"Error running unit tests: {e}", "ERROR")
        return False

def generate_coverage(dry_run=False):
    """Generate coverage reports"""
    if dry_run:
        log("DRY RUN: Would create .coveragerc with proper exclusions", "DRY_RUN")
        log("DRY RUN: Would run pytest --cov=src --cov-report=xml --cov-report=html", 
            "DRY_RUN")
        return True
    
    log("Generating coverage reports...", "STEP")
    
    try:
        # Create .coveragerc if it doesn't exist
        coveragerc = Path(".coveragerc")
        if not coveragerc.exists():
            coveragerc_content = """[run]
omit =
    scripts/*
    tests/*
    */test_*
    */__pycache__/*
    */venv/*
    */env/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    class .*\\bProtocol\\):
    @(abc\\.)?abstractmethod
"""
            with open(coveragerc, "w") as f:
                f.write(coveragerc_content)
            log("Created .coveragerc configuration", "INFO")
        
        # Run coverage
        cmd = [
            "pytest", 
            "--cov=src", 
            "--cov-report=xml", 
            "--cov-report=html",
            "--cov-report=term-missing"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            log("Coverage reports generated successfully", "SUCCESS")
            
            # Check if coverage files were created
            if Path("coverage.xml").exists():
                log("✓ coverage.xml created", "SUCCESS")
            if Path("htmlcov").exists():
                log("✓ htmlcov/ directory created", "SUCCESS")
            
            # Check coverage percentage
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
                    else:
                        log(f"⚠️ Coverage below target (need ≥85%, have {coverage_pct:.1f}%)", 
                            "WARNING")
            except Exception as e:
                log(f"Could not parse coverage percentage: {e}", "WARNING")
            
            return True
        else:
            log("Coverage generation failed", "ERROR")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        log("Coverage generation timed out", "ERROR")
        return False
    except Exception as e:
        log(f"Error generating coverage: {e}", "ERROR")
        return False

def run_dashboard_check(dry_run=False):
    """Run the progress monitor dashboard"""
    if dry_run:
        log("DRY RUN: Would run progress_monitor.py --dashboard", "DRY_RUN")
        return True
    
    log("Running progress monitor dashboard...", "STEP")
    
    try:
        result = subprocess.run(
            ["python", "scripts/progress_monitor.py", "--dashboard"],
            capture_output=True, text=True, timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Check if dashboard shows PASS
        if "Overall Status: PASS" in result.stdout:
            log("✓ Dashboard shows PASS status", "SUCCESS")
        elif "Overall Status: FAIL" in result.stdout:
            log("❌ Dashboard still shows FAIL status", "ERROR")
        else:
            log("⚠️ Could not determine dashboard status", "WARNING")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        log("Dashboard check timed out", "ERROR")
        return False
    except Exception as e:
        log(f"Error running dashboard: {e}", "ERROR")
        return False

def main():
    parser = argparse.ArgumentParser(description="Quick Fix Monitor")
    parser.add_argument("--fix-all", action="store_true", 
                       help="Fix all three issues")
    parser.add_argument("--start-cost", action="store_true",
                       help="Start cost meter")
    parser.add_argument("--fix-tests", action="store_true",
                       help="Fix unit tests")
    parser.add_argument("--generate-coverage", action="store_true",
                       help="Generate coverage reports")
    parser.add_argument("--check-dashboard", action="store_true",
                       help="Run dashboard check")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without executing")
    parser.add_argument("--verify", action="store_true",
                       help="Verify fixes are working")
    
    args = parser.parse_args()
    
    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║                QUICK FIX MONITOR                           ║")
    print(f"║                    Address Monitoring Issues               ║")
    if args.dry_run:
        print(f"║                        DRY RUN MODE                      ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
    
    success_count = 0
    total_steps = 0
    
    if args.fix_all or args.start_cost:
        total_steps += 1
        if start_cost_meter(args.dry_run):
            success_count += 1
    
    if args.fix_all or args.fix_tests:
        total_steps += 1
        if fix_unit_tests(args.dry_run):
            success_count += 1
    
    if args.fix_all or args.generate_coverage:
        total_steps += 1
        if generate_coverage(args.dry_run):
            success_count += 1
    
    if args.check_dashboard or args.fix_all:
        total_steps += 1
        if run_dashboard_check(args.dry_run):
            success_count += 1
    
    # Verification step
    if args.verify and not args.dry_run:
        log("Running verification checks...", "STEP")
        if verify_cost_meter():
            log("✓ Cost meter verification passed", "SUCCESS")
        else:
            log("❌ Cost meter verification failed", "ERROR")
    
    # Summary
    print(f"\n{Colors.CYAN}📊 Quick Fix Summary:{Colors.NC}")
    print(f"  Total steps: {total_steps}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {total_steps - success_count}")
    
    if args.dry_run:
        log("DRY RUN completed - no changes made", "DRY_RUN")
        print(f"\n{Colors.CYAN}💡 To apply fixes, run without --dry-run{Colors.NC}")
    elif success_count == total_steps:
        log("All fixes completed successfully!", "SUCCESS")
        print(f"\n{Colors.GREEN}🎉 Ready for production run!{Colors.NC}")
        print(f"\n{Colors.BLUE}📋 Next steps:{Colors.NC}")
        print("  1. Run: python scripts/progress_monitor.py --dashboard")
        print("  2. Check: tail -f logs/cost.log")
        print("  3. Verify: jq . results/bench_latest.json | head")
    else:
        log("Some fixes failed - check output above", "WARNING")
    
    return success_count == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 