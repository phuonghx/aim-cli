#!/usr/bin/env python3
"""Static performance auditor for React / Next.js code trees.

Walks a project directory and applies a handful of cheap heuristics that flag the
performance smells documented in the numbered reference files of this skill. The
output is a prioritized text report, not a hard pass/fail gate -- treat every hit as
a prompt to go look, since regex heuristics over source text inevitably produce some
false positives.

Usage:
    python react_performance_checker.py <project_path>
"""

import os
import re
import sys
from pathlib import Path


# --- Finding model -----------------------------------------------------------

# Severity buckets, ordered from most to least urgent. The numeric weight is only
# used to sort findings for display.
SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM-HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
}


class Finding:
    """A single thing the audit noticed, tied back to a reference file."""

    def __init__(self, path, severity, summary, remedy, reference):
        self.path = path            # project-relative file path (str)
        self.severity = severity    # one of SEVERITY_ORDER's keys
        self.summary = summary      # what looks wrong
        self.remedy = remedy        # what to do about it
        self.reference = reference  # which reference .md explains it

    def rank(self):
        """Sort key: more severe findings come first."""
        return SEVERITY_ORDER.get(self.severity, 99)


# --- Source-tree traversal ---------------------------------------------------

# Directories we never want to descend into -- they hold dependencies or build
# output, not the project's own source.
SKIP_DIRS = {"node_modules", ".next", ".git", "dist", "build", "out", "coverage"}


def walk_sources(root, suffixes):
    """Yield Path objects under ``root`` whose extension is in ``suffixes``.

    ``suffixes`` is given without the leading dot (e.g. ("ts", "tsx")). We skip
    vendored / generated directories entirely and silently ignore files that cannot
    be read as UTF-8 text.
    """
    wanted = {"." + s for s in suffixes}
    for current, dirs, files in os.walk(root):
        # Prune unwanted directories in place so os.walk does not recurse into them.
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if os.path.splitext(name)[1] in wanted:
                yield Path(current) / name


def read_text(path):
    """Return the file's text, or None if it cannot be decoded."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def rel(path, root):
    """Render ``path`` relative to the project root for tidy reporting."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


# --- Individual heuristics ---------------------------------------------------
#
# Each scanner takes the project root Path and returns a list of Finding objects.

# Two awaits back-to-back with nothing pulling them into Promise.all.
_SEQUENTIAL_AWAIT = re.compile(r"await\s+\w+.*?\n\s*await\s+\w+")


def scan_waterfalls(root):
    """Flag back-to-back awaits that likely form a request waterfall (file 1)."""
    print("\n[*] Scanning for sequential awaits (waterfalls)...")
    hits = []
    for path in walk_sources(root, ("ts", "tsx", "js", "jsx")):
        text = read_text(path)
        if text is None:
            continue
        if _SEQUENTIAL_AWAIT.search(text):
            hits.append(Finding(
                rel(path, root),
                "CRITICAL",
                "Consecutive awaits look like a data-fetching waterfall",
                "Run independent calls together with Promise.all()",
                "1-async-eliminating-waterfalls.md",
            ))
    return hits


# Import that resolves through an explicit index file, or a relative import with no
# file extension (which often points at a directory's barrel file).
_BARREL_INDEX = re.compile(r"""import.*from\s+['"](@/.*?)/index['"]""")
_BARREL_RELATIVE = re.compile(r"""import.*from\s+['"]\.\.?/.*?['"](?!.*?\.tsx?)""")


def scan_barrel_imports(root):
    """Flag imports that probably pull in a barrel file (file 2)."""
    print("[*] Scanning for barrel imports...")
    hits = []
    for path in walk_sources(root, ("ts", "tsx", "js", "jsx")):
        text = read_text(path)
        if text is None:
            continue
        if _BARREL_INDEX.search(text) or _BARREL_RELATIVE.search(text):
            hits.append(Finding(
                rel(path, root),
                "CRITICAL",
                "Possible barrel-file import",
                "Import directly from the specific module",
                "2-bundle-bundle-size-optimization.md",
            ))
    return hits


# Size threshold (bytes) above which a component is "heavy" enough to be worth
# splitting out with a dynamic import.
HEAVY_FILE_BYTES = 10_000


def scan_static_heavy_imports(root):
    """Flag large components that are imported statically elsewhere (file 2).

    For each oversized component file we look for another file that imports it by
    name but never calls dynamic(). That combination suggests the heavy module is
    being pulled into a bundle it could be lazy-loaded out of.
    """
    print("[*] Scanning for heavy components imported statically...")
    hits = []

    # Cache contents once -- the inner loop reads every other file repeatedly.
    tsx_files = list(walk_sources(root, ("ts", "tsx")))
    contents = {}
    for path in tsx_files:
        text = read_text(path)
        if text is not None:
            contents[path] = text

    for path, text in contents.items():
        if len(text) <= HEAVY_FILE_BYTES:
            continue
        name = path.stem

        for other, other_text in contents.items():
            if other is path:
                continue
            imports_it = (
                ("import %s" % name) in other_text
                or ("import { %s" % name) in other_text
            )
            if imports_it and "dynamic(" not in other_text:
                hits.append(Finding(
                    rel(other, root),
                    "CRITICAL",
                    "Heavy component '%s' is imported statically" % name,
                    "Code-split it with dynamic()",
                    "2-bundle-bundle-size-optimization.md",
                ))
                break  # one report per heavy component is enough
    return hits


