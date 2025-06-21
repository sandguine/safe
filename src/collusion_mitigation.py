"""
Collusion mitigation system for AZR oversight curriculum.
Addresses concerns about model collusion and task difficulty drift.
"""

import os
import sys
import random
import hashlib
import time
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from model import ask


class ModelRole(Enum):
    """Different roles for different models"""
    PROPOSER = "proposer"
    SOLVER = "solver"
    REFEREE = "referee"


@dataclass
class CollusionMitigationConfig:
    """Configuration for collusion mitigation"""
    use_different_models: bool = True
    add_random_salt: bool = True
    salt_length: int = 16
    track_difficulty_drift: bool = True
    proposer_model: str = "claude-3-haiku-20240307"
    solver_model: str = "claude-3-5-sonnet-20241022"
    referee_model: str = "claude-3-5-sonnet-20241022"


@dataclass
class DifficultyMetrics:
    """Metrics for tracking task difficulty"""
    cycle: int
    avg_complexity: float
    avg_success_rate: float
    avg_solution_time: float
    difficulty_score: float
    drift_detected: bool


class CollusionMitigator:
    """
    Collusion mitigation system.
    
    Features:
    1. Different Claude versions for different roles
    2. Random salt in prompts to prevent memorization
    3. Task difficulty drift detection
    4. Statistical analysis of performance patterns
    """
    
    def __init__(self, config: CollusionMitigationConfig = None):
        
        self.config = config or CollusionMitigationConfig()
        self.difficulty_history = []
        self.salt_history = []
        
        # Initialize random seed
        random.seed(int(time.time()))
        
    def add_salt_to_prompt(self, prompt: str, role: ModelRole) -> str:
        """Add random salt to prompt to prevent memorization"""
        
        if not self.config.add_random_salt:
            return prompt
        
        # Generate random salt
        salt = self._generate_salt(role)
        self.salt_history.append({
            'timestamp': time.time(),
            'role': role.value,
            'salt': salt
        })
        
        # Add salt to prompt
        salted_prompt = f"{prompt}\n\n[System: {salt}]"
        
        return salted_prompt
    
    def get_model_for_role(self, role: ModelRole) -> str:
        """Get appropriate model for given role"""
        
        if not self.config.use_different_models:
            return "claude-3-5-sonnet-20241022"
        
        model_map = {
            ModelRole.PROPOSER: self.config.proposer_model,
            ModelRole.SOLVER: self.config.solver_model,
            ModelRole.REFEREE: self.config.referee_model
        }
        
        return model_map.get(role, self.config.solver_model)
    
    def track_difficulty_drift(self, 
                              cycle: int,
                              puzzles: List[Dict],
                              solutions: List[Dict]) -> DifficultyMetrics:
        """Track task difficulty drift over time"""
        
        if not self.config.track_difficulty_drift:
            return None
        
        # Calculate complexity metrics
        complexity_scores = []
        success_rates = []
        solution_times = []
        
        for puzzle in puzzles:
            # Complexity based on code length and structure
            complexity = self._calculate_complexity(puzzle.get('content', ''))
            complexity_scores.append(complexity)
        
        for solution in solutions:
            # Success rate
            success_rate = 1.0 if solution.get('is_correct', False) else 0.0
            success_rates.append(success_rate)
            
            # Solution time (if available)
            solution_time = solution.get('generation_time', 1.0)
            solution_times.append(solution_time)
        
        # Calculate averages
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0.0
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
        avg_solution_time = sum(solution_times) / len(solution_times) if solution_times else 0.0
        
        # Calculate overall difficulty score
        difficulty_score = self._calculate_difficulty_score(
            avg_complexity, avg_success_rate, avg_solution_time
        )
        
        # Check for drift
        drift_detected = self._detect_difficulty_drift(difficulty_score)
        
        # Create metrics
        metrics = DifficultyMetrics(
            cycle=cycle,
            avg_complexity=avg_complexity,
            avg_success_rate=avg_success_rate,
            avg_solution_time=avg_solution_time,
            difficulty_score=difficulty_score,
            drift_detected=drift_detected
        )
        
        self.difficulty_history.append(metrics)
        
        return metrics
    
    def _generate_salt(self, role: ModelRole) -> str:
        """Generate random salt for prompt"""
        
        # Create salt based on role and timestamp
        base = f"{role.value}_{int(time.time())}_{random.random()}"
        salt = hashlib.md5(base.encode()).hexdigest()[:self.config.salt_length]
        
        return salt
    
    def _calculate_complexity(self, code: str) -> float:
        """Calculate complexity score for code"""
        
        if not code:
            return 0.0
        
        # Simple complexity metrics
        lines = len(code.split('\n'))
        functions = code.count('def ')
        loops = code.count('for ') + code.count('while ')
        conditionals = code.count('if ') + code.count('elif ') + code.count('else:')
        imports = code.count('import ')
        
        # Weighted complexity score
        complexity = (
            lines * 0.1 +
            functions * 0.3 +
            loops * 0.2 +
            conditionals * 0.15 +
            imports * 0.05
        )
        
        return min(complexity, 10.0)  # Cap at 10.0
    
    def _calculate_difficulty_score(self, 
                                   complexity: float, 
                                   success_rate: float, 
                                   solution_time: float) -> float:
        """Calculate overall difficulty score"""
        
        # Normalize factors
        norm_complexity = complexity / 10.0  # 0-1
        norm_success = 1.0 - success_rate  # Higher success = lower difficulty
        norm_time = min(solution_time / 10.0, 1.0)  # Cap at 10 seconds
        
        # Weighted difficulty score
        difficulty = (
            norm_complexity * 0.4 +
            norm_success * 0.4 +
            norm_time * 0.2
        )
        
        return difficulty
    
    def _detect_difficulty_drift(self, current_difficulty: float) -> bool:
        """Detect if task difficulty is drifting downward"""
        
        if len(self.difficulty_history) < 3:
            return False
        
        # Get recent difficulty scores
        recent_scores = [m.difficulty_score for m in self.difficulty_history[-3:]]
        
        # Check for downward trend
        if len(recent_scores) >= 3:
            trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
            
            # Detect significant downward drift
            return trend < -0.1  # 10% decrease per cycle
        
        return False
    
    def generate_collusion_report(self) -> str:
        """Generate collusion mitigation report"""
        
        report = []
        report.append("COLLUSION MITIGATION REPORT")
        report.append("=" * 40)
        report.append(f"Different Models: {'✅' if self.config.use_different_models else '❌'}")
        report.append(f"Random Salt: {'✅' if self.config.add_random_salt else '❌'}")
        report.append(f"Difficulty Tracking: {'✅' if self.config.track_difficulty_drift else '❌'}")
        report.append("")
        
        if self.config.use_different_models:
            report.append("Model Assignment:")
            report.append(f"  Proposer: {self.config.proposer_model}")
            report.append(f"  Solver: {self.config.solver_model}")
            report.append(f"  Referee: {self.config.referee_model}")
            report.append("")
        
        if self.difficulty_history:
            report.append("Difficulty Drift Analysis:")
            report.append("-" * 25)
            
            for metrics in self.difficulty_history[-5:]:  # Last 5 cycles
                drift_indicator = "⚠️" if metrics.drift_detected else "✅"
                report.append(f"Cycle {metrics.cycle}: {metrics.difficulty_score:.3f} {drift_indicator}")
            
            # Overall trend
            if len(self.difficulty_history) >= 2:
                first_difficulty = self.difficulty_history[0].difficulty_score
                last_difficulty = self.difficulty_history[-1].difficulty_score
                trend = last_difficulty - first_difficulty
                trend_indicator = "↗️" if trend > 0 else "↘️" if trend < 0 else "→"
                report.append(f"Overall Trend: {trend:+.3f} {trend_indicator}")
        
        if self.salt_history:
            report.append(f"\nSalt Usage: {len(self.salt_history)} salts generated")
        
        return "\n".join(report)
    
    def save_mitigation_data(self, filepath: str = "results/collusion_mitigation.json"):
        """Save collusion mitigation data"""
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            'config': {
                'use_different_models': self.config.use_different_models,
                'add_random_salt': self.config.add_random_salt,
                'salt_length': self.config.salt_length,
                'track_difficulty_drift': self.config.track_difficulty_drift,
                'proposer_model': self.config.proposer_model,
                'solver_model': self.config.solver_model,
                'referee_model': self.config.referee_model
            },
            'difficulty_history': [
                {
                    'cycle': m.cycle,
                    'avg_complexity': m.avg_complexity,
                    'avg_success_rate': m.avg_success_rate,
                    'avg_solution_time': m.avg_solution_time,
                    'difficulty_score': m.difficulty_score,
                    'drift_detected': m.drift_detected
                }
                for m in self.difficulty_history
            ],
            'salt_history': self.salt_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Collusion mitigation data saved to {filepath}")
    
    def statistical_drift_test(self) -> Dict[str, Any]:
        """Perform statistical test for task difficulty drift"""
        
        if len(self.difficulty_history) < 5:
            return {'test_performed': False, 'reason': 'Insufficient data'}
        
        difficulties = [m.difficulty_score for m in self.difficulty_history]
        
        # Simple linear regression test
        n = len(difficulties)
        x = list(range(n))
        
        # Calculate slope
        sum_x = sum(x)
        sum_y = sum(difficulties)
        sum_xy = sum(x[i] * difficulties[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Calculate R-squared
        mean_y = sum_y / n
        ss_tot = sum((difficulties[i] - mean_y) ** 2 for i in range(n))
        ss_res = sum((difficulties[i] - (slope * x[i] + (sum_y - slope * sum_x) / n)) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Determine significance
        significant_drift = abs(slope) > 0.05 and r_squared > 0.3
        drift_direction = "downward" if slope < 0 else "upward" if slope > 0 else "stable"
        
        return {
            'test_performed': True,
            'slope': slope,
            'r_squared': r_squared,
            'significant_drift': significant_drift,
            'drift_direction': drift_direction,
            'data_points': n,
            'mean_difficulty': mean_y,
            'difficulty_range': max(difficulties) - min(difficulties)
        } 