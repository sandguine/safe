"""
Integrated pipeline combining AZR, best-of-n sampling, and HHH filtering.
Implements the complete pipeline recommended for the hackathon demo.
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .deduction_loop import DeductionLoop, Puzzle, Solution
from .best_of_n import BestOfNSampler, BestOfNSample
from .hhh_filter import HHHFilter, HHHResult, SafetyLevel
from .model import ask


@dataclass
class PipelineResult:
    """Result from the integrated pipeline"""
    puzzle: Puzzle
    solution: Solution
    best_of_n_samples: List[BestOfNSample]
    hhh_result: HHHResult
    final_approved: bool
    pipeline_metrics: Dict


class IntegratedPipeline:
    """
    Integrated pipeline: AZR → Best-of-N → HHH Filter
    
    This implements the complete pipeline recommended for the hackathon:
    1. AZR generates puzzles and solutions
    2. Best-of-N sampling improves solution quality
    3. HHH filter ensures safety and appropriateness
    """
    
    def __init__(self,
                 model_name: str = "claude-3-5-sonnet-20241022",
                 n_samples: int = 16,
                 enable_best_of_n: bool = True,
                 enable_hhh_filter: bool = True,
                 hhh_strict_mode: bool = True):
        
        self.model_name = model_name
        self.enable_best_of_n = enable_best_of_n
        self.enable_hhh_filter = enable_hhh_filter
        
        # Initialize components
        self.azr_loop = DeductionLoop(
            model_name=model_name,
            enable_referee=False,  # We'll use HHH filter instead
            max_puzzles_per_cycle=2,
            max_solutions_per_puzzle=1
        )
        
        self.best_of_n_sampler = BestOfNSampler(
            model_name=model_name,
            n_samples=n_samples
        ) if enable_best_of_n else None
        
        self.hhh_filter = HHHFilter(
            model_name=model_name,
            strict_mode=hhh_strict_mode
        ) if enable_hhh_filter else None
        
        # Pipeline state
        self.cycle_count = 0
        self.results: List[PipelineResult] = []
        
    def run_cycle(self) -> Dict:
        """Run one complete pipeline cycle"""
        
        self.cycle_count += 1
        print(f"\n🔄 Pipeline Cycle {self.cycle_count}")
        print("=" * 50)
        
        cycle_start = time.time()
        cycle_results = []
        
        # Step 1: AZR generates puzzles
        print("📝 Step 1: AZR Puzzle Generation")
        puzzles = self._generate_puzzles()
        
        for puzzle in puzzles:
            print(f"\n--- Processing Puzzle: {puzzle.id} ---")
            
            # Step 2: Best-of-N sampling for solutions
            if self.enable_best_of_n and self.best_of_n_sampler:
                print("🎯 Step 2: Best-of-N Sampling")
                solution, samples = self._best_of_n_solve(puzzle)
            else:
                print("🎯 Step 2: Single Solution Generation")
                solution, samples = self._single_solve(puzzle)
            
            # Step 3: HHH filtering
            if self.enable_hhh_filter and self.hhh_filter:
                print("🛡️  Step 3: HHH Safety Filter")
                hhh_result = self._hhh_filter_content(solution.content)
            else:
                print("🛡️  Step 3: HHH Filter Disabled")
                hhh_result = self._create_default_hhh_result()
            
            # Determine final approval
            final_approved = hhh_result.is_approved if self.enable_hhh_filter else True
            
            # Create pipeline result
            result = PipelineResult(
                puzzle=puzzle,
                solution=solution,
                best_of_n_samples=samples,
                hhh_result=hhh_result,
                final_approved=final_approved,
                pipeline_metrics=self._compute_pipeline_metrics(samples, hhh_result)
            )
            
            cycle_results.append(result)
            self.results.append(result)
            
            # Print result summary
            self._print_result_summary(result)
        
        # Compute cycle metrics
        cycle_metrics = self._compute_cycle_metrics(cycle_results)
        cycle_metrics['cycle_duration'] = time.time() - cycle_start
        
        print(f"\n✅ Cycle {self.cycle_count} completed in {cycle_metrics['cycle_duration']:.2f}s")
        
        return cycle_metrics
    
    def _generate_puzzles(self) -> List[Puzzle]:
        """Generate puzzles using AZR"""
        # Use the existing AZR puzzle generation
        return self.azr_loop._propose_phase()
    
    def _best_of_n_solve(self, puzzle: Puzzle) -> Tuple[Solution, List[BestOfNSample]]:
        """Solve puzzle using best-of-n sampling"""
        # Create solve prompt based on puzzle type
        solve_prompt = self._create_solve_prompt(puzzle)
        
        # Use best-of-n sampler
        solution, samples = self.best_of_n_sampler.sample_best_solution(
            puzzle, solve_prompt
        )
        
        return solution, samples
    
    def _single_solve(self, puzzle: Puzzle) -> Tuple[Solution, List[BestOfNSample]]:
        """Solve puzzle using single generation (fallback)"""
        solve_prompt = self._create_solve_prompt(puzzle)
        
        # Generate single solution
        response = ask(solve_prompt, model=self.model_name, max_tokens=512)
        solution_content = self._parse_solution_response(response, puzzle.puzzle_type)
        
        # Evaluate solution
        is_correct, execution_result, reward = self._evaluate_solution(puzzle, solution_content)
        
        solution = Solution(
            puzzle_id=puzzle.id,
            content=solution_content,
            is_correct=is_correct,
            execution_result=execution_result,
            reward=reward
        )
        
        return solution, []
    
    def _hhh_filter_content(self, content: str) -> HHHResult:
        """Apply HHH filter to content"""
        return self.hhh_filter.evaluate_content(content, "code")
    
    def _create_default_hhh_result(self) -> HHHResult:
        """Create default HHH result when filter is disabled"""
        from .hhh_filter import HHHResult, SafetyLevel
        
        return HHHResult(
            is_approved=True,
            safety_level=SafetyLevel.SAFE,
            helpful_score=0.8,
            harmless_score=0.9,
            honest_score=0.8,
            overall_score=0.83,
            feedback="HHH filter disabled"
        )
    
    def _create_solve_prompt(self, puzzle: Puzzle) -> str:
        """Create solve prompt based on puzzle type"""
        if puzzle.puzzle_type == 'code_i':
            return self.azr_loop._create_code_i_solve_prompt(puzzle.content)
        elif puzzle.puzzle_type == 'code_o':
            return self.azr_loop._create_code_o_solve_prompt(puzzle.content)
        elif puzzle.puzzle_type == 'code_e':
            return self.azr_loop._create_code_e_solve_prompt(puzzle.content)
        elif puzzle.puzzle_type == 'code_f':
            return self.azr_loop._create_code_f_solve_prompt(puzzle.content)
        else:
            return f"Solve this puzzle:\n{puzzle.content}"
    
    def _parse_solution_response(self, response: str, puzzle_type: str) -> str:
        """Parse solution from response"""
        if '```python' in response:
            start = response.find('```python') + 9
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        return response.strip()
    
    def _evaluate_solution(self, puzzle: Puzzle, solution: str) -> Tuple[bool, Optional[str], float]:
        """Evaluate solution (simplified)"""
        # Use the same evaluation logic as best-of-n sampler
        if self.best_of_n_sampler:
            return self.best_of_n_sampler._evaluate_solution(puzzle, solution)
        else:
            # Simple evaluation
            if 'def ' in solution:
                return True, "Function defined", 0.8
            else:
                return False, None, 0.3
    
    def _compute_pipeline_metrics(self, samples: List[BestOfNSample], 
                                hhh_result: HHHResult) -> Dict:
        """Compute metrics for pipeline result"""
        metrics = {}
        
        # Best-of-N metrics
        if samples:
            best_of_n_metrics = self.best_of_n_sampler.get_metrics(samples)
            metrics.update(best_of_n_metrics)
        
        # HHH metrics
        metrics.update({
            'hhh_helpful_score': hhh_result.helpful_score,
            'hhh_harmless_score': hhh_result.harmless_score,
            'hhh_honest_score': hhh_result.honest_score,
            'hhh_overall_score': hhh_result.overall_score,
            'hhh_approved': hhh_result.is_approved,
            'safety_level': hhh_result.safety_level.value
        })
        
        return metrics
    
    def _compute_cycle_metrics(self, cycle_results: List[PipelineResult]) -> Dict:
        """Compute metrics for the entire cycle"""
        if not cycle_results:
            return {}
        
        total_puzzles = len(cycle_results)
        approved_puzzles = [r for r in cycle_results if r.final_approved]
        
        # Best-of-N metrics
        all_samples = []
        for result in cycle_results:
            all_samples.extend(result.best_of_n_samples)
        
        best_of_n_metrics = {}
        if all_samples and self.best_of_n_sampler:
            best_of_n_metrics = self.best_of_n_sampler.get_metrics(all_samples)
        
        # HHH metrics
        hhh_results = [r.hhh_result for r in cycle_results]
        hhh_metrics = {}
        if hhh_results and self.hhh_filter:
            hhh_metrics = self.hhh_filter.get_safety_report(hhh_results)
        
        return {
            'total_puzzles': total_puzzles,
            'approved_puzzles': len(approved_puzzles),
            'approval_rate': len(approved_puzzles) / total_puzzles,
            'best_of_n_metrics': best_of_n_metrics,
            'hhh_metrics': hhh_metrics
        }
    
    def _print_result_summary(self, result: PipelineResult):
        """Print summary of pipeline result"""
        print(f"📊 Result Summary:")
        print(f"  Puzzle: {result.puzzle.id} ({result.puzzle.puzzle_type})")
        print(f"  Solution: {'✅ Correct' if result.solution.is_correct else '❌ Incorrect'}")
        print(f"  Reward: {result.solution.reward:.3f}")
        
        if result.best_of_n_samples:
            print(f"  Best-of-N: {len(result.best_of_n_samples)} samples, "
                  f"{sum(1 for s in result.best_of_n_samples if s.is_correct)} correct")
        
        print(f"  HHH: {result.hhh_result.feedback}")
        print(f"  Final: {'✅ APPROVED' if result.final_approved else '❌ REJECTED'}")
        
        if not result.final_approved and result.hhh_result.refusal_reason:
            print(f"  Reason: {result.hhh_result.refusal_reason}")
    
    def toggle_best_of_n(self, enable: bool = None):
        """Toggle best-of-n sampling"""
        if enable is not None:
            self.enable_best_of_n = enable
        else:
            self.enable_best_of_n = not self.enable_best_of_n
        
        print(f"Best-of-N: {'ENABLED' if self.enable_best_of_n else 'DISABLED'}")
    
    def toggle_hhh_filter(self, enable: bool = None):
        """Toggle HHH filter"""
        if enable is not None:
            self.enable_hhh_filter = enable
        else:
            self.enable_hhh_filter = not self.enable_hhh_filter
        
        print(f"HHH Filter: {'ENABLED' if self.enable_hhh_filter else 'DISABLED'}")
    
    def toggle_hhh_strict_mode(self):
        """Toggle HHH strict mode"""
        if self.hhh_filter:
            self.hhh_filter.toggle_strict_mode()
    
    def get_pipeline_summary(self) -> Dict:
        """Get summary of all pipeline results"""
        if not self.results:
            return {}
        
        total_results = len(self.results)
        approved_results = [r for r in self.results if r.final_approved]
        
        # Collect all samples and HHH results
        all_samples = []
        all_hhh_results = []
        
        for result in self.results:
            all_samples.extend(result.best_of_n_samples)
            all_hhh_results.append(result.hhh_result)
        
        # Compute metrics
        best_of_n_summary = {}
        if all_samples and self.best_of_n_sampler:
            best_of_n_summary = self.best_of_n_sampler.get_metrics(all_samples)
        
        hhh_summary = {}
        if all_hhh_results and self.hhh_filter:
            hhh_summary = self.hhh_filter.get_safety_report(all_hhh_results)
        
        return {
            'total_results': total_results,
            'approved_results': len(approved_results),
            'overall_approval_rate': len(approved_results) / total_results,
            'best_of_n_summary': best_of_n_summary,
            'hhh_summary': hhh_summary,
            'cycles_completed': self.cycle_count
        } 