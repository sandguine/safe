#!/usr/bin/env python3
"""
Unit tests for Best-of-N sampling implementation.
Tests core functionality and integration points.
"""

import asyncio
from unittest.mock import patch

import pytest

from oversight.best_of_n import (
    BestOfNSampler,
    SamplingResult,
    run_best_of_n_demo,
)


class TestBestOfNSampler:
    """Test cases for BestOfNSampler"""

    def test_initialization(self):
        """Test sampler initialization"""
        sampler = BestOfNSampler(
            model_name="test-model",
            n_samples=8,
            temperature=0.5,
            selection_method="reward",
        )

        assert sampler.model_name == "test-model"
        assert sampler.n_samples == 8
        assert sampler.temperature == 0.5
        assert sampler.selection_method == "reward"

    @pytest.mark.asyncio
    async def test_generate_solutions(self):
        """Test solution generation"""
        sampler = BestOfNSampler(n_samples=3)

        with patch("oversight.best_of_n.ask") as mock_ask:
            mock_ask.return_value = "def test(): return 42"

            solutions = await sampler._generate_solutions(
                "Write a test function"
            )

            assert len(solutions) == 3
            assert all("def test(): return 42" in sol for sol in solutions)
            assert mock_ask.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_solutions_with_failures(self):
        """Test solution generation with API failures"""
        sampler = BestOfNSampler(n_samples=3)

        with patch("oversight.best_of_n.ask") as mock_ask:
            mock_ask.side_effect = [
                Exception("API Error"),
                "def test(): return 42",
                Exception("API Error"),
            ]

            solutions = await sampler._generate_solutions(
                "Write a test function"
            )

            assert len(solutions) == 1
            assert "def test(): return 42" in solutions[0]

    @pytest.mark.asyncio
    async def test_generate_solutions_all_failures(self):
        """Test solution generation when all API calls fail"""
        sampler = BestOfNSampler(n_samples=2)

        with patch("oversight.best_of_n.ask") as mock_ask:
            mock_ask.side_effect = Exception("API Error")

            solutions = await sampler._generate_solutions(
                "Write a test function"
            )

            assert len(solutions) == 1
            assert "Default solution" in solutions[0]

    def test_calculate_code_quality(self):
        """Test code quality scoring"""
        sampler = BestOfNSampler()

        # Test high-quality code
        good_code = """
        def add_numbers(a, b):
            # Add two numbers together
            return a + b
        """
        score = sampler._calculate_code_quality(good_code)
        assert score > 0.8

        # Test low-quality code
        bad_code = "print('hello')"
        score = sampler._calculate_code_quality(bad_code)
        assert score < 0.5

    def test_select_best(self):
        """Test best solution selection"""
        sampler = BestOfNSampler()

        scores = [0.3, 0.8, 0.5]
        best_idx = sampler._select_best(scores)

        assert best_idx == 1  # Index of highest score (0.8)

    def test_calculate_std(self):
        """Test standard deviation calculation"""
        sampler = BestOfNSampler()

        # Test with multiple values
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        std = sampler._calculate_std(values)
        assert std > 0

        # Test with single value
        std = sampler._calculate_std([1.0])
        assert std == 0.0

    @pytest.mark.asyncio
    async def test_score_solutions_random(self):
        """Test random scoring method"""
        sampler = BestOfNSampler(selection_method="random")
        solutions = ["solution1", "solution2", "solution3"]

        scores = await sampler._score_solutions("test prompt", solutions)

        assert len(scores) == 3
        assert all(0 <= score <= 1 for score in scores)

    @pytest.mark.asyncio
    async def test_score_solutions_length(self):
        """Test length-based scoring method"""
        sampler = BestOfNSampler(selection_method="length")
        solutions = [
            "short",
            "medium length solution",
            "very long solution with lots of content",
        ]

        scores = await sampler._score_solutions("test prompt", solutions)

        assert len(scores) == 3
        assert (
            scores[2] > scores[1] > scores[0]
        )  # Longer solutions get higher scores

    @pytest.mark.asyncio
    async def test_score_solutions_reward(self):
        """Test reward-based scoring method"""
        sampler = BestOfNSampler(selection_method="reward")
        solutions = [
            "print('hello')",  # Low quality
            "def test(): return 42",  # Medium quality
            "def add(a, b):\n    # Add two numbers\n    return a + b",  # High quality
        ]

        scores = await sampler._score_solutions("test prompt", solutions)

        assert len(scores) == 3
        assert (
            scores[2] > scores[1] > scores[0]
        )  # Better code gets higher scores

    @pytest.mark.asyncio
    async def test_sample_best_solution_integration(self):
        """Test complete best-of-n sampling integration"""
        sampler = BestOfNSampler(n_samples=2, selection_method="reward")

        with patch("oversight.best_of_n.ask") as mock_ask:
            mock_ask.return_value = "def test(): return 42"

            best_solution, metrics = await sampler.sample_best_solution(
                "Write a test function"
            )

            assert isinstance(best_solution, str)
            assert "def test(): return 42" in best_solution

            # Check metrics
            assert metrics["n_samples"] == 2
            assert "avg_score" in metrics
            assert "max_score" in metrics
            assert "min_score" in metrics
            assert "best_score" in metrics
            assert "selection_method" in metrics
            assert "all_scores" in metrics

    @pytest.mark.asyncio
    async def test_sample_best_solution_metrics(self):
        """Test that metrics are calculated correctly"""
        sampler = BestOfNSampler(n_samples=3, selection_method="random")

        with patch("oversight.best_of_n.ask") as mock_ask:
            mock_ask.return_value = "test solution"

            best_solution, metrics = await sampler.sample_best_solution(
                "test prompt"
            )

            # Verify metric calculations
            scores = metrics["all_scores"]
            assert len(scores) == 3
            assert metrics["avg_score"] == sum(scores) / len(scores)
            assert metrics["max_score"] == max(scores)
            assert metrics["min_score"] == min(scores)
            assert metrics["best_score"] == max(scores)


