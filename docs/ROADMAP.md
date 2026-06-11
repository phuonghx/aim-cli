# AIM Roadmap

> **Positioning thesis:** AIM is the **living context layer** for AI coding
> assistants — the one place project context (rules, tasks, memory, docs) lives,
> compiles out to every tool, *and stays trustworthy over time*. We do not
> compete on task-management or rules-sync breadth (task-master, Backlog.md,
> rulesync each win their slice). Our wedge is the problem none of them own:
> **context drift** — stale rules and corrections that never get captured, which
> account for the majority of real-world AI-assistant failures.

## Product decisions (locked 2026-06-11)

These four rulings shape every phase below:

1. **Core user = small team (2–5 devs)**, not solo. Consequence: memory carries
   an `author` (from `git config user.name`, no permissions — git is the audit
   log); cross-branch task-ID collisions are a real risk handled pragmatically
   (a `doctor` check + `aim task renumber`, *not* a new ID scheme); GitHub sync
   becomes a first-class phase (teams live on GitHub).
2. **Zero-dependency core + optional extras.** `pip install aim-cli` runs every
   core feature with stdlib only. `pip install aim-cli[semantic]` later adds
   embeddings so `doctor` can detect *contradiction* (not just "file changed")
   and enable true semantic search. No extra is ever required for core.
3. **Time-tracking / users / dashboard = keep simple, maintenance-only** until
   the wedge is proven. Not cut. The future investment there is **GitHub
   Projects sync** (Phase 5), not bespoke PM features.
4. **Phase 1 is a real validation gate.** If `aim doctor` dogfooded on real
   repos surfaces no useful warnings, we **stop and re-orient** — we do not
   build Phases 2–5 on an unproven wedge.

**Everything that shells out (git, gh) keeps AIM zero-dependency** — the same
trick that makes `doctor` work also makes GitHub sync work without OAuth libs.

This roadmap supersedes the previous one (a lint/SSE/3D-graph plan that did not
match this direction). Each phase lands in `aim/core.py` (pure, unit-tested via
the `workspace` fixture) and is surfaced across all three frontends: CLI, the
MCP server, and the dashboard.

## The throughline

```
"Living context layer" — context that keeps itself fresh and closes the correction loop
│
├─ Phase 0  Complete the memory subsystem        (foundation)
├─ Phase 1  WEDGE: aim doctor + correction loop   (#1 + #2)   ← VALIDATION GATE
├─ Phase 2  aim ingest (reverse-sync)             (#5)        adoption unlock
├─ Phase 3  Task intelligence: deps + next_task   (#3)        deterministic, zero-dep
├─ Phase 4  Spec traceability + spec-kit import   (#4)        close spec→task→code loop
└─ Phase 5  GitHub Issues / Projects sync                     team's display layer
```

**Strategic principle — invert the LLM dependency.** AIM stays zero-dependency
and never holds an API key. When a feature needs intelligence (PRD
decomposition, restructuring imported prose), AIM exposes it through MCP and the
*connected agent* does the thinking, then writes structured results back. AIM is
the deterministic substrate; the agent is the intelligence.

---

## Phase 0 — Complete the memory subsystem · effort: S–M

Foundation for Phases 1–2. The audit confirmed memory is half-built: the
`global` layer is a label only, there is no edit/delete, and nothing records
when a memory was last verified.

**Data model** (`add_memory` in `aim/core.py`): add `reviewedAt` (defaults to
`createdAt`), `refs` (file paths / `@`-refs extracted from content), `status`
(`active` / `archived`), and **`author`** (from `git config user.name`, falling
back to the OS user). `author` is required up front because retrofitting
ownership onto existing memories later is lossy — it is the one team-readiness
hook we bake in now.

**Build**
- `core.update_memory(id, ...)`, `core.delete_memory(id)`, `core.review_memory(id)` (resets `reviewedAt`).
- `core.extract_refs(text)` — extract `@task-N`, `@doc/...`, and source paths (`aim/foo.py`, `src/**`). Pure, easily tested.
- `core.current_author()` — `git config user.name` via the same git seam, OS-user fallback.
- Real `global` layer: read/write `~/.aim/memories.json`, merged on list.
- Surfaces: CLI `aim memory edit/rm/review`; MCP `update_memory`/`delete_memory`/`review_memory`; dashboard edit/delete in the existing memory grid.

