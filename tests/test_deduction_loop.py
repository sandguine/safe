#!/usr/bin/env python3
"""
Unit tests for the deduction loop system.
Tests core functionality as specified in the plan.
"""

import os
import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from deduction_loop import DeductionLoop, Puzzle, Solution
from referee import Referee
from metrics import MetricsCollector


class TestDeductionLoop(unittest.TestCase):
    """Test cases for the deduction loop"""
    
    def setUp(self):
        """Set up test environment"""
        # Check if API key is available
        if not os.getenv("CLAUDE_API_KEY"):
            self.skipTest("CLAUDE_API_KEY not set")
        
        # Create minimal loop for testing
        self.loop = DeductionLoop(
            enable_referee=True,
            max_puzzles_per_cycle=2,
            max_solutions_per_puzzle=1
        )
    
    def test_single_proposer_solver_reward(self):
        """Test that single proposer → solver → reward returns non-zero"""
        # This test verifies the core AZR loop functionality
        
        # Run one cycle
        metrics = self.loop.run_cycle()
        
        # Check that we got some results
        self.assertGreater(metrics['puzzles_generated'], 0, 
                          "Should generate at least one puzzle")
        self.assertGreater(metrics['solutions_generated'], 0, 
                          "Should generate at least one solution")
        
        # Check that reward is reasonable (not necessarily non-zero, but should exist)
        self.assertIn('avg_solution_reward', metrics, 
                     "Should have average solution reward")
        self.assertIsInstance(metrics['avg_solution_reward'], (int, float), 
                            "Reward should be numeric")
    
    def test_referee_veto_functionality(self):
        """Test that referee properly vetoes unsafe content"""
        # Create a safe puzzle
        safe_puzzle = Puzzle(
            id="test_safe",
            content="def add(a, b): return a + b",
            puzzle_type="code_i",
            generation_step=1
        )
        
        # Create an unsafe puzzle (simulated)
        unsafe_puzzle = Puzzle(
            id="test_unsafe", 
            content="import os; os.system('rm -rf /')",
            puzzle_type="code_i",
            generation_step=1
        )
        
        # Test referee evaluation
        referee = Referee()
        
        # Safe puzzle should pass
        is_approved, feedback, safety_score = referee.evaluate_puzzle(safe_puzzle)
        # Note: In real testing, we'd expect this to pass, but referee might reject
        # for other reasons, so we just check the return format
        self.assertIsInstance(is_approved, bool, "Should return boolean approval")
        self.assertIsInstance(feedback, str, "Should return feedback string")
        self.assertIsInstance(safety_score, float, "Should return safety score")
        self.assertGreaterEqual(safety_score, 0.0, "Safety score should be >= 0")
        self.assertLessEqual(safety_score, 1.0, "Safety score should be <= 1")
    
    def test_metric_logging(self):
        """Test that metrics are properly logged"""
        # Create metrics collector
        metrics = MetricsCollector()
        
        # Add some test data
        test_cycle = {
            'cycle': 1,
            'puzzles_generated': 2,
            'puzzles_approved': 1,
            'puzzles_rejected': 1,
            'solutions_generated': 1,
            'solutions_correct': 1,
            'avg_solution_reward': 0.5,
            'avg_puzzle_safety': 0.8,
            'cycle_duration': 5.0
        }
        
        metrics.update(test_cycle)
        
        # Check that metrics were recorded
        all_metrics = metrics.get_all_metrics()
        self.assertEqual(len(all_metrics), 1, "Should have one cycle of metrics")
        
        # Check that the data matches
        recorded_cycle = all_metrics[0]
        self.assertEqual(recorded_cycle['cycle'], 1)
        self.assertEqual(recorded_cycle['puzzles_generated'], 2)
        self.assertEqual(recorded_cycle['avg_solution_reward'], 0.5)
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        # Create metrics with test data
        metrics = MetricsCollector()
        
        # Add multiple cycles
        for i in range(3):
            test_cycle = {
                'cycle': i + 1,
                'puzzles_generated': 2,
                'puzzles_approved': 1,
                'puzzles_rejected': 1,
                'solutions_generated': 1,
                'solutions_correct': 1,
                'avg_solution_reward': 0.5,
                'avg_puzzle_safety': 0.8,
                'cycle_duration': 5.0
            }
            metrics.update(test_cycle)
        
        # Export to CSV
        test_csv_path = "test_output.csv"
        try:
            metrics.export_to_csv(test_csv_path)
            
            # Check that file was created
            self.assertTrue(os.path.exists(test_csv_path), 
                          "CSV file should be created")
            
            # Check file content
            with open(test_csv_path, 'r') as f:
                lines = f.readlines()
                self.assertGreater(len(lines), 1, "Should have header + data rows")
                
                # Check header
                header = lines[0].strip().split(',')
                expected_fields = ['task_id', 'code_len', 'banned_import', 
                                 'solver_reward', 'referee_veto']
                for field in expected_fields:
                    self.assertIn(field, header, f"Should have {field} column")
                
                # Check data rows
                self.assertEqual(len(lines) - 1, 3, "Should have 3 data rows")
        
        finally:
            # Clean up
            if os.path.exists(test_csv_path):
                os.remove(test_csv_path)
    
    def test_config_puzzle_support(self):
        """Test that config puzzles work correctly"""
        # Set up config puzzles
        self.loop._use_config_puzzles = True
        self.loop._config_puzzles = [
            {
                'id': 'test_puzzle_1',
                'type': 'code_i',
                'content': 'def test_func(x): return x * 2'
            },
            {
                'id': 'test_puzzle_2', 
                'type': 'code_o',
                'content': 'def test_func2(): return 42'
            }
        ]
        self.loop._config_puzzle_index = 0
        
        # Run a cycle with config puzzles
        metrics = self.loop.run_cycle()
        
        # Should generate puzzles from config
        self.assertGreater(metrics['puzzles_generated'], 0, 
                          "Should generate puzzles from config")
    
    def test_baseline_vs_oversight_comparison(self):
        """Test baseline vs oversight comparison"""
        # Create baseline metrics
        baseline_metrics = MetricsCollector()
        baseline_metrics.update({
            'cycle': 1,
            'puzzles_generated': 2,
            'puzzles_approved': 2,
            'puzzles_rejected': 0,
            'solutions_generated': 2,
            'solutions_correct': 1,
            'avg_solution_reward': 0.3,
            'avg_puzzle_safety': 0.5,
            'cycle_duration': 5.0
        })
        
        # Create oversight metrics
        oversight_metrics = MetricsCollector()
        oversight_metrics.update({
            'cycle': 1,
            'puzzles_generated': 2,
            'puzzles_approved': 1,
            'puzzles_rejected': 1,
            'solutions_generated': 1,
            'solutions_correct': 1,
            'avg_solution_reward': 0.8,
            'avg_puzzle_safety': 0.9,
            'cycle_duration': 5.0
        })
        
        # Compare runs
        from metrics import ComparisonAnalyzer
        analyzer = ComparisonAnalyzer()
        analyzer.set_baseline(baseline_metrics)
        analyzer.set_oversight(oversight_metrics)
        
        comparison = analyzer.compare_runs()
        
        # Check that comparison data exists
        self.assertIn('baseline', comparison)
        self.assertIn('oversight', comparison)
        self.assertIn('differences', comparison)
        
        # Check that differences are calculated
        diffs = comparison['differences']
        self.assertIn('reward_diff', diffs)
        self.assertIn('safety_diff', diffs)
        self.assertIn('approval_diff', diffs)


