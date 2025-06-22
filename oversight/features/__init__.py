"""
Feature-flagged modules for oversight curriculum.
These modules are loaded conditionally based on feature flags.
"""

from ..core.config import FeatureFlags

# Only import features if they're enabled
if FeatureFlags.is_enabled("HUMANEVAL"):
    try:
        from .humaneval_integration import (
            AsyncHumanEvalRunner,
            ExecutionResult,
            HumanEvalTask,
            calculate_pass_at_k,
            save_results,
        )

        HUMANEVAL_AVAILABLE = True
    except ImportError:
        HUMANEVAL_AVAILABLE = False
else:
    HUMANEVAL_AVAILABLE = False

if FeatureFlags.is_enabled("HHH_FILTER"):
    try:
        from .hhh_filter import HHHFilter, SafetyLevel

        HHH_FILTER_AVAILABLE = True
    except ImportError:
        HHH_FILTER_AVAILABLE = False
else:
    HHH_FILTER_AVAILABLE = False

if FeatureFlags.is_enabled("REFEREE"):
    try:
        from .referee import Referee

        REFEREE_AVAILABLE = True
    except ImportError:
        REFEREE_AVAILABLE = False
else:
    REFEREE_AVAILABLE = False

if FeatureFlags.is_enabled("RED_TEAM"):
    try:
        from .red_team_suite import (
            HarmCategory,
            RedTeamPrompt,
            RedTeamResult,
            RedTeamSuite,
        )

        RED_TEAM_AVAILABLE = True
    except ImportError:
        RED_TEAM_AVAILABLE = False
else:
    RED_TEAM_AVAILABLE = False

__all__ = [
    "FeatureFlags",
    "HUMANEVAL_AVAILABLE",
    "HHH_FILTER_AVAILABLE",
    "REFEREE_AVAILABLE",
    "RED_TEAM_AVAILABLE",
]

# Conditionally add exports based on availability
if HUMANEVAL_AVAILABLE:
    __all__.extend(
        [
            "AsyncHumanEvalRunner",
            "ExecutionResult",
            "HumanEvalTask",
            "calculate_pass_at_k",
            "save_results",
        ]
    )

if HHH_FILTER_AVAILABLE:
    __all__.extend(["HHHFilter", "SafetyLevel"])

if REFEREE_AVAILABLE:
    __all__.append("Referee")

if RED_TEAM_AVAILABLE:
    __all__.extend(
        [
            "RedTeamSuite",
            "RedTeamPrompt",
            "RedTeamResult",
            "HarmCategory",
        ]
    )
