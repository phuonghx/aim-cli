# Changelog

All notable changes to the AIM CLI and Control Hub project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-06-11

### Added
- **MCP server** (`aim mcp`): serves the workspace over the Model Context Protocol (stdio transport, zero dependencies — pure stdlib JSON-RPC). AI assistants (Claude Code, Cursor, Windsurf) can query and mutate tasks/docs/memories directly via the tools `list_tasks`, `get_task`, `create_task`, `search`, `add_memory`, `list_memories`. Register with `claude mcp add aim -- aim mcp`.
- **Modern sync targets**: `aim sync` now also emits `AGENTS.md` (cross-tool agent-instructions convention), `GEMINI.md` (Gemini CLI/Code Assist), and `.cursor/rules/aim.mdc` (Cursor's current rules format, with proper MDC frontmatter). Legacy `.cursorrules`/`.windsurfrules` are still emitted for backwards compatibility. `aim status` tracks all 8 targets automatically.

### Changed
- **Shared service layer** (`aim/core.py`): status aggregation, reference validation, search, memory add, and user-rename propagation are now implemented once and consumed by the CLI, the dashboard server, and the MCP server (previously duplicated between `aim_cli.py` and `browser_server.py`). CLI output and dashboard JSON shapes are unchanged.
- The dashboard SPA was extracted from a 3,000-line Python string literal into `aim/dashboard.html` (shipped via package data); `browser_server.py` shrank from ~4,000 to ~680 lines.
- `aim task list`, `aim board`, and `/api/tasks` now return tasks in deterministic ID order.

---

## [1.3.0] - 2026-06-11

### Fixed (Data Integrity)
- Task markdown round-trip is no longer lossy: the `## Notes` section, unknown custom sections, sub-headings inside `## Description`, and in-progress `[/]` AC states now survive every `task edit` / `time stop` / `user rename`. Checkboxes are only parsed from the `## Acceptance Criteria` section, so checklists in descriptions no longer migrate into ACs or shift `--check-ac` indices.
- All JSON stores (`memories.json`, `time_log.json`, `users.json`, timer state) are now written atomically (temp file + `os.replace`); a corrupt store is backed up to `*.corrupt-<timestamp>` instead of being silently clobbered.
- Task IDs are now allocated with exclusive file creation and retry, so concurrent creates from the CLI and dashboard can no longer overwrite each other.
- Fixed `UnicodeEncodeError` crash on Windows when output is piped (the way AI agents invoke the CLI) by forcing UTF-8 stdout/stderr.
- `aim sync` no longer overwrites user-authored `CLAUDE.md` / rule files: generated content lives between `<!-- AIM:BEGIN -->` / `<!-- AIM:END -->` markers, everything outside is preserved, and pre-existing files are backed up to `.bak` on first sync.
- Re-running `aim init` no longer deletes customized `.aim-agents/` or `.ai-context/skills/`; reinstalling requires `--force` and keeps a timestamped backup.
- Parent-cycle validation: a task can no longer become its own ancestor (CLI and dashboard), which previously made tasks vanish from `task list`.
- `aim validate` doc-reference regex no longer matches across whitespace, eliminating false "broken link" failures on ordinary prose.
- Template YAML parser: consecutive `- name:` list items no longer merge into one entry, and `#` inside quoted values is no longer treated as a comment.
- Timer stop now persists the time log before deleting timer state, and durations are clamped to zero on clock skew.
- `aim doc create` refuses to overwrite an existing document with the same slug.
- Malformed task files are reported and skipped instead of crashing `aim board` and the `/api/tasks` endpoint.

### Security (Dashboard)
- Removed the wildcard `Access-Control-Allow-Origin: *` header that let any website read and mutate all workspace data.
- Every `/api` request now requires a per-launch session token (embedded in the served HTML), blocking cross-origin and DNS-rebinding access; the Host header is validated against localhost.
- Fixed path traversal through the task `id` field in POST endpoints (arbitrary `.md` deletion/read).
- All user content rendered into the dashboard is HTML-escaped, and Markdown is sanitized with DOMPurify (stored-XSS fix).
- Mutating endpoints now require `Content-Type: application/json`.

### Added
- `aim --version` flag; version single-sourced from `aim/__init__.py`.
- `LICENSE` file (MIT), `pyproject.toml`, test suite (`tests/`), and a CI workflow (ruff + pytest on Windows/Ubuntu). Releases now run tests before publishing.
- `blocked` status: validated in `task edit --status` and shown as its own column on `aim board`.
- Dashboard server is now multi-threaded (no more one-slow-request stalls).

### Changed
- One-line installers now point to the correct repository (`phuonghx/aim-cli`); `aim.sh` prefers `python3`; `install.ps1` prefers `python`/`py` on Windows (avoids the Microsoft Store alias stub).
- `aim sync` failures now exit with code 1 and the error message recommends `aim init` (not `setup.py`).
- Project root discovery walks all the way up the directory tree (previously only one level), so running commands in a subdirectory no longer silently creates a second `.ai-context`.

---

## [1.2.0] - 2026-06-10

### Added
- Integrated the raw `taste-skill` ruleset under `aim/skills/taste-skill/SKILL.md` and `aim/templates/aim-agents/skills/taste-skill/SKILL.md` to govern default agent design behaviors on initialization.
- Imported the clean `@phosphor-icons/web` icon set via CDN to evict emojis across all dashboard tabs, headers, metric cards, list nodes, and form components.

### Changed
- Refactored the dashboard CSS variables and templates to conform to a professional dark-mode Zinc palette (Neutral slate theme with `#09090b` background, `#18181b` surface/cards, and `#27272a` borders) and a singular accent Indigo (`#6366f1` / hover `#4f46e5`).
- Unified all component border-radii across buttons, input fields, badges, tabs, cards, and modals to a strict, clean `6px`.
- Implemented snappy active transitions (`transform: scale(0.97)`) on all UI buttons for immediate tactile feedback.

---

## [1.1.0] - 2026-06-09

### Added
- Implemented HTML5 drag-and-drop operations for Kanban board task cards, automatically persisting column moves back to task markdown files.
- Added manual task creation via a `+ New Task` modal form.
- Added live priority editing dropdown inside the task detail modal.
- Added manual task deletion with referential integrity (automatically cleaning up/removing child subtasks and updating markdown files).

---

## [1.0.0] - 2026-06-08

### Added
- Initial release of AIM (Agent Integration Module) CLI and dashboard.
- Key features: local status compilation, task listing, doc library indexing, and project metadata setup.
