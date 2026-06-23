# Changelog

All notable changes to AIM are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-23

Initial public release of **AIM (AI Memory / Mind)** — a zero-dependency CLI that unifies memory, tasks, docs, and instructions for AI coding assistants.

### Core
- `aim init` / `aim sync` — compile a single source of truth (`.ai-context/`) into `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.windsurfrules`, `GEMINI.md`, and `.github/copilot-instructions.md`. Content outside the AIM markers is preserved.
  - Interactive selection of target AI agents during initialization (`aim init`).
  - Git tracking strategy for generated files (`track-all`, `ignore-all`, `rules-only`) to automatically manage `.gitignore`.
  - Slash command (`/aim-*`) generation support for the `antigravity` agent.
- `aim ingest` — import existing hand-written rule files into AIM.

### Tasks & specs
- Task hierarchy with subtasks, dependencies, labels, and acceptance criteria, plus an ASCII Kanban board (`aim task`, `aim board`, `aim status`).
- `aim spec new` — scaffold requirements / design / tasks with **EARS** acceptance criteria; `aim spec import` and `aim spec coverage`.

### Memory
- Persistent project/global memory with an `importance` score; ranked recall via `aim memory context` and the `get_memory_context` MCP tool (relevance × importance × recency).
- `aim doctor` — deterministic context-drift detection (stale memory vs git history, broken references, duplicate IDs); CI-friendly.

### Integrations
- Zero-dependency **MCP server** (`aim mcp`) exposing tasks, docs, and memory over stdio to any MCP client. Configured with a valid bundled config (`.aim-agents/mcp_config.json`).
- Two-way **GitHub Issues / Projects** sync (`aim github`).
- Local **web dashboard** (`aim browser`) — Kanban, knowledge graph, and a Health tab; bound to localhost with a per-session token.

### Tooling
- `aim lint` — validate bundled `SKILL.md` files against the Agent Skills conventions (`--fix` folds the legacy `when_to_use` field into `description`).
- `aim upgrade` plus an interactive "new release available" check — runs at most once a day, only in a TTY, and opts out with `AIM_NO_UPDATE_CHECK=1`.
- Optional `[semantic]` extra for embeddings-powered search and duplicate detection.
- A bundled suite of specialist agents, skills, and workflows.
- CI/CD release pipeline with automated smoke-testing (`aim --version`, `aim init`, `aim lint`) on Ubuntu and Windows.

### Notes
- Time tracking and user management are frozen; see [ADR 0001](docs/decisions/0001-freeze-time-tracking-and-users.md).
