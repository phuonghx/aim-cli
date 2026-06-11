# Changelog

All notable changes to the AIM CLI and Control Hub project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2026-06-11

Backlog items from the AIM Roadmap project.

### Added
- **`aim task renumber <old> <new>`** (#10) — rename a task and rewrite every
  reference to it (`@task-N` in any task/doc, plus `dependsOn`/parent pointers).
  Resolves the duplicate/mismatched-id findings from `aim doctor`. Refuses a
  target id that is already taken.

### Changed
- **`aim github push --project N`** (#8) now sets each card's Project (v2)
  **Status** field to match its AIM status (todo→Todo, in-progress/in-review→
  In Progress, done→Done) — no more manually moving cards. Best-effort; no-op if
  the project has no Status field.

---

## [1.5.0] - 2026-06-11

Roadmap Phase 5 (final) — GitHub sync. Projects AIM tasks onto GitHub Issues
and Projects so a team gets a familiar board; AIM stays the agent's working
layer. Zero-dependency: shells out to the `gh` CLI (no OAuth libraries).

### Added
- **`aim github push [id] [--all] [--project N]`** — create/update a GitHub
  issue per task (idempotent via a stored `**GitHub Issue:**` number). Maps
  done → closed, otherwise open; optionally adds issues to a Project (v2).
- **`aim github status`** — show each task's linked issue.
- **`aim github create-project <title>`** — create a GitHub Project (v2) for the
  repo owner.
- Tasks carry a `githubIssue` field (a `**GitHub Issue:**` line).

---

## [1.4.0] - 2026-06-11

Roadmap Phase 4 — spec-driven development. Makes the existing `spec`/`plan`
task fields meaningful and integrates with GitHub spec-kit.

### Added
- **`aim spec import <dir>`** — imports a spec-kit feature directory (`spec.md`,
  optional `plan.md`) into `.ai-context/docs/specs|plans` and creates an umbrella
  task linked to the spec (expand it via the `decompose_prd` MCP prompt).
- **`aim spec coverage`** — reports how many tasks have a linked spec.
- **`aim validate --require-spec`** — also fails when any task has no linked spec
  (CI gate for spec-driven workflows). Broken spec `@doc` links were already
  caught by reference validation.

---

## [1.3.0] - 2026-06-11

Roadmap Phase 3 — task intelligence. Takes the deterministic parts of an
AI task manager (dependencies, "what's next", PRD decomposition) without
adding any LLM dependency.

### Added
- **Task dependencies** — tasks carry `dependsOn` (a `**Depends On:**` line in
  the file). `aim task create --depends-on N` and `aim task edit --add-dep N /
  --remove-dep N`, with cycle detection.
- **`aim task next`** — returns the next actionable task: highest priority
  (then lowest id) among not-done, not-blocked tasks whose dependencies are all
  done. Also exposed as the MCP tool `next_task`.
- **PRD decomposition (LLM inversion)** — MCP prompt `decompose_prd` instructs
  the connected agent to break a PRD into tasks and create them via the new
  batch tool **`create_tasks`**, which resolves within-batch dependency chains
  via per-task `key` references. The MCP server now advertises the `prompts`
  capability (`prompts/list`, `prompts/get`).

### Changed
- `create_task` MCP tool accepts `dependsOn`.

---

## [1.2.0] - 2026-06-11

Roadmap Phase 2 — reverse-sync. Removes the biggest adoption barrier: you
already have rules scattered across CLAUDE.md, .cursorrules, .clinerules, etc.

### Added
- **`aim ingest`** — scans known rule files (every sync target plus
  `.clinerules`/`.rules`/`.aider.conf.yml`), collects the hand-written content,
  and consolidates it into `.ai-context/imported/*.md`. `aim sync` then re-emits
  it into every client file under one "Imported Project Rules" section.
  - Strips the AIM `BEGIN/END` managed block and leading frontmatter, so AIM
    never re-imports its own generated output — `ingest` is safe to re-run
    (idempotent).
  - `--dry-run` previews what would be imported without writing.
  - `--emit` prints the raw content plus an instruction for the connected agent
    to restructure it into `config.json` (`conventions`/`constraints`/
    `customRules`) — the zero-dependency "invert the LLM" path.

### Changed
- `aim sync` now appends consolidated imported rules (from
  `.ai-context/imported/`) to every generated client file.

### Added
- **`aim doctor`** — diagnoses context drift with deterministic, no-LLM checks:
  stale memories (cross-referenced against git history of the files they
  mention), broken `@task`/`@doc` references, duplicate/mismatched task IDs
  (cross-branch merge artifacts), spec drift on done tasks, idle in-progress
  tasks, and spec coverage. Exits non-zero on actionable findings (CI-friendly).
  `--mine` filters to your own memories.
- **Correction loop** — new MCP tool `record_correction(what_was_wrong,
  correct_approach, refs)` captures a mid-session correction as a memory, so the
  lesson survives across sessions and syncs to every tool. New MCP tools
  `review_memory` and `doctor` as well.
- **Memory lifecycle** — `aim memory edit/rm/review` (the subsystem was
  previously add/list only). `review` resets a memory's staleness clock.
- **Real global memory layer** — `-l global` now persists to `~/.aim/memories.json`
  and is merged into every project (previously the flag was a no-op label).

### Changed
- Memory records now carry `author` (from `git config user.name`), `reviewedAt`,
  `status`, and auto-extracted `refs` (file paths / `@`-refs found in the
  content). These power `aim doctor`; `aim memory list` shows the author.
- All staleness logic lives in `aim/core.py` behind a `git_commits_since` seam,
  so it is unit-tested without requiring a real git repo.

---

## [1.0.0] - 2026-06-11

First stable public release of **AIM** (AI Memory/Mind) — a centralized,
stdlib-only context/task/memory manager for AI coding assistants. Earlier
`0.x` builds were internal pre-releases and are not part of this history.

### Workspace & CLI
- Task management with subtasks, labels, priorities, assignees, acceptance
  criteria, spec/plan links, and a lossless markdown round-trip (`## Notes`,
  custom sections, and in-progress `[/]` AC states survive every edit).
- Structured docs library (`aim doc`), persistent memory (`aim memory`),
  keyword search (`aim search`), and reference validation (`aim validate`).
- Time tracking (`aim time start/stop/status/log/report`), ASCII Kanban
  board (`aim board`, including a `blocked` column), and a project status
  summary (`aim status`).
- User/assignee management (`aim user`) and code-generation templates
  (`aim template`) with case helpers and a hand-rolled YAML/handlebars
  engine.
- `aim demo` generates an interactive AeroMap sample workspace.
- `aim --version` and consistent exit codes throughout.

### AI-client integration
- `aim sync` compiles `.ai-context/config.json` into client instruction
  files: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `ANTIGRAVITY.md`,
  `.cursor/rules/aim.mdc` (plus legacy `.cursorrules`/`.windsurfrules`),
  and `.github/copilot-instructions.md`.
- Non-destructive sync: generated content lives between
  `<!-- AIM:BEGIN -->` / `<!-- AIM:END -->` markers; anything outside is
  preserved, and pre-existing files are backed up to `.bak` on first sync.
- **MCP server** (`aim mcp`): serves the workspace over the Model Context
  Protocol (stdio, zero dependencies — pure stdlib JSON-RPC) so assistants
  query/mutate tasks, docs, and memories directly. Tools: `list_tasks`,
  `get_task`, `create_task`, `search`, `add_memory`, `list_memories`.

### Control Hub dashboard
- Local web dashboard (`aim browser`): Kanban with HTML5 drag-and-drop,
  task CRUD, docs viewer, memory grid, time tracking, dependency graph,
  and command-palette search, on a dark-mode Zinc/Indigo theme with
  Phosphor icons.
- Security-hardened: localhost-only with a per-launch session token and
  Host-header validation (blocks cross-origin and DNS-rebinding access),
  task-id path-traversal guards, HTML-escaping plus DOMPurify-sanitized
  Markdown (XSS), and `Content-Type` enforcement on mutating endpoints.
  Multi-threaded request handling.

### Reliability
- Atomic JSON writes (temp file + `os.replace`); corrupt stores are backed
  up to `*.corrupt-<timestamp>` rather than silently overwritten.
- Race-safe task-ID allocation; parent-cycle prevention; clock-skew-safe
  time tracking; UTF-8 stdout/stderr (no `UnicodeEncodeError` on piped
  output, including non-ASCII content on Windows).
- `aim init --force` reinstalls skills/agents with timestamped backups
  instead of destructive overwrites.

### Project layout & quality
- Shared service layer (`aim/core.py`) backing the CLI, dashboard, and MCP
  server from one implementation.
- MIT `LICENSE`, `pyproject.toml`, version single-sourced from
  `aim/__init__.py`, and a 36-test pytest suite with CI (ruff + pytest on
  Windows & Ubuntu, Python 3.9/3.13) gating releases.
