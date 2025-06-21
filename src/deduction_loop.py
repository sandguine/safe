"""
Core deduction loop implementation for oversight curriculum.
This is a simplified version of the AZR deduction loop that focuses on:
1. PROPOSE: Generate reasoning tasks (code snippets)
2. SOLVE: Attempt to solve self-generated tasks
3. Oversight: Referee system to filter unsafe/trivial content
4. Metrics: Track performance and learning
"""

import os
import sys
import json
import time
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

from model import ask
from referee import Referee
from metrics import MetricsCollector


@dataclass
class Puzzle:
    """Represents a puzzle/task in the deduction loop"""
    id: str
    content: str
    puzzle_type: str  # 'code_i', 'code_o', 'code_e', 'code_f'
    generation_step: int
    is_approved: bool = True
    referee_feedback: str = ""
    complexity_score: float = 0.0
    safety_score: float = 1.0


@dataclass
class Solution:
    """Represents a solution to a puzzle"""
    puzzle_id: str
    content: str
    is_correct: bool
    execution_result: Optional[str] = None
    reward: float = 0.0


class DeductionLoop:
    """
    Core deduction loop implementing the AZR self-play system.
    
    The loop consists of:
    1. PROPOSE phase: Generate puzzles using Claude
    2. SOLVE phase: Solve puzzles using Claude  
    3. Oversight: Referee filters unsafe/trivial content
    4. Metrics: Track performance and learning
    """
    
    def __init__(self, 
                 model_name: str = "claude-3-5-sonnet-20241022",
                 enable_referee: bool = True,
                 max_puzzles_per_cycle: int = 10,
                 max_solutions_per_puzzle: int = 3):
        
        self.model_name = model_name
        self.enable_referee = enable_referee
        self.max_puzzles_per_cycle = max_puzzles_per_cycle
        self.max_solutions_per_puzzle = max_solutions_per_puzzle
        
        # Initialize components
        self.referee = Referee(model_name=model_name) if enable_referee else None
        self.metrics = MetricsCollector()
        
        # State tracking
        self.cycle_count = 0
        self.puzzles: List[Puzzle] = []
        self.solutions: List[Solution] = []
        
        # Config puzzle support (for plan compliance)
        self._use_config_puzzles = False
        self._config_puzzles = []
        self._config_puzzle_index = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def run_cycle(self) -> Dict:
        """
        Run one complete deduction cycle (propose + solve)
        
        Returns:
            Dict containing cycle metrics and results
        """
        self.cycle_count += 1
        self.logger.info(f"Starting deduction cycle {self.cycle_count}")
        
        cycle_start = time.time()
        
        # Phase 1: PROPOSE - Generate puzzles
        self.logger.info("Phase 1: PROPOSE - Generating puzzles...")
        new_puzzles = self._propose_phase()
        
        # Phase 2: SOLVE - Solve puzzles  
        self.logger.info("Phase 2: SOLVE - Solving puzzles...")
        new_solutions = self._solve_phase(new_puzzles)
        
        # Update metrics
        cycle_metrics = self._compute_cycle_metrics(new_puzzles, new_solutions)
        cycle_metrics['cycle_duration'] = time.time() - cycle_start
        
        self.logger.info(f"Cycle {self.cycle_count} completed in {cycle_metrics['cycle_duration']:.2f}s")
        self.logger.info(f"Generated {len(new_puzzles)} puzzles, {len(new_solutions)} solutions")
        
        return cycle_metrics
    
    def _propose_phase(self) -> List[Puzzle]:
        """Generate puzzles using Claude or config"""
        new_puzzles = []
        
        if self._use_config_puzzles and self._config_puzzles:
            # Use hard-coded config puzzles (plan compliance)
            puzzles_to_generate = min(self.max_puzzles_per_cycle, 
                                    len(self._config_puzzles) - self._config_puzzle_index)
            
            for i in range(puzzles_to_generate):
                if self._config_puzzle_index >= len(self._config_puzzles):
                    break
                    
                config_puzzle = self._config_puzzles[self._config_puzzle_index]
                self._config_puzzle_index += 1
                
                puzzle = Puzzle(
                    id=config_puzzle['id'],
                    content=config_puzzle['content'],
                    puzzle_type=config_puzzle['type'],
                    generation_step=self.cycle_count
                )
                
                # Apply referee oversight if enabled
                if self.enable_referee and self.referee:
                    is_approved, feedback, safety_score = self.referee.evaluate_puzzle(puzzle)
                    puzzle.is_approved = is_approved
                    puzzle.referee_feedback = feedback
                    puzzle.safety_score = safety_score
                    
                    if not is_approved:
                        self.logger.info(f"Puzzle rejected by referee: {feedback}")
                        continue
                
                new_puzzles.append(puzzle)
                self.puzzles.append(puzzle)
        else:
            # Use dynamic puzzle generation (original implementation)
            puzzle_types = ['code_i', 'code_o', 'code_e', 'code_f']
            
            for puzzle_type in puzzle_types:
                puzzles_to_generate = self.max_puzzles_per_cycle // len(puzzle_types)
                
                for i in range(puzzles_to_generate):
                    try:
                        puzzle = self._generate_single_puzzle(puzzle_type)
                        if puzzle:
                            new_puzzles.append(puzzle)
                            self.puzzles.append(puzzle)
                    except Exception as e:
                        self.logger.error(f"Failed to generate {puzzle_type} puzzle: {e}")
        
        return new_puzzles
    
    def _generate_single_puzzle(self, puzzle_type: str) -> Optional[Puzzle]:
        """Generate a single puzzle of the specified type"""
        
        # Create prompt based on puzzle type
        if puzzle_type == 'code_i':
            prompt = self._create_code_i_prompt()
        elif puzzle_type == 'code_o':
            prompt = self._create_code_o_prompt()
        elif puzzle_type == 'code_e':
            prompt = self._create_code_e_prompt()
        elif puzzle_type == 'code_f':
            prompt = self._create_code_f_prompt()
        else:
            raise ValueError(f"Unknown puzzle type: {puzzle_type}")
        
        # Generate puzzle using Claude
        response = ask(prompt, model=self.model_name, max_tokens=512)
        
        # Parse response and create puzzle
        puzzle_content = self._parse_puzzle_response(response, puzzle_type)
        if not puzzle_content:
            return None
            
        puzzle = Puzzle(
            id=f"{puzzle_type}_{self.cycle_count}_{len(self.puzzles)}",
            content=puzzle_content,
            puzzle_type=puzzle_type,
            generation_step=self.cycle_count
        )
        
        # Apply referee oversight if enabled
        if self.enable_referee and self.referee:
            is_approved, feedback, safety_score = self.referee.evaluate_puzzle(puzzle)
            puzzle.is_approved = is_approved
            puzzle.referee_feedback = feedback
            puzzle.safety_score = safety_score
            
            if not is_approved:
                self.logger.info(f"Puzzle rejected by referee: {feedback}")
                return None
        
        return puzzle
    
    def _solve_phase(self, puzzles: List[Puzzle]) -> List[Solution]:
        """Solve puzzles using Claude"""
        solutions = []
        
        for puzzle in puzzles:
            if not puzzle.is_approved:
                continue
                
            for i in range(self.max_solutions_per_puzzle):
                try:
                    solution = self._solve_single_puzzle(puzzle)
                    if solution:
                        solutions.append(solution)
                        self.solutions.append(solution)
                except Exception as e:
                    self.logger.error(f"Failed to solve puzzle {puzzle.id}: {e}")
        
        return solutions
    
    def _solve_single_puzzle(self, puzzle: Puzzle) -> Optional[Solution]:
        """Solve a single puzzle"""
        
        # Create solve prompt based on puzzle type
        if puzzle.puzzle_type == 'code_i':
            prompt = self._create_code_i_solve_prompt(puzzle.content)
        elif puzzle.puzzle_type == 'code_o':
            prompt = self._create_code_o_solve_prompt(puzzle.content)
        elif puzzle.puzzle_type == 'code_e':
            prompt = self._create_code_e_solve_prompt(puzzle.content)
        elif puzzle.puzzle_type == 'code_f':
            prompt = self._create_code_f_solve_prompt(puzzle.content)
        else:
            raise ValueError(f"Unknown puzzle type: {puzzle.puzzle_type}")
        
        # Generate solution using Claude
        response = ask(prompt, model=self.model_name, max_tokens=512)
        
        # Parse response and create solution
        solution_content = self._parse_solution_response(response, puzzle.puzzle_type)
        if not solution_content:
            return None
        
        # Evaluate solution (simplified - in real implementation would use code execution)
        is_correct, execution_result, reward = self._evaluate_solution(puzzle, solution_content)
        
        solution = Solution(
            puzzle_id=puzzle.id,
            content=solution_content,
            is_correct=is_correct,
            execution_result=execution_result,
            reward=reward
        )
        
        return solution
    
    def _evaluate_solution(self, puzzle: Puzzle, solution: str) -> Tuple[bool, str, float]:
        """Evaluate a solution (simplified implementation)"""
        # This is a simplified evaluation - in the real AZR system,
        # this would involve actual code execution and testing
        
        # For now, use a simple heuristic based on solution length and content
        if len(solution.strip()) < 10:
            return False, "Solution too short", 0.0
        
        # Check if solution contains code-like patterns
        code_indicators = ['def ', 'return ', 'if ', 'for ', 'while ', 'import ']
        has_code = any(indicator in solution for indicator in code_indicators)
        
        if not has_code:
            return False, "No code detected", 0.0
        
        # Simple reward based on solution quality
        reward = min(1.0, len(solution) / 100.0)  # Normalize by length
        
        return True, "Solution executed successfully", reward
    
    def _compute_cycle_metrics(self, new_puzzles: List[Puzzle], new_solutions: List[Solution]) -> Dict:
        """Compute metrics for the current cycle"""
        metrics = {
            'cycle': self.cycle_count,
            'puzzles_generated': len(new_puzzles),
            'puzzles_approved': len([p for p in new_puzzles if p.is_approved]),
            'puzzles_rejected': len([p for p in new_puzzles if not p.is_approved]),
            'solutions_generated': len(new_solutions),
            'solutions_correct': len([s for s in new_solutions if s.is_correct]),
            'avg_solution_reward': sum(s.reward for s in new_solutions) / max(len(new_solutions), 1),
            'avg_puzzle_safety': sum(p.safety_score for p in new_puzzles) / max(len(new_puzzles), 1),
        }
        
        # Update global metrics
        self.metrics.update(metrics)
        
        return metrics
    
    # Prompt templates for different puzzle types
    def _create_code_i_prompt(self) -> str:
        return """Generate a Python function that takes an input and produces an output. 
        The function should be interesting but not too complex.
        
        Format your response as:
        ```python
        def function_name(input):
            # Your function implementation here
            return output
        ```
        
        Also provide 2-3 example input-output pairs to test the function."""
    
    def _create_code_o_prompt(self) -> str:
        return """Generate a Python function that produces a specific output.
        The function should be interesting and demonstrate good programming practices.
        
        Format your response as:
        ```python
        def function_name():
            # Your function implementation here
            return output
        ```
        
        Also provide the expected output."""
    
    def _create_code_e_prompt(self) -> str:
        return """Generate a Python function that handles errors gracefully.
        The function should demonstrate error handling and edge cases.
        
        Format your response as:
        ```python
        def function_name(input):
            # Your function implementation with error handling
            return output
        ```
        
        Also provide examples of inputs that might cause errors."""
    
    def _create_code_f_prompt(self) -> str:
        return """Generate a complete Python program that solves a specific problem.
        The program should be self-contained and demonstrate good programming practices.
        
        Format your response as:
        ```python
        # Your complete program here
        def main():
            # Main logic
            pass
        
        if __name__ == "__main__":
            main()
        ```
        
        Also provide a brief description of what the program does."""
    
    # Solve prompt templates
    def _create_code_i_solve_prompt(self, puzzle_content: str) -> str:
        return f"""Solve this code puzzle by implementing the function:

{puzzle_content}

Provide your solution in Python code."""
    
    def _create_code_o_solve_prompt(self, puzzle_content: str) -> str:
        return f"""Solve this code puzzle by implementing the function:

{puzzle_content}

Provide your solution in Python code."""
    
    def _create_code_e_solve_prompt(self, puzzle_content: str) -> str:
        return f"""Solve this code puzzle by implementing the function with proper error handling:

{puzzle_content}

Provide your solution in Python code."""
    
    def _create_code_f_solve_prompt(self, puzzle_content: str) -> str:
        return f"""Solve this code puzzle by implementing the complete program:

{puzzle_content}

Provide your solution in Python code."""
    
    def _parse_puzzle_response(self, response: str, puzzle_type: str) -> str:
        """Parse Claude's response to extract puzzle content"""
        # Simple parsing - extract code blocks
        if '```python' in response:
            start = response.find('```python') + 9
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        
        # Fallback: return the whole response
        return response.strip()
    
    def _parse_solution_response(self, response: str, puzzle_type: str) -> str:
        """Parse Claude's response to extract solution content"""
        # Same parsing logic as puzzle response
        return self._parse_puzzle_response(response, puzzle_type)
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics across all cycles"""
        return self.metrics.get_summary()
    
    def save_state(self, filepath: str):
        """Save the current state to a file"""
        state = {
            'cycle_count': self.cycle_count,
            'puzzles': [vars(p) for p in self.puzzles],
            'solutions': [vars(s) for s in self.solutions],
            'metrics': self.metrics.get_all_metrics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str):
        """Load state from a file"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.cycle_count = state['cycle_count']
        self.puzzles = [Puzzle(**p) for p in state['puzzles']]
        self.solutions = [Solution(**s) for s in state['solutions']]
        self.metrics.load_metrics(state['metrics']) 