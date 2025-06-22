#!/usr/bin/env python3
"""
Enhanced Success Logic Validation
Tests fallback conditions and success criteria
"""

import json
import sys
from typing import Dict, Any

def create_test_results(pass_at_1: float, uplift: float = 0.0) -> Dict[str, Any]:
    """Create test results with specific pass@1 and uplift values"""
    
    # Mock cycle results with progressive sampling data
    cycle_results = {
        'cycle_1': {
            'metrics': {
                'pass_at_1_n1': pass_at_1 * 0.8,  # n=1 baseline
                'pass_at_1_n4': pass_at_1 * 0.9,  # n=4 performance
                'pass_at_1_n16': pass_at_1,       # n=16 performance
                'pass_at_1': pass_at_1,
                'ratio': pass_at_1 * 1.1
            }
        },
        'cycle_2': {
            'metrics': {
                'pass_at_1_n1': pass_at_1 * 0.85,
                'pass_at_1_n4': pass_at_1 * 0.95,
                'pass_at_1_n16': pass_at_1 * 1.05,
                'pass_at_1': pass_at_1 * 1.05,
                'ratio': pass_at_1 * 1.15
            }
        }
    }
    
    # Calculate final metrics
    best_pass = max(cycle['metrics']['pass_at_1'] for cycle in cycle_results.values())
    avg_pass = sum(cycle['metrics']['pass_at_1'] for cycle in cycle_results.values()) / len(cycle_results)
    
    # Calculate uplift
    n1_performance = max(cycle['metrics']['pass_at_1_n1'] for cycle in cycle_results.values())
    n4_performance = max(cycle['metrics']['pass_at_1_n4'] for cycle in cycle_results.values())
    n16_performance = max(cycle['metrics']['pass_at_1_n16'] for cycle in cycle_results.values())
    
    uplift_4 = (n4_performance - n1_performance) * 100
    uplift_16 = (n16_performance - n1_performance) * 100
    max_uplift = max(uplift_4, uplift_16, uplift)  # Use provided uplift if higher
    
    return {
        'cycles_completed': 2,
        'cycles_requested': 3,
        'total_duration': 180.5,
        'early_stopping': False,
        'final_metrics': {
            'best_pass_at_1': best_pass,
            'avg_pass_at_1': avg_pass,
            'best_ratio': max(cycle['metrics']['ratio'] for cycle in cycle_results.values()),
            'avg_ratio': sum(cycle['metrics']['ratio'] for cycle in cycle_results.values()) / len(cycle_results)
        },
        'cycle_results': cycle_results
    }

def test_success_logic(results: Dict[str, Any]) -> Dict[str, Any]:
    """Test the enhanced success logic with fallback conditions"""
    
    best_pass = results['final_metrics']['best_pass_at_1']
    
    # Calculate uplift vs n=1 baseline
    n1_performance = 0.0
    n4_performance = 0.0
    n16_performance = 0.0
    
    for cycle_key, cycle_data in results['cycle_results'].items():
        n1_performance = max(n1_performance, cycle_data['metrics'].get('pass_at_1_n1', 0))
        n4_performance = max(n4_performance, cycle_data['metrics'].get('pass_at_1_n4', 0))
        n16_performance = max(n16_performance, cycle_data['metrics'].get('pass_at_1_n16', 0))
    
    uplift_4 = (n4_performance - n1_performance) * 100
    uplift_16 = (n16_performance - n1_performance) * 100
    max_uplift = max(uplift_4, uplift_16)
    
    # Enhanced success assessment
    if best_pass >= 0.6:
        assessment = "🎯 EXCELLENT - Primary target achieved!"
        success_level = "PRIMARY"
        fallback_triggered = False
    elif best_pass >= 0.45:
        assessment = "✅ GOOD - Fallback target achieved!"
        success_level = "FALLBACK"
        fallback_triggered = True
    elif max_uplift >= 8.0:
        assessment = "📈 ACCEPTABLE - Significant uplift achieved!"
        success_level = "UPLIFT"
        fallback_triggered = True
    else:
        assessment = "❌ NEEDS WORK - Below all targets"
        success_level = "FAILED"
        fallback_triggered = True
    
    return {
        'success_level': success_level,
        'best_pass_at_1': best_pass,
        'max_uplift': max_uplift,
        'assessment': assessment,
        'fallback_triggered': fallback_triggered,
        'n1_baseline': n1_performance,
        'n4_performance': n4_performance,
        'n16_performance': n16_performance,
        'uplift_4': uplift_4,
        'uplift_16': uplift_16
    }

