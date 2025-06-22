#!/usr/bin/env python3
"""
Changelog Tracker for Oversight Curriculum
Automated change tracking and changelog generation
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import subprocess
import re


@dataclass
class FileChange:
    """Record of a file change"""
    file_path: str
    change_type: str  # "added", "modified", "deleted"
    timestamp: str
    size_bytes: Optional[int] = None
    hash: Optional[str] = None
    lines_added: Optional[int] = None
    lines_removed: Optional[int] = None


@dataclass
class ChangelogEntry:
    """A changelog entry"""
    version: str
    date: str
    changes: List[str]
    files_changed: List[FileChange]
    author: Optional[str] = None
    commit_hash: Optional[str] = None


class ChangelogTracker:
    """Automated changelog tracking system"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.parent
        self.changelog_dir = self.script_dir / "changelogs"
        self.changelog_dir.mkdir(exist_ok=True)
        
        # File patterns to track
        self.tracked_patterns = [
            "*.py",
            "*.md",
            "*.json",
            "*.yaml",
            "*.yml",
            "*.txt",
            "*.sh"
        ]
        
        # Directories to ignore
        self.ignored_dirs = {
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            "env",
            ".pytest_cache",
            "logs",
            "temp"
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{level}] [{timestamp}] {message}")
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def get_file_stats(self, file_path: Path) -> Dict[str, Any]:
        """Get file statistics"""
        try:
            stat = file_path.stat()
            return {
                "size_bytes": stat.st_size,
                "modified_time": stat.st_mtime,
                "hash": self.get_file_hash(file_path)
            }
        except Exception:
            return {}
    
    def count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except Exception:
            return 0
    
    def scan_files(self) -> Dict[str, Dict[str, Any]]:
        """Scan all tracked files"""
        file_snapshot = {}
        
        for pattern in self.tracked_patterns:
            for file_path in self.script_dir.rglob(pattern):
                # Skip ignored directories
                if any(ignored in file_path.parts for ignored in self.ignored_dirs):
                    continue
                
                relative_path = str(file_path.relative_to(self.script_dir))
                stats = self.get_file_stats(file_path)
                stats["line_count"] = self.count_lines(file_path)
                
                file_snapshot[relative_path] = stats
        
        return file_snapshot
    
    def load_previous_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Load previous file snapshot"""
        snapshot_file = self.changelog_dir / "file_snapshot.json"
        
        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"Error loading snapshot: {e}", "WARNING")
        
        return {}
    
    def save_snapshot(self, snapshot: Dict[str, Dict[str, Any]]):
        """Save current file snapshot"""
        snapshot_file = self.changelog_dir / "file_snapshot.json"
        
        try:
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot, f, indent=2)
        except Exception as e:
            self.log(f"Error saving snapshot: {e}", "ERROR")
    
    def detect_changes(self) -> List[FileChange]:
        """Detect changes since last snapshot"""
        current_snapshot = self.scan_files()
        previous_snapshot = self.load_previous_snapshot()
        
        changes = []
        timestamp = datetime.now().isoformat()
        
        # Find added and modified files
        for file_path, current_stats in current_snapshot.items():
            if file_path in previous_snapshot:
                # File exists in both snapshots - check for modifications
                previous_stats = previous_snapshot[file_path]
                
                if current_stats.get("hash") != previous_stats.get("hash"):
                    # File was modified
                    lines_added = max(0, current_stats.get("line_count", 0) - 
                                    previous_stats.get("line_count", 0))
                    lines_removed = max(0, previous_stats.get("line_count", 0) - 
                                      current_stats.get("line_count", 0))
                    
                    change = FileChange(
                        file_path=file_path,
                        change_type="modified",
                        timestamp=timestamp,
                        size_bytes=current_stats.get("size_bytes"),
                        hash=current_stats.get("hash"),
                        lines_added=lines_added,
                        lines_removed=lines_removed
                    )
                    changes.append(change)
            else:
                # File was added
                change = FileChange(
                    file_path=file_path,
                    change_type="added",
                    timestamp=timestamp,
                    size_bytes=current_stats.get("size_bytes"),
                    hash=current_stats.get("hash"),
                    lines_added=current_stats.get("line_count", 0)
                )
                changes.append(change)
        
        # Find deleted files
        for file_path in previous_snapshot:
            if file_path not in current_snapshot:
                change = FileChange(
                    file_path=file_path,
                    change_type="deleted",
                    timestamp=timestamp
                )
                changes.append(change)
        
        # Save current snapshot
        self.save_snapshot(current_snapshot)
        
        return changes
    
    def generate_changelog_entry(self, changes: List[FileChange], 
                               version: Optional[str] = None) -> ChangelogEntry:
        """Generate a changelog entry from changes"""
        if not version:
            version = datetime.now().strftime("%Y.%m.%d-%H%M")
        
        # Categorize changes
        added_files = [c for c in changes if c.change_type == "added"]
        modified_files = [c for c in changes if c.change_type == "modified"]
        deleted_files = [c for c in changes if c.change_type == "deleted"]
        
        # Generate change descriptions
        change_descriptions = []
        
        if added_files:
            change_descriptions.append(f"Added {len(added_files)} new files")
        
        if modified_files:
            total_lines_added = sum(c.lines_added or 0 for c in modified_files)
            total_lines_removed = sum(c.lines_removed or 0 for c in modified_files)
            change_descriptions.append(
                f"Modified {len(modified_files)} files "
                f"(+{total_lines_added} lines, -{total_lines_removed} lines)"
            )
        
        if deleted_files:
            change_descriptions.append(f"Deleted {len(deleted_files)} files")
        
        # Try to get git info
        author = self.get_git_author()
        commit_hash = self.get_git_commit_hash()
        
        entry = ChangelogEntry(
            version=version,
            date=datetime.now().isoformat(),
            changes=change_descriptions,
            files_changed=changes,
            author=author,
            commit_hash=commit_hash
        )
        
        return entry
    
    def get_git_author(self) -> Optional[str]:
        """Get current git author"""
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True, text=True, cwd=self.script_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def get_git_commit_hash(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, cwd=self.script_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()[:8]  # Short hash
        except Exception:
            pass
        return None
    
    def save_changelog_entry(self, entry: ChangelogEntry):
        """Save changelog entry to file"""
        # Save individual entry
        entry_file = self.changelog_dir / f"changelog_{entry.version}.json"
        
        try:
            with open(entry_file, 'w') as f:
                json.dump(asdict(entry), f, indent=2)
        except Exception as e:
            self.log(f"Error saving changelog entry: {e}", "ERROR")
        
        # Update main changelog
        self.update_main_changelog(entry)
    
    def update_main_changelog(self, entry: ChangelogEntry):
        """Update main changelog file"""
        main_changelog = self.changelog_dir / "CHANGELOG.md"
        
        # Read existing changelog
        existing_content = ""
        if main_changelog.exists():
            try:
                with open(main_changelog, 'r') as f:
                    existing_content = f.read()
            except Exception:
                pass
        
        # Generate new entry
        new_entry = f"""
