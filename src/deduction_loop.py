"""
Deduction loop for oversight curriculum.
Implements the core deduction and oversight mechanism.
"""

import json
import time
import logging
import re
from typing import Dict, List, Optional, Tuple

from model import ask
from referee import Referee
from metrics import MetricsCollector
from models import Puzzle, Solution


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
        
        # Evaluate solution
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
        """Evaluate a solution for correctness and reward"""
        
        # Simple evaluation - in practice, this would be more sophisticated
        # For now, just check if the solution contains expected patterns
        
        is_correct = False
        execution_result = "Solution generated"
        reward = 0.0
        
        # Basic correctness check based on puzzle type
        if puzzle.puzzle_type == 'code_i':
            # Check if solution contains input handling
            if 'input(' in solution.lower() or 'sys.argv' in solution:
                is_correct = True
                reward = 0.8
        elif puzzle.puzzle_type == 'code_o':
            # Check if solution contains output
            if 'print(' in solution.lower():
                is_correct = True
                reward = 0.7
        elif puzzle.puzzle_type == 'code_e':
            # Check if solution contains error handling
            if 'try:' in solution.lower() or 'except' in solution.lower():
                is_correct = True
                reward = 0.9
        elif puzzle.puzzle_type == 'code_f':
            # Check if solution contains function definition
            if 'def ' in solution.lower():
                is_correct = True
                reward = 0.8
        
        return is_correct, execution_result, reward
    
    def _compute_cycle_metrics(self, new_puzzles: List[Puzzle], new_solutions: List[Solution]) -> Dict:
        """Compute metrics for the current cycle"""
        
        total_puzzles = len(self.puzzles)
        approved_puzzles = sum(1 for p in self.puzzles if p.is_approved)
        total_solutions = len(self.solutions)
        correct_solutions = sum(1 for s in self.solutions if s.is_correct)
        
        return {
            'cycle_number': self.cycle_count,
            'new_puzzles': len(new_puzzles),
            'new_solutions': len(new_solutions),
            'total_puzzles': total_puzzles,
            'approved_puzzles': approved_puzzles,
            'approval_rate': approved_puzzles / total_puzzles if total_puzzles > 0 else 0.0,
            'total_solutions': total_solutions,
            'correct_solutions': correct_solutions,
            'accuracy': correct_solutions / total_solutions if total_solutions > 0 else 0.0,
            'avg_reward': sum(s.reward for s in self.solutions) / total_solutions if total_solutions > 0 else 0.0
        }
    
    def _create_code_i_prompt(self) -> str:
        """Create prompt for code input puzzle"""
        return """Generate a Python programming puzzle that requires handling user input.
The puzzle should be clear, educational, and appropriate for learning.
Focus on input validation, type conversion, or interactive programs.
Return only the puzzle description, no code solution."""

    def _create_code_o_prompt(self) -> str:
        """Create prompt for code output puzzle"""
        return """Generate a Python programming puzzle that focuses on output formatting.
The puzzle should be clear, educational, and appropriate for learning.
Focus on string formatting, data display, or report generation.
Return only the puzzle description, no code solution."""

    def _create_code_e_prompt(self) -> str:
        """Create prompt for code error handling puzzle"""
        return """Generate a Python programming puzzle that requires error handling.
The puzzle should be clear, educational, and appropriate for learning.
Focus on try-catch blocks, input validation, or robust programming.
Return only the puzzle description, no code solution."""

    def _create_code_f_prompt(self) -> str:
        """Create prompt for code function puzzle"""
        return """Generate a Python programming puzzle that requires writing functions.
The puzzle should be clear, educational, and appropriate for learning.
Focus on function design, parameters, return values, or algorithms.
Return only the puzzle description, no code solution."""

    def _create_code_i_solve_prompt(self, puzzle_content: str) -> str:
        """Create solve prompt for code input puzzle"""
        return f"Solve this Python puzzle about input handling:\n\n{puzzle_content}\n\nProvide a complete Python solution:"

    def _create_code_o_solve_prompt(self, puzzle_content: str) -> str:
        """Create solve prompt for code output puzzle"""
        return f"Solve this Python puzzle about output formatting:\n\n{puzzle_content}\n\nProvide a complete Python solution:"

    def _create_code_e_solve_prompt(self, puzzle_content: str) -> str:
        """Create solve prompt for code error handling puzzle"""
        return f"Solve this Python puzzle about error handling:\n\n{puzzle_content}\n\nProvide a complete Python solution:"

    def _create_code_f_solve_prompt(self, puzzle_content: str) -> str:
        """Create solve prompt for code function puzzle"""
        return f"Solve this Python puzzle about functions:\n\n{puzzle_content}\n\nProvide a complete Python solution:"

    def _parse_puzzle_response(self, response: str, puzzle_type: str) -> str:
        """Parse puzzle response from Claude"""
        # Simple parsing - just return the response
        # In practice, this would be more sophisticated
        return response.strip()

    def _parse_solution_response(self, response: str, puzzle_type: str) -> str:
        """Parse solution response from Claude"""
        # Simple parsing - just return the response
        # In practice, this would be more sophisticated
        return response.strip()

    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        return self._compute_cycle_metrics([], [])

    def save_state(self, filepath: str):
        """Save current state to file"""
        state = {
            'cycle_count': self.cycle_count,
            'puzzles': [p.__dict__ for p in self.puzzles],
            'solutions': [s.__dict__ for s in self.solutions]
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self, filepath: str):
        """Load state from file"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.cycle_count = state['cycle_count']
        self.puzzles = [Puzzle(**p) for p in state['puzzles']]
        self.solutions = [Solution(**s) for s in state['solutions']] 