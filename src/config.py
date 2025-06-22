"""
Configuration management for oversight curriculum.
Uses Pydantic for type-safe configuration loading and validation.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import yaml
from pydantic import BaseSettings, Field, validator


class ModelConfig(BaseSettings):
    """Model configuration settings"""
    name: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 512
    temperature: float = 0.7
    timeout_seconds: int = 30


class ExecutionModeConfig(BaseSettings):
    """Configuration for a specific execution mode"""
    cycles: int = 5
    max_puzzles_per_cycle: int = 2
    max_solutions_per_puzzle: int = 1
    enable_referee: bool = True
    enable_hhh_filter: bool = True
    enable_best_of_n: bool = False


class ExecutionConfig(BaseSettings):
    """Execution configuration for all modes"""
    demo: ExecutionModeConfig = Field(default_factory=ExecutionModeConfig)
    robust: ExecutionModeConfig = Field(default_factory=ExecutionModeConfig)
    hackathon: ExecutionModeConfig = Field(default_factory=ExecutionModeConfig)
    
    @validator('demo', 'robust', 'hackathon', pre=True)
    def set_mode_defaults(cls, v, values, **kwargs):
        if isinstance(v, dict):
            return ExecutionModeConfig(**v)
        return v


class RefereeConfig(BaseSettings):
    """Referee safety configuration"""
    safety_threshold: float = 0.7
    complexity_threshold: float = 0.3
    banned_keywords: List[str] = Field(default_factory=lambda: [
        "hack", "exploit", "vulnerability", "password", "credit_card",
        "delete", "rm -rf", "os.system", "subprocess"
    ])


class HHHEFilterConfig(BaseSettings):
    """HHH filter configuration"""
    safety_level: str = "medium"  # low, medium, high
    max_harm_score: float = 0.5
    enable_strict_mode: bool = False


class SafetyConfig(BaseSettings):
    """Safety configuration"""
    enable_referee: bool = True
    enable_hhh_filter: bool = True
    enable_best_of_n: bool = False
    strict_mode: bool = False
    referee: RefereeConfig = Field(default_factory=RefereeConfig)
    hhh_filter: HHHEFilterConfig = Field(default_factory=HHHEFilterConfig)


class BestOfNConfig(BaseSettings):
    """Best-of-N sampling configuration"""
    enabled: bool = False
    n_samples: int = 16
    selection_method: str = "reward"  # reward, safety, combined
    min_samples: int = 3


class SuccessCriteria(BaseSettings):
    """Success criteria configuration"""
    baseline_approval_rate: float = 0.6
    oversight_approval_rate: float = 0.7
    learning_improvement: float = 0.15
    safety_compliance: float = 0.05


class MetricsConfig(BaseSettings):
    """Metrics configuration"""
    enable_csv_export: bool = True
    enable_json_export: bool = True
    enable_plots: bool = True
    save_intermediate_results: bool = True
    success_criteria: SuccessCriteria = Field(default_factory=SuccessCriteria)


class OutputConfig(BaseSettings):
    """Output configuration"""
    base_dir: str = "results"
    create_timestamped_dirs: bool = True
    save_logs: bool = True
    save_plots: bool = True
    save_reports: bool = True
    
    file_patterns: Dict[str, str] = Field(default_factory=lambda: {
        "baseline_metrics": "baseline_metrics_{timestamp}.json",
        "oversight_metrics": "oversight_metrics_{timestamp}.json",
        "comparison_results": "comparison_results_{timestamp}.json",
        "summary_report": "summary_report_{timestamp}.txt"
    })


class CostConfig(BaseSettings):
    """Cost management configuration"""
    max_usd_per_run: float = 15.0
    enable_monitoring: bool = True
    alert_threshold: float = 10.0
    
    api_costs: Dict[str, Dict[str, float]] = Field(default_factory=lambda: {
        "claude-3-5-sonnet-20241022": {
            "input": 0.003,
            "output": 0.015
        }
    })


class LoggingConfig(BaseSettings):
    """Logging configuration"""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    
    files: Dict[str, str] = Field(default_factory=lambda: {
        "main": "logs/oversight.log",
        "errors": "logs/errors.log",
        "metrics": "logs/metrics.log"
    })


class TestingConfig(BaseSettings):
    """Testing configuration"""
    enable_mocks: bool = True
    mock_api_responses: bool = True
    test_timeout: int = 30
    enable_coverage: bool = True
    coverage_threshold: int = 80
    
    test_puzzles: List[Dict[str, str]] = Field(default_factory=lambda: [
        {"id": "test_puzzle_1", "type": "code_i", "content": "def add(a, b): return a + b"},
        {"id": "test_puzzle_2", "type": "code_o", "content": "def multiply(x, y): return x * y"}
    ])


class DevelopmentConfig(BaseSettings):
    """Development configuration"""
    enable_debug_mode: bool = False
    enable_profiling: bool = False
    enable_memory_tracking: bool = False
    
    debug: Dict[str, bool] = Field(default_factory=lambda: {
        "log_api_calls": False,
        "log_metrics_details": False,
        "save_intermediate_states": False
    })


class Settings(BaseSettings):
    """Main settings class that combines all configuration sections"""
    model: ModelConfig = Field(default_factory=ModelConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    best_of_n: BestOfNConfig = Field(default_factory=BestOfNConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    cost: CostConfig = Field(default_factory=CostConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    testing: TestingConfig = Field(default_factory=TestingConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def load_settings(config_path: Optional[str] = None) -> Settings:
    """Load settings from YAML file and environment variables"""
    global _settings
    
    if _settings is not None:
        return _settings
    
    # Default config path
    if config_path is None:
        config_path = "config/settings.yaml"
    
    # Load YAML configuration
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
    else:
        yaml_config = {}
    
    # Create settings with YAML defaults
    _settings = Settings(**yaml_config)
    
    return _settings


def get_settings() -> Settings:
    """Get the global settings instance"""
    if _settings is None:
        return load_settings()
    return _settings


def reload_settings(config_path: Optional[str] = None) -> Settings:
    """Reload settings from file"""
    global _settings
    _settings = None
    return load_settings(config_path)


# Convenience functions for common settings
def get_model_config() -> ModelConfig:
    """Get model configuration"""
    return get_settings().model


def get_execution_config(mode: str = "demo") -> ExecutionModeConfig:
    """Get execution configuration for a specific mode"""
    settings = get_settings()
    if mode == "demo":
        return settings.execution.demo
    elif mode == "robust":
        return settings.execution.robust
    elif mode == "hackathon":
        return settings.execution.hackathon
    else:
        raise ValueError(f"Unknown execution mode: {mode}")


def get_safety_config() -> SafetyConfig:
    """Get safety configuration"""
    return get_settings().safety


def get_output_config() -> OutputConfig:
    """Get output configuration"""
    return get_settings().output


def get_cost_config() -> CostConfig:
    """Get cost configuration"""
    return get_settings().cost


def get_logging_config() -> LoggingConfig:
    """Get logging configuration"""
    return get_settings().logging 