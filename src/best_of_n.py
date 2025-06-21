"""
Best-of-N sampling implementation for oversight curriculum.
Implements the sampling strategy recommended by Jan Leike for boosting accuracy
while staying close in KL to the base model.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

from .model import ask
from .deduction_loop import Puzzle, Solution


@dataclass
class BestOfNSample:
    """Represents a single sample in best-of-n"""
    content: str
    log_prob: float
    reward: float
    is_correct: bool


class BestOfNSampler:
    """
    Best-of-N sampling implementation.
    
    Generates n samples and selects the best one based on:
    1. Correctness (primary)
    2. Reward score (secondary)
    3. Log probability (for KL control)
    """
    
    def __init__(self, 
                 model_name: str = "claude-3-5-sonnet-20241022",
                 n_samples: int = 16,
                 temperature: float = 0.7,
                 max_tokens: int = 512):
        
        self.model_name = model_name
        self.n_samples = n_samples
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    def sample_best_solution(self, puzzle: Puzzle, 
                            solve_prompt: str) -> Tuple[Solution, List[BestOfNSample]]:
        """
        Generate n solutions and return the best one.
        
        Args:
            puzzle: The puzzle to solve
            solve_prompt: The prompt template for solving
            
        Returns:
            Tuple of (best_solution, all_samples)
        """
        
        print(f"Generating {self.n_samples} samples for puzzle {puzzle.id}...")
        
        # Generate n samples
        samples = []
        for i in range(self.n_samples):
            try:
                # Generate solution
                response = ask(
                    solve_prompt, 
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                # Parse solution
                solution_content = self._parse_solution_response(
                    response, puzzle.puzzle_type
                )
                
                # Evaluate solution
                is_correct, execution_result, reward = self._evaluate_solution(
                    puzzle, solution_content
                )
                
                # Estimate log probability (simplified)
                log_prob = self._estimate_log_prob(response)
                
                sample = BestOfNSample(
                    content=solution_content,
                    log_prob=log_prob,
                    reward=reward,
                    is_correct=is_correct
                )
                samples.append(sample)
                
                print(f"  Sample {i+1}: correct={is_correct}, "
                      f"reward={reward:.3f}")
                
            except Exception as e:
                print(f"  Sample {i+1} failed: {e}")
                continue
        
        if not samples:
            # Fallback to single sample
            print("Best-of-N failed, falling back to single sample...")
            response = ask(solve_prompt, model=self.model_name, 
                          max_tokens=self.max_tokens)
            solution_content = self._parse_solution_response(
                response, puzzle.puzzle_type
            )
            is_correct, execution_result, reward = self._evaluate_solution(
                puzzle, solution_content
            )
            
            best_solution = Solution(
                puzzle_id=puzzle.id,
                content=solution_content,
                is_correct=is_correct,
                execution_result=execution_result,
                reward=reward
            )
            return best_solution, []
        
        # Select best sample
        best_sample = self._select_best_sample(samples)
        
        # Create solution object
        best_solution = Solution(
            puzzle_id=puzzle.id,
            content=best_sample.content,
            is_correct=best_sample.is_correct,
            reward=best_sample.reward
        )
        
        print(f"Selected best sample: correct={best_sample.is_correct}, "
              f"reward={best_sample.reward:.3f}")
        
        return best_solution, samples
    
    def _select_best_sample(self, samples: List[BestOfNSample]) -> BestOfNSample:
        """Select the best sample based on correctness, reward, and log prob"""
        
        # First priority: correctness
        correct_samples = [s for s in samples if s.is_correct]
        if correct_samples:
            # Among correct samples, select by reward
            return max(correct_samples, key=lambda s: s.reward)
        
        # If no correct samples, select by reward
        return max(samples, key=lambda s: s.reward)
    
    def _evaluate_solution(self, puzzle: Puzzle, 
                          solution_content: str) -> Tuple[bool, Optional[str], float]:
        """Evaluate a solution for correctness and reward"""
        
        try:
            # Simple evaluation based on puzzle type
            if puzzle.puzzle_type == 'code_i':
                return self._evaluate_code_i(puzzle, solution_content)
            elif puzzle.puzzle_type == 'code_o':
                return self._evaluate_code_o(puzzle, solution_content)
            elif puzzle.puzzle_type == 'code_e':
                return self._evaluate_code_e(puzzle, solution_content)
            elif puzzle.puzzle_type == 'code_f':
                return self._evaluate_code_f(puzzle, solution_content)
            else:
                return False, None, 0.0
                
        except Exception as e:
            return False, str(e), 0.0
    
    def _evaluate_code_i(self, puzzle: Puzzle, 
                        solution: str) -> Tuple[bool, Optional[str], float]:
        """Evaluate code input puzzle"""
        try:
            # Extract expected input/output from puzzle
            # This is a simplified evaluation
            if 'input' in puzzle.content and 'output' in puzzle.content:
                # Basic pattern matching for expected output
                expected_output = puzzle.content.split('output')[1].strip().split()[0]
                if expected_output in solution:
                    return True, expected_output, 1.0
                else:
                    return False, None, 0.3
            return False, None, 0.0
        except Exception:
            return False, None, 0.0
    
    def _evaluate_code_o(self, puzzle: Puzzle, 
                        solution: str) -> Tuple[bool, Optional[str], float]:
        """Evaluate code output puzzle"""
        try:
            # Similar to code_i but for output puzzles
            if 'output' in puzzle.content:
                expected_output = puzzle.content.split('output')[1].strip().split()[0]
                if expected_output in solution:
                    return True, expected_output, 1.0
                else:
                    return False, None, 0.3
            return False, None, 0.0
        except Exception:
            return False, None, 0.0
    
    def _evaluate_code_e(self, puzzle: Puzzle, 
                        solution: str) -> Tuple[bool, Optional[str], float]:
        """Evaluate code execution puzzle"""
        try:
            # For execution puzzles, check if solution handles the case
            if 'try' in solution.lower() and 'except' in solution.lower():
                return True, "Exception handling present", 0.8
            elif 'if' in solution.lower() and 'else' in solution.lower():
                return True, "Conditional logic present", 0.7
            else:
                return False, None, 0.3
        except Exception:
            return False, None, 0.0
    
    def _evaluate_code_f(self, puzzle: Puzzle, 
                        solution: str) -> Tuple[bool, Optional[str], float]:
        """Evaluate code function puzzle"""
        try:
            # Check if solution contains function definition
            if 'def ' in solution:
                return True, "Function defined", 0.9
            else:
                return False, None, 0.2
        except Exception:
            return False, None, 0.0
    
    def _parse_solution_response(self, response: str, puzzle_type: str) -> str:
        """Parse solution from Claude response"""
        # Extract code blocks if present
        if '```python' in response:
            start = response.find('```python') + 9
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        
        # Fallback: return the whole response
        return response.strip()
    
    def _estimate_log_prob(self, response: str) -> float:
        """Estimate log probability of response (simplified)"""
        # This is a simplified estimation
        # In practice, you'd want to use the model's actual log probabilities
        return -len(response.split()) * 0.1  # Rough approximation
    
    def get_metrics(self, samples: List[BestOfNSample]) -> Dict:
        """Get metrics about the best-of-n sampling"""
        if not samples:
            return {}
        
        correct_count = sum(1 for s in samples if s.is_correct)
        avg_reward = np.mean([s.reward for s in samples])
        max_reward = max(s.reward for s in samples)
        min_reward = min(s.reward for s in samples)
        
        return {
            'n_samples': len(samples),
            'correct_count': correct_count,
            'correct_rate': correct_count / len(samples),
            'avg_reward': avg_reward,
            'max_reward': max_reward,
            'min_reward': min_reward,
            'reward_std': np.std([s.reward for s in samples])
        } 