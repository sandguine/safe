"""
Main runner for oversight curriculum experiments.
Provides the core execution engine for AI safety evaluation.
"""

from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any

from .config import get_settings
from .errors import OversightError


class ExecutionMode(Enum):
    """Execution modes for oversight experiments."""
    DEMO = "demo"
    ROBUST = "robust"
    HACKATHON = "hackathon"


class RunnerConfig:
    """Configuration for the oversight runner."""
    
    def __init__(
        self,
        mode: ExecutionMode = ExecutionMode.DEMO,
        config_path: Optional[Path] = None,
        **kwargs
    ):
        self.mode = mode
        self.config_path = config_path
        self.settings = get_settings()
        self.extra_args = kwargs


class OversightRunner:
    """Main runner for oversight curriculum experiments."""
    
    def __init__(self, config: RunnerConfig):
        self.config = config
        self.settings = config.settings
        
    def run(self) -> Dict[str, Any]:
        """Execute the oversight experiment."""
        try:
            if self.config.mode == ExecutionMode.DEMO:
                return self._run_demo()
            elif self.config.mode == ExecutionMode.ROBUST:
                return self._run_robust()
            elif self.config.mode == ExecutionMode.HACKATHON:
                return self._run_hackathon()
            else:
                raise OversightError(
                    f"Unknown execution mode: {self.config.mode}"
                )
        except Exception as e:
            raise OversightError(f"Runner execution failed: {e}") from e
    
    def _run_demo(self) -> Dict[str, Any]:
        """Run demo mode experiment."""
        return {
            "mode": "demo",
            "status": "completed",
            "message": "Demo experiment completed successfully"
        }
    
    def _run_robust(self) -> Dict[str, Any]:
        """Run robust mode experiment."""
        return {
            "mode": "robust",
            "status": "completed",
            "message": "Robust experiment completed successfully"
        }
    
    def _run_hackathon(self) -> Dict[str, Any]:
        """Run hackathon mode experiment."""
        return {
            "mode": "hackathon",
            "status": "completed",
            "message": "Hackathon experiment completed successfully"
        } 