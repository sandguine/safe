#!/usr/bin/env python3
"""
Real-time cost monitoring for API usage.
Logs cumulative cost each minute and provides cost tracking.
"""

import os
import time
import json
import argparse
import threading
from datetime import datetime
import signal
import sys


class CostMonitor:
    """Monitors API costs in real-time"""
    
    def __init__(self, log_file: str = "cost.log", max_cost: float = 110.0):
        self.log_file = log_file
        self.max_cost = max_cost
        self.current_cost = 0.0
        self.total_calls = 0
        self.cost_history = []
        self.running = True
        self.lock = threading.Lock()
        
        # Cost estimates per API call (approximate)
        self.cost_estimates = {
            "claude-3-5-sonnet-20241022": {
                "input": 0.003,   # per 1K tokens
                "output": 0.015   # per 1K tokens
            }
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Cost monitor received signal {signum}, shutting down...")
        self.running = False
        self.save_final_report()
        sys.exit(0)
    
    def estimate_cost(self, model: str, input_tokens: int, 
                     output_tokens: int) -> float:
        """Estimate cost for an API call"""
        if model not in self.cost_estimates:
            return 0.0
        
        rates = self.cost_estimates[model]
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        
        return input_cost + output_cost
    
    def add_cost(self, model: str, input_tokens: int, output_tokens: int):
        """Add cost for an API call"""
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        
        with self.lock:
            self.current_cost += cost
            self.total_calls += 1
            timestamp = datetime.now().isoformat()
            self.cost_history.append({
                "timestamp": timestamp,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "cumulative_cost": self.current_cost,
                "total_calls": self.total_calls
            })
            
            # Check if we're approaching the limit
            if self.current_cost >= self.max_cost * 0.9:
                print(f"⚠️  WARNING: Cost at ${self.current_cost:.2f} "
                      f"(90% of ${self.max_cost} limit)")
            
            if self.current_cost >= self.max_cost:
                print(f"🚨 CRITICAL: Cost limit reached! ${self.current_cost:.2f}")
                self.running = False
    
    def log_current_cost(self):
        """Log current cost to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.lock:
            cost_info = {
                "timestamp": timestamp,
                "current_cost": self.current_cost,
                "max_cost": self.max_cost,
                "percentage": (self.current_cost / self.max_cost) * 100,
                "total_calls": self.total_calls
            }
        
        log_entry = (f"[{timestamp}] calls={self.total_calls} | "
                    f"USD=${self.current_cost:.2f} | "
                    f"limit=${self.max_cost:.2f} | "
                    f"({cost_info['percentage']:.1f}%)")
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
        
        print(log_entry)
    
    def save_final_report(self):
        """Save detailed cost report"""
        report = {
            "final_cost": self.current_cost,
            "max_cost": self.max_cost,
            "percentage_used": (self.current_cost / self.max_cost) * 100,
            "total_calls": self.total_calls,
            "cost_history": self.cost_history,
            "summary": {
                "total_calls": len(self.cost_history),
                "average_cost_per_call": (self.current_cost / len(self.cost_history) 
                                        if self.cost_history else 0),
                "start_time": (self.cost_history[0]["timestamp"] 
                             if self.cost_history else None),
                "end_time": datetime.now().isoformat()
            }
        }
        
        with open("cost_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Cost report saved to cost_report.json")
        print(f"💰 Final cost: ${self.current_cost:.2f} / ${self.max_cost:.2f}")
        print(f"📞 Total calls: {self.total_calls}")
    
    def start_monitoring(self, interval: int = 60):
        """Start cost monitoring loop"""
        print(f"💰 Starting cost monitoring...")
        print(f"📊 Log file: {self.log_file}")
        print(f"💵 Max cost: ${self.max_cost} (abort at ${self.max_cost})")
        print(f"⏱️  Logging interval: {interval} seconds")
        print(f"🛑 Press Ctrl+C to stop monitoring")
        
        # Create log file header
        with open(self.log_file, 'w') as f:
            f.write(f"# Cost monitoring started at {datetime.now().isoformat()}\n")
            f.write(f"# Max cost: ${self.max_cost}\n")
            f.write(f"# Format: [timestamp] calls=X | USD=$X.XX | limit=$X.XX | (XX.X%)\n\n")
        
        while self.running:
            self.log_current_cost()
            
            # Sleep for interval
            for _ in range(interval):
                if not self.running:
                    break
                time.sleep(1)
        
        self.save_final_report()


def main():
    parser = argparse.ArgumentParser(description="Monitor API costs in real-time")
    parser.add_argument("--log-file", default="cost.log", 
                       help="Cost log file")
    parser.add_argument("--max-cost", type=float, default=110.0, 
                       help="Maximum cost limit (default: 110)")
    parser.add_argument("--interval", type=int, default=60, 
                       help="Logging interval in seconds")
    
    args = parser.parse_args()
    
    # Set environment variable for other scripts
    os.environ["COST_LOG"] = args.log_file
    
    monitor = CostMonitor(log_file=args.log_file, max_cost=args.max_cost)
    monitor.start_monitoring(interval=args.interval)


if __name__ == "__main__":
    main() 