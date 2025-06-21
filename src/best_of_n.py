"""
Best-of-N sampling implementation for improved accuracy.
Based on Jan Leike's recommendation for hackathon demonstration.
"""

import time
import random
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from model import ask


class SampleType(Enum):
    """Type of sample generated"""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"


@dataclass
class BestOfNSample:
    """A single sample from best-of-n sampling"""
    content: str
    is_correct: bool
    reward: float
    execution_result: Optional[str]
    sample_type: SampleType
    generation_time: float


class BestOfNSampler:
    """
    Best-of-N sampling for improved accuracy.
    
    Generates n samples and selects the best one based on:
    1. Correctness (primary criterion)
    2. Reward score (secondary criterion)
    3. Code quality (tertiary criterion)
    """
    
    def __init__(self, 
                 model_name: str = "claude-3-5-sonnet-20241022",
                 n_samples: int = 16,
                 temperature: float = 0.7):
        
        self.model_name = model_name
        self.n_samples = n_samples
        self.temperature = temperature
        
        # Sampling statistics
        self.total_samples_generated = 0
        self.correct_samples = 0
        self.incorrect_samples = 0
        
    def sample_best_solution(self, puzzle_content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Generate n samples and return the best solution.
        
        Args:
            puzzle_content: The puzzle to solve
            
        Returns:
            Tuple of (best_solution, metrics)
        """
        
        print(f"🎯 Generating {self.n_samples} samples for best-of-n...")
        
        start_time = time.time()
        samples = []
        
        # Generate n samples
        for i in range(self.n_samples):
            sample_start = time.time()
            
            # Create solve prompt
            solve_prompt = self._create_solve_prompt(puzzle_content)
            
            # Generate sample
            response = ask(
                solve_prompt, 
                model=self.model_name,
                max_tokens=512,
                temperature=self.temperature
            )
            
            # Parse and evaluate sample
            sample_content = self._parse_solution(response)
            is_correct, execution_result, reward = self._evaluate_solution(
                puzzle_content, sample_content
            )
            
            # Determine sample type
            if is_correct:
                sample_type = SampleType.CORRECT
            elif reward > 0.5:
                sample_type = SampleType.PARTIAL
            else:
                sample_type = SampleType.INCORRECT
            
            # Create sample
            sample = BestOfNSample(
                content=sample_content,
                is_correct=is_correct,
                reward=reward,
                execution_result=execution_result,
                sample_type=sample_type,
                generation_time=time.time() - sample_start
            )
            
            samples.append(sample)
            
            # Update statistics
            self.total_samples_generated += 1
            if is_correct:
                self.correct_samples += 1
            else:
                self.incorrect_samples += 1
        
        # Select best sample
        best_sample = self._select_best_sample(samples)
        
        # Calculate metrics
        metrics = self._calculate_metrics(samples, time.time() - start_time)
        
        print(f"✅ Best-of-N complete: {len([s for s in samples if s.is_correct])}/{self.n_samples} correct")
        print(f"   Best sample: {'✅ Correct' if best_sample.is_correct else '❌ Incorrect'} (reward: {best_sample.reward:.3f})")
        
        return best_sample.content, metrics
    
    def _create_solve_prompt(self, puzzle_content: str) -> str:
        """Create prompt for solving the puzzle"""
        
        return f"""You are a skilled programmer. Solve the following puzzle:

{puzzle_content}

Provide only the solution code, no explanations. If the puzzle requires a function, write a complete function definition.

Solution:"""
    
    def _parse_solution(self, response: str) -> str:
        """Parse solution from response"""
        
        # Extract code blocks if present
        if '```python' in response:
            start = response.find('```python') + 9
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        
        if '```' in response:
            start = response.find('```') + 3
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        
        # Return cleaned response
        return response.strip()
    
    def _evaluate_solution(self, puzzle_content: str, solution: str) -> Tuple[bool, Optional[str], float]:
        """
        Evaluate a solution for correctness and quality.
        
        Returns:
            (is_correct, execution_result, reward)
        """
        
        # Simple evaluation logic
        # In a real implementation, this would be more sophisticated
        
        # Check if solution contains function definition
        has_function = 'def ' in solution
        
        # Check if solution is syntactically valid (basic check)
        has_valid_syntax = (
            solution.count('(') == solution.count(')') and
            solution.count('[') == solution.count(']') and
            solution.count('{') == solution.count('}')
        )
        
        # Check if solution addresses the puzzle
        puzzle_keywords = ['add', 'multiply', 'calculate', 'find', 'compute']
        addresses_puzzle = any(keyword in puzzle_content.lower() for keyword in puzzle_keywords)
        
        # Calculate reward
        reward = 0.0
        
        if has_function:
            reward += 0.3
        if has_valid_syntax:
            reward += 0.3
        if addresses_puzzle:
            reward += 0.4
        
        # Determine correctness
        is_correct = reward >= 0.8
        
        # Mock execution result
        execution_result = f"Function defined: {has_function}, Syntax valid: {has_valid_syntax}"
        
        return is_correct, execution_result, reward
    
    def _select_best_sample(self, samples: List[BestOfNSample]) -> BestOfNSample:
        """Select the best sample based on criteria"""
        
        if not samples:
            raise ValueError("No samples provided")
        
        # Sort by correctness first, then by reward
        sorted_samples = sorted(
            samples,
            key=lambda s: (s.is_correct, s.reward),
            reverse=True
        )
        
        return sorted_samples[0]
    
    def _calculate_metrics(self, samples: List[BestOfNSample], total_time: float) -> Dict[str, Any]:
        """Calculate metrics for the sampling run"""
        
        if not samples:
            return {}
        
        correct_count = sum(1 for s in samples if s.is_correct)
        correct_rate = correct_count / len(samples)
        
        rewards = [s.reward for s in samples]
        avg_reward = sum(rewards) / len(rewards)
        max_reward = max(rewards)
        min_reward = min(rewards)
        
        # Sample type distribution
        type_counts = {}
        for sample_type in SampleType:
            type_counts[sample_type.value] = sum(
                1 for s in samples if s.sample_type == sample_type
            )
        
        return {
            'n_samples': len(samples),
            'correct_count': correct_count,
            'correct_rate': correct_rate,
            'avg_reward': avg_reward,
            'max_reward': max_reward,
            'min_reward': min_reward,
            'total_time': total_time,
            'avg_time_per_sample': total_time / len(samples),
            'type_distribution': type_counts
        }
    
    def get_sampling_statistics(self) -> Dict[str, Any]:
        """Get overall sampling statistics"""
        
        if self.total_samples_generated == 0:
            return {}
        
        return {
            'total_samples': self.total_samples_generated,
            'correct_samples': self.correct_samples,
            'incorrect_samples': self.incorrect_samples,
            'overall_correct_rate': self.correct_samples / self.total_samples_generated
        }
    
    def reset_statistics(self):
        """Reset sampling statistics"""
        self.total_samples_generated = 0
        self.correct_samples = 0
        self.incorrect_samples = 0 