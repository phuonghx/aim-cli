#!/usr/bin/env python3
"""Run a Lighthouse audit against a URL and report the headline scores.

Thin wrapper around the Lighthouse CLI: it asks Lighthouse to emit a JSON
report to a temp file, reads the four category scores back out, and prints
them (plus a one-line verdict) as JSON.

Usage:
    python lighthouse_audit.py https://example.com

Prerequisite:
    The Lighthouse CLI on PATH -- `npm install -g lighthouse`.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

AUDIT_TIMEOUT_SECONDS = 120
CATEGORIES = ("performance", "accessibility", "best-practices", "seo")


def _score_percent(categories: dict, key: str) -> int:
    """Pull a 0..1 category score and scale it to an integer percentage."""
    raw = categories.get(key, {}).get("score") or 0
    return int(raw * 100)


def _verdict(performance_pct: int) -> str:
    """Map the performance score onto a short status line."""
    if performance_pct >= 90:
        return "[OK] Excellent performance"
    if performance_pct >= 50:
        return "[!] Needs improvement"
    return "[X] Poor performance"


def audit(url: str) -> dict:
    """Invoke Lighthouse for `url` and return a scores dict (or an error)."""
    binary = shutil.which("lighthouse")
    if not binary:
        return {"error": "Lighthouse CLI not found. Install with: npm install -g lighthouse"}

    # Reserve a temp path for Lighthouse to write its JSON report into.
    handle, report_path = tempfile.mkstemp(suffix=".json")
    os.close(handle)

    argv = [
        binary,
        url,
        "--output=json",
        f"--output-path={report_path}",
        "--chrome-flags=--headless",
        "--only-categories=" + ",".join(CATEGORIES),
    ]

    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=AUDIT_TIMEOUT_SECONDS,
            shell=False,
        )

        if not os.path.exists(report_path) or os.path.getsize(report_path) == 0:
            return {
                "error": "Lighthouse did not produce a report",
                "stderr": (completed.stderr or "")[:500],
            }

        with open(report_path, encoding="utf-8") as report_file:
            report = json.load(report_file)

        categories = report.get("categories", {})
        return {
            "url": url,
            "scores": {
                "performance": _score_percent(categories, "performance"),
                "accessibility": _score_percent(categories, "accessibility"),
                "best_practices": _score_percent(categories, "best-practices"),
                "seo": _score_percent(categories, "seo"),
            },
            "summary": _verdict(_score_percent(categories, "performance")),
        }

    except subprocess.TimeoutExpired:
        return {"error": "Lighthouse audit timed out"}
    finally:
        # Clean up the temp report regardless of how things went.
        try:
            os.unlink(report_path)
        except OSError:
            pass


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python lighthouse_audit.py <url>"}))
        sys.exit(1)

    print(json.dumps(audit(sys.argv[1]), indent=2))


if __name__ == "__main__":
    main()
