#!/usr/bin/env python3
"""Detect a project's test framework, run it, and summarize the result.

Recognizes the common Node runners (jest, vitest, or whatever `npm test`
maps to) and Python's pytest. It runs the suite, scrapes pass/fail counts
out of the output when it can, and emits both a readable summary and a
JSON object. Pass ``--coverage`` to prefer the coverage variant of the
command when one is known.

Usage:
    python test_runner.py <project_path> [--coverage]
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Unicode-safe stdout on legacy Windows consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

TEST_TIMEOUT_SECONDS = 300  # suites can be slow; give them five minutes
PASS_RE = re.compile(r"(\d+)\s+passed", re.IGNORECASE)
FAIL_RE = re.compile(r"(\d+)\s+failed", re.IGNORECASE)


def _read_package_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def identify_runner(root: Path) -> dict:
    """Work out which test framework the project uses and how to invoke it."""
    info = {"stack": "unknown", "framework": None, "run": None, "run_coverage": None}

    package_json = root / "package.json"
    if package_json.exists():
        info["stack"] = "node"
        manifest = _read_package_json(package_json)
        scripts = manifest.get("scripts", {})
        deps = {**manifest.get("dependencies", {}), **manifest.get("devDependencies", {})}

        if "test" in scripts:
            # Respect the project's own test script as the default entry point.
            info["framework"] = "npm test"
            info["run"] = ["npm", "test"]
            # ...but if we recognize the underlying runner, we know its coverage flag.
            if "vitest" in deps:
                info["framework"] = "vitest"
                info["run_coverage"] = ["npx", "vitest", "run", "--coverage"]
            elif "jest" in deps:
                info["framework"] = "jest"
                info["run_coverage"] = ["npx", "jest", "--coverage"]
        elif "vitest" in deps:
            info["framework"] = "vitest"
            info["run"] = ["npx", "vitest", "run"]
            info["run_coverage"] = ["npx", "vitest", "run", "--coverage"]
        elif "jest" in deps:
            info["framework"] = "jest"
            info["run"] = ["npx", "jest"]
            info["run_coverage"] = ["npx", "jest", "--coverage"]

    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        info["stack"] = "python"
        info["framework"] = "pytest"
        info["run"] = ["python", "-m", "pytest", "-v"]
        info["run_coverage"] = ["python", "-m", "pytest", "--cov", "--cov-report=term-missing"]

    return info


def _resolve(argv: list) -> list:
    """Resolve argv[0] to a concrete path so no shell is needed to find it."""
    resolved = list(argv)
    located = shutil.which(resolved[0])
    if located:
        resolved[0] = located
    return resolved


def _tally(text: str) -> tuple:
    """Extract (passed, failed) counts from runner output, defaulting to 0."""
    passed = int(PASS_RE.search(text).group(1)) if PASS_RE.search(text) else 0
    failed = int(FAIL_RE.search(text).group(1)) if FAIL_RE.search(text) else 0
    return passed, failed


def run_suite(argv: list, root: Path) -> dict:
    """Execute the test command and parse what we can from its output."""
    result = {
        "ok": False, "stdout": "", "stderr": "",
        "total": 0, "passed": 0, "failed": 0,
    }

    try:
        completed = subprocess.run(
            _resolve(argv),
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TEST_TIMEOUT_SECONDS,
            shell=False,
        )
        result["stdout"] = (completed.stdout or "")[:3000]
        result["stderr"] = (completed.stderr or "")[:500]
        result["ok"] = completed.returncode == 0

        passed, failed = _tally(completed.stdout or "")
        result["passed"] = passed
        result["failed"] = failed
        result["total"] = passed + failed

    except FileNotFoundError:
        result["stderr"] = f"Command not found: {argv[0]}"
    except subprocess.TimeoutExpired:
        result["stderr"] = f"Timed out after {TEST_TIMEOUT_SECONDS}s"
    except OSError as err:
        result["stderr"] = str(err)

    return result


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    want_coverage = "--coverage" in sys.argv

    bar = "=" * 60
    print(f"\n{bar}")
    print("[TEST RUNNER] Unified Test Execution")
    print(bar)
    print(f"Project: {root}")
    print(f"Coverage: {'enabled' if want_coverage else 'disabled'}")
    print(f"Time: {datetime.now():%Y-%m-%d %H:%M:%S}")

    info = identify_runner(root)
    print(f"Stack: {info['stack']}")
    print(f"Framework: {info['framework']}")
    print("-" * 60)

    if not info["run"]:
        print("No test framework detected for this project.")
        print(json.dumps({
            "script": "test_runner",
            "project": str(root),
            "type": info["stack"],
            "framework": None,
            "passed": True,
            "message": "No tests configured",
        }, indent=2))
        sys.exit(0)

    argv = info["run_coverage"] if want_coverage and info["run_coverage"] else info["run"]
    print(f"Running: {' '.join(argv)}")
    print("-" * 60)

    result = run_suite(argv, root)

    # Echo a bounded slice of the runner's own output.
    if result["stdout"]:
        lines = result["stdout"].splitlines()
        for line in lines[:30]:
            print(line)
        if len(lines) > 30:
            print(f"... ({len(lines) - 30} more lines)")

    print(f"\n{bar}")
    print("SUMMARY")
    print(bar)
    if result["ok"]:
        print("[PASS] All tests passed")
    else:
        print("[FAIL] Some tests failed")
        if result["stderr"]:
            print(f"Error: {result['stderr'][:200]}")

    if result["total"] > 0:
        print(f"Tests: {result['total']} total, {result['passed']} passed, {result['failed']} failed")

    print("\n" + json.dumps({
        "script": "test_runner",
        "project": str(root),
        "type": info["stack"],
        "framework": info["framework"],
        "tests_run": result["total"],
        "tests_passed": result["passed"],
        "tests_failed": result["failed"],
        "passed": result["ok"],
    }, indent=2))

    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
