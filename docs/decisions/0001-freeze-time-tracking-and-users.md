# ADR 0001 — Freeze time-tracking and user management (maintenance-only)

- **Status:** Accepted
- **Date:** 2026-06-11
- **Resolves:** AIM Roadmap issue #12

## Context

AIM's positioning is the **living context layer** for AI coding assistants —
keeping project context (rules, tasks, memory, docs) trustworthy and synced
across tools. Two existing surfaces sit at the edge of that mission:

- **Time tracking** (`aim time start/stop/status/log/report`)
- **User / assignee management** (`aim user ...`)

Both are project-management features. They overlap with what teams already get
from GitHub (now that `aim github` projects tasks onto Issues/Projects), and
investing further in them pulls AIM toward competing with Jira/GitHub rather
than deepening the context-layer wedge.

## Decision

**Freeze** time-tracking and user management as **maintenance-only**:

- Keep them working and supported — no removal, no breaking changes, no
  deprecation warnings. Existing users and data are unaffected.
- Do **not** invest in new features there. New product energy goes to the
  context layer (doctor/freshness, sync, GitHub integration, spec-driven flow).
- Assignment/ownership for teams is expected to live on GitHub via `aim github`,
  not in bespoke AIM PM features.

This is deliberately **not** a deprecation: we considered removing them at 2.0
and rejected it as needless churn for current users.

## Consequences

- The roadmap's "Deliberately deferred" section is updated to record this.
- Bug fixes to `cmd_time` / `cmd_user` are still welcome; feature PRs there will
  be declined unless they serve the context-layer mission.
- Revisit only if usage data or user demand clearly justifies reinvestment.
