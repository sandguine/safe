"""
Oversight Curriculum - AI Safety & Reasoning System

A unified system for AI safety evaluation using AZR self-play,
best-of-n sampling, and HHH safety filtering.
"""

__version__ = "1.0.0"
__author__ = "Oversight Curriculum Team"
__description__ = "AI Safety & Reasoning System"

# Import main components for easy access
from .runner import OversightRunner, RunnerConfig, ExecutionMode
from .config import load_settings, get_settings
from .errors import OversightError, ModelError, SafetyViolation
from .metrics import MetricsCollector, ComparisonAnalyzer

__all__ = [
    "OversightRunner",
    "RunnerConfig", 
    "ExecutionMode",
    "load_settings",
    "get_settings",
    "OversightError",
    "ModelError",
    "SafetyViolation",
    "MetricsCollector",
    "ComparisonAnalyzer"
] 