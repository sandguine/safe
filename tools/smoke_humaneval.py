import os
import subprocess
import sys
import tempfile
import textwrap

PROMPT = textwrap.dedent(
    """
def add(a: int, b: int) -> int:
    # Return the sum of two integers.
    return a + b
"""
)


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "solution.py")
        with open(src, "w") as f:
            f.write(PROMPT)

        # run in the same sandbox you use for full HumanEval
        p = subprocess.run(
            ["python", src],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if p.returncode != 0:
            print(p.stderr)
            sys.exit("❌ sandbox smoke failed ➜ preexec_fn still broken")

    print("✅ sandbox smoke passed")


if __name__ == "__main__":
    main()