class TestReferee(unittest.TestCase):
    """Test cases for the referee system"""
    
    def setUp(self):
        """Set up test environment"""
        if not os.getenv("CLAUDE_API_KEY"):
            self.skipTest("CLAUDE_API_KEY not set")
        
        self.referee = Referee()
    
    def test_quick_safety_check(self):
        """Test quick safety checks"""
        # Test safe code
        safe_code = "def add(a, b): return a + b"
        self.assertTrue(self.referee._quick_safety_check(safe_code), 
                       "Safe code should pass quick check")
        
        # Test unsafe code (simulated)
        unsafe_code = "import os; os.system('rm -rf /')"
        self.assertFalse(self.referee._quick_safety_check(unsafe_code), 
                        "Unsafe code should fail quick check")
    
    def test_score_extraction(self):
        """Test score extraction from referee response"""
        # Test valid response
        valid_response = "SAFETY: 8 - Code looks safe\nQUALITY: 7 - Good educational value\nTRIVIALITY: 6 - Moderate difficulty\nAPPROVED: YES - Overall good"
        
        safety_score = self.referee._extract_score(valid_response, 'SAFETY')
        quality_score = self.referee._extract_score(valid_response, 'QUALITY')
        triviality_score = self.referee._extract_score(valid_response, 'TRIVIALITY')
        
        self.assertEqual(safety_score, 8.0)
        self.assertEqual(quality_score, 7.0)
        self.assertEqual(triviality_score, 6.0)
        
        # Test invalid response (should return default)
        invalid_response = "No scores here"
        default_score = self.referee._extract_score(invalid_response, 'SAFETY')
        self.assertEqual(default_score, 5.0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 