# fetch( appearing anywhere inside a useEffect( ... ) span (DOTALL across lines).
_EFFECT_FETCH = re.compile(r"useEffect.*?fetch\(", re.DOTALL)


def scan_effect_fetching(root):
    """Flag data fetching done inside useEffect (file 4)."""
    print("[*] Scanning for data fetching inside useEffect...")
    hits = []
    for path in walk_sources(root, ("ts", "tsx")):
        text = read_text(path)
        if text is None or "useEffect" not in text:
            continue
        if _EFFECT_FETCH.search(text):
            hits.append(Finding(
                rel(path, root),
                "MEDIUM-HIGH",
                "fetch() inside useEffect",
                "Prefer SWR or React Query for dedup and caching",
                "4-client-client-side-data-fetching.md",
            ))
    return hits


# A component declaration is a const/function whose name starts with a capital.
_COMPONENT_DECL = re.compile(r"(?:export\s+)?(?:const|function)\s+([A-Z]\w+)")


def scan_unmemoized_components(root):
    """Flag prop-taking components that are never memoized (file 5)."""
    print("[*] Scanning for components that could be memoized...")
    hits = []
    for path in walk_sources(root, ("tsx",)):
        text = read_text(path)
        if text is None:
            continue

        has_component = bool(_COMPONENT_DECL.search(text))
        is_memoized = "React.memo" in text or "memo(" in text
        takes_props = "props:" in text or "Props>" in text

        if has_component and not is_memoized and takes_props:
            hits.append(Finding(
                rel(path, root),
                "MEDIUM",
                "Component takes props but is not memoized",
                "Wrap it in React.memo when its props are stable",
                "5-rerender-re-render-optimization.md",
            ))
    return hits


def scan_raw_img_tags(root):
    """Flag raw <img> usage where next/image is not imported (file 6)."""
    print("[*] Scanning for raw <img> tags...")
    hits = []
    for path in walk_sources(root, ("ts", "tsx", "js", "jsx")):
        text = read_text(path)
        if text is None:
            continue
        if "<img" in text and "next/image" not in text:
            hits.append(Finding(
                rel(path, root),
                "MEDIUM",
                "Raw <img> tag instead of next/image",
                "Use next/image for automatic optimization",
                "6-rendering-rendering-performance.md",
            ))
    return hits


# Order in which the scanners run. Append new heuristics here to register them.
SCANNERS = (
    scan_waterfalls,
    scan_barrel_imports,
    scan_static_heavy_imports,
    scan_effect_fetching,
    scan_unmemoized_components,
    scan_raw_img_tags,
)


# --- Reporting ---------------------------------------------------------------

MAX_LISTED = 12  # cap on how many findings we print before summarizing the rest


def print_findings(findings):
    """Print findings grouped as critical first, then everything else."""
    bar = "=" * 60

    criticals = [f for f in findings if f.severity == "CRITICAL"]
    others = [f for f in findings if f.severity != "CRITICAL"]
    others.sort(key=Finding.rank)

    print("\n" + bar)
    print("REACT / NEXT.JS PERFORMANCE AUDIT")
    print(bar)

    print("\n[CRITICAL] (%d)" % len(criticals))
    for f in criticals:
        print("  - %s" % f.path)
        print("    Smell:     %s" % f.summary)
        print("    Suggested: %s" % f.remedy)
        print("    See:       %s\n" % f.reference)

    print("\n[OTHER FINDINGS] (%d)" % len(others))
    for f in others[:MAX_LISTED]:
        print("  - [%s] %s" % (f.severity, f.path))
        print("    Smell:     %s" % f.summary)
        print("    Suggested: %s" % f.remedy)
        print("    See:       %s\n" % f.reference)
    leftover = len(others) - MAX_LISTED
    if leftover > 0:
        print("  ... plus %d more" % leftover)

    print("\n" + bar)
    print("TOTALS")
    print("  Critical: %d" % len(criticals))
    print("  Other:    %d" % len(others))
    print(bar)

    if not findings:
        print("\n[CLEAN] No obvious performance smells found.")
    else:
        print("\n[REVIEW] Investigate the items above.")
        print("Work top-down: CRITICAL > HIGH > MEDIUM-HIGH > MEDIUM > LOW")


def audit(project_path):
    """Run every registered scanner and report the combined findings."""
    root = Path(project_path)
    bar = "=" * 60
    print(bar)
    print("React / Next.js performance auditor")
    print(bar)
    print("Target: %s" % root)

    findings = []
    for scanner in SCANNERS:
        findings.extend(scanner(root))

    print_findings(findings)


def main():
    """Parse the single positional argument and kick off the audit."""
    if len(sys.argv) < 2:
        print("Usage: python react_performance_checker.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]
    if not os.path.exists(project_path):
        print("[ERROR] No such path: %s" % project_path)
        sys.exit(1)

    audit(project_path)


if __name__ == "__main__":
    main()