## [{entry.version}] - {datetime.fromisoformat(entry.date).strftime('%Y-%m-%d %H:%M')}

"""
        
        for change in entry.changes:
            new_entry += f"- {change}\n"
        
        if entry.files_changed:
            new_entry += "\n### Files Changed\n"
            for file_change in entry.files_changed:
                if file_change.change_type == "added":
                    new_entry += f"- ✨ Added: `{file_change.file_path}`\n"
                elif file_change.change_type == "modified":
                    new_entry += f"- 🔄 Modified: `{file_change.file_path}`"
                    if file_change.lines_added or file_change.lines_removed:
                        new_entry += f" (+{file_change.lines_added or 0}, -{file_change.lines_removed or 0})"
                    new_entry += "\n"
                elif file_change.change_type == "deleted":
                    new_entry += f"- 🗑️ Deleted: `{file_change.file_path}`\n"
        
        if entry.author:
            new_entry += f"\n**Author:** {entry.author}\n"
        
        if entry.commit_hash:
            new_entry += f"**Commit:** {entry.commit_hash}\n"
        
        # Prepend to existing content
        new_content = new_entry + "\n" + existing_content
        
        # Write back to file
        try:
            with open(main_changelog, 'w') as f:
                f.write(new_content)
        except Exception as e:
            self.log(f"Error updating main changelog: {e}", "ERROR")
    
    def run_change_detection(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Run change detection and generate changelog"""
        self.log("🔍 Detecting changes...")
        
        changes = self.detect_changes()
        
        if not changes:
            self.log("No changes detected")
            return {"changes_detected": False, "changes": []}
        
        self.log(f"Detected {len(changes)} changes")
        
        # Generate changelog entry
        entry = self.generate_changelog_entry(changes, version)
        
        # Save entry
        self.save_changelog_entry(entry)
        
        # Print summary
        self.log("📝 Changelog Entry Generated:")
        self.log(f"  Version: {entry.version}")
        self.log(f"  Changes: {len(entry.changes)}")
        self.log(f"  Files: {len(entry.files_changed)}")
        
        for change in entry.changes:
            self.log(f"    - {change}")
        
        return {
            "changes_detected": True,
            "version": entry.version,
            "changes": entry.changes,
            "files_changed": len(entry.files_changed),
            "entry": asdict(entry)
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Changelog tracker")
    parser.add_argument("--version", "-v", help="Version for this change")
    parser.add_argument("--check", "-c", action="store_true", help="Check for changes only")
    parser.add_argument("--output", "-o", help="Output file for results")
    
    args = parser.parse_args()
    
    tracker = ChangelogTracker()
    
    try:
        if args.check:
            # Just check for changes
            changes = tracker.detect_changes()
            print(f"Changes detected: {len(changes)}")
            
            for change in changes:
                print(f"  {change.change_type}: {change.file_path}")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump([asdict(change) for change in changes], f, indent=2)
        else:
            # Run full change detection and changelog generation
            result = tracker.run_change_detection(args.version)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
            
            # Exit with appropriate code
            sys.exit(0 if result["changes_detected"] else 1)
    
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 