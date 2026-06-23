#!/usr/bin/env python3
"""Detect a project's stack and run its linters / type checkers.

The script figures out whether it is looking at a Node or Python project,
builds the list of checks that make sense, runs each one, and prints both
a human summary and a machine-readable JSON blob. Exit status is zero only
when every check passes.

Usage:
    python lint_runner.py <project_path>

Covers:
    Node.js -> npm run lint (or eslint), tsc --noEmit
    Python  -> ruff check, mypy
"""

import json
import platform
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

IS_WINDOWS = platform.system() == "Windows"
CHECK_TIMEOUT_SECONDS = 120


def _read_package_json(path: Path) -> dict:
    """Parse package.json, returning {} on any problem."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def plan_checks(root: Path) -> dict:
    """Inspect the project and produce the list of checks to run."""
    plan = {"stack": "unknown", "checks": []}

    package_json = root / "package.json"
    if package_json.exists():
        plan["stack"] = "node"
        manifest = _read_package_json(package_json)
        scripts = manifest.get("scripts", {})
        deps = {**manifest.get("dependencies", {}), **manifest.get("devDependencies", {})}

        # Prefer a project-defined lint script; fall back to eslint directly.
        if "lint" in scripts:
            plan["checks"].append({"label": "npm lint", "argv": ["npm", "run", "lint"]})
        elif "eslint" in deps:
            plan["checks"].append({"label": "eslint", "argv": ["npx", "eslint", "."]})

        # Type checking when TypeScript is in the picture.
        if "typescript" in deps or (root / "tsconfig.json").exists():
            plan["checks"].append({"label": "tsc", "argv": ["npx", "tsc", "--noEmit"]})

    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        plan["stack"] = "python"
        plan["checks"].append({"label": "ruff", "argv": ["ruff", "check", "."]})
        if (root / "mypy.ini").exists() or (root / "pyproject.toml").exists():
            plan["checks"].append({"label": "mypy", "argv": ["mypy", "."]})

    return plan


def _resolve_executable(argv: list) -> list:
    """Return argv with its program resolved to a concrete path.

    On Windows, tools like npm/npx ship as ``.cmd`` shims that the bare
    name will not find without a shell. ``shutil.which`` locates the real
    file, which lets us launch it through a plain argument list -- no
    ``shell=True`` and therefore no shell-injection surface.
    """
    resolved = list(argv)
    located = shutil.which(resolved[0])
    if located:
        resolved[0] = located
    return resolved


def execute_check(check: dict, root: Path) -> dict:
    """Run a single check and capture its outcome."""
    outcome = {"label": check["label"], "ok": False, "stdout": "", "stderr": ""}

    argv = _resolve_executable(check["argv"])

    try:
        completed = subprocess.run(
            argv,
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=CHECK_TIMEOUT_SECONDS,
            shell=False,  # explicit: never hand argv to a shell
        )
        outcome["stdout"] = (completed.stdout or "")[:2000]
        outcome["stderr"] = (completed.stderr or "")[:500]
        outcome["ok"] = completed.returncode == 0
    except FileNotFoundError:
        outcome["stderr"] = f"Command not found: {check['argv'][0]}"
    except subprocess.TimeoutExpired:
        outcome["stderr"] = f"Timed out after {CHECK_TIMEOUT_SECONDS}s"
    except OSError as err:
        outcome["stderr"] = str(err)

    return outcome


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    bar = "=" * 60
    print(f"\n{bar}")
    print("[LINT RUNNER] Unified Linting")
    print(bar)
    print(f"Project: {root}")
    print(f"Time: {datetime.now():%Y-%m-%d %H:%M:%S}")

    plan = plan_checks(root)
    print(f"Stack: {plan['stack']}")
    print(f"Checks queued: {len(plan['checks'])}")
    print("-" * 60)

    if not plan["checks"]:
        print("No linters apply to this project.")
        print(json.dumps({
            "script": "lint_runner",
            "project": str(root),
            "type": plan["stack"],
            "checks": [],
            "passed": True,
            "message": "No linters configured",
        }, indent=2))
        sys.exit(0)

    outcomes = []
    every_check_passed = True

    for check in plan["checks"]:
        print(f"\nRunning: {check['label']}...")
        outcome = execute_check(check, root)
        outcomes.append(outcome)
        if outcome["ok"]:
            print(f"  [PASS] {check['label']}")
        else:
            print(f"  [FAIL] {check['label']}")
            if outcome["stderr"]:
                print(f"  Error: {outcome['stderr'][:200]}")
            every_check_passed = False

    print(f"\n{bar}")
    print("SUMMARY")
    print(bar)
    for outcome in outcomes:
        badge = "[PASS]" if outcome["ok"] else "[FAIL]"
        print(f"{badge} {outcome['label']}")

    # Re-key outcomes to match the legacy JSON shape consumers may expect.
    serialized_checks = [
        {
            "name": o["label"],
            "passed": o["ok"],
            "output": o["stdout"],
            "error": o["stderr"],
        }
        for o in outcomes
    ]

    print("\n" + json.dumps({
        "script": "lint_runner",
        "project": str(root),
        "type": plan["stack"],
        "checks": serialized_checks,
        "passed": every_check_passed,
    }, indent=2))

    sys.exit(0 if every_check_passed else 1)


if __name__ == "__main__":
    main()
