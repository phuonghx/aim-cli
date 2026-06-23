---
name: web-design-guidelines
description: Audits front-end UI code against an external, regularly updated set of web interface guidelines covering accessibility, usability, and interaction quality, then reports each issue in a compact file-and-line format. Fits when reviewing existing UI for best-practice compliance, checking accessibility, or auditing UX after a feature is built. It pulls the current rules at review time rather than relying on a baked-in copy, so findings track the latest published guidance.
---

# Web Interface Guidelines Audit

This skill reviews UI source against a living checklist of interface best practices and
reports what falls short. Because the rules are fetched fresh each run, the audit reflects
the most recent published guidance rather than a snapshot frozen into this file.

## What it does

Given one or more files (or a glob), it retrieves the current guidelines, reads the target
code, evaluates every applicable rule, and emits concise findings keyed to `file:line` so
each issue is easy to locate and fix.

## Procedure

1. **Pull the current rules.** Fetch the guidelines document from the source below at the
   start of every review — do not work from memory or a cached copy. The fetched content
   carries both the rules to apply and the exact output format to follow.
2. **Gather the targets.** Read the files named in the request. If none were given, ask
   which files or pattern to review before continuing.
3. **Evaluate.** Walk the code against each rule in the fetched guidelines.
4. **Report.** Write findings in the terse `file:line` form the guidelines specify, one
   issue per line.

## Where the rules come from

Retrieve the latest rules before each audit:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use a web fetch to load that URL. Treat whatever it returns as the authority for both the
checks and the reporting format — it supersedes anything described here.

## How this fits a design workflow

Two skills bracket the act of building UI: one informs the design before code exists, this
one inspects the result after.

| Phase | Skill | Purpose |
|---|---|---|
| Before coding | `frontend-design` | Learn the principles — color, type, spacing, UX |
| After coding | `web-design-guidelines` (this) | Audit the implementation for compliance |

```text
1. DESIGN  -> absorb the principles
2. BUILD   -> implement the interface
3. AUDIT   -> run this review        <- you are here
4. FIX     -> resolve the findings
```
