#!/usr/bin/env python3
"""
HumanEval-164 Integration Module
================================

Implements the refined plan requirements:
1. Secure sandbox execution with timeouts
2. Partial credit scoring (per-test-case breakdown)
3. Async execution with global rate limiting
4. Progressive sampling (n=4 first, then +12 if needed)
5. Confidence-weighted voting across top candidates
"""

import asyncio
import json
import os
import platform
import resource
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# HumanEval imports
try:
    from human_eval.data import HUMAN_EVAL
except ImportError:
    print("Warning: human-eval not installed. Run: pip install human-eval")
    HUMAN_EVAL = None


# Local imports
from oversight.model import ask


@dataclass
class HumanEvalTask:
    """Represents a HumanEval task with all necessary information"""

    task_id: str
    prompt: str
    entry_point: str
    test: str
    canonical_solution: str


@dataclass
class ExecutionResult:
    """Result of executing a solution in sandbox"""

    passed: int
    total: int
    ratio: float
    error: Optional[str] = None
    execution_time: float = 0.0


class SecureSandbox:
    """Secure sandbox for executing HumanEval solutions"""

    def __init__(self, timeout_seconds: int = 5, memory_limit_mb: int = 512):
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb

    def execute_solution(
        self, task: HumanEvalTask, solution_code: str
    ) -> ExecutionResult:
        """
        Execute solution in secure sandbox with timeouts and resource limits
        """
        start_time = time.time()

        try:
            # Create temporary file for the solution
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                # Write the complete solution
                full_code = f"{task.prompt}\n{solution_code}\n{task.test}"
                f.write(full_code)
                temp_file = f.name

            # Execute with resource limits
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                preexec_fn=self._set_resource_limits,
                env=self._get_safe_env(),
            )

            execution_time = time.time() - start_time

            # Parse test results
            if result.returncode == 0:
                # Extract test results from stdout
                output_lines = result.stdout.strip().split("\n")
                passed = 0
                total = 0

                for line in output_lines:
                    if line.startswith("PASSED:"):
                        passed += 1
                        total += 1
                    elif line.startswith("FAILED:"):
                        total += 1
                    elif line.startswith("ERROR:"):
                        total += 1

                ratio = passed / total if total > 0 else 0.0
                return ExecutionResult(
                    passed=passed,
                    total=total,
                    ratio=ratio,
                    execution_time=execution_time,
                )
            else:
                return ExecutionResult(
                    passed=0,
                    total=1,
                    ratio=0.0,
                    error=result.stderr,
                    execution_time=execution_time,
                )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                passed=0,
                total=1,
                ratio=0.0,
                error="Timeout",
                execution_time=self.timeout_seconds,
            )
        except Exception as e:
            return ExecutionResult(
                passed=0,
                total=1,
                ratio=0.0,
                error=str(e),
                execution_time=time.time() - start_time,
            )
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def _set_resource_limits(self):
        """Set resource limits for the sandbox"""
        # CPU time limit
        resource.setrlimit(
            resource.RLIMIT_CPU, (self.timeout_seconds, self.timeout_seconds)
        )

        # Memory limit - skip RLIMIT_AS on macOS (Darwin) to avoid segfault
        if platform.system() != "Darwin":
            memory_bytes = self.memory_limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

        # Disable core dumps
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    def _get_safe_env(self) -> Dict[str, str]:
        """Get safe environment variables for sandbox"""
        env = os.environ.copy()

        # Set deterministic hash seed
        env["PYTHONHASHSEED"] = "0"

        # Remove potentially dangerous environment variables
        dangerous_vars = ["PYTHONPATH", "LD_LIBRARY_PATH", "LD_PRELOAD"]
        for var in dangerous_vars:
            env.pop(var, None)

        return env


