#!/usr/bin/env python3
"""Audit public pages for common on-page SEO problems.

Restricts itself to files that are plausibly real, public pages -- HTML
documents and React route components -- and skips utilities, configs, and
tests. For each page it checks the title, meta description, Open Graph
tags, heading structure, and image alt text, then summarizes the issues
found across the project.

Usage:
    python seo_checker.py <project_path>
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Unicode-safe console on legacy Windows terminals.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


# Whole directories that never contain public pages.
EXCLUDED_DIRS = frozenset({
    "node_modules", ".next", "dist", "build", ".git", ".github",
    "__pycache__", ".vscode", ".idea", "coverage", "test", "tests",
    "__tests__", "spec", "docs", "documentation", "examples",
})

# Substrings in a filename that mark it as non-page code.
NON_PAGE_TOKENS = (
    "config", "setup", "util", "helper", "hook", "context", "store",
    "service", "api", "lib", "constant", "type", "interface", "mock",
    ".test.", ".spec.", "_test.", "_spec.",
)

# Directory names whose contents are treated as pages.
PAGE_DIRS = ("pages", "app", "routes", "views", "screens")

# Stems that hint a file is itself a page.
PAGE_STEM_HINTS = (
    "page", "index", "home", "about", "contact", "blog",
    "post", "article", "product", "landing", "layout",
)

MAX_PAGES = 50
MAX_LISTED_FILES = 5


def is_public_page(path: Path) -> bool:
    """Heuristically decide whether `path` is a public-facing page."""
    name = path.name.lower()

    if any(token in name for token in NON_PAGE_TOKENS):
        return False

    if any(folder in (segment.lower() for segment in path.parts) for folder in PAGE_DIRS):
        return True

    if any(hint in path.stem.lower() for hint in PAGE_STEM_HINTS):
        return True

    return path.suffix.lower() in {".html", ".htm"}


def collect_pages(root: Path) -> list:
    """Return up to MAX_PAGES candidate page files under `root`."""
    found = []
    for pattern in ("**/*.html", "**/*.htm", "**/*.jsx", "**/*.tsx"):
        for candidate in root.glob(pattern):
            if EXCLUDED_DIRS.intersection(candidate.parts):
                continue
            if is_public_page(candidate):
                found.append(candidate)
    return found[:MAX_PAGES]


def inspect_page(path: Path) -> dict:
    """Check a single page and return the list of SEO issues on it."""
    try:
        markup = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as err:
        return {"file": path.name, "issues": [f"Could not read: {err}"]}

    issues = []
    lowered = markup.lower()

    # Pages that own a <head>/<Head> are where the document-level tags belong.
    owns_head = "<head" in lowered or "<head>" in lowered

    if owns_head:
        has_title = "<title" in lowered or "title=" in markup or "Head>" in markup
        if not has_title:
            issues.append("Missing <title> tag")

        if 'name="description"' not in lowered and "name='description'" not in lowered:
            issues.append("Missing meta description")

        if "og:" not in markup and 'property="og:' not in lowered:
            issues.append("Missing Open Graph tags")

    # More than one H1 muddies the page's primary topic.
    h1_count = len(re.findall(r"<h1[^>]*>", markup, re.IGNORECASE))
    if h1_count > 1:
        issues.append(f"Multiple H1 tags ({h1_count})")

    # Image accessibility: missing or empty alt text (report once each).
    for img_tag in re.findall(r"<img[^>]+>", markup, re.IGNORECASE):
        lowered_tag = img_tag.lower()
        if "alt=" not in lowered_tag:
            issues.append("Image missing alt attribute")
            break
    for img_tag in re.findall(r"<img[^>]+>", markup, re.IGNORECASE):
        if 'alt=""' in img_tag or "alt=''" in img_tag:
            issues.append("Image has empty alt attribute")
            break

    return {"file": path.name, "issues": issues}


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    bar = "=" * 60
    print(f"\n{bar}")
    print("  SEO CHECKER - Search Engine Optimization Audit")
    print(bar)
    print(f"Project: {root}")
    print(f"Time: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("-" * 60)

    pages = collect_pages(root)

    if not pages:
        print("\n[!] No page files found.")
        print("    Searched: HTML / JSX / TSX under page or route folders")
        print("\n" + json.dumps(
            {"script": "seo_checker", "files_checked": 0, "passed": True}, indent=2
        ))
        sys.exit(0)

    print(f"Auditing {len(pages)} page file(s)\n")

    flagged = [report for report in (inspect_page(p) for p in pages) if report["issues"]]

    print(bar)
    print("SEO ANALYSIS RESULTS")
    print(bar)

    if flagged:
        # Roll issues up by type so the most common problems surface first.
        frequency: dict = {}
        for report in flagged:
            for issue in report["issues"]:
                frequency[issue] = frequency.get(issue, 0) + 1

        print("\nIssue summary:")
        for issue, count in sorted(frequency.items(), key=lambda pair: -pair[1]):
            print(f"  [{count}] {issue}")

        print(f"\nAffected files ({len(flagged)}):")
        for report in flagged[:MAX_LISTED_FILES]:
            print(f"  - {report['file']}")
        if len(flagged) > MAX_LISTED_FILES:
            print(f"  ... and {len(flagged) - MAX_LISTED_FILES} more")
    else:
        print("\n[OK] No SEO issues found!")

    total_issues = sum(len(report["issues"]) for report in flagged)
    passed = total_issues == 0

    print("\n" + json.dumps({
        "script": "seo_checker",
        "project": str(root),
        "files_checked": len(pages),
        "files_with_issues": len(flagged),
        "issues_found": total_issues,
        "passed": passed,
    }, indent=2))

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
