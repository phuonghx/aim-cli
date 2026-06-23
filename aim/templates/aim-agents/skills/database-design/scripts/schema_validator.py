#!/usr/bin/env python3
"""Schema Validator.

Scans a project for database schema definitions (Prisma today, with a slot
for Drizzle) and reports common modeling smells: bad casing, absent primary
keys, missing audit timestamps, and foreign keys that lack an index.

Run:
    python schema_validator.py <project_path>

The exit status is always 0 -- findings are treated as advisory, not as a
build-breaking gate.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# On some Windows terminals the default code page mangles non-ASCII output;
# switch stdout to UTF-8 and swallow anything that still cannot be encoded.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# Directories that never contain hand-written schema we care about.
SCHEMA_FILE_CAP = 10


def locate_schemas(root: Path):
    """Return a list of (kind, path) pairs for schema files under *root*.

    Prisma lives at a well-known path; Drizzle is spread across *.ts files
    that mention "schema" or "table" in their name.
    """
    discovered = []

    # Prisma keeps everything in a single schema.prisma file.
    for path in root.glob("**/prisma/schema.prisma"):
        discovered.append(("prisma", path))

    # Drizzle definitions tend to sit under drizzle/ or schema/ folders.
    candidate_ts = list(root.glob("**/drizzle/*.ts"))
    candidate_ts += list(root.glob("**/schema/*.ts"))
    for path in candidate_ts:
        lowered = path.name.lower()
        if "schema" in lowered or "table" in lowered:
            discovered.append(("drizzle", path))

    return discovered[:SCHEMA_FILE_CAP]


def _model_blocks(source: str):
    """Yield (name, body) for every `model Name { ... }` block."""
    return re.findall(r"model\s+(\w+)\s*\{([^}]+)\}", source, re.DOTALL)


def inspect_prisma(path: Path):
    """Collect advisory findings for a single Prisma schema file."""
    findings = []

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as err:
        return [f"Could not read schema: {str(err)[:50]}"]

    for name, body in _model_blocks(text):
        # Models should read as PascalCase types.
        if not name[:1].isupper():
            findings.append(f"Model '{name}' should use PascalCase")

        # Every model normally needs an identifier.
        if "@id" not in body and "id" not in body.lower():
            findings.append(f"Model '{name}' may have no @id field")

        # Audit timestamp is recommended but not mandatory.
        if "createdAt" not in body and "created_at" not in body:
            findings.append(
                f"Model '{name}' has no createdAt field (recommended)"
            )

        # Foreign-key-shaped columns (somethingId) usually want an index.
        for fk in re.findall(r"(\w+Id)\s+\w+", body):
            bracketed = f"@@index([{fk}])"
            quoted = f'@@index(["{fk}"])'
            if bracketed not in text and quoted not in text:
                findings.append(
                    f"Consider @@index([{fk}]) on {name} to speed up lookups"
                )

    # Enums follow the same PascalCase rule as models.
    for enum_name in re.findall(r"enum\s+(\w+)\s*\{", text):
        if not enum_name[:1].isupper():
            findings.append(f"Enum '{enum_name}' should use PascalCase")

    return findings


def _print_banner(target: Path):
    line = "=" * 60
    print(f"\n{line}")
    print("[SCHEMA VALIDATOR] Database Schema Validation")
    print(line)
    print(f"Project: {target}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)


def run(target: Path):
    """Validate every schema found under *target* and emit a report."""
    _print_banner(target)

    schemas = locate_schemas(target)
    print(f"Found {len(schemas)} schema files")

    # Nothing to validate -- report a clean pass and stop.
    if not schemas:
        empty = {
            "script": "schema_validator",
            "project": str(target),
            "schemas_checked": 0,
            "issues_found": 0,
            "passed": True,
            "message": "No schema files found",
        }
        print(json.dumps(empty, indent=2))
        return 0

    grouped = []
    for kind, path in schemas:
        print(f"\nValidating: {path.name} ({kind})")

        if kind == "prisma":
            findings = inspect_prisma(path)
        else:
            # Drizzle support is a placeholder for now.
            findings = []

        if findings:
            grouped.append(
                {"file": path.name, "type": kind, "issues": findings}
            )

    print("\n" + "=" * 60)
    print("SCHEMA ISSUES")
    print("=" * 60)

    if grouped:
        for entry in grouped:
            print(f"\n{entry['file']} ({entry['type']}):")
            for note in entry["issues"][:5]:
                print(f"  - {note}")
            remainder = len(entry["issues"]) - 5
            if remainder > 0:
                print(f"  ... and {remainder} more issues")
    else:
        print("No schema issues found!")

    total = sum(len(entry["issues"]) for entry in grouped)

    report = {
        "script": "schema_validator",
        "project": str(target),
        "schemas_checked": len(schemas),
        "issues_found": total,
        # Findings are advisory, so the run always passes.
        "passed": True,
        "issues": grouped,
    }
    print("\n" + json.dumps(report, indent=2))
    return 0


def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else "."
    target = Path(raw).resolve()
    sys.exit(run(target))


if __name__ == "__main__":
    main()
