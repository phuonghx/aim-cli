#!/usr/bin/env python3
"""Inspect a project's API surface for common design gaps.

Walks a directory looking for route handlers and OpenAPI/Swagger specs,
then reports which good-practice signals are present and which are missing.
Exits non-zero when blocking problems are detected so it can gate a pipeline.
"""
import json
import re
import sys
from pathlib import Path

# Console output includes box-drawing and marker glyphs; force UTF-8 so it
# does not blow up on a legacy Windows code page. Older runtimes lack
# reconfigure(), in which case we simply leave the stream as-is.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

# Directories that never hold first-party source worth scanning.
SKIP_DIRS = ("node_modules", ".git", "dist", "build", "__pycache__")

# Glob patterns that tend to capture API code and contract files.
SOURCE_GLOBS = (
    "**/*api*.ts", "**/*api*.js", "**/*api*.py",
    "**/routes/*.ts", "**/routes/*.js", "**/routes/*.py",
    "**/controllers/*.ts", "**/controllers/*.js",
    "**/endpoints/*.ts", "**/endpoints/*.py",
    "**/*.openapi.json", "**/*.openapi.yaml",
    "**/swagger.json", "**/swagger.yaml",
    "**/openapi.json", "**/openapi.yaml",
)

# Cap on how many files we inspect, to keep a run fast on huge repos.
MAX_FILES = 15

# Markers used in report lines. PASS and INFO are informational; FAIL marks
# a blocking issue and WARN marks an advisory one.
PASS, FAIL, WARN, INFO = "[OK]", "[X]", "[!]", "[i]"


def gather_candidates(root):
    """Return API-related files under *root*, minus vendored/build paths."""
    seen = []
    for pattern in SOURCE_GLOBS:
        for hit in root.glob(pattern):
            if any(part in str(hit) for part in SKIP_DIRS):
                continue
            seen.append(hit)
    return seen


def _has_any(text, patterns, ignore_case=False):
    """True if any regex in *patterns* matches somewhere in *text*."""
    flags = re.IGNORECASE if ignore_case else 0
    return any(re.search(p, text, flags) for p in patterns)


class FileReport:
    """Collects pass/fail/warn lines for a single examined file."""

    def __init__(self, path, kind):
        self.path = str(path)
        self.kind = kind          # "spec" or "code"
        self.lines = []           # tuples of (marker, message)

    def ok(self, msg):
        self.lines.append((PASS, msg))

    def fail(self, msg):
        self.lines.append((FAIL, msg))

    def warn(self, msg):
        self.lines.append((WARN, msg))

    def note(self, msg):
        self.lines.append((INFO, msg))

    def count_passes(self):
        return sum(1 for marker, _ in self.lines if marker == PASS)

    def count_blockers(self):
        return sum(1 for marker, _ in self.lines if marker == FAIL)


def audit_yaml_spec(report, body):
    """Apply lightweight, text-based checks to a YAML contract file."""
    if "openapi:" in body or "swagger:" in body:
        report.ok("OpenAPI/Swagger version declared")
    else:
        report.fail("No OpenAPI/Swagger version line")

    if "paths:" in body:
        report.ok("paths block present")
    else:
        report.fail("No paths block")

    if "components:" in body or "definitions:" in body:
        report.ok("Reusable schema components present")


def audit_json_spec(report, body):
    """Parse a JSON contract and validate its core structure."""
    try:
        spec = json.loads(body)
    except json.JSONDecodeError as err:
        report.fail("Could not parse spec: {}".format(err))
        return

    if "openapi" in spec or "swagger" in spec:
        report.ok("OpenAPI/Swagger version declared")

    info = spec.get("info")
    if isinstance(info, dict):
        if "title" in info:
            report.ok("API title set")
        if "version" in info:
            report.ok("API version set")
        if "description" not in info:
            report.warn("info.description is empty")

    paths = spec.get("paths")
    if isinstance(paths, dict):
        report.ok("{} path(s) described".format(len(paths)))
        verbs = {"get", "post", "put", "patch", "delete"}
        for route, ops in paths.items():
            if not isinstance(ops, dict):
                continue
            for verb, meta in ops.items():
                if verb not in verbs or not isinstance(meta, dict):
                    continue
                label = "{} {}".format(verb.upper(), route)
                if "responses" not in meta:
                    report.fail("{}: no responses declared".format(label))
                if "summary" not in meta and "description" not in meta:
                    report.warn("{}: undocumented".format(label))


