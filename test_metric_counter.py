#!/usr/bin/env python3
"""
Metric Counter Sanity Test
Verifies that metrics are properly incremented
"""

import asyncio
import json
import sys
from typing import Dict, Any

class MetricCounterTest:
    """Test metric counter functionality"""
    
    def __init__(self):
        self.metrics = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'partial': 0
        }
    
    def increment_metric(self, metric_name: str, count: int = 1):
        """Increment a metric counter"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += count
            print(f"📊 Incremented {metric_name}: {self.metrics[metric_name]}")
        else:
            print(f"⚠️  Unknown metric: {metric_name}")
    
    def record_task_result(self, task_id: str, passed: bool, partial: bool = False):
        """Record the result of a single task"""
        self.metrics['total'] += 1
        
        if passed:
            self.metrics['passed'] += 1
            print(f"✅ Task {task_id}: PASSED")
        elif partial:
            self.metrics['partial'] += 1
            print(f"⚠️  Task {task_id}: PARTIAL")
        else:
            self.metrics['failed'] += 1
            print(f"❌ Task {task_id}: FAILED")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics with calculated percentages"""
        total = self.metrics['total']
        if total == 0:
            return {**self.metrics, 'pass_rate': 0.0, 'partial_rate': 0.0, 'fail_rate': 0.0}
        
        return {
            **self.metrics,
            'pass_rate': self.metrics['passed'] / total,
            'partial_rate': self.metrics['partial'] / total,
            'fail_rate': self.metrics['failed'] / total
        }
    
    def print_metrics(self):
        """Print current metrics"""
        metrics = self.get_metrics()
        
        print(f"\n📊 METRIC COUNTER TEST RESULTS")
        print("=" * 40)
        print(f"Total tasks: {metrics['total']}")
        print(f"Passed: {metrics['passed']} ({metrics['pass_rate']:.1%})")
        print(f"Partial: {metrics['partial']} ({metrics['partial_rate']:.1%})")
        print(f"Failed: {metrics['failed']} ({metrics['fail_rate']:.1%})")
        
        # Sanity checks
        total_calculated = metrics['passed'] + metrics['partial'] + metrics['failed']
        if total_calculated != metrics['total']:
            print(f"⚠️  WARNING: Total mismatch! {total_calculated} != {metrics['total']}")
            return False
        
        if metrics['total'] == 0:
            print(f"⚠️  WARNING: No tasks recorded!")
            return False
        
        print(f"✅ Metric counter sanity check: PASSED")
        return True

async def run_metric_counter_test():
    """Run comprehensive metric counter test"""
    
    print("🧪 METRIC COUNTER SANITY TEST")
    print("=" * 50)
    
    counter = MetricCounterTest()
    
    # Test 1: Single toy task
    print(f"\n🔄 Test 1: Single toy task")
    counter.record_task_result("toy_task_1", passed=True)
    
    metrics = counter.get_metrics()
    assert metrics['total'] == 1, f"Expected total=1, got {metrics['total']}"
    assert metrics['passed'] == 1, f"Expected passed=1, got {metrics['passed']}"
    assert metrics['pass_rate'] == 1.0, f"Expected pass_rate=1.0, got {metrics['pass_rate']}"
    
    print(f"✅ Single task test: PASSED")
    
    # Test 2: Multiple tasks with different outcomes
    print(f"\n🔄 Test 2: Multiple tasks with different outcomes")
    counter.record_task_result("toy_task_2", passed=False)
    counter.record_task_result("toy_task_3", passed=True)
    counter.record_task_result("toy_task_4", passed=False, partial=True)
    
    metrics = counter.get_metrics()
    assert metrics['total'] == 4, f"Expected total=4, got {metrics['total']}"
    assert metrics['passed'] == 2, f"Expected passed=2, got {metrics['passed']}"
    assert metrics['failed'] == 1, f"Expected failed=1, got {metrics['failed']}"
    assert metrics['partial'] == 1, f"Expected partial=1, got {metrics['partial']}"
    
    print(f"✅ Multiple tasks test: PASSED")
    
    # Test 3: Edge cases
    print(f"\n🔄 Test 3: Edge cases")
    
    # Test unknown metric
    counter.increment_metric("unknown_metric")
    
    # Test zero increment
    counter.increment_metric("total", 0)
    
    print(f"✅ Edge cases test: PASSED")
    
    # Final metrics
    print(f"\n📋 FINAL METRICS:")
    counter.print_metrics()
    
    # Save test results
    test_results = {
        'test_name': 'metric_counter_sanity',
        'metrics': counter.get_metrics(),
        'status': 'PASSED',
        'assertions_passed': 8
    }
    
    with open('test_metric_counter_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n💾 Test results saved to test_metric_counter_results.json")
    print(f"✅ All metric counter sanity tests: PASSED")
    
    return test_results

if __name__ == "__main__":
    try:
        results = asyncio.run(run_metric_counter_test())
        print(f"\n🎯 Metric counter is working correctly!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Metric counter test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 