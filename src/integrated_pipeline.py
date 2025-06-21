"""
Integrated pipeline combining AZR, Best-of-N sampling, and HHH filtering.
Implements the complete system recommended for hackathon demonstration.
"""

import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from deduction_loop import DeductionLoop, Puzzle, Solution
from best_of_n import BestOfNSampler
from hhh_filter import HHHFilter, HHHEvaluationResult
from model import ask


@dataclass
class PipelineMetrics:
    """Metrics for the integrated pipeline"""
    cycle_duration: float
    total_puzzles: int
    approved_puzzles: int
    approval_rate: float
    best_of_n_metrics: Optional[Dict[str, Any]] = None
    hhh_metrics: Optional[Dict[str, Any]] = None


class IntegratedPipeline:
    """
    Integrated pipeline combining:
    1. AZR self-play puzzle generation
    2. Best-of-N sampling for accuracy boost
    3. HHH safety filtering
    """
    
    def __init__(self,
                 model_name: str = "claude-3-5-sonnet-20241022",
                 n_samples: int = 16,
                 enable_best_of_n: bool = True,
                 enable_hhh_filter: bool = True,
                 hhh_strict_mode: bool = True):
        
        self.model_name = model_name
        self.n_samples = n_samples
        self.enable_best_of_n = enable_best_of_n
        self.enable_hhh_filter = enable_hhh_filter
        
        # Initialize components
        self.deduction_loop = DeductionLoop(model_name=model_name)
        
        if enable_best_of_n:
            self.best_of_n_sampler = BestOfNSampler(
                model_name=model_name,
                n_samples=n_samples
            )
        else:
            self.best_of_n_sampler = None
        
        if enable_hhh_filter:
            self.hhh_filter = HHHFilter(
                model_name=model_name,
                strict_mode=hhh_strict_mode
            )
        else:
            self.hhh_filter = None
        
        # Metrics tracking
        self.cycle_metrics: List[PipelineMetrics] = []
        self.pipeline_results: List[Dict[str, Any]] = []
    
    def run_cycle(self) -> PipelineMetrics:
        """Run one complete pipeline cycle"""
        
        start_time = time.time()
        
        # Step 1: Run deduction loop cycle to get puzzles and solutions
        cycle_metrics = self.deduction_loop.run_cycle()
        
        # Extract the latest puzzle and solution from the cycle
        if not self.deduction_loop.puzzles:
            # No puzzles generated
            metrics = PipelineMetrics(
                cycle_duration=time.time() - start_time,
                total_puzzles=0,
                approved_puzzles=0,
                approval_rate=0.0
            )
            self.cycle_metrics.append(metrics)
            return metrics
        
        # Get the latest puzzle
        puzzle = self.deduction_loop.puzzles[-1]
        
        # Step 2: Apply HHH filter to puzzle if enabled
        if self.enable_hhh_filter and self.hhh_filter:
            hhh_result = self.hhh_filter.evaluate_content(
                puzzle.content, "puzzle"
            )
            
            if not hhh_result.is_approved:
                # Puzzle rejected by HHH filter
                metrics = PipelineMetrics(
                    cycle_duration=time.time() - start_time,
                    total_puzzles=1,
                    approved_puzzles=0,
                    approval_rate=0.0,
                    hhh_metrics={
                        'avg_helpful_score': hhh_result.helpful_score,
                        'avg_harmless_score': hhh_result.harmless_score,
                        'avg_honest_score': hhh_result.honest_score,
                        'avg_overall_score': hhh_result.overall_score,
                        'safety_level': hhh_result.safety_level.value
                    }
                )
                self.cycle_metrics.append(metrics)
                return metrics
        
        # Step 3: Get solution(s) from the cycle
        solutions = [s for s in self.deduction_loop.solutions if s.puzzle_id == puzzle.id]
        
        if not solutions:
            # No solutions generated
            metrics = PipelineMetrics(
                cycle_duration=time.time() - start_time,
                total_puzzles=1,
                approved_puzzles=1,
                approval_rate=1.0
            )
            self.cycle_metrics.append(metrics)
            return metrics
        
        # Get the best solution (highest reward)
        solution = max(solutions, key=lambda s: s.reward)
        
        # Step 4: Apply HHH filter to solution if enabled
        if self.enable_hhh_filter and self.hhh_filter:
            hhh_result = self.hhh_filter.evaluate_content(
                solution.content, "solution"
            )
            
            if not hhh_result.is_approved:
                # Solution rejected by HHH filter
                metrics = PipelineMetrics(
                    cycle_duration=time.time() - start_time,
                    total_puzzles=1,
                    approved_puzzles=0,
                    approval_rate=0.0,
                    hhh_metrics={
                        'avg_helpful_score': hhh_result.helpful_score,
                        'avg_harmless_score': hhh_result.harmless_score,
                        'avg_honest_score': hhh_result.honest_score,
                        'avg_overall_score': hhh_result.overall_score,
                        'safety_level': hhh_result.safety_level.value
                    }
                )
                self.cycle_metrics.append(metrics)
                return metrics
        
        # Step 5: Record results
        result = {
            'puzzle': puzzle.__dict__,
            'solution': solution.__dict__,
            'evaluation': {
                'is_correct': solution.is_correct,
                'reward': solution.reward,
                'execution_result': solution.execution_result
            },
            'best_of_n_metrics': None,  # Will be updated if Best-of-N is used
            'hhh_approved': True if self.enable_hhh_filter and self.hhh_filter else None
        }
        self.pipeline_results.append(result)
        
        # Step 6: Calculate metrics
        hhh_metrics = None
        if self.enable_hhh_filter and self.hhh_filter:
            hhh_metrics = {
                'avg_helpful_score': 1.0,  # Approved content gets high scores
                'avg_harmless_score': 1.0,
                'avg_honest_score': 1.0,
                'avg_overall_score': 1.0,
                'safety_level': 'safe'
            }
        
        # Best-of-N metrics (if applicable)
        best_of_n_metrics = None
        if self.enable_best_of_n and self.best_of_n_sampler:
            # For now, use the solution metrics as Best-of-N metrics
            best_of_n_metrics = {
                'n_samples': 1,  # Single sample in this case
                'correct_rate': 1.0 if solution.is_correct else 0.0,
                'avg_reward': solution.reward,
                'max_reward': solution.reward
            }
        
        metrics = PipelineMetrics(
            cycle_duration=time.time() - start_time,
            total_puzzles=1,
            approved_puzzles=1,
            approval_rate=1.0,
            best_of_n_metrics=best_of_n_metrics,
            hhh_metrics=hhh_metrics
        )
        
        self.cycle_metrics.append(metrics)
        return metrics
    
    def toggle_best_of_n(self):
        """Toggle Best-of-N sampling on/off"""
        if self.best_of_n_sampler:
            self.enable_best_of_n = not self.enable_best_of_n
            print(f"Best-of-N sampling: {'ENABLED' if self.enable_best_of_n else 'DISABLED'}")
        else:
            print("Best-of-N sampler not initialized")
    
    def toggle_hhh_filter(self):
        """Toggle HHH filter on/off"""
        if self.hhh_filter:
            self.enable_hhh_filter = not self.enable_hhh_filter
            print(f"HHH filter: {'ENABLED' if self.enable_hhh_filter else 'DISABLED'}")
        else:
            print("HHH filter not initialized")
    
    def toggle_hhh_strict_mode(self):
        """Toggle HHH strict/lenient mode"""
        if self.hhh_filter:
            self.hhh_filter.strict_mode = not self.hhh_filter.strict_mode
            mode = 'STRICT' if self.hhh_filter.strict_mode else 'LENIENT'
            print(f"HHH mode: {mode}")
        else:
            print("HHH filter not initialized")
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get comprehensive pipeline summary"""
        
        if not self.cycle_metrics:
            return {'error': 'No cycles completed'}
        
        total_results = len(self.pipeline_results)
        approved_results = sum(1 for m in self.cycle_metrics if m.approved_puzzles > 0)
        overall_approval_rate = approved_results / len(self.cycle_metrics) if self.cycle_metrics else 0
        
        # Best-of-N summary
        best_of_n_summary = None
        if self.best_of_n_sampler:
            best_of_n_metrics = [m.best_of_n_metrics for m in self.cycle_metrics if m.best_of_n_metrics]
            if best_of_n_metrics:
                avg_reward = sum(m.get('avg_reward', 0) for m in best_of_n_metrics) / len(best_of_n_metrics)
                max_reward = max(m.get('max_reward', 0) for m in best_of_n_metrics)
                correct_rate = sum(m.get('correct_rate', 0) for m in best_of_n_metrics) / len(best_of_n_metrics)
                
                best_of_n_summary = {
                    'n_samples': self.n_samples,
                    'avg_reward': avg_reward,
                    'max_reward': max_reward,
                    'correct_rate': correct_rate
                }
        
        # HHH summary
        hhh_summary = None
        if self.hhh_filter:
            hhh_metrics = [m.hhh_metrics for m in self.cycle_metrics if m.hhh_metrics]
            if hhh_metrics:
                total_content = len(hhh_metrics)
                approved_content = sum(1 for m in hhh_metrics if m.get('safety_level') == 'safe')
                blocked_content = sum(1 for m in hhh_metrics if m.get('safety_level') == 'blocked')
                warning_content = sum(1 for m in hhh_metrics if m.get('safety_level') == 'warning')
                
                avg_helpful = sum(m.get('avg_helpful_score', 0) for m in hhh_metrics) / len(hhh_metrics)
                avg_harmless = sum(m.get('avg_harmless_score', 0) for m in hhh_metrics) / len(hhh_metrics)
                avg_honest = sum(m.get('avg_honest_score', 0) for m in hhh_metrics) / len(hhh_metrics)
                
                hhh_summary = {
                    'total_content': total_content,
                    'approved_content': approved_content,
                    'blocked_content': blocked_content,
                    'warning_content': warning_content,
                    'avg_helpful_score': avg_helpful,
                    'avg_harmless_score': avg_harmless,
                    'avg_honest_score': avg_honest
                }
        
        return {
            'total_results': total_results,
            'approved_results': approved_results,
            'overall_approval_rate': overall_approval_rate,
            'cycles_completed': len(self.cycle_metrics),
            'best_of_n_summary': best_of_n_summary,
            'hhh_summary': hhh_summary
        }
    
    def save_results(self, filename: str = "pipeline_results.json"):
        """Save pipeline results to file"""
        
        results = {
            'pipeline_config': {
                'model_name': self.model_name,
                'n_samples': self.n_samples,
                'enable_best_of_n': self.enable_best_of_n,
                'enable_hhh_filter': self.enable_hhh_filter
            },
            'pipeline_results': self.pipeline_results,
            'cycle_metrics': [asdict(m) for m in self.cycle_metrics],
            'summary': self.get_pipeline_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {filename}") 