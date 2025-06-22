#!/usr/bin/env python3
"""
Blocker Tracker for Oversight Curriculum
Issue tracking and resolution monitoring
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class BlockerStatus(Enum):
    """Blocker status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class BlockerPriority(Enum):
    """Blocker priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Blocker:
    """A blocker/issue record"""
    id: str
    title: str
    description: str
    status: BlockerStatus
    priority: BlockerPriority
    created_at: str
    updated_at: str
    assigned_to: Optional[str] = None
    tags: List[str] = None
    resolution_notes: Optional[str] = None
    estimated_resolution_time: Optional[str] = None
    actual_resolution_time: Optional[str] = None


class BlockerTracker:
    """Blocker tracking system"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.parent
        self.blockers_dir = self.script_dir / "blockers"
        self.blockers_dir.mkdir(exist_ok=True)
        
        self.blockers_file = self.blockers_dir / "blockers.json"
        self.blockers: List[Blocker] = []
        
        self.load_blockers()
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{level}] [{timestamp}] {message}")
    
    def load_blockers(self):
        """Load blockers from file"""
        if self.blockers_file.exists():
            try:
                with open(self.blockers_file, 'r') as f:
                    data = json.load(f)
                
                self.blockers = []
                for blocker_data in data:
                    blocker = Blocker(
                        id=blocker_data["id"],
                        title=blocker_data["title"],
                        description=blocker_data["description"],
                        status=BlockerStatus(blocker_data["status"]),
                        priority=BlockerPriority(blocker_data["priority"]),
                        created_at=blocker_data["created_at"],
                        updated_at=blocker_data["updated_at"],
                        assigned_to=blocker_data.get("assigned_to"),
                        tags=blocker_data.get("tags", []),
                        resolution_notes=blocker_data.get("resolution_notes"),
                        estimated_resolution_time=blocker_data.get("estimated_resolution_time"),
                        actual_resolution_time=blocker_data.get("actual_resolution_time")
                    )
                    self.blockers.append(blocker)
                
                self.log(f"Loaded {len(self.blockers)} blockers")
                
            except Exception as e:
                self.log(f"Error loading blockers: {e}", "ERROR")
                self.blockers = []
        else:
            self.blockers = []
    
    def save_blockers(self):
        """Save blockers to file"""
        try:
            data = [asdict(blocker) for blocker in self.blockers]
            with open(self.blockers_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.log(f"Error saving blockers: {e}", "ERROR")
    
    def generate_id(self) -> str:
        """Generate unique blocker ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"BLOCKER-{timestamp}"
    
    def add_blocker(self, title: str, description: str, priority: BlockerPriority,
                   assigned_to: Optional[str] = None, tags: List[str] = None) -> Blocker:
        """Add a new blocker"""
        blocker = Blocker(
            id=self.generate_id(),
            title=title,
            description=description,
            status=BlockerStatus.OPEN,
            priority=priority,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            assigned_to=assigned_to,
            tags=tags or []
        )
        
        self.blockers.append(blocker)
        self.save_blockers()
        
        self.log(f"Added blocker: {blocker.id} - {title}")
        return blocker
    
    def update_blocker(self, blocker_id: str, **kwargs) -> Optional[Blocker]:
        """Update a blocker"""
        for blocker in self.blockers:
            if blocker.id == blocker_id:
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(blocker, key):
                        setattr(blocker, key, value)
                
                # Update timestamp
                blocker.updated_at = datetime.now().isoformat()
                
                # If resolving, set resolution time
                if kwargs.get("status") == BlockerStatus.RESOLVED:
                    blocker.actual_resolution_time = datetime.now().isoformat()
                
                self.save_blockers()
                self.log(f"Updated blocker: {blocker_id}")
                return blocker
        
        self.log(f"Blocker not found: {blocker_id}", "WARNING")
        return None
    
    def resolve_blocker(self, blocker_id: str, resolution_notes: str) -> bool:
        """Resolve a blocker"""
        blocker = self.update_blocker(
            blocker_id,
            status=BlockerStatus.RESOLVED,
            resolution_notes=resolution_notes
        )
        return blocker is not None
    
    def close_blocker(self, blocker_id: str) -> bool:
        """Close a blocker"""
        blocker = self.update_blocker(blocker_id, status=BlockerStatus.CLOSED)
        return blocker is not None
    
    def get_blocker(self, blocker_id: str) -> Optional[Blocker]:
        """Get a specific blocker"""
        for blocker in self.blockers:
            if blocker.id == blocker_id:
                return blocker
        return None
    
    def get_blockers_by_status(self, status: BlockerStatus) -> List[Blocker]:
        """Get blockers by status"""
        return [b for b in self.blockers if b.status == status]
    
    def get_blockers_by_priority(self, priority: BlockerPriority) -> List[Blocker]:
        """Get blockers by priority"""
        return [b for b in self.blockers if b.priority == priority]
    
    def get_active_blockers(self) -> List[Blocker]:
        """Get active blockers (open or in progress)"""
        return [b for b in self.blockers if b.status in [BlockerStatus.OPEN, BlockerStatus.IN_PROGRESS]]
    
    def get_critical_blockers(self) -> List[Blocker]:
        """Get critical blockers"""
        return [b for b in self.blockers if b.priority == BlockerPriority.CRITICAL and b.status != BlockerStatus.RESOLVED]
    
    def get_blocker_stats(self) -> Dict[str, Any]:
        """Get blocker statistics"""
        total_blockers = len(self.blockers)
        open_blockers = len(self.get_blockers_by_status(BlockerStatus.OPEN))
        in_progress_blockers = len(self.get_blockers_by_status(BlockerStatus.IN_PROGRESS))
        resolved_blockers = len(self.get_blockers_by_status(BlockerStatus.RESOLVED))
        closed_blockers = len(self.get_blockers_by_status(BlockerStatus.CLOSED))
        
        critical_blockers = len(self.get_critical_blockers())
        high_priority_blockers = len([b for b in self.blockers if b.priority == BlockerPriority.HIGH and b.status != BlockerStatus.RESOLVED])
        
        # Calculate resolution time for resolved blockers
        resolution_times = []
        for blocker in self.blockers:
            if blocker.status == BlockerStatus.RESOLVED and blocker.actual_resolution_time:
                created = datetime.fromisoformat(blocker.created_at)
                resolved = datetime.fromisoformat(blocker.actual_resolution_time)
                resolution_time = (resolved - created).total_seconds() / 3600  # hours
                resolution_times.append(resolution_time)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            "total_blockers": total_blockers,
            "open_blockers": open_blockers,
            "in_progress_blockers": in_progress_blockers,
            "resolved_blockers": resolved_blockers,
            "closed_blockers": closed_blockers,
            "critical_blockers": critical_blockers,
            "high_priority_blockers": high_priority_blockers,
            "avg_resolution_time_hours": avg_resolution_time,
            "resolution_rate": resolved_blockers / total_blockers if total_blockers > 0 else 0
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate blocker report"""
        stats = self.get_blocker_stats()
        active_blockers = self.get_active_blockers()
        critical_blockers = self.get_critical_blockers()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "active_blockers": [asdict(b) for b in active_blockers],
            "critical_blockers": [asdict(b) for b in critical_blockers],
            "summary": {
                "has_critical_blockers": len(critical_blockers) > 0,
                "has_active_blockers": len(active_blockers) > 0,
                "overall_status": "blocked" if len(critical_blockers) > 0 else "clear"
            }
        }
        
        return report
    
    def save_report(self, output_file: Optional[Path] = None):
        """Save blocker report"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.blockers_dir / f"blocker_report_{timestamp}.json"
        
        report = self.generate_report()
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.log(f"Blocker report saved to {output_file}")
            return output_file
        except Exception as e:
            self.log(f"Error saving report: {e}", "ERROR")
            return None
    
    def print_summary(self):
        """Print blocker summary"""
        stats = self.get_blocker_stats()
        active_blockers = self.get_active_blockers()
        critical_blockers = self.get_critical_blockers()
        
        print(f"\n📊 BLOCKER SUMMARY")
        print("=" * 50)
        print(f"Total blockers: {stats['total_blockers']}")
        print(f"Open: {stats['open_blockers']}")
        print(f"In progress: {stats['in_progress_blockers']}")
        print(f"Resolved: {stats['resolved_blockers']}")
        print(f"Closed: {stats['closed_blockers']}")
        print(f"Critical: {stats['critical_blockers']}")
        print(f"High priority: {stats['high_priority_blockers']}")
        print(f"Resolution rate: {stats['resolution_rate']:.1%}")
        print(f"Avg resolution time: {stats['avg_resolution_time_hours']:.1f} hours")
        
        if critical_blockers:
            print(f"\n🚨 CRITICAL BLOCKERS:")
            for blocker in critical_blockers:
                print(f"  {blocker.id}: {blocker.title}")
                print(f"    Status: {blocker.status.value}")
                print(f"    Assigned: {blocker.assigned_to or 'Unassigned'}")
        
        if active_blockers:
            print(f"\n📋 ACTIVE BLOCKERS:")
            for blocker in active_blockers:
                print(f"  {blocker.id}: {blocker.title}")
                print(f"    Priority: {blocker.priority.value}")
                print(f"    Status: {blocker.status.value}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Blocker tracker")
    parser.add_argument("--add", "-a", action="store_true", help="Add new blocker")
    parser.add_argument("--title", help="Blocker title")
    parser.add_argument("--description", help="Blocker description")
    parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], 
                       default="medium", help="Blocker priority")
    parser.add_argument("--assign", help="Assign to user")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--update", "-u", help="Update blocker by ID")
    parser.add_argument("--resolve", "-r", help="Resolve blocker by ID")
    parser.add_argument("--close", "-c", help="Close blocker by ID")
    parser.add_argument("--notes", help="Resolution notes")
    parser.add_argument("--status", choices=["open", "in_progress", "resolved", "closed"], 
                       help="New status for update")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--summary", "-s", action="store_true", help="Print summary")
    parser.add_argument("--output", "-o", help="Output file for report")
    
    args = parser.parse_args()
    
    tracker = BlockerTracker()
    
    try:
        if args.add:
            # Add new blocker
            if not args.title:
                print("Error: --title is required for adding a blocker")
                sys.exit(1)
            
            priority = BlockerPriority(args.priority)
            tags = args.tags.split(",") if args.tags else []
            
            blocker = tracker.add_blocker(
                title=args.title,
                description=args.description or "",
                priority=priority,
                assigned_to=args.assign,
                tags=tags
            )
            
            print(f"Added blocker: {blocker.id}")
        
        elif args.update:
            # Update blocker
            if not args.status:
                print("Error: --status is required for updating a blocker")
                sys.exit(1)
            
            status = BlockerStatus(args.status)
            success = tracker.update_blocker(args.update, status=status) is not None
            
            if success:
                print(f"Updated blocker: {args.update}")
            else:
                print(f"Blocker not found: {args.update}")
                sys.exit(1)
        
        elif args.resolve:
            # Resolve blocker
            if not args.notes:
                print("Error: --notes is required for resolving a blocker")
                sys.exit(1)
            
            success = tracker.resolve_blocker(args.resolve, args.notes)
            
            if success:
                print(f"Resolved blocker: {args.resolve}")
            else:
                print(f"Blocker not found: {args.resolve}")
                sys.exit(1)
        
        elif args.close:
            # Close blocker
            success = tracker.close_blocker(args.close)
            
            if success:
                print(f"Closed blocker: {args.close}")
            else:
                print(f"Blocker not found: {args.close}")
                sys.exit(1)
        
        elif args.report:
            # Generate report
            if args.output:
                output_file = Path(args.output)
            else:
                output_file = None
            
            tracker.save_report(output_file)
        
        elif args.summary:
            # Print summary
            tracker.print_summary()
        
        else:
            # Show help
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 