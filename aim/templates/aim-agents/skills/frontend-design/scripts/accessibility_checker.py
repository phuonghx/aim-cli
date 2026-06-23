#!/usr/bin/env python3
"""Accessibility Checker.

Scans markup-bearing files (HTML, JSX, TSX) for a handful of common WCAG
pitfalls -- unlabeled inputs, text-less buttons, missing language hints,
keyboard-handler gaps, and a few related issues.

Run:
    python accessibility_checker.py <project_path>

A small number of findings is tolerated; the process only exits non-zero
once the total crosses a low threshold.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Older Windows consoles default to a non-UTF code page; nudge stdout to
# UTF-8 so symbols in the report don't blow up, and ignore failures.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# Folders that hold generated or vendored code we never want to lint.
IGNORED_DIRS = {"node_modules", ".next", "dist", "build", ".git"}
# Glob patterns for the markup we do care about.
MARKUP_GLOBS = ("**/*.html", "**/*.jsx", "**/*.tsx")
# Cap how many files we examine so huge trees stay fast.
MAX_FILES = 50
# Allow this many findings before the run is considered a failure.
FAILURE_THRESHOLD = 5


def gather_markup(root: Path):
    """Collect markup files under *root*, skipping vendored directories."""
    collected = []
    for glob_pattern in MARKUP_GLOBS:
        for candidate in root.glob(glob_pattern):
            if any(part in IGNORED_DIRS for part in candidate.parts):
                continue
            collected.append(candidate)
    return collected[:MAX_FILES]


def _inputs_missing_labels(markup: str):
    """True if any non-hidden input lacks both an id and an aria-label."""
    for tag in re.findall(r"<input[^>]*>", markup, re.IGNORECASE):
        lowered = tag.lower()
        if 'type="hidden"' in lowered:
            continue
        if "aria-label" not in lowered and "id=" not in lowered:
            return True
    return False


def _buttons_missing_text(markup: str):
    """True if any <button> has neither inner text nor an aria-label."""
    for tag in re.findall(r"<button[^>]*>[^<]*</button>", markup, re.IGNORECASE):
        if "aria-label" in tag.lower():
            continue
        inner = re.sub(r"<[^>]+>", "", tag)
        if not inner.strip():
            return True
    return False


def _has_positive_tabindex(markup: str):
    """True if a positive (>=1) tabindex is present, which we discourage."""
    lowered = markup.lower()
    if "tabindex=" not in lowered:
        return False
    # Anything other than the safe values 0 and -1 is suspect.
    if 'tabindex="-1"' in lowered or 'tabindex="0"' in lowered:
        # There may still be a positive one alongside the safe ones.
        pass
    return bool(re.findall(r'tabindex="([1-9]\d*)"', markup, re.IGNORECASE))


def _div_role_button_without_tabindex(markup: str):
    """True if a div carries role="button" but no tabindex to focus it."""
    if 'role="button"' not in markup.lower():
        return False
    for tag in re.findall(r'<div[^>]*role="button"[^>]*>', markup, re.IGNORECASE):
        if "tabindex" not in tag.lower():
            return True
    return False


def review_file(path: Path):
    """Return a list of accessibility findings for a single file."""
    findings = []

    try:
        markup = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as err:
        return [f"Error reading file: {str(err)[:50]}"]

    lowered = markup.lower()

    # Form controls need a programmatic name.
    if _inputs_missing_labels(markup):
        findings.append("Input without label or aria-label")

    # Icon-only buttons must expose an accessible name.
    if _buttons_missing_text(markup):
        findings.append("Button without accessible text")

    # The document language helps screen readers pick pronunciation.
    if "<html" in lowered and "lang=" not in lowered:
        findings.append("Missing lang attribute on <html>")

    # A skip link lets keyboard users bypass repeated navigation.
    if "<main" in lowered or "<body" in lowered:
        if "skip" not in lowered and "#main" not in lowered:
            findings.append("Consider adding skip-to-main-content link")

    # Mouse handlers without a keyboard equivalent exclude keyboard users.
    click_count = lowered.count("onclick=")
    key_count = lowered.count("onkeydown=") + lowered.count("onkeyup=")
    if click_count > 0 and key_count == 0:
        findings.append("onClick without keyboard handler (onKeyDown)")

    # Positive tabindex values fight the natural focus order.
    if _has_positive_tabindex(markup):
        findings.append("Avoid positive tabIndex values")

    # Autoplaying media should be muted to avoid surprising the user.
    if "autoplay" in lowered and "muted" not in lowered:
        findings.append("Autoplay media should be muted")

    # A div acting as a button needs to be reachable by keyboard.
    if _div_role_button_without_tabindex(markup):
        findings.append("role='button' without tabindex")

    return findings


def _print_header(target: Path):
    bar = "=" * 60
    print(f"\n{bar}")
    print("[ACCESSIBILITY CHECKER] WCAG Compliance Audit")
    print(bar)
    print(f"Project: {target}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)


def run(target: Path):
    """Audit every markup file under *target* and emit a report."""
    _print_header(target)

    files = gather_markup(target)
    print(f"Found {len(files)} HTML/JSX/TSX files")

    # No markup to review -- report a clean pass.
    if not files:
        empty = {
            "script": "accessibility_checker",
            "project": str(target),
            "files_checked": 0,
            "issues_found": 0,
            "passed": True,
            "message": "No HTML files found",
        }
        print(json.dumps(empty, indent=2))
        return 0

    # Keep only files that actually have findings.
    flagged = []
    for path in files:
        findings = review_file(path)
        if findings:
            flagged.append({"file": path.name, "issues": findings})

    print("\n" + "=" * 60)
    print("ACCESSIBILITY ISSUES")
    print("=" * 60)

    if flagged:
        for entry in flagged[:10]:
            print(f"\n{entry['file']}:")
            for note in entry["issues"]:
                print(f"  - {note}")
        overflow = len(flagged) - 10
        if overflow > 0:
            print(f"\n... and {overflow} more files with issues")
    else:
        print("No accessibility issues found!")

    total = sum(len(entry["issues"]) for entry in flagged)
    # A few minor issues are acceptable; only a larger count fails the run.
    passed = total < FAILURE_THRESHOLD

    report = {
        "script": "accessibility_checker",
        "project": str(target),
        "files_checked": len(files),
        "files_with_issues": len(flagged),
        "issues_found": total,
        "passed": passed,
    }
    print("\n" + json.dumps(report, indent=2))
    return 0 if passed else 1


def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else "."
    target = Path(raw).resolve()
    sys.exit(run(target))


if __name__ == "__main__":
    main()