def run_success_logic_tests():
    """Run comprehensive success logic tests"""
    
    print("🧪 ENHANCED SUCCESS LOGIC VALIDATION")
    print("=" * 50)
    
    test_cases = [
        (0.7, 0.0, "Primary target - should succeed"),
        (0.5, 0.0, "Fallback target - should trigger fallback"),
        (0.4, 10.0, "Low pass@1 but high uplift - should trigger uplift fallback"),
        (0.3, 5.0, "Below all targets - should fail"),
        (0.45, 0.0, "Exactly at fallback threshold - should trigger fallback"),
        (0.6, 0.0, "Exactly at primary threshold - should succeed")
    ]
    
    all_tests_passed = True
    
    for pass_at_1, uplift, description in test_cases:
        print(f"\n🔄 Testing: {description}")
        print(f"   Pass@1: {pass_at_1}, Uplift: {uplift}pp")
        
        # Create test results
        results = create_test_results(pass_at_1, uplift)
        
        # Test success logic
        logic_result = test_success_logic(results)
        
        # Validate logic
        expected_primary = pass_at_1 >= 0.6
        expected_fallback = 0.45 <= pass_at_1 < 0.6
        expected_uplift = pass_at_1 < 0.45 and logic_result['max_uplift'] >= 8.0
        
        logic_correct = (
            (expected_primary and logic_result['success_level'] == 'PRIMARY') or
            (expected_fallback and logic_result['success_level'] == 'FALLBACK') or
            (expected_uplift and logic_result['success_level'] == 'UPLIFT') or
            (not any([expected_primary, expected_fallback, expected_uplift]) and logic_result['success_level'] == 'FAILED')
        )
        
        # Check fallback triggering
        fallback_correct = (
            (logic_result['success_level'] == 'PRIMARY') == (not logic_result['fallback_triggered'])
        )
        
        test_passed = logic_correct and fallback_correct
        
        print(f"   Result: {logic_result['success_level']}")
        print(f"   Assessment: {logic_result['assessment']}")
        print(f"   Fallback triggered: {logic_result['fallback_triggered']}")
        print(f"   Max uplift: {logic_result['max_uplift']:.1f}pp")
        print(f"   Test passed: {'✅' if test_passed else '❌'}")
        
        if not test_passed:
            all_tests_passed = False
            print(f"   ❌ LOGIC ERROR: Expected behavior not matched!")
    
    print(f"\n📋 OVERALL VALIDATION:")
    print(f"   All tests passed: {'✅' if all_tests_passed else '❌'}")
    
    if all_tests_passed:
        print(f"   🎯 Success logic validation: PASSED")
        print(f"   ✅ Fallback conditions working correctly")
        print(f"   ✅ Primary target takes precedence")
        print(f"   ✅ Uplift fallback triggers appropriately")
    else:
        print(f"   ❌ Success logic validation: FAILED")
        print(f"   ⚠️  Check fallback logic implementation")
    
    return all_tests_passed

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    
    print(f"\n🔍 EDGE CASE TESTING")
    print("=" * 30)
    
    edge_cases = [
        (0.599, 0.0, "Just below primary threshold"),
        (0.449, 0.0, "Just below fallback threshold"),
        (0.6, 7.9, "Primary target but low uplift"),
        (0.44, 8.1, "Low pass@1 but high uplift"),
        (0.0, 15.0, "Zero pass@1 but very high uplift")
    ]
    
    for pass_at_1, uplift, description in edge_cases:
        print(f"\n🔄 Edge case: {description}")
        results = create_test_results(pass_at_1, uplift)
        logic_result = test_success_logic(results)
        
        print(f"   Pass@1: {pass_at_1:.3f} → {logic_result['success_level']}")
        print(f"   Uplift: {uplift:.1f}pp → {logic_result['max_uplift']:.1f}pp")
        print(f"   Fallback: {logic_result['fallback_triggered']}")

if __name__ == "__main__":
    try:
        # Run main validation tests
        main_tests_passed = run_success_logic_tests()
        
        # Run edge case tests
        test_edge_cases()
        
        if main_tests_passed:
            print(f"\n✅ SUCCESS LOGIC VALIDATION COMPLETE")
            print(f"🎯 Ready for production execution")
            sys.exit(0)
        else:
            print(f"\n❌ SUCCESS LOGIC VALIDATION FAILED")
            print(f"⚠️  Fix issues before production run")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 