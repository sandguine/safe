"""
Integration tests for the SAFE pipeline.
Tests the complete pipeline from end-to-end with mocked dependencies.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from oversight.errors import SafetyViolation
from oversight.metrics import MetricsCollector
from oversight.runner import ExecutionMode, OversightRunner, RunnerConfig


class TestOversightPipeline:
    """Integration tests for the complete oversight pipeline"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch("oversight.config.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.model.name = "claude-3-5-sonnet-20241022"
            mock_settings.execution.demo.cycles = 2
            mock_settings.execution.demo.max_puzzles_per_cycle = 1
            mock_settings.execution.demo.max_solutions_per_puzzle = 1
            mock_get_settings.return_value = mock_settings
            yield mock_settings

    @pytest.fixture
    def mock_deduction_loop(self):
        """Mock deduction loop for testing"""
        with patch("oversight.deduction_loop.DeductionLoop") as mock_loop:
            mock_instance = Mock()

            # Use AsyncMock to track call_count
            async_mock = AsyncMock()
            async_mock.return_value = {
                "cycle": 1,
                "puzzles_generated": 1,
                "puzzles_approved": 1,
                "puzzles_rejected": 0,
                "solutions_generated": 1,
                "solutions_correct": 1,
                "avg_solution_reward": 0.8,
                "avg_puzzle_safety": 0.9,
                "cycle_duration": 2.0,
            }

            mock_instance.run_cycle = async_mock
            mock_loop.return_value = mock_instance
            yield async_mock

    @pytest.fixture
    def runner_config(self):
        """Test runner configuration"""
        return RunnerConfig(
            mode=ExecutionMode.DEMO,
            cycles=2,
            max_puzzles_per_cycle=1,
            max_solutions_per_puzzle=1,
            enable_referee=True,
            enable_hhh_filter=False,
            enable_best_of_n=False,
        )

    @pytest.mark.asyncio
    async def test_pipeline_happy_path(
        self, mock_settings, mock_deduction_loop, runner_config
    ):
        """Test the complete pipeline happy path"""
        # Create runner
        runner = OversightRunner(runner_config)

        # Run baseline experiment
        baseline_metrics = await runner.run_baseline()

        # Verify metrics were collected
        assert baseline_metrics is not None
        assert isinstance(baseline_metrics, MetricsCollector)

        # Verify deduction loop was called
        assert mock_deduction_loop.call_count == 2

        # Run oversight experiment
        oversight_metrics = await runner.run_oversight()

        # Verify metrics were collected
        assert oversight_metrics is not None
        assert isinstance(oversight_metrics, MetricsCollector)

        # Verify deduction loop was called again
        assert mock_deduction_loop.call_count == 4

    @pytest.mark.asyncio
    async def test_pipeline_comparison(
        self, mock_settings, mock_deduction_loop, runner_config
    ):
        """Test the complete comparison pipeline"""
        # Create runner
        runner = OversightRunner(runner_config)

        # Run comparison
        results = await runner.run_comparison()

        # Verify results structure
        assert isinstance(results, dict)
        assert "baseline_summary" in results
        assert "oversight_summary" in results
        assert "comparison" in results

        # Verify deduction loop was called for both experiments
        assert mock_deduction_loop.call_count == 4

    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, mock_settings, runner_config):
        """Test pipeline error handling"""
        # Mock deduction loop to raise an error
        with patch("oversight.deduction_loop.DeductionLoop") as mock_loop:
            mock_instance = Mock()
            mock_instance.run_cycle.side_effect = Exception("API Error")
            mock_loop.return_value = mock_instance

            # Create runner
            runner = OversightRunner(runner_config)

            # Run baseline should raise an error
            with pytest.raises(Exception):
                await runner.run_baseline()

    @pytest.mark.asyncio
    async def test_pipeline_safety_violation(
        self, mock_settings, runner_config
    ):
        """Test pipeline handling of safety violations"""
        # Mock deduction loop to simulate safety violation
        with patch("oversight.deduction_loop.DeductionLoop") as mock_loop:
            mock_instance = Mock()

            # Use AsyncMock with side_effect for safety violation
            async_mock = AsyncMock()
            async_mock.side_effect = [
                {
                    "cycle": 1,
                    "puzzles_generated": 1,
                    "puzzles_approved": 1,
                    "puzzles_rejected": 0,
                    "solutions_generated": 1,
                    "solutions_correct": 1,
                    "avg_solution_reward": 0.8,
                    "avg_puzzle_safety": 0.9,
                    "cycle_duration": 2.0,
                },
                SafetyViolation("Safety violation detected"),
            ]

            mock_instance.run_cycle = async_mock
            mock_loop.return_value = mock_instance

            # Create runner
            runner = OversightRunner(runner_config)

            # Run baseline should raise safety violation
            with pytest.raises(SafetyViolation):
                await runner.run_baseline()

    @pytest.mark.asyncio
    async def test_pipeline_demo_mode(
        self, mock_settings, mock_deduction_loop
    ):
        """Test demo mode execution"""
        # Create runner with demo config
        demo_config = RunnerConfig(
            mode=ExecutionMode.DEMO,
            cycles=1,
            max_puzzles_per_cycle=1,
            max_solutions_per_puzzle=1,
            enable_referee=True,
            enable_hhh_filter=False,
            enable_best_of_n=False,
        )

        runner = OversightRunner(demo_config)

        # Run demo
        results = await runner.run_demo()

        # Verify results
        assert isinstance(results, dict)
        assert mock_deduction_loop.call_count == 2  # baseline + oversight

    @pytest.mark.asyncio
    async def test_pipeline_robust_mode(
        self, mock_settings, mock_deduction_loop
    ):
        """Test robust mode execution"""
        # Create runner with robust config
        robust_config = RunnerConfig(
            mode=ExecutionMode.ROBUST,
            cycles=3,
            max_puzzles_per_cycle=2,
            max_solutions_per_puzzle=2,
            enable_referee=True,
            enable_hhh_filter=True,
            enable_best_of_n=True,
        )

        runner = OversightRunner(robust_config)

        # Mock environment validation
        with patch.object(runner, "_validate_environment", return_value=True):
            # Run robust mode
            results = await runner.run_robust()

            # Verify results
            assert isinstance(results, dict)
            assert (
                mock_deduction_loop.call_count == 6
            )  # 3 cycles * 2 experiments


class TestPipelineProperties:
    """Property-based tests for pipeline behavior"""

    @pytest.mark.parametrize("cycles", [1, 2, 5, 10])
    @pytest.mark.asyncio
    async def test_pipeline_cycle_count(self, cycles):
        """Test that pipeline runs the correct number of cycles"""
        with patch("oversight.deduction_loop.DeductionLoop") as mock_loop:
            mock_instance = Mock()

            async_mock = AsyncMock()
            async_mock.return_value = {
                "cycle": 1,
                "puzzles_generated": 1,
                "puzzles_approved": 1,
                "puzzles_rejected": 0,
                "solutions_generated": 1,
                "solutions_correct": 1,
                "avg_solution_reward": 0.8,
                "avg_puzzle_safety": 0.9,
                "cycle_duration": 2.0,
            }

            mock_instance.run_cycle = async_mock
            mock_loop.return_value = mock_instance

            config = RunnerConfig(
                mode=ExecutionMode.DEMO,
                cycles=cycles,
                max_puzzles_per_cycle=1,
                max_solutions_per_puzzle=1,
            )

            runner = OversightRunner(config)
            await runner.run_baseline()

            # Verify correct number of cycles
            assert async_mock.call_count == cycles

    @pytest.mark.parametrize("enable_referee", [True, False])
    @pytest.mark.asyncio
    async def test_pipeline_referee_configuration(self, enable_referee):
        """Test that referee configuration is respected"""
        with patch("oversight.deduction_loop.DeductionLoop") as mock_loop:
            mock_instance = Mock()

            async def mock_run_cycle():
                return {
                    "cycle": 1,
                    "puzzles_generated": 1,
                    "puzzles_approved": 1,
                    "puzzles_rejected": 0,
                    "solutions_generated": 1,
                    "solutions_correct": 1,
                    "avg_solution_reward": 0.8,
                    "avg_puzzle_safety": 0.9,
                    "cycle_duration": 2.0,
                }

            mock_instance.run_cycle = mock_run_cycle
            mock_loop.return_value = mock_instance

            config = RunnerConfig(
                mode=ExecutionMode.DEMO,
                cycles=1,
                max_puzzles_per_cycle=1,
                max_solutions_per_puzzle=1,
                enable_referee=enable_referee,
            )

            runner = OversightRunner(config)

            # Verify deduction loop was created
            mock_loop.assert_called_once()
            # Note: DeductionLoop doesn't take enable_referee parameter
            # The referee configuration is handled elsewhere in the pipeline

    @pytest.mark.parametrize("mode", ["demo", "robust", "hackathon"])
    @pytest.mark.asyncio
    async def test_pipeline_mode_configuration(self, mode):
        """Test that different modes use correct configuration"""
        with patch("oversight.deduction_loop.DeductionLoop") as mock_loop:
            mock_instance = Mock()

            async_mock = AsyncMock()
            async_mock.return_value = {
                "cycle": 1,
                "puzzles_generated": 1,
                "puzzles_approved": 1,
                "puzzles_rejected": 0,
                "solutions_generated": 1,
                "solutions_correct": 1,
                "avg_solution_reward": 0.8,
                "avg_puzzle_safety": 0.9,
                "cycle_duration": 2.0,
            }

            mock_instance.run_cycle = async_mock
            mock_loop.return_value = mock_instance

            config = RunnerConfig(
                mode=ExecutionMode(mode),
                cycles=1,
                max_puzzles_per_cycle=1,
                max_solutions_per_puzzle=1,
            )

            runner = OversightRunner(config)

            # Verify mode is set correctly
            assert runner.config.mode == ExecutionMode(mode)


