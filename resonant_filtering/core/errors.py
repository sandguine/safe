"""
Error handling for resonant filtering framework.
"""


class ResonantFilteringError(Exception):
    """Base exception for resonant filtering errors."""


class ModelError(ResonantFilteringError):
    """Error related to model operations."""


class SafetyViolation(ResonantFilteringError):
    """Error when safety constraints are violated."""
