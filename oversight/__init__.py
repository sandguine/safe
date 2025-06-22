"""
Oversight Curriculum - AI Safety & Reasoning System
==================================================

A comprehensive framework for evaluating AI safety through iterative reasoning
and oversight mechanisms.
"""

__version__ = "0.1.0"
__author__ = "Oversight Team"

from .config import get_execution_config, get_settings, load_settings
from .errors import ModelError, OversightError, SafetyViolation
from .metrics import ExperimentMetrics, MetricsCollector

# Import main components for easy access
from .runner import ExecutionMode, OversightRunner, RunnerConfig

__all__ = [
    "OversightRunner",
    "RunnerConfig",
    "ExecutionMode",
    "load_settings",
    "get_settings",
    "get_execution_config",
    "OversightError",
    "ModelError",
    "SafetyViolation",
    "MetricsCollector",
    "ExperimentMetrics",
]