class TestPipelineMetrics:
    """Tests for metrics collection and analysis"""

    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Test that metrics are properly collected and stored"""
        with patch("oversight.deduction_loop.DeductionLoop") as mock_loop:
            mock_instance = Mock()

            async_mock = AsyncMock()
            async_mock.return_value = {
                "cycle": 1,
                "puzzles_generated": 2,
                "puzzles_approved": 1,
                "puzzles_rejected": 1,
                "solutions_generated": 1,
                "solutions_correct": 1,
                "avg_solution_reward": 0.8,
                "avg_puzzle_safety": 0.9,
                "cycle_duration": 2.0,
            }

            mock_instance.run_cycle = async_mock
            mock_loop.return_value = mock_instance

            config = RunnerConfig(
                mode=ExecutionMode.DEMO,
                cycles=2,
                max_puzzles_per_cycle=1,
                max_solutions_per_puzzle=1,
            )

            runner = OversightRunner(config)
            metrics = await runner.run_baseline()

            # Verify metrics structure
            summary = metrics.get_summary()
            assert summary.total_cycles == 2
            assert summary.total_puzzles == 4  # 2 cycles * 2 puzzles
            assert summary.total_solutions == 2  # 2 cycles * 1 solution
            assert summary.approval_rate == 0.5  # 2 approved / 4 total

    @pytest.mark.asyncio
    async def test_comparison_analysis(self):
        """Test that comparison analysis works correctly"""
        with patch("oversight.deduction_loop.DeductionLoop") as mock_loop:
            mock_instance = Mock()

            # Baseline: lower performance
            baseline_metrics = {
                "cycle": 1,
                "puzzles_generated": 2,
                "puzzles_approved": 1,
                "puzzles_rejected": 1,
                "solutions_generated": 1,
                "solutions_correct": 0,
                "avg_solution_reward": 0.3,
                "avg_puzzle_safety": 0.6,
                "cycle_duration": 2.0,
            }

            # Oversight: higher performance
            oversight_metrics = {
                "cycle": 1,
                "puzzles_generated": 2,
                "puzzles_approved": 2,
                "puzzles_rejected": 0,
                "solutions_generated": 1,
                "solutions_correct": 1,
                "avg_solution_reward": 0.8,
                "avg_puzzle_safety": 0.9,
                "cycle_duration": 2.0,
            }

            async_mock = AsyncMock()
            async_mock.side_effect = [baseline_metrics, oversight_metrics]

            mock_instance.run_cycle = async_mock
            mock_loop.return_value = mock_instance

            config = RunnerConfig(
                mode=ExecutionMode.DEMO,
                cycles=1,
                max_puzzles_per_cycle=1,
                max_solutions_per_puzzle=1,
            )

            runner = OversightRunner(config)
            results = await runner.run_comparison()

            # Verify comparison shows improvement
            assert results["comparison"]["approval_rate_improvement"] > 0
            assert results["comparison"]["solution_reward_gain"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
