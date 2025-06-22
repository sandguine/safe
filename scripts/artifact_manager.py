#!/usr/bin/env python3
"""
Artifact Manager - Timestamped artifacts with cleanup
====================================================

Manages timestamped artifacts and keeps only the last 7 days.
Implements the user's suggestion for historical tracking.

Usage:
    python scripts/artifact_manager.py --save coverage.xml
    python scripts/artifact_manager.py --cleanup
    python scripts/artifact_manager.py --list
"""

import os
import sys
import shutil
import time
from pathlib import Path
import argparse
import json

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
        "STEP": Colors.PURPLE
    }
    color_code = level_colors.get(level, Colors.BLUE)
    print(f"{color_code}[{level}]{Colors.NC} [{timestamp}] {message}")


def save_artifact(source_path, artifact_type="general"):
    """Save an artifact with timestamp"""
    source = Path(source_path)
    if not source.exists():
        log(f"Source file not found: {source_path}", "ERROR")
        return False
    
    # Create artifacts directory structure
    today = time.strftime("%Y-%m-%d")
    artifacts_dir = Path("artifacts") / today
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamped filename
    timestamp = time.strftime("%H%M%S")
    extension = source.suffix
    name = source.stem
    
    if artifact_type == "coverage":
        dest_name = f"coverage_{timestamp}{extension}"
    elif artifact_type == "benchmark":
        dest_name = f"benchmark_{timestamp}{extension}"
    elif artifact_type == "dashboard":
        dest_name = f"dashboard_{timestamp}{extension}"
    else:
        dest_name = f"{name}_{timestamp}{extension}"
    
    dest_path = artifacts_dir / dest_name
    
    try:
        shutil.copy2(source, dest_path)
        log(f"✓ Saved {source_path} → {dest_path}", "SUCCESS")
        
        # Create metadata
        metadata = {
            "source": str(source),
            "artifact_type": artifact_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "size_bytes": source.stat().st_size
        }
        
        metadata_file = dest_path.with_suffix('.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True
    except Exception as e:
        log(f"Error saving artifact: {e}", "ERROR")
        return False


def cleanup_old_artifacts(days_to_keep=7):
    """Remove artifacts older than specified days"""
    log(f"Cleaning up artifacts older than {days_to_keep} days", "STEP")
    
    artifacts_dir = Path("artifacts")
    if not artifacts_dir.exists():
        log("No artifacts directory found", "INFO")
        return True
    
    cutoff_time = time.time() - (days_to_keep * 86400)
    removed_count = 0
    
    for date_dir in artifacts_dir.iterdir():
        if not date_dir.is_dir():
            continue
        
        try:
            # Check if directory is older than cutoff
            dir_time = date_dir.stat().st_mtime
            if dir_time < cutoff_time:
                shutil.rmtree(date_dir)
                log(f"Removed old artifacts: {date_dir.name}", "INFO")
                removed_count += 1
        except Exception as e:
            log(f"Error removing {date_dir}: {e}", "WARNING")
    
    log(f"Cleanup complete: removed {removed_count} old artifact directories", 
        "SUCCESS")
    return True


def list_artifacts():
    """List all artifacts with metadata"""
    log("Listing artifacts", "STEP")
    
    artifacts_dir = Path("artifacts")
    if not artifacts_dir.exists():
        log("No artifacts found", "INFO")
        return
    
    total_size = 0
    artifact_count = 0
    
    for date_dir in sorted(artifacts_dir.iterdir(), reverse=True):
        if not date_dir.is_dir():
            continue
        
        print(f"\n{Colors.CYAN}📁 {date_dir.name}{Colors.NC}")
        print("-" * 40)
        
        try:
            files = list(date_dir.glob("*"))
            for file_path in sorted(files):
                if file_path.suffix == '.json':
                    continue  # Skip metadata files
                
                size = file_path.stat().st_size
                total_size += size
                artifact_count += 1
                
                # Format size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024*1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size/(1024*1024):.1f}MB"
                
                print(f"  {file_path.name:<30} {size_str:>8}")
                
                # Show metadata if available
                metadata_file = file_path.with_suffix('.json')
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        timestamp = metadata.get('timestamp', 'Unknown')
                        print(f"    └─ {timestamp}")
                    except Exception:
                        pass
                        
        except Exception as e:
            log(f"Error reading {date_dir}: {e}", "WARNING")
    
    print(f"\n{Colors.CYAN}📊 Summary:{Colors.NC}")
    print(f"  Total artifacts: {artifact_count}")
    print(f"  Total size: {total_size/(1024*1024):.1f}MB")


def save_coverage_artifacts():
    """Save coverage artifacts with timestamp"""
    log("Saving coverage artifacts", "STEP")
    
    artifacts = [
        ("coverage.xml", "coverage"),
        ("htmlcov/", "coverage"),
    ]
    
    success_count = 0
    for source, artifact_type in artifacts:
        if Path(source).exists():
            if Path(source).is_dir():
                # Handle directories
                today = time.strftime("%Y-%m-%d")
                timestamp = time.strftime("%H%M%S")
                artifacts_dir = Path("artifacts") / today
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                
                dest_name = f"htmlcov_{timestamp}"
                dest_path = artifacts_dir / dest_name
                
                try:
                    shutil.copytree(source, dest_path)
                    log(f"✓ Saved {source} → {dest_path}", "SUCCESS")
                    success_count += 1
                except Exception as e:
                    log(f"Error saving {source}: {e}", "ERROR")
            else:
                # Handle files
                if save_artifact(source, artifact_type):
                    success_count += 1
        else:
            log(f"Coverage artifact not found: {source}", "WARNING")
    
    return success_count == len(artifacts)


def save_benchmark_artifacts():
    """Save benchmark artifacts with timestamp"""
    log("Saving benchmark artifacts", "STEP")
    
    # Find benchmark files
    bench_files = list(Path("results").glob("*bench*.json"))
    if not bench_files:
        log("No benchmark files found", "WARNING")
        return False
    
    success_count = 0
    for bench_file in bench_files:
        if save_artifact(bench_file, "benchmark"):
            success_count += 1
    
    log(f"Saved {success_count}/{len(bench_files)} benchmark artifacts", 
        "SUCCESS" if success_count == len(bench_files) else "WARNING")
    return success_count > 0


def main():
    parser = argparse.ArgumentParser(description="Artifact Manager")
    parser.add_argument("--save", type=str, help="Save specific file as artifact")
    parser.add_argument("--save-coverage", action="store_true", 
                       help="Save coverage artifacts")
    parser.add_argument("--save-benchmark", action="store_true",
                       help="Save benchmark artifacts")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up old artifacts")
    parser.add_argument("--list", action="store_true",
                       help="List all artifacts")
    parser.add_argument("--days", type=int, default=7,
                       help="Days to keep artifacts (default: 7)")
    
    args = parser.parse_args()
    
    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║                ARTIFACT MANAGER                           ║")
    print(f"║                    Timestamped Artifacts & Cleanup        ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
    
    success = True
    
    if args.save:
        success = save_artifact(args.save)
    
    if args.save_coverage:
        success = save_coverage_artifacts() and success
    
    if args.save_benchmark:
        success = save_benchmark_artifacts() and success
    
    if args.cleanup:
        success = cleanup_old_artifacts(args.days) and success
    
    if args.list:
        list_artifacts()
    
    if not any([args.save, args.save_coverage, args.save_benchmark, 
                args.cleanup, args.list]):
        # Default: save all artifacts
        log("No specific action specified, saving all artifacts", "INFO")
        success = save_coverage_artifacts() and success
        success = save_benchmark_artifacts() and success
        success = cleanup_old_artifacts(args.days) and success
    
    if success:
        log("Artifact management completed successfully", "SUCCESS")
    else:
        log("Some artifact operations failed", "WARNING")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 