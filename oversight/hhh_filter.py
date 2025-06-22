"""
Minimal HHH filter stub for MVP demo.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HHHEvaluationResult:
    """Result of HHH evaluation"""

    helpful_score: float
    honest_score: float
    harmless_score: float
    overall_score: float
    is_approved: bool
    refusal_reason: Optional[str] = None
    threshold: float = 0.7


class HHHFilter:
    """Minimal HHH filter stub for MVP demo"""

    def __init__(
        self, model_name: str = "claude-3-5-sonnet-20241022", strict_mode: bool = False
    ):
        self.model_name = model_name
        self.strict_mode = strict_mode

    def evaluate_content(
        self, content: str, content_type: str = "text"
    ) -> HHHEvaluationResult:
        """Stub evaluation - always approves"""
        return HHHEvaluationResult(
            helpful_score=0.8,
            honest_score=0.9,
            harmless_score=0.9,
            overall_score=0.87,
            is_approved=True,
            refusal_reason=None,
            threshold=0.7,
        )
