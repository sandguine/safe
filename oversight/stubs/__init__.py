"""
Stub implementations for SAFE.
Used when feature flags are disabled to provide mock functionality.
"""

from .model_stub import ask, ask_with_retry

__all__ = ["ask", "ask_with_retry"]
