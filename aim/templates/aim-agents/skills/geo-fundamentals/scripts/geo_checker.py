#!/usr/bin/env python3
"""Audit public-facing pages for generative-engine citation readiness.

The aim is to look only at material that an answer engine (ChatGPT,
Perplexity, Gemini, ...) might actually retrieve and quote. That means
rendered pages -- HTML documents and React route components -- and
deliberately *not* developer markdown, which never gets indexed as
public content.

For every candidate page we tally signals that make a passage easy to
lift and trust (structured data, a single clear topic, attribution,
dates, Q&A blocks, quotable numbers, ...) and turn that into a percent
score.

Run it with:
    python geo_checker.py <project_path>
"""

import json
import re
import sys
from pathlib import Path

# Keep Unicode output from blowing up on a legacy Windows console.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        # reconfigure landed in 3.7; older runtimes just carry on.
        pass


# Folders that never hold public pages -- walk straight past them.
EXCLUDED_FOLDERS = frozenset({
    "node_modules", ".next", "dist", "build", ".git", ".github",
    "__pycache__", ".vscode", ".idea", "coverage", "test", "tests",
    "__tests__", "spec", "docs", "documentation",
})

# Filename stems that signal tooling/config rather than a page.
NON_PAGE_STEMS = (
    "jest.config", "webpack.config", "vite.config", "tsconfig",
    "package.json", "package-lock", "yarn.lock", ".eslintrc",
    "tailwind.config", "postcss.config", "next.config",
)

# Stems that hint a file is a real page.
PAGE_STEM_HINTS = (
    "page", "index", "home", "about", "contact", "blog",
    "post", "article", "product", "service", "landing",
)

# Directory names that, when present in the path, mark route files.
ROUTE_FOLDERS = ("pages", "app", "routes")

MAX_PAGES = 30
PASS_THRESHOLD = 60


def looks_like_a_page(path: Path) -> bool:
    """Best-effort guess at whether `path` is a public page worth auditing."""
    stem = path.stem.lower()

    # Drop obvious config/tooling files.
    if any(token in stem for token in NON_PAGE_STEMS):
        return False

    # Drop test specs regardless of extension.
    if stem.endswith((".test", ".spec")) or stem.startswith(("test_", "spec_")):
        return False

    lowered_parts = [segment.lower() for segment in path.parts]

    # Anything living under a routing directory is treated as a page.
    if any(folder in lowered_parts for folder in ROUTE_FOLDERS):
        return True

    # Filename-based hints.
    if any(hint in stem for hint in PAGE_STEM_HINTS):
        return True

    # Raw HTML is almost always a page.
    return path.suffix.lower() in {".html", ".htm"}


def gather_pages(root: Path) -> list:
    """Collect up to MAX_PAGES candidate page files beneath `root`."""
    collected = []
    for glob_pattern in ("**/*.html", "**/*.htm", "**/*.jsx", "**/*.tsx"):
        for candidate in root.glob(glob_pattern):
            if EXCLUDED_FOLDERS.intersection(candidate.parts):
                continue
            if looks_like_a_page(candidate):
                collected.append(candidate)
    return collected[:MAX_PAGES]


def _count(pattern: str, text: str) -> int:
    """Number of case-insensitive matches for `pattern` in `text`."""
    return len(re.findall(pattern, text, re.IGNORECASE))


def _present(text: str, needles) -> bool:
    """True if any regex in `needles` appears (case-insensitive) in `text`."""
    return any(re.search(n, text, re.IGNORECASE) for n in needles)