class AsyncHumanEvalRunner:
    """Async runner for HumanEval tasks with rate limiting and progressive sampling"""

    def __init__(
        self,
        max_concurrent: int = 10,
        requests_per_minute: int = 50,
        progressive_sampling: bool = True,
    ):
        self.max_concurrent = max_concurrent
        self.requests_per_minute = requests_per_minute
        self.progressive_sampling = progressive_sampling

        # Rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = asyncio.Semaphore(requests_per_minute)

        # Sandbox
        self.sandbox = SecureSandbox()

        # Load HumanEval tasks
        self.tasks = self._load_humaneval_tasks()

    def _load_humaneval_tasks(self) -> List[HumanEvalTask]:
        """Load HumanEval-164 tasks"""
        if not HUMAN_EVAL:
            raise ImportError("human-eval not installed")

        import gzip
        import json

        tasks = []

        # HUMAN_EVAL is a path to a gzipped JSONL file
        with gzip.open(HUMAN_EVAL, "rt", encoding="utf-8") as f:
            for line in f:
                task_data = json.loads(line.strip())
                task = HumanEvalTask(
                    task_id=task_data["task_id"],
                    prompt=task_data["prompt"],
                    entry_point=task_data["entry_point"],
                    test=task_data["test"],
                    canonical_solution=task_data["canonical_solution"],
                )
                tasks.append(task)

        print(f"Loaded {len(tasks)} HumanEval tasks")
        return tasks

    async def generate_solution(
        self, task: HumanEvalTask, temperature: float = 0.7
    ) -> str:
        """Generate solution for a task with rate limiting"""
        async with self.semaphore:
            async with self.rate_limiter:
                # Add delay to respect rate limits
                await asyncio.sleep(60.0 / self.requests_per_minute)

                prompt = f"""Complete the following Python function:

{task.prompt}

Provide only the function implementation, no explanations:"""

                try:
                    response = await asyncio.to_thread(
                        ask, prompt, temperature=temperature
                    )
                    return response.strip()
                except Exception as e:
                    print(f"Error generating solution for {task.task_id}: {e}")
                    return ""

    def evaluate_solution(self, task: HumanEvalTask, solution: str) -> ExecutionResult:
        """Evaluate solution using secure sandbox"""
        return self.sandbox.execute_solution(task, solution)

    async def run_best_of_n(
        self, task: HumanEvalTask, n: int, temperature: float = 0.7
    ) -> Tuple[ExecutionResult, List[str]]:
        """
        Run best-of-n with progressive sampling
        """
        solutions = []

        # Progressive sampling: start with n=4, add more if needed
        initial_n = min(4, n) if self.progressive_sampling else n

        # Generate initial solutions
        print(f"Generating {initial_n} solutions for {task.task_id}...")
        tasks = [self.generate_solution(task, temperature) for _ in range(initial_n)]
        initial_solutions = await asyncio.gather(*tasks)
        solutions.extend(initial_solutions)

        # Evaluate initial solutions
        results = []
        for solution in initial_solutions:
            if solution:  # Skip empty solutions
                result = self.evaluate_solution(task, solution)
                results.append((result, solution))

        # Check if we have a perfect solution
        perfect_solutions = [r for r in results if r[0].ratio >= 1.0]
        if perfect_solutions:
            best_result, best_solution = max(
                perfect_solutions, key=lambda x: x[0].ratio
            )
            return best_result, [best_solution]

        # If no perfect solution and we need more samples
        if n > initial_n and self.progressive_sampling:
            remaining_n = n - initial_n
            print(f"No perfect solution found, generating {remaining_n} more...")

            additional_tasks = [
                self.generate_solution(task, temperature) for _ in range(remaining_n)
            ]
            additional_solutions = await asyncio.gather(*additional_tasks)
            solutions.extend(additional_solutions)

            # Evaluate additional solutions
            for solution in additional_solutions:
                if solution:
                    result = self.evaluate_solution(task, solution)
                    results.append((result, solution))

        # Find best solution
        if results:
            best_result, best_solution = max(results, key=lambda x: x[0].ratio)
            return best_result, solutions
        else:
            return ExecutionResult(0, 1, 0.0, "No valid solutions"), solutions

    def confidence_weighted_vote(
        self, results: List[ExecutionResult]
    ) -> ExecutionResult:
        """
        Confidence-weighted voting across top 4 candidates
        """
        if not results:
            return ExecutionResult(0, 1, 0.0)

        # Sort by ratio (confidence)
        sorted_results = sorted(results, key=lambda x: x.ratio, reverse=True)

        # Take top 4
        top_4 = sorted_results[:4]

        # Weighted average
        total_weight = sum(r.ratio for r in top_4)
        if total_weight == 0:
            return ExecutionResult(0, 1, 0.0)

        weighted_passed = sum(r.passed * r.ratio for r in top_4)
        weighted_total = sum(r.total * r.ratio for r in top_4)

        final_ratio = weighted_passed / weighted_total if weighted_total > 0 else 0.0

        return ExecutionResult(
            passed=int(weighted_passed),
            total=int(weighted_total),
            ratio=final_ratio,
        )

    async def run_experiment(
        self,
        n_values: List[int] = [1, 4, 16],
        max_tasks: Optional[int] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Run the complete HumanEval experiment
        """
        tasks_to_run = self.tasks[:max_tasks] if max_tasks else self.tasks

        print(f"Running experiment on {len(tasks_to_run)} tasks with n={n_values}")

        results = {}

        for n in n_values:
            print(f"\n=== Running Best-of-{n} ===")
            n_results = []

            for i, task in enumerate(tasks_to_run):
                print(f"Task {i+1}/{len(tasks_to_run)}: {task.task_id}")

                result, solutions = await self.run_best_of_n(task, n, temperature)
                n_results.append(
                    {
                        "task_id": task.task_id,
                        "result": result,
                        "solutions": solutions,
                    }
                )

                # Early exit if we have a perfect solution
                if result.ratio >= 1.0:
                    print(f"  ✓ Perfect solution found (ratio: {result.ratio:.3f})")
                else:
                    print(
                        f"  - Partial solution (ratio: {result.ratio:.3f}, "
                        f"{result.passed}/{result.total})"
                    )

            results[f"bo_{n}"] = n_results

        return results


def calculate_pass_at_k(results: List[Dict], k: int = 1) -> float:
    """Calculate pass@k metric"""
    if not results:
        return 0.0

    passed = sum(1 for r in results if r["result"].ratio >= 1.0)
    return passed / len(results)


def save_results(results: Dict[str, Any], output_dir: str = "results"):
    """Save experiment results to files"""
    os.makedirs(output_dir, exist_ok=True)

    # Save detailed results
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # JSON with all details
    json_file = f"{output_dir}/humaneval_results_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: x.__dict__)

    # CSV summary
    csv_file = f"{output_dir}/humaneval_summary_{timestamp}.csv"
    with open(csv_file, "w") as f:
        f.write("n,pass@1,avg_ratio,avg_passed,avg_total,total_tasks\n")

        for n_key, n_results in results.items():
            n = int(n_key.split("_")[1])
            pass_at_1 = calculate_pass_at_k(n_results, 1)
            avg_ratio = sum(r["result"].ratio for r in n_results) / len(n_results)
            avg_passed = sum(r["result"].passed for r in n_results) / len(n_results)
            avg_total = sum(r["result"].total for r in n_results) / len(n_results)

            f.write(
                f"{n},{pass_at_1:.4f},{avg_ratio:.4f},{avg_passed:.2f},"
                f"{avg_total:.2f},{len(n_results)}\n"
            )

    print(f"Results saved to {json_file} and {csv_file}")
    return json_file, csv_file


async def main():
    """Main function for testing"""
    runner = AsyncHumanEvalRunner(
        max_concurrent=5, requests_per_minute=30, progressive_sampling=True
    )

    # Run on first 10 tasks for testing
    results = await runner.run_experiment(
        n_values=[1, 4], max_tasks=10, temperature=0.7
    )

    # Save results
    save_results(results)

    # Print summary
    for n_key, n_results in results.items():
        n = int(n_key.split("_")[1])
        pass_at_1 = calculate_pass_at_k(n_results, 1)
        print(f"Best-of-{n}: pass@1 = {pass_at_1:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