**Tests** memory edit/delete round-trip; `extract_refs` on non-ASCII + paths; global-layer merge; `author` capture with git seam monkeypatched.

---

## Phase 1 — WEDGE: `aim doctor` + correction loop · effort: M · 🔑 the moat

The capability no competitor owns, aimed squarely at context drift.

### 1a. `aim doctor` — infer staleness from git, no new metadata required (read-only)

| Check | Deterministic logic | Severity |
|---|---|---|
| Broken refs | reuse `core.validate_references()` | high |
| Memory stale vs code | for each path `ref`: `git log --since=<reviewedAt> -- <path>` count; over threshold → likely stale | medium |
| Memory unreviewed | `now - reviewedAt > 90d` (configurable) | low |
| Done task, spec changed after | spec/plan doc modified after the task's last update | medium |
| In-progress task idle | no update in > N days | low |
| Duplicate / mismatched task IDs | two files claim the same id, or filename ≠ header (cross-branch merge artifact) | high |
| Orphans | doc/task with no inbound refs | info |
| Spec coverage | tasks without a spec link (ties to Phase 4) | info |

**Team mode (small team).** `aim doctor --mine` filters stale-memory warnings to
the current `author`, so each dev is nudged about *their own* context, not spammed
with the whole team's. `aim task renumber <old> <new>` resolves an ID collision and
rewrites every `@task-N` reference pointing at it — far cheaper than changing the
ID scheme.

**Key design:** isolate a seam `core.git_commits_since(path, iso_ts)` (shells out
to `git`; returns empty if not a git repo / git absent) so checks are unit-testable
by monkeypatching the seam — no real git needed in tests. Output is a
severity-grouped report with an exit code (0 when only info/low). Surface via MCP
`doctor` and a dashboard "Health" tab.

### 1b. Correction loop

MCP tool `record_correction(what_was_wrong, correct_approach, refs)` → writes a
`category="correction"` memory with `refs`. When an agent is corrected mid-session,
the lesson enters AIM → `aim sync` pushes it to every tool → the next agent does
not repeat it. This closes the feedback loop the 2026 context-engineering
research flags as the missing link.

> **🚪 VALIDATION GATE — riskiest assumption:** *do users actually feel the pain
> of stale context?* Cheapest test: ship `aim doctor` read-only first and dogfood
> it on AIM's own `.ai-context/` (real memories + git history already exist). If
> it surfaces genuinely useful warnings, the wedge is real — invest in Phases 2–4.
> If not, stop here.

**Tests** one fixture per check (temp git or monkeypatched seam); correction-loop round-trip.

---

## Phase 2 — `aim ingest` (reverse-sync) · effort: M · adoption unlock

Everyone already has rules scattered across files. Sync tools only compile
*outward*; AIM reads *inward* — the migration path that removes the #1 adoption
barrier.

**Build** `aim ingest [--dry-run]` scans the `SYNC_TARGETS` paths plus
`.clinerules`, **strips the `AIM:BEGIN/END` managed block** (never re-imports our
own output), and collects user-authored content.

**Merge strategy (avoid fuzzy prose→config parsing):**
- Deterministic MVP: collect into `.ai-context/imported/<source>.md`; `sync` re-emits it as one block; user reviews the diff first.
- LLM-inversion: `aim ingest --emit` outputs the raw content plus an instruction for the *connected agent* to restructure it into `conventions`/`constraints`/`customRules`. AIM stays zero-dependency.

**Tests** ingest skips the AIM-managed block; ingest→sync round-trip does not duplicate content.

---

## Phase 3 — Task intelligence: dependencies + `next_task` · effort: M

Take only the *deterministic* parts of task-master's value — the parts AIM can do
without an LLM — rather than competing head-on.

- **3a. Dependencies.** Add `dependsOn: [ids]` to the task model → a
  `**Depends On:**` metadata line parsed/rendered in `aim/aim_cli.py`. Extend
  `detect_parent_cycle` to detect cycles across the dependency graph.
