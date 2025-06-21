"""
Shared data models for oversight curriculum.
Contains common data structures used across modules.
"""

from dataclasses import dataclass
from typing import Optional


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