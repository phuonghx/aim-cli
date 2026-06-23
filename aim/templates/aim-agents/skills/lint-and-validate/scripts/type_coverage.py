#!/usr/bin/env python3
"""Estimate how thoroughly a codebase is type-annotated.

This is a lightweight, regex-driven heuristic rather than a real type
checker. For TypeScript it counts `any` usages and the ratio of typed to
untyped function signatures; for Python it looks at how many `def`s carry
annotations and how often `Any` shows up. Both produce a rough coverage
percentage plus pass/warn/fail markers.

Usage:
    python type_coverage.py <project_path>
"""

import re
import sys
from pathlib import Path

# Keep Unicode markers printable on older Windows shells.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

FILE_SCAN_LIMIT = 30
SKIP_FRAGMENTS = ("node_modules", ".git", "dist", "build", "__pycache__", "venv")


def _eligible(path: Path, extra_skip=()) -> bool:
    blocked = SKIP_FRAGMENTS + tuple(extra_skip)
    return not any(fragment in str(path) for fragment in blocked)


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def measure_typescript(root: Path) -> dict:
    """Approximate TypeScript type coverage."""
    tally = {"any": 0, "untyped_fns": 0, "all_fns": 0}
    wins, flags = [], []

    files = [
        p for ext in ("*.ts", "*.tsx")
        for p in root.rglob(ext)
        if _eligible(p) and ".d.ts" not in str(p)
    ]

    if not files:
        return {"lang": "typescript", "count": 0, "wins": [], "flags": ["[!] No TypeScript files found"], "tally": tally}

    for path in files[:FILE_SCAN_LIMIT]:
        src = _safe_read(path)
        if not src:
            continue

        tally["any"] += len(re.findall(r":\s*any\b", src))

        # Function forms missing an explicit return type.
        untyped = re.findall(r"function\s+\w+\s*\([^)]*\)\s*{", src)
        untyped += re.findall(r"=\s*\([^:)]*\)\s*=>", src)

        # Function forms that do declare a return type.
        typed = re.findall(r"function\s+\w+\s*\([^)]*\)\s*:\s*\w+", src)
        typed += re.findall(r":\s*\([^)]*\)\s*=>\s*\w+", src)

        tally["untyped_fns"] += len(untyped)
        tally["all_fns"] += len(typed) + len(untyped)

    # 'any' verdict.
    if tally["any"] == 0:
        wins.append("[OK] No 'any' types found")
    elif tally["any"] <= 5:
        flags.append(f"[!] {tally['any']} 'any' types (tolerable)")
    else:
        flags.append(f"[X] {tally['any']} 'any' types (excessive)")

    # Coverage verdict.
    if tally["all_fns"] > 0:
        covered = (tally["all_fns"] - tally["untyped_fns"]) / tally["all_fns"] * 100
        if covered >= 80:
            wins.append(f"[OK] Type coverage: {covered:.0f}%")
        elif covered >= 50:
            flags.append(f"[!] Type coverage: {covered:.0f}% (improve)")
        else:
            flags.append(f"[X] Type coverage: {covered:.0f}% (too low)")

    wins.append(f"[OK] Scanned {len(files)} TypeScript file(s)")
    return {"lang": "typescript", "count": len(files), "wins": wins, "flags": flags, "tally": tally}


def measure_python(root: Path) -> dict:
    """Approximate Python type-hint coverage."""
    tally = {"untyped_fns": 0, "typed_fns": 0, "any": 0}
    wins, flags = [], []

    files = [p for p in root.rglob("*.py") if _eligible(p)]

    if not files:
        return {"lang": "python", "count": 0, "wins": [], "flags": ["[!] No Python files found"], "tally": tally}

    for path in files[:FILE_SCAN_LIMIT]:
        src = _safe_read(path)
        if not src:
            continue

        tally["any"] += len(re.findall(r":\s*Any\b", src))

        # Annotated signatures: either a typed parameter or a return arrow.
        annotated = re.findall(r"def\s+\w+\s*\([^)]*:[^)]+\)", src)
        annotated += re.findall(r"def\s+\w+\s*\([^)]*\)\s*->", src)
        tally["typed_fns"] += len(annotated)

        every_def = re.findall(r"def\s+\w+\s*\(", src)
        tally["untyped_fns"] += len(every_def) - len(annotated)

    total = tally["typed_fns"] + tally["untyped_fns"]
    if total > 0:
        covered = tally["typed_fns"] / total * 100
        if covered >= 70:
            wins.append(f"[OK] Type hint coverage: {covered:.0f}%")
        elif covered >= 40:
            flags.append(f"[!] Type hint coverage: {covered:.0f}%")
        else:
            flags.append(f"[X] Type hint coverage: {covered:.0f}% (add hints)")

    if tally["any"] == 0:
        wins.append("[OK] No 'Any' types found")
    elif tally["any"] <= 3:
        flags.append(f"[!] {tally['any']} 'Any' types")
    else:
        flags.append(f"[X] {tally['any']} 'Any' types")

    wins.append(f"[OK] Scanned {len(files)} Python file(s)")
    return {"lang": "python", "count": len(files), "wins": wins, "flags": flags, "tally": tally}


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

    print("\n" + "=" * 60)
    print("  TYPE COVERAGE CHECKER")
    print("=" * 60)

    reports = [r for r in (measure_typescript(root), measure_python(root)) if r["count"] > 0]

    if not reports:
        print("\n[!] No TypeScript or Python files found.")
        sys.exit(0)

    blockers = 0
    for report in reports:
        print(f"\n[{report['lang'].upper()}]")
        print("-" * 40)
        for line in report["wins"]:
            print(f"  {line}")
        for line in report["flags"]:
            print(f"  {line}")
            if line.startswith("[X]"):
                blockers += 1

    print("\n" + "=" * 60)
    if blockers == 0:
        print("[OK] TYPE COVERAGE: ACCEPTABLE")
        sys.exit(0)
    print(f"[X] TYPE COVERAGE: {blockers} critical issue(s)")
    sys.exit(1)


if __name__ == "__main__":
    main()
