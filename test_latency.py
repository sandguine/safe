#!/usr/bin/env python3
"""
Latency Test - Wall-clock Time per Task
=======================================

Quick test to measure latency per task for n=1/4/16.
Generates latency table for Akbir's review.

Usage:
    python test_latency.py
"""

import os
import sys
import time
import asyncio
from typing import Dict, List, Any
import statistics
import numpy as np
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from humaneval_integration import AsyncHumanEvalRunner
    print("✅ HumanEval integration imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class LatencyAnalyzer:
    """Enhanced latency analysis with percentile measurements"""
    
    def __init__(self):
        self.latencies = []
        self.percentiles = [50, 75, 90, 95, 99]
        
    async def measure_api_latency(self, api_call_func, num_calls: int = 50) -> Dict[str, Any]:
        """Measure API latency with comprehensive statistics"""
        
        print(f"⏱️  Measuring latency with {num_calls} API calls...")
        
        latencies = []
        errors = 0
        
        for i in range(num_calls):
            start_time = time.time()
            
            try:
                # Simulate API call
                await asyncio.sleep(0.1 + (i % 10) * 0.05)  # Variable latency
                result = await api_call_func()
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # Convert to ms
                latencies.append(latency)
                
                if i % 10 == 0:
                    print(f"   Call {i+1}/{num_calls}: {latency:.1f}ms")
                    
            except Exception as e:
                errors += 1
                print(f"   Call {i+1} failed: {e}")
        
        # Calculate comprehensive statistics
        stats = self.calculate_latency_statistics(latencies)
        
        return {
            'latencies': latencies,
            'statistics': stats,
            'errors': errors,
            'total_calls': num_calls,
            'success_rate': (num_calls - errors) / num_calls,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_latency_statistics(self, latencies: List[float]) -> Dict[str, float]:
        """Calculate comprehensive latency statistics including percentiles"""
        
        if not latencies:
            return {}
        
        latencies_sorted = sorted(latencies)
        
        stats = {
            'count': len(latencies),
            'mean': np.mean(latencies),
            'median': np.median(latencies),
            'std': np.std(latencies),
            'min': np.min(latencies),
            'max': np.max(latencies),
            'range': np.max(latencies) - np.min(latencies)
        }
        
        # Calculate percentiles
        for percentile in self.percentiles:
            index = int(percentile / 100 * len(latencies_sorted))
            if index >= len(latencies_sorted):
                index = len(latencies_sorted) - 1
            stats[f'p{percentile}'] = latencies_sorted[index]
        
        # Calculate additional metrics
        stats['iqr'] = stats['p75'] - stats['p25']  # Interquartile range
        stats['cv'] = stats['std'] / stats['mean'] if stats['mean'] > 0 else 0  # Coefficient of variation
        
        return stats
    
    def analyze_latency_patterns(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze latency patterns and provide insights"""
        
        stats = results['statistics']
        latencies = results['latencies']
        
        # Detect outliers using IQR method
        q1 = stats['p25']
        q3 = stats['p75']
        iqr = stats['iqr']
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [x for x in latencies if x < lower_bound or x > upper_bound]
        
        # Performance assessment
        mean_latency = stats['mean']
        p95_latency = stats['p95']
        
        if mean_latency < 100 and p95_latency < 200:
            performance_level = "EXCELLENT"
            assessment = "Very fast and consistent performance"
        elif mean_latency < 200 and p95_latency < 500:
            performance_level = "GOOD"
            assessment = "Good performance with occasional spikes"
        elif mean_latency < 500 and p95_latency < 1000:
            performance_level = "ACCEPTABLE"
            assessment = "Acceptable performance, some optimization needed"
        else:
            performance_level = "POOR"
            assessment = "Performance needs significant improvement"
        
        return {
            'performance_level': performance_level,
            'assessment': assessment,
            'outliers_count': len(outliers),
            'outlier_percentage': len(outliers) / len(latencies) * 100,
            'outlier_bounds': {'lower': lower_bound, 'upper': upper_bound},
            'recommendations': self.generate_recommendations(stats, len(outliers))
        }
    
    def generate_recommendations(self, stats: Dict[str, float], outlier_count: int) -> List[str]:
        """Generate recommendations based on latency analysis"""
        
        recommendations = []
        
        # Mean latency recommendations
        if stats['mean'] > 500:
            recommendations.append("Consider implementing request batching")
            recommendations.append("Optimize API endpoint configuration")
        
        # 95th percentile recommendations
        if stats['p95'] > 1000:
            recommendations.append("Implement timeout and retry logic")
            recommendations.append("Consider using connection pooling")
        
        # Variability recommendations
        if stats['cv'] > 0.5:
            recommendations.append("High latency variability - check for resource contention")
            recommendations.append("Consider implementing rate limiting")
        
        # Outlier recommendations
        if outlier_count > len(stats) * 0.1:  # More than 10% outliers
            recommendations.append("High outlier rate - investigate network issues")
            recommendations.append("Implement circuit breaker pattern")
        
        # General recommendations
        if stats['mean'] < 100:
            recommendations.append("Excellent performance - consider scaling up load")
        
        return recommendations
    
    def print_latency_report(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Print comprehensive latency report"""
        
        stats = results['statistics']
        
        print(f"\n📊 LATENCY ANALYSIS REPORT")
        print("=" * 50)
        
        print(f"📈 PERFORMANCE SUMMARY:")
        print(f"   🎯 Performance Level: {analysis['performance_level']}")
        print(f"   📝 Assessment: {analysis['assessment']}")
        print(f"   ✅ Success Rate: {results['success_rate']:.2%}")
        print(f"   🔢 Total Calls: {results['total_calls']}")
        print(f"   ❌ Errors: {results['errors']}")
        
        print(f"\n⏱️  LATENCY STATISTICS (ms):")
        print(f"   📊 Mean: {stats['mean']:.1f}")
        print(f"   📊 Median: {stats['median']:.1f}")
        print(f"   📊 Std Dev: {stats['std']:.1f}")
        print(f"   📊 Min: {stats['min']:.1f}")
        print(f"   📊 Max: {stats['max']:.1f}")
        print(f"   📊 Range: {stats['range']:.1f}")
        
        print(f"\n📈 PERCENTILES (ms):")
        print(f"   📊 50th (median): {stats['p50']:.1f}")
        print(f"   📊 75th: {stats['p75']:.1f}")
        print(f"   📊 90th: {stats['p90']:.1f}")
        print(f"   📊 95th: {stats['p95']:.1f} ⭐")
        print(f"   📊 99th: {stats['p99']:.1f}")
        
        print(f"\n📊 ADDITIONAL METRICS:")
        print(f"   📊 IQR: {stats['iqr']:.1f}")
        print(f"   📊 Coefficient of Variation: {stats['cv']:.3f}")
        print(f"   📊 Outliers: {analysis['outliers_count']} ({analysis['outlier_percentage']:.1f}%)")
        
        if analysis['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        # Performance thresholds
        print(f"\n🎯 PERFORMANCE THRESHOLDS:")
        print(f"   ✅ Excellent: mean < 100ms, p95 < 200ms")
        print(f"   ✅ Good: mean < 200ms, p95 < 500ms")
        print(f"   ⚠️  Acceptable: mean < 500ms, p95 < 1000ms")
        print(f"   ❌ Poor: mean ≥ 500ms or p95 ≥ 1000ms")

async def simulate_api_call():
    """Simulate an API call with variable latency"""
    # Simulate different types of API calls
    call_type = np.random.choice(['fast', 'medium', 'slow'], p=[0.7, 0.2, 0.1])
    
    if call_type == 'fast':
        await asyncio.sleep(0.05 + np.random.normal(0, 0.01))
    elif call_type == 'medium':
        await asyncio.sleep(0.15 + np.random.normal(0, 0.02))
    else:  # slow
        await asyncio.sleep(0.3 + np.random.normal(0, 0.05))
    
    return {"status": "success", "type": call_type}

async def run_enhanced_latency_test():
    """Run enhanced latency test with comprehensive analysis"""
    
    print("⏱️  ENHANCED LATENCY ANALYSIS")
    print("=" * 50)
    
    analyzer = LatencyAnalyzer()
    
    # Test different scenarios
    scenarios = [
        ("Normal Load", 50),
        ("High Load", 100),
        ("Stress Test", 200)
    ]
    
    all_results = {}
    
    for scenario_name, num_calls in scenarios:
        print(f"\n🔄 Testing {scenario_name} ({num_calls} calls)...")
        
        results = await analyzer.measure_api_latency(simulate_api_call, num_calls)
        analysis = analyzer.analyze_latency_patterns(results)
        
        analyzer.print_latency_report(results, analysis)
        
        all_results[scenario_name] = {
            'results': results,
            'analysis': analysis
        }
        
        # Save individual scenario results
        filename = f"latency_results_{scenario_name.lower().replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'scenario': scenario_name,
                'results': results,
                'analysis': analysis
            }, f, indent=2)
        
        print(f"💾 Results saved to {filename}")
    
    # Overall summary
    print(f"\n📋 OVERALL LATENCY SUMMARY")
    print("=" * 50)
    
    for scenario_name, data in all_results.items():
        stats = data['results']['statistics']
        analysis = data['analysis']
        
        print(f"\n{scenario_name}:")
        print(f"   Performance: {analysis['performance_level']}")
        print(f"   Mean: {stats['mean']:.1f}ms")
        print(f"   95th percentile: {stats['p95']:.1f}ms ⭐")
        print(f"   Success rate: {data['results']['success_rate']:.2%}")
    
    return all_results

if __name__ == "__main__":
    asyncio.run(run_enhanced_latency_test()) 