def audit_page(path: Path) -> dict:
    """Score one page against the GEO signal checklist."""
    try:
        markup = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as err:
        return {"file": path.name, "wins": [], "gaps": [f"Could not read: {err}"], "score": 0}

    wins = []   # signals found
    gaps = []   # signals missing / weak

    # --- Structured data (a major retrieval lever) -------------------------
    if "application/ld+json" in markup:
        wins.append("JSON-LD structured data present")
        if '"@type"' in markup:
            if "Article" in markup:
                wins.append("Article schema declared")
            if "FAQPage" in markup:
                wins.append("FAQ schema declared")
            if "Organization" in markup or "Person" in markup:
                wins.append("Entity schema declared")
    else:
        gaps.append("No JSON-LD structured data (engines favour structured pages)")

    # --- Heading topology --------------------------------------------------
    h1_total = _count(r"<h1[^>]*>", markup)
    h2_total = _count(r"<h2[^>]*>", markup)

    if h1_total == 1:
        wins.append("Exactly one H1 (clear single topic)")
    elif h1_total == 0:
        gaps.append("No H1 -- page topic is ambiguous")
    else:
        gaps.append(f"{h1_total} H1 tags -- competing topics confuse extraction")

    if h2_total >= 2:
        wins.append(f"{h2_total} H2 sections (scannable structure)")
    else:
        gaps.append("Too few H2 sections for a scannable layout")

    # --- Authorship (an E-E-A-T trust marker) ------------------------------
    if _present(markup, [r"\bauthor\b", r"byline", r"written-by", r"contributor", r'rel="author"']):
        wins.append("Author attribution present")
    else:
        gaps.append("No author info (attributed content is preferred)")

    # --- Freshness ---------------------------------------------------------
    if _present(markup, [r"datePublished", r"dateModified", r"datetime=", r"pubdate", r"article:published"]):
        wins.append("Publication / update date present")
    else:
        gaps.append("No date metadata (freshness influences citations)")

    # --- Bonus signals (counted only when found) ---------------------------
    if _present(markup, [r"<details", r"\bfaq\b", r"frequently.?asked", r'"FAQPage"']):
        wins.append("FAQ-style content (highly quotable)")

    list_total = _count(r"<(?:ul|ol)[^>]*>", markup)
    if list_total >= 2:
        wins.append(f"{list_total} lists (structured content)")

    table_total = _count(r"<table[^>]*>", markup)
    if table_total >= 1:
        wins.append(f"{table_total} table(s) (comparison data)")

    if _present(markup, [
        r'"@type"\s*:\s*"Organization"',
        r'"@type"\s*:\s*"LocalBusiness"',
        r'"@type"\s*:\s*"Brand"',
        r"itemtype.*schema\.org/(?:Organization|Person|Brand)",
        r'rel="author"',
    ]):
        wins.append("Brand/entity recognition signals")

    # Quotable data points: a couple of these flips it into a "win".
    quant_signals = (
        r"\d+%",
        r"\$[\d,]+",
        r"study\s+(?:shows|found)",
        r"according to",
        r"data\s+(?:shows|reveals)",
        r"\d+x\s+(?:faster|better|more)",
        r"(?:million|billion|trillion)",
    )
    if sum(1 for sig in quant_signals if re.search(sig, markup, re.IGNORECASE)) >= 2:
        wins.append("First-party-style statistics (citation magnet)")

    if _present(markup, [
        r"is defined as", r"refers to", r"means that",
        r"the answer is", r"in short,", r"simply put,", r"<dfn",
    ]):
        wins.append("Direct-answer phrasing (LLM friendly)")

    # --- Score = share of checked signals that passed ----------------------
    checked = len(wins) + len(gaps)
    score = round(len(wins) / checked * 100) if checked else 0

    return {"file": path.name, "wins": wins, "gaps": gaps, "score": score}


def _verdict(avg: float) -> str:
    if avg >= 80:
        return "[OK] Excellent -- pages are well prepared for AI citations"
    if avg >= PASS_THRESHOLD:
        return "[OK] Good -- a few refinements would help"
    if avg >= 40:
        return "[!] Needs work -- add more structured signals"
    return "[X] Poor -- significant GEO work required"


def main() -> None:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    bar = "=" * 60
    print(f"\n{bar}")
    print("  GEO CHECKER - AI Citation Readiness Audit")
    print(bar)
    print(f"Project: {target}")
    print("-" * 60)

    pages = gather_pages(target)

    if not pages:
        print("\n[!] No public web pages located.")
        print("    Searched: HTML / JSX / TSX under page or route folders")
        print("    Skipped: docs, tests, config, node_modules")
        print("\n" + json.dumps(
            {"script": "geo_checker", "pages_found": 0, "passed": True}, indent=2
        ))
        sys.exit(0)

    print(f"Auditing {len(pages)} public page(s)\n")

    reports = [audit_page(page) for page in pages]

    for report in reports:
        marker = "[OK]" if report["score"] >= PASS_THRESHOLD else "[!]"
        print(f"{marker} {report['file']}: {report['score']}%")
        if report["gaps"] and report["score"] < PASS_THRESHOLD:
            for gap in report["gaps"][:2]:
                print(f"    - {gap}")

    average = sum(r["score"] for r in reports) / len(reports)

    print(f"\n{bar}")
    print(f"AVERAGE GEO SCORE: {average:.0f}%")
    print(bar)
    print(_verdict(average))

    print("\n" + json.dumps({
        "script": "geo_checker",
        "project": str(target),
        "pages_checked": len(reports),
        "average_score": round(average),
        "passed": average >= PASS_THRESHOLD,
    }, indent=2))

    sys.exit(0 if average >= PASS_THRESHOLD else 1)


if __name__ == "__main__":
    main()
