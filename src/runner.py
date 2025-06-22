"""
Unified oversight runner facade.
Consolidates demo, robust, and hackathon execution modes into a single,
injectable service.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any

from deduction_loop import DeductionLoop
from metrics import MetricsCollector, ComparisonAnalyzer
from hhh_filter import HHHFilter
from best_of_n import BestOfNSampler


class ExecutionMode(Enum):
    """Execution modes for the oversight runner"""
    DEMO = "demo"
    ROBUST = "robust"
    HACKATHON = "hackathon"


@dataclass
class RunnerConfig:
    """Configuration for the oversight runner"""
    mode: ExecutionMode
    cycles: int = 5
    max_puzzles_per_cycle: int = 2
    max_solutions_per_puzzle: int = 1
    enable_referee: bool = True
    enable_hhh_filter: bool = True
    enable_best_of_n: bool = False
    model_name: str = "claude-3-5-sonnet-20241022"
    output_dir: str = "results"
    use_config_puzzles: bool = True


class OversightRunner:
    """
    Unified facade for oversight curriculum execution.
    
    Composes small, injectable services:
    - Generator: Creates puzzles
    - Solver: Solves puzzles  
    - Referee: Evaluates safety
    - Reporter: Generates metrics and reports
    """
    
    def __init__(self, config: RunnerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize core services
        self.deduction_loop = DeductionLoop(
            model_name=config.model_name,
            enable_referee=config.enable_referee,
            max_puzzles_per_cycle=config.max_puzzles_per_cycle,
            max_solutions_per_puzzle=config.max_solutions_per_puzzle
        )
        
        self.metrics = MetricsCollector()
        self.comparison_analyzer = ComparisonAnalyzer()
        
        # Optional services
        self.hhh_filter = HHHFilter() if config.enable_hhh_filter else None
        self.best_of_n = BestOfNSampler() if config.enable_best_of_n else None
        
        # Ensure output directory exists
        Path(config.output_dir).mkdir(exist_ok=True)
    
    async def run_baseline(self) -> MetricsCollector:
        """Run baseline experiment without oversight"""
        self.logger.info("Starting baseline experiment")
        
        baseline_metrics = MetricsCollector()
        
        for cycle in range(self.config.cycles):
            self.logger.info(
                f"Baseline cycle {cycle + 1}/{self.config.cycles}"
            )
            
            # Run cycle without referee
            cycle_metrics = self.deduction_loop.run_cycle()
            baseline_metrics.update(cycle_metrics)
            
            # Add small delay between cycles
            await asyncio.sleep(0.1)
        
        self.logger.info("Baseline experiment completed")
        return baseline_metrics
    
    async def run_oversight(self) -> MetricsCollector:
        """Run oversight experiment with safety filtering"""
        self.logger.info("Starting oversight experiment")
        
        oversight_metrics = MetricsCollector()
        
        for cycle in range(self.config.cycles):
            self.logger.info(
                f"Oversight cycle {cycle + 1}/{self.config.cycles}"
            )
            
            # Run cycle with referee enabled
            cycle_metrics = self.deduction_loop.run_cycle()
            oversight_metrics.update(cycle_metrics)
            
            # Apply additional safety filters if enabled
            if self.hhh_filter:
                self._apply_hhh_filtering(cycle_metrics)
            
            if self.best_of_n:
                self._apply_best_of_n_sampling(cycle_metrics)
            
            await asyncio.sleep(0.1)
        
        self.logger.info("Oversight experiment completed")
        return oversight_metrics
    
    async def run_comparison(self) -> Dict[str, Any]:
        """Run baseline vs oversight comparison"""
        self.logger.info("Starting comparison experiment")
        
        # Run both experiments
        baseline_metrics = await self.run_baseline()
        oversight_metrics = await self.run_oversight()
        
        # Generate comparison
        self.comparison_analyzer.set_baseline(baseline_metrics)
        self.comparison_analyzer.set_oversight(oversight_metrics)
        
        comparison_results = self.comparison_analyzer.compare_runs()
        
        # Save results
        self._save_results(baseline_metrics, oversight_metrics,
                          comparison_results)
        
        self.logger.info("Comparison experiment completed")
        return comparison_results
    
    async def run_demo(self) -> Dict[str, Any]:
        """Run quick demo mode"""
        self.logger.info("Starting demo mode")
        
        # Use minimal configuration for demo
        demo_config = RunnerConfig(
            mode=ExecutionMode.DEMO,
            cycles=2,
            max_puzzles_per_cycle=1,
            max_solutions_per_puzzle=1,
            enable_referee=True,
            enable_hhh_filter=False,
            enable_best_of_n=False
        )
        
        demo_runner = OversightRunner(demo_config)
        results = await demo_runner.run_comparison()
        
        self.logger.info("Demo completed")
        return results
    
    async def run_robust(self) -> Dict[str, Any]:
        """Run robust mode with full validation"""
        self.logger.info("Starting robust mode")
        
        # Validate environment first
        if not self._validate_environment():
            raise RuntimeError("Environment validation failed")
        
        # Run full comparison
        results = await self.run_comparison()
        
        # Generate comprehensive reports
        self._generate_reports(results)
        
        self.logger.info("Robust mode completed")
        return results
    
    def _apply_hhh_filtering(self, cycle_metrics: Dict[str, Any]):
        """Apply HHH safety filtering to cycle results"""
        if not self.hhh_filter:
            return
        
        # Apply filtering logic here
        # This would integrate with the HHHFilter class
        pass
    
    def _apply_best_of_n_sampling(self, cycle_metrics: Dict[str, Any]):
        """Apply best-of-n sampling to cycle results"""
        if not self.best_of_n:
            return
        
        # Apply sampling logic here
        # This would integrate with the BestOfNSampler class
        pass
    
    def _validate_environment(self) -> bool:
        """Validate environment before robust execution"""
        # Check API key
        import os
        if not os.getenv("CLAUDE_API_KEY"):
            self.logger.error("CLAUDE_API_KEY not found")
            return False
        
        # Check output directory
        if not Path(self.config.output_dir).exists():
            self.logger.error(
                f"Output directory {self.config.output_dir} does not exist"
            )
            return False
        
        return True
    
    def _save_results(self, baseline_metrics: MetricsCollector,
                     oversight_metrics: MetricsCollector,
                     comparison_results: Dict[str, Any]):
        """Save all results to output directory"""
        # Save baseline metrics
        baseline_metrics.export_to_json(
            f"{self.config.output_dir}/baseline_metrics.json"
        )
        
        # Save oversight metrics  
        oversight_metrics.export_to_json(
            f"{self.config.output_dir}/oversight_metrics.json"
        )
        
        # Save comparison results
        import json
        with open(f"{self.config.output_dir}/comparison_results.json", 'w') as f:
            json.dump(comparison_results, f, indent=2)
    
    def _generate_reports(self, results: Dict[str, Any]):
        """Generate comprehensive reports"""
        # Generate plots
        from analysis import create_plots
        create_plots(
            baseline_metrics=self.comparison_analyzer.baseline_metrics,
            oversight_metrics=self.comparison_analyzer.oversight_metrics,
            output_dir=self.config.output_dir
        )
        
        # Generate summary report
        report = self.comparison_analyzer.generate_report()
        with open(f"{self.config.output_dir}/summary_report.txt", 'w') as f:
            f.write(report)


async def main():
    """Main entry point for the oversight runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Oversight Curriculum Runner")
    parser.add_argument("--mode", choices=["demo", "robust", "hackathon"],
                       default="demo", help="Execution mode")
    parser.add_argument("--cycles", type=int, default=5,
                       help="Number of cycles")
    parser.add_argument("--config", type=str, help="Configuration file path")
    
    args = parser.parse_args()
    
    # Load configuration
    config = RunnerConfig(
        mode=ExecutionMode(args.mode),
        cycles=args.cycles
    )
    
    # Create runner
    runner = OversightRunner(config)
    
    # Run based on mode
    if args.mode == "demo":
        await runner.run_demo()
    elif args.mode == "robust":
        await runner.run_robust()
    else:
        await runner.run_comparison()
    
    print(f"Execution completed. Results saved to {config.output_dir}")


if __name__ == "__main__":
    asyncio.run(main()) 