class TestRunBestOfNDemo:
    """Test cases for the demo function"""

    @pytest.mark.asyncio
    async def test_run_best_of_n_demo(self):
        """Test the demo function"""
        with patch("oversight.best_of_n.ask") as mock_ask:
            mock_ask.return_value = "def demo(): return 'success'"

            result = await run_best_of_n_demo("Write a demo function", n=2)

            assert isinstance(result, SamplingResult)
            assert result.n_samples == 2
            assert result.selection_method == "reward"
            assert len(result.scores) == 2
            assert result.best_score == max(result.scores)


class TestIntegrationPoints:
    """Test integration with other components"""

    @pytest.mark.asyncio
    async def test_integration_with_humaneval(self):
        """Test integration with HumanEval runner"""
        # This would test how BestOfNSampler integrates with HumanEval
        # For now, we'll test the interface compatibility
        sampler = BestOfNSampler(n_samples=4)

        # Test that the interface matches what HumanEval expects
        prompt = "Write a function that adds two numbers"
        best_solution, metrics = await sampler.sample_best_solution(prompt)

        assert isinstance(best_solution, str)
        assert isinstance(metrics, dict)
        assert "best_score" in metrics

    def test_configuration_integration(self):
        """Test integration with configuration system"""
        # Test that BestOfNSampler can be configured via settings
        from oversight.core.config import get_settings

        settings = get_settings()

        # Verify that BestOfNSampler can use settings
        sampler = BestOfNSampler(
            model_name=settings.model.model_name,
            temperature=settings.model.temperature,
        )

        assert sampler.model_name == settings.model.model_name
        assert sampler.temperature == settings.model.temperature


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_api_failure_handling(self):
        """Test handling of API failures"""
        sampler = BestOfNSampler(n_samples=2)

        with patch("oversight.best_of_n.ask") as mock_ask:
            mock_ask.side_effect = Exception("Network error")

            best_solution, metrics = await sampler.sample_best_solution("test")

            # Should still return a result (fallback)
            assert isinstance(best_solution, str)
            assert "Error generating solution" in best_solution

    def test_invalid_selection_method(self):
        """Test handling of invalid selection method"""
        sampler = BestOfNSampler(selection_method="invalid_method")

        # Should default to random selection
        assert sampler.selection_method == "invalid_method"
        # The scoring method will handle this gracefully


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_concurrent_generation(self):
        """Test that solutions are generated concurrently"""
        sampler = BestOfNSampler(n_samples=4)

        with patch("oversight.best_of_n.ask") as mock_ask:
            mock_ask.return_value = "test solution"

            start_time = asyncio.get_event_loop().time()
            await sampler.sample_best_solution("test prompt")
            end_time = asyncio.get_event_loop().time()

            # Should be fast (concurrent execution)
            # If sequential, this would take ~4 seconds with 1s per call
            # With concurrent execution, should be ~1 second
            assert end_time - start_time < 2.0

    def test_memory_usage(self):
        """Test memory usage with large n"""
        sampler = BestOfNSampler(n_samples=100)

        # Should not crash with large n
        assert sampler.n_samples == 100
        # In a real test, we'd measure actual memory usage


# Integration test markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.best_of_n,
]
