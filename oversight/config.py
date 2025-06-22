"""
Configuration management for oversight curriculum.
Uses Pydantic for type-safe configuration loading and validation.
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class ModelConfig(BaseSettings):
    """Configuration for model settings."""

    model_name: str = Field(default="gpt-4", description="Model to use for reasoning")
    temperature: float = Field(
        default=0.1, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=2048, gt=0, description="Maximum tokens to generate"
    )
    top_p: float = Field(
        default=0.9, ge=0.0, le=1.0, description="Top-p sampling parameter"
    )

    class Config:
        env_prefix = "MODEL_"


class SafetyConfig(BaseSettings):
    """Configuration for safety filtering."""

    hhh_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="HHH safety threshold"
    )
    max_violations: int = Field(
        default=3, ge=0, description="Maximum safety violations allowed"
    )
    enable_filtering: bool = Field(
        default=True, description="Enable HHH safety filtering"
    )

    class Config:
        env_prefix = "SAFETY_"


class ExecutionConfig(BaseSettings):
    """Configuration for execution settings."""

    max_iterations: int = Field(
        default=10, gt=0, description="Maximum reasoning iterations"
    )
    timeout_seconds: int = Field(default=300, gt=0, description="Timeout in seconds")
    enable_logging: bool = Field(default=True, description="Enable detailed logging")
    output_dir: Path = Field(default=Path("./output"), description="Output directory")

    class Config:
        env_prefix = "EXEC_"


class OversightConfig(BaseSettings):
    """Main configuration class combining all settings."""

    model: ModelConfig = Field(default_factory=ModelConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)

    @classmethod
    def load_from_file(cls, config_path: Path) -> "OversightConfig":
        """Load configuration from YAML file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(self.dict(), f, default_flow_style=False, indent=2)


# Global configuration instance
_settings: Optional[OversightConfig] = None


def load_settings(config_path: Optional[Path] = None) -> OversightConfig:
    """Load settings from file or environment variables."""
    global _settings

    if config_path:
        _settings = OversightConfig.load_from_file(config_path)
    else:
        _settings = OversightConfig()

    return _settings


def get_settings() -> OversightConfig:
    """Get current settings, loading defaults if not already loaded."""
    global _settings

    if _settings is None:
        _settings = OversightConfig()

    return _settings


def get_execution_config(mode: str = "demo") -> ExecutionConfig:
    """Get execution config for specific mode with backward compatibility."""
    settings = get_settings()

    # Mode-specific overrides
    if mode == "demo":
        return ExecutionConfig(
            max_iterations=2,
            timeout_seconds=60,
            enable_logging=True,
            output_dir=Path("./output/demo"),
        )
    elif mode == "robust":
        return ExecutionConfig(
            max_iterations=10,
            timeout_seconds=300,
            enable_logging=True,
            output_dir=Path("./output/robust"),
        )
    elif mode == "hackathon":
        return ExecutionConfig(
            max_iterations=5,
            timeout_seconds=120,
            enable_logging=False,
            output_dir=Path("./output/hackathon"),
        )
    else:
        # Default to settings.execution for backward compatibility
        return settings.execution
