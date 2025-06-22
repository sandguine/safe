"""
Domain-specific exceptions and error handling for SAFE.
Provides custom exceptions and retry/back-off mechanisms for robust execution.
"""


class OversightError(Exception):
    """Base exception for oversight errors."""


class ModelError(OversightError):
    """Exception for model-related errors."""


class SafetyViolation(OversightError):
    """Exception for safety violations."""