- **3b. `next_task`** (task-master's signature feature, done deterministically):
  among not-done tasks, return the highest-priority one whose dependencies are all
  done. No LLM. Surface `aim task next` + MCP `next_task`.
- **3c. PRD→tasks via inversion.** Add MCP prompts capability (`prompts/list` +
  `prompts/get`) with a `decompose_prd` prompt instructing the agent to break a PRD
  into AIM tasks and write them via a new batch `create_tasks` tool with deps.

**Tests** `dependsOn` round-trip; `next_task` across dependency chains + cycle; batch create.

---

## Phase 4 — Spec traceability + spec-kit import · effort: S–M

Make the existing `spec`/`plan` task fields meaningful, and integrate with
GitHub spec-kit rather than reinventing it.

- `aim validate --require-spec`: flag tasks lacking a spec link or whose spec file is missing; add "spec coverage %" to `aim doctor`.
- `aim spec import <dir>`: read spec-kit output (`spec.md`/`plan.md`/`tasks.md`) → create AIM docs + an umbrella task linked to the spec doc; agents expand it via Phase 3.

**Tests** `--require-spec` exit code; spec-kit import creates the expected docs + links.

---

## Phase 5 — GitHub Issues / Projects sync · effort: M–L · team display layer

Small teams live on GitHub. Rather than building bespoke multi-user PM features,
project AIM tasks onto GitHub Issues + Projects. **Role split: GitHub is the
team's display/collaboration layer; AIM stays the agent's working layer.**

**Zero-dependency via `gh`.** Shell out to the GitHub CLI (same pattern as the
`git` seam) — no OAuth libraries, no token handling in AIM.

**Build (one-way MVP first, then two-way)**
- `aim task push-github [id|--all]` — create/update an Issue per task; map status → Issue state + a Project status field; store `githubIssue: #42` in task metadata so updates are idempotent.
- `aim github status` — show which tasks are linked / drifted from their Issue.
- Later: two-way pull (Issue edits → task files), label/assignee mapping, and a `doctor` check for AIM↔GitHub drift.

**Risks** `gh` must be installed + authenticated (detect and guide, like the
installers do for Python); mapping AIM's richer task model (subtasks, deps, AC)
onto Issues is lossy — decide what is canonical per field (proposal: AIM canonical
for AC/deps, GitHub canonical for discussion/assignment).

**Tests** task↔Issue field mapping (pure function, `gh` mocked); idempotent
re-push; drift detection.

---

## Sequencing rationale

- **0 before 1** — doctor needs `reviewedAt`/`refs`.
- **1 is the gate** — cheap, read-only, validates the entire positioning. Do not build 2–4 until 1 proves the wedge.
- **2 before 3–4** — ingest grows the install base, giving doctor and deps real data to work on.
- **3 before 4** — spec-import (4) creates tasks; dependency/next logic (3) is what makes those tasks valuable.
- **5 last** — GitHub sync should project a *mature* task model (deps, spec links from 3–4); syncing a thin model first would lock in a lossy mapping.

## Deliberately deferred (scope discipline)

- **Time-tracking / users — FROZEN (maintenance-only)** as of 2026-06-11. The
  open question is resolved: they are kept and supported but get no new
  investment; team assignment lives on GitHub via `aim github`. See
  [ADR 0001](decisions/0001-freeze-time-tracking-and-users.md). (Issue #12)
- **True semantic search / contradiction detection** — shipping as the optional
  `pip install aim-cli[semantic]` extra (embeddings); the core stays
  zero-dependency. (Issue #11)

## Status (2026-06-11)

All roadmap phases shipped (v1.0.0 → v1.8.0). Backlog from the AIM Roadmap
project: #7 (two-way sync), #8 (Project status sync), #9 (Health tab), #10
(task renumber) are done; #11 (semantic extra) is in progress; #12 (this
freeze decision) is recorded above.

## Comparable tools (landscape reference)

- Rules sync: rulesync, agent_sync — broader client coverage; not our moat.
- AI task management: claude-task-master (PRD→tasks, MCP), Backlog.md (git-native markdown).
- Memory/persistence: MCP knowledge-graph memory (official), Cline Memory Bank.
- Spec-driven: GitHub spec-kit (integrate, don't reinvent).