def inspect_spec_file(path):
    """Build a report for an OpenAPI/Swagger document."""
    report = FileReport(path, "spec")
    try:
        body = path.read_text(encoding="utf-8")
    except OSError as err:
        report.fail("Could not read file: {}".format(err))
        return report

    if path.suffix == ".json":
        audit_json_spec(report, body)
    else:
        audit_yaml_spec(report, body)
    return report


# Each entry pairs a label with the regexes that signal the practice, plus
# how to treat its absence: "fail", "warn", or None (silent when missing).
_CODE_SIGNALS = (
    ("Error handling in place",
     (r"try\s*{", r"try:", r"\.catch\(", r"except\s+", r"catch\s*\("),
     "fail"),
    ("Explicit HTTP status codes",
     (r"status\s*\(\s*\d{3}\s*\)", r"statusCode\s*[=:]\s*\d{3}",
      r"HttpStatus\.", r"status_code\s*=\s*\d{3}",
      r"\.status\(\d{3}\)", r"res\.status\("),
     "warn"),
    ("Request validation",
     (r"validate", r"schema", r"zod", r"joi", r"yup",
      r"pydantic", r"@Body\(", r"@Query\("),
     "warn"),
    ("Auth handling",
     (r"auth", r"jwt", r"bearer", r"token",
      r"middleware", r"guard", r"@Authenticated"),
     None),
    ("Rate limiting",
     (r"rateLimit", r"throttle", r"rate.?limit"),
     None),
    ("Logging",
     (r"console\.log", r"logger\.", r"logging\.", r"log\."),
     None),
)


def inspect_code_file(path):
    """Build a report for a route/controller source file."""
    report = FileReport(path, "code")
    try:
        body = path.read_text(encoding="utf-8")
    except OSError as err:
        report.fail("Could not read file: {}".format(err))
        return report

    for label, patterns, on_missing in _CODE_SIGNALS:
        # Status-code patterns are case-sensitive; the rest are not.
        case_sensitive = label in ("Explicit HTTP status codes", "Logging")
        if _has_any(body, patterns, ignore_case=not case_sensitive):
            report.ok(label)
        elif on_missing == "fail":
            report.fail("Missing: {}".format(label.lower()))
        elif on_missing == "warn":
            report.warn("Missing: {}".format(label.lower()))
    return report


def looks_like_spec(name):
    """Heuristic: does this filename refer to an API contract document?"""
    lowered = name.lower()
    return "openapi" in lowered or "swagger" in lowered


def render(reports):
    """Print every report and return (total_passes, total_blockers)."""
    passes = blockers = 0
    for report in reports:
        print("\n[FILE] {} [{}]".format(report.path, report.kind))
        for marker, message in report.lines:
            print("   {} {}".format(marker, message))
        passes += report.count_passes()
        blockers += report.count_blockers()
    return passes, blockers


def run(argv):
    """Entry point: scan the given path and return a process exit code."""
    root = Path(argv[1] if len(argv) > 1 else ".")

    bar = "=" * 60
    print("\n" + bar)
    print("  API VALIDATOR - Endpoint Best Practices Check")
    print(bar + "\n")

    candidates = gather_candidates(root)
    if not candidates:
        print("{} No API files found.".format(WARN))
        print("   Looked in: routes/, controllers/, api/, openapi.json/yaml")
        return 0

    reports = []
    for path in candidates[:MAX_FILES]:
        if looks_like_spec(path.name):
            reports.append(inspect_spec_file(path))
        else:
            reports.append(inspect_code_file(path))

    passes, blockers = render(reports)

    print("\n" + bar)
    print("[RESULTS] {} passed, {} critical issues".format(passes, blockers))
    print(bar)

    if blockers:
        print("{} Fix critical issues before deployment".format(FAIL))
        return 1
    print("{} API validation passed".format(PASS))
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv))
