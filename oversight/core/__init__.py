"""
Core SAFE modules.
These modules are always loaded and provide the essential functionality.
"""

from .config import (
    COLLUSION_MITIGATION_ENABLED,  # Feature flag constants
    ENHANCED_AZR_ENABLED,
    HHH_FILTER_ENABLED,
    HUMANEVAL_ENABLED,
    KL_ANALYSIS_ENABLED,
    RED_TEAM_ENABLED,
    REFEREE_ENABLED,
    TRANSPARENCY_ENABLED,
    VALIDATION_ENABLED,
    ExecutionConfig,
    FeatureFlags,
    ModelConfig,
    OversightConfig,
    SafetyConfig,
    get_execution_config,
    get_settings,
    load_settings,
)
from .deduction_loop import DeductionLoop
from .errors import ModelError, OversightError, SafetyViolation
from .metrics import ExperimentMetrics, MetricsCollector, Summary
from .model import ask, ask_with_retry

__all__ = [
    # Configuration
    "FeatureFlags",
    "ModelConfig",
    "SafetyConfig",
    "ExecutionConfig",
    "OversightConfig",
    "load_settings",
    "get_settings",
    "get_execution_config",
    # Feature flags
    "HUMANEVAL_ENABLED",
    "HHH_FILTER_ENABLED",
    "RED_TEAM_ENABLED",
    "REFEREE_ENABLED",
    "ENHANCED_AZR_ENABLED",
    "TRANSPARENCY_ENABLED",
    "VALIDATION_ENABLED",
    "COLLUSION_MITIGATION_ENABLED",
    "KL_ANALYSIS_ENABLED",
    # Core functionality
    "OversightError",
    "ModelError",
    "SafetyViolation",
    "MetricsCollector",
    "ExperimentMetrics",
    "Summary",
    "DeductionLoop",
    "ask",
    "ask_with_retry",
]
