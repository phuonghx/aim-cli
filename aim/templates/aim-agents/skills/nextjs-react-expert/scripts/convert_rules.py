#!/usr/bin/env python3
"""Maintenance helper: fold per-rule markdown into grouped section files.

The source of truth for the performance rules is a directory of one-rule-per-file
markdown documents. Each file's name begins with a short prefix (``async``,
``bundle``, ...) that says which section it belongs to. This script reads that
directory, buckets the rules by prefix, and emits one combined ``N-prefix-title.md``
file per section -- the numbered reference files shipped alongside this skill.

Run with no arguments:
    python convert_rules.py
"""

import sys
from collections import namedtuple
from pathlib import Path


# Static description of every section: the order it appears in, its human title, a
# severity label, and a one-line focus statement used in the generated header.
Section = namedtuple("Section", ["order", "title", "severity", "focus"])

# Keyed by the filename prefix that marks a rule as belonging to the section.
SECTION_TABLE = {
    "async": Section(
        1,
        "Eliminating Waterfalls",
        "CRITICAL",
        "Waterfalls are the #1 performance killer. Each sequential await adds full "
        "network latency. Eliminating them yields the largest gains.",
    ),
    "bundle": Section(
        2,
        "Bundle Size Optimization",
        "CRITICAL",
        "Reducing initial bundle size improves Time to Interactive and Largest "
        "Contentful Paint.",
    ),
    "server": Section(
        3,
        "Server-Side Performance",
        "HIGH",
        "Optimizing server-side rendering and data fetching eliminates server-side "
        "waterfalls and reduces response times.",
    ),
    "client": Section(
        4,
        "Client-Side Data Fetching",
        "MEDIUM-HIGH",
        "Automatic deduplication and efficient data fetching patterns reduce "
        "redundant network requests.",
    ),
    "rerender": Section(
        5,
        "Re-render Optimization",
        "MEDIUM",
        "Reducing unnecessary re-renders minimizes wasted computation and improves "
        "UI responsiveness.",
    ),
    "rendering": Section(
        6,
        "Rendering Performance",
        "MEDIUM",
        "Optimizing the rendering process reduces the work the browser needs to do.",
    ),
    "js": Section(
        7,
        "JavaScript Performance",
        "LOW-MEDIUM",
        "Micro-optimizations for hot paths can add up to meaningful improvements.",
    ),
    "advanced": Section(
        8,
        "Advanced Patterns",
        "VARIABLE",
        "Advanced patterns for specific cases that require careful implementation.",
    ),
}


def split_frontmatter(raw):
    """Separate a markdown document into (metadata dict, body string).

    Frontmatter is the optional ``---`` delimited block at the top of the file. We
    parse it as flat ``key: value`` lines; anything without a leading frontmatter
    block yields an empty dict and the original text as the body.
    """
    if not raw.startswith("---"):
        return {}, raw.strip()

    chunks = raw.split("---", 2)
    if len(chunks) < 3:
        return {}, raw.strip()

    meta = {}
    for line in chunks[1].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()

    return meta, chunks[2].strip()


def load_rule(path):
    """Read one rule file and return a plain dict describing it."""
    raw = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)

    stem = path.stem
    prefix = stem.split("-", 1)[0]

    return {
        "prefix": prefix,
        "title": meta.get("title", stem),
        "impact": meta.get("impact", ""),
        "tags": meta.get("tags", ""),
        "body": body,
    }


def bucket_rules(rules_dir):
    """Read every rule file and group them into lists keyed by section prefix."""
    buckets = {prefix: [] for prefix in SECTION_TABLE}

    for path in sorted(rules_dir.glob("*.md")):
        # Underscore-prefixed files (e.g. _sections.md) are metadata, not rules.
        if path.name.startswith("_"):
            continue

        rule = load_rule(path)
        prefix = rule["prefix"]
        if prefix in buckets:
            buckets[prefix].append(rule)
        else:
            print("[WARN] file '%s' has unknown prefix '%s'" % (path.name, prefix))

    return buckets


def render_section(prefix, rules):
    """Build the full markdown text for one section from its list of rules."""
    section = SECTION_TABLE[prefix]

    # Stable, alphabetical rule order within the section.
    ordered = sorted(rules, key=lambda r: r["title"])

    lines = [
        "# %d. %s" % (section.order, section.title),
        "",
        "> **Impact:** %s" % section.severity,
        "> **Focus:** %s" % section.focus,
        "",
        "---",
        "",
        "## Overview",
        "",
        "This section contains **%d rules** focused on %s."
        % (len(ordered), section.title.lower()),
        "",
    ]

    for index, rule in enumerate(ordered, start=1):
        lines.append("---")
        lines.append("")
        lines.append("## Rule %d.%d: %s" % (section.order, index, rule["title"]))
        lines.append("")
        if rule["impact"]:
            lines.append("**Impact:** %s  " % rule["impact"])
        if rule["tags"]:
            lines.append("**Tags:** %s  " % rule["tags"])
        lines.append("")
        lines.append(rule["body"])
        lines.append("")
        lines.append("")

    return "\n".join(lines)


def section_filename(prefix):
    """Compute the output filename for a section (e.g. 1-async-eliminating-...)."""
    section = SECTION_TABLE[prefix]
    slug = section.title.lower().replace(" ", "-")
    return "%d-%s-%s.md" % (section.order, prefix, slug)


def write_section(prefix, rules, output_dir):
    """Render and write one section file; skip sections that have no rules."""
    if not rules:
        print("[WARN] no rules for section '%s', skipping" % prefix)
        return

    out_path = output_dir / section_filename(prefix)
    out_path.write_text(render_section(prefix, rules), encoding="utf-8")
    print("[OK] wrote %s (%d rules)" % (out_path.name, len(rules)))


def convert(rules_dir, output_dir):
    """Top-level conversion: read rules, group them, emit every section file."""
    print("[*] reading rules from: %s" % rules_dir)
    print("[*] writing sections to: %s" % output_dir)
    print()

    if not rules_dir.exists():
        print("[ERROR] rules directory not found: %s" % rules_dir)
        return

    print("[*] grouping rules by section prefix...")
    buckets = bucket_rules(rules_dir)

    total = sum(len(rules) for rules in buckets.values())
    print("[*] found %d rules total" % total)
    print()

    print("[*] generating section files...")
    # Emit in declared section order rather than dict order for tidy output.
    for prefix in sorted(SECTION_TABLE, key=lambda p: SECTION_TABLE[p].order):
        write_section(prefix, buckets[prefix], output_dir)

    print()
    print("[DONE] produced %d section files from %d rules"
          % (len(SECTION_TABLE), total))


def main():
    """Resolve the default input/output paths relative to this file and run."""
    # The repo layout places the rule source and the generated skill five
    # directories above this script; mirror the original locations.
    base = Path(__file__).parents[4]
    rules_dir = base / "others/agent-skills/skills/react-best-practices/rules"
    output_dir = base / ".aim-agents/skills/react-best-practices"

    convert(rules_dir, output_dir)


if __name__ == "__main__":
    main()
