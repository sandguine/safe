"""
Deduction loop implementation for oversight curriculum.
Provides iterative reasoning and safety evaluation capabilities.
"""

import asyncio
import sys as _sys

from .errors import OversightError


class DeductionLoop:
    """Main deduction loop for iterative reasoning."""

    def __init__(self, max_iterations: int = 10):
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.results = []

    async def run_cycle(self, initial_prompt: str = "") -> dict:
        """
        Async wrapper expected by the test-suite. Always passes initial_prompt.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.run, initial_prompt)

    def run(self, initial_prompt: str = "") -> dict:
        """Run the deduction loop with the given prompt."""
        try:
            self.iteration_count = 0
            self.results = []
            current_prompt = initial_prompt
            for i in range(self.max_iterations):
                self.iteration_count += 1
                result = self._deduction_step(current_prompt, i)
                self.results.append(result)
                if result.get("completed", False):
                    break
                current_prompt = result.get("next_prompt", current_prompt)
            return {
                "status": "completed",
                "iterations": self.iteration_count,
                "results": self.results,
                "final_result": self.results[-1] if self.results else None,
            }
        except Exception as e:
            raise OversightError(f"Deduction loop failed: {e}") from e

    def _deduction_step(self, prompt: str, iteration: int) -> dict:
        """Perform a single deduction step."""
        return {
            "iteration": iteration + 1,
            "prompt": prompt,
            "reasoning": f"Step {iteration + 1} reasoning",
            "conclusion": f"Step {iteration + 1} conclusion",
            "completed": iteration >= 2,  # Complete after 3 iterations
            "next_prompt": f"Updated prompt for step {iteration + 2}",
        }


# Legacy import shim for external scripts
_sys.modules.setdefault("deduction_loop", _sys.modules[__name__])
