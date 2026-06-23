#!/usr/bin/env python3
"""Surface internationalization gaps in a codebase.

Two independent checks run side by side:

1. Catalog sync -- load every JSON translation file, group by language,
   and report keys that exist in one language but are missing (or extra)
   in another.
2. Hardcoded text -- scan source files for literal user-facing strings
   that look like they should have been routed through a translation
   helper, while giving credit to files that already use one.

Usage:
    python i18n_checker.py <project_path>
"""

import json
import re
import sys
from pathlib import Path

# Make Unicode-heavy output safe on older Windows terminals.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


# Regexes per file family that tend to indicate untranslated literals.
LITERAL_TEXT_RULES = {
    "markup": [
        # Visible text wedged between JSX/Vue tags: >Some Words</
        r">\s*[A-Z][a-zA-Z\s]{3,30}\s*</",
        # Human-readable attribute values.
        r'(?:title|placeholder|label|alt|aria-label)="[A-Z][a-zA-Z\s]{2,}"',
        # Text inside common text-bearing elements.
        r"<(?:button|h[1-6]|p|span|label)[^>]*>\s*[A-Z][a-zA-Z\s!?.,]{3,}\s*</",
    ],
    "python": [
        # print()/raise with a sentence-like literal.
        r"(?:print|raise\s+\w+)\s*\(\s*[\"'][A-Z][^\"']{5,}[\"']",
        # Flask flash() messages.
        r"flash\s*\(\s*[\"'][A-Z][^\"']{5,}[\"']",
    ],
}

# Signs that a file already speaks i18n -- presence earns it a pass.
TRANSLATION_HELPERS = (
    r"\bt\([\"']",        # t('key')
    r"useTranslation",     # react-i18next hook
    r"\$t\(",             # vue-i18n
    r"_\([\"']",          # gettext shorthand
    r"gettext\(",          # gettext
    r"useTranslations",    # next-intl
    r"FormattedMessage",   # react-intl
    r"i18n\.",             # generic namespace
)

# Map source extensions onto a rule family.
EXT_TO_FAMILY = {
    ".tsx": "markup", ".jsx": "markup", ".ts": "markup", ".js": "markup",
    ".vue": "markup",
    ".py": "python",
}

# Path fragments that mark non-application code we should ignore.
IGNORED_FRAGMENTS = (
    "node_modules", ".git", "dist", "build",
    "__pycache__", "venv", "test", "spec",
)

CATALOG_GLOBS = (
    "**/locales/**/*.json",
    "**/translations/**/*.json",
    "**/lang/**/*.json",
    "**/i18n/**/*.json",
    "**/messages/*.json",
    "**/*.po",
)

MAX_SOURCE_FILES = 50
MAX_EXAMPLES = 5


def flatten(mapping: dict, prefix: str = "") -> set:
    """Return the set of dotted leaf keys for a (possibly nested) dict."""
    leaves = set()
    for key, value in mapping.items():
        dotted = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            leaves |= flatten(value, dotted)
        else:
            leaves.add(dotted)
    return leaves


def locate_catalogs(root: Path) -> list:
    """Find translation files anywhere under `root`, skipping deps."""
    hits = []
    for pattern in CATALOG_GLOBS:
        hits.extend(root.glob(pattern))
    return [f for f in hits if "node_modules" not in str(f)]


def audit_catalog_sync(catalogs: list) -> dict:
    """Compare key sets across languages and report drift."""
    good, bad = [], []

    if not catalogs:
        return {"good": [], "bad": ["[!] No locale files found"]}

    # languages[language][namespace] -> set of keys
    languages: dict = {}
    for path in catalogs:
        if path.suffix != ".json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        language = path.parent.name
        languages.setdefault(language, {})[path.stem] = flatten(data)

    if len(languages) < 2:
        good.append(f"[OK] Found {len(catalogs)} locale file(s)")
        return {"good": good, "bad": bad}

    good.append(f"[OK] {len(languages)} language(s): {', '.join(languages)}")

    names = list(languages)
    reference = names[0]

    for namespace, ref_keys in languages[reference].items():
        for other in names[1:]:
            other_keys = languages[other].get(namespace, set())

            absent = ref_keys - other_keys
            if absent:
                bad.append(f"[X] {other}/{namespace}: {len(absent)} key(s) missing")

            surplus = other_keys - ref_keys
            if surplus:
                bad.append(f"[!] {other}/{namespace}: {len(surplus)} extra key(s)")

    if not bad:
        good.append("[OK] Key sets match across languages")

    return {"good": good, "bad": bad}


def _is_app_source(path: Path) -> bool:
    return not any(fragment in str(path) for fragment in IGNORED_FRAGMENTS)


def audit_hardcoded_text(root: Path) -> dict:
    """Scan source files for literal strings that bypass i18n."""
    good, bad = [], []

    sources = []
    for ext in EXT_TO_FAMILY:
        sources.extend(p for p in root.rglob(f"*{ext}") if _is_app_source(p))

    if not sources:
        return {"good": ["[!] No source files found"], "bad": []}

    using_i18n = 0
    with_literals = 0
    examples = []

    for path in sources[:MAX_SOURCE_FILES]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        speaks_i18n = any(re.search(rule, text) for rule in TRANSLATION_HELPERS)
        if speaks_i18n:
            using_i18n += 1
            # Files already wired for i18n are assumed handled.
            continue

        family = EXT_TO_FAMILY.get(path.suffix, "markup")
        flagged = False
        for rule in LITERAL_TEXT_RULES.get(family, []):
            found = re.findall(rule, text)
            if found:
                flagged = True
                if len(examples) < MAX_EXAMPLES:
                    snippet = str(found[0])[:40]
                    examples.append(f"{path.name}: {snippet}...")

        if flagged:
            with_literals += 1

    good.append(f"[OK] Scanned {len(sources)} source file(s)")
    if using_i18n:
        good.append(f"[OK] {using_i18n} file(s) already use i18n")

    if with_literals:
        bad.append(f"[X] {with_literals} file(s) may contain hardcoded strings")
        for example in examples:
            bad.append(f"   -> {example}")
    else:
        good.append("[OK] No obvious hardcoded strings detected")

    return {"good": good, "bad": bad}


def _emit(section: str, result: dict) -> None:
    print(f"\n[{section}]")
    print("-" * 40)
    for line in result["good"] + result["bad"]:
        print(f"  {line}")


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

    print("\n" + "=" * 60)
    print("  i18n CHECKER - Internationalization Audit")
    print("=" * 60)

    catalog_result = audit_catalog_sync(locate_catalogs(root))
    source_result = audit_hardcoded_text(root)

    _emit("LOCALE FILES", catalog_result)
    _emit("CODE ANALYSIS", source_result)

    blockers = sum(
        1 for line in catalog_result["bad"] + source_result["bad"]
        if line.startswith("[X]")
    )

    print("\n" + "=" * 60)
    if blockers == 0:
        print("[OK] i18n CHECK: PASSED")
        sys.exit(0)
    print(f"[X] i18n CHECK: {blockers} issue(s) found")
    sys.exit(1)


if __name__ == "__main__":
    main()
