# AIM CLI Reference Guide 🛠️

This document provides a comprehensive command-line reference for **AIM** (AI Memory/Mind). It covers every subcommand, available flags, and real-world command examples.

---

## Table of Contents
1. [Core Lifecycle Commands](#1-core-lifecycle-commands)
   * [`aim init`](#aim-init)
   * [`aim sync`](#aim-sync)
2. [Task Management](#2-task-management)
   * [`aim task create`](#aim-task-create)
   * [`aim task list`](#aim-task-list)
   * [`aim task next`](#aim-task-next)
   * [`aim task view`](#aim-task-view)
   * [`aim task edit`](#aim-task-edit)
3. [User & Team Management](#3-user--team-management)
   * [`aim user list`](#aim-user-list)
   * [`aim user add`](#aim-user-add)
   * [`aim user rename`](#aim-user-rename)
   * [`aim user remove`](#aim-user-remove)
4. [Structured Documentation](#4-structured-documentation)
   * [`aim doc create`](#aim-doc-create)
   * [`aim doc list`](#aim-doc-list)
   * [`aim doc view`](#aim-doc-view)
5. [Persistent Memory](#5-persistent-memory)
   * [`aim memory add`](#aim-memory-add)
   * [`aim memory list`](#aim-memory-list)
   * [`aim memory edit`](#aim-memory-edit)
   * [`aim memory review`](#aim-memory-review)
   * [`aim memory rm`](#aim-memory-rm)
6. [Global Command Suite](#6-global-command-suite)
   * [`aim search`](#aim-search)
   * [`aim validate`](#aim-validate)
   * [`aim spec`](#aim-spec)
   * [`aim ingest`](#aim-ingest)
   * [`aim doctor`](#aim-doctor)
   * [`aim status`](#aim-status)
   * [`aim board`](#aim-board)
7. [Time Tracking](#7-time-tracking)
   * [`aim time start`](#aim-time-start)
   * [`aim time status`](#aim-time-status)
   * [`aim time stop`](#aim-time-stop)
   * [`aim time log`](#aim-time-log)
   * [`aim time report`](#aim-time-report)
8. [Code Generation Templates](#8-code-generation-templates)
   * [`aim template create`](#aim-template-create)
   * [`aim template list`](#aim-template-list)
   * [`aim template view`](#aim-template-view)
   * [`aim template run`](#aim-template-run)
9. [AI Assistant Integration](#9-ai-assistant-integration)
   * [`aim mcp`](#aim-mcp)
   * [`aim browser`](#aim-browser)
10. [Demo Workspace](#10-demo-workspace)
   * [`aim demo`](#aim-demo)

---

## 1. Core Lifecycle Commands

### `aim init`
Initialize AIM in the project root directory. Creates `.ai-context/` directory, default templates, specialist agents, and shims configuration files.
* **Usage:** `aim init`
* **Example:**
  ```bash
  aim init
  ```

### `aim sync`
Compile and synchronize `.ai-context/config.json` into client-specific instruction files:
* `CLAUDE.md` (Claude Code), `AGENTS.md` (cross-tool convention), `GEMINI.md` (Gemini CLI/Code Assist), `ANTIGRAVITY.md` (Antigravity)
* `.cursor/rules/aim.mdc` (Cursor's modern rules format), plus legacy `.cursorrules` / `.windsurfrules` for backwards compatibility
* `.github/copilot-instructions.md` (GitHub Copilot)

Generated content is written between `<!-- AIM:BEGIN -->` / `<!-- AIM:END -->` markers; anything you write outside the markers is preserved on every re-sync.
* **Usage:** `aim sync`
* **Example:**
  ```bash
  aim sync
  ```

---

## 2. Task Management

### `aim task create`
Create a new task with optional parent relationships, tags, and cross-reference links.
* **Arguments:**
  * `title` (Required): Short title of the task.
* **Options:**
  * `-d`, `--desc`: Detailed description of the task.
  * `--ac`: Acceptance criteria item (repeatable for multiple ACs).
  * `-p`, `--priority`: Task priority (`low`, `medium`, `high`, `urgent`). Default: `medium`.
  * `-a`, `--assignee`: Project username to assign this task. Default: `unassigned`.
  * `--parent`: Parent task ID (creates subtask relationship).
  * `--depends-on`: Prerequisite task ID this task is blocked by (repeatable).
  * `-l`, `--label`: Categorization tag/label (repeatable for multiple labels).
  * `--spec`: Linked specification doc path (e.g. `@doc/sdd/auth.md`).
  * `--plan`: Linked implementation plan doc path (e.g. `@doc/plans/auth-plan.md`).
* **Example:**
  ```bash
  aim task create "Set up JWT Authentication" \
    -d "Implement secure login/signup using JWT tokens" \
    --ac "Verify passwords with bcrypt" \
    --ac "Generate 24h expiration JWT tokens" \
    -p high \
    -a "charlotte" \
    -l backend -l security \
    --spec "@doc/auth-sdd"
  ```

### `aim task list`
Display all active tasks rendered in an indented tree view according to parent-child subtask relationships.
* **Usage:** `aim task list`
* **Example:**
  ```bash
  aim task list
  ```

### `aim task next`
Print the next actionable task — the highest-priority (then lowest-id) task that
is not done, not blocked, and whose dependencies are all done. The deterministic,
no-LLM equivalent of "what should I work on next"; also available to agents as the
MCP `next_task` tool.
* **Usage:** `aim task next`
* **Example:**
  ```bash
  aim task next
  ```

### `aim task view`
View the full markdown content of a specific task.
* **Arguments:**
  * `id` (Required): The integer ID of the task.
* **Example:**
  ```bash
  aim task view 1
  ```

### `aim task edit`
Update task properties, mark acceptance criteria, or manage labels.
* **Arguments:**
  * `id` (Required): The integer ID of the task to edit.
* **Options:**
  * `-s`, `--status`: Update status (`todo`, `in-progress`, `in-review`, `done`, `blocked`).
  * `-a`, `--assignee`: Change task assignee.
  * `--add-ac`: Add a new acceptance criteria item.
  * `--check-ac`: Mark an AC index as completed (1-based index).
  * `--parent`: Update parent task ID (set to `0` to detach and make a root task).
  * `--add-dep`: Add a prerequisite task ID, with cycle detection (repeatable).
  * `--remove-dep`: Remove a prerequisite task ID (repeatable).
  * `--add-label`: Add a new label tag.
  * `--remove-label`: Remove an existing label tag.
  * `--spec`: Update linked specification document path.
  * `--plan`: Update linked plan document path.
  * `-d`, `--desc`: Update detailed task description.
* **Example:**
  ```bash
  aim task edit 1 -s "in-progress" --check-ac 1 --add-label "refactor"
  ```

---

## 3. User & Team Management

### `aim user list`
List all registered project team members.
* **Usage:** `aim user list`
* **Example:**
  ```bash
  aim user list
  ```

### `aim user add`
Register a new user in the database.
* **Arguments:**
  * `username` (Required): Unique username to add.
* **Example:**
  ```bash
  aim user add alice
  ```

### `aim user rename`
Rename an existing user. Automatically propagates name updates to the `assignee` field in all active task files.
* **Arguments:**
  * `old_username` (Required): Existing username.
  * `new_username` (Required): New username to set.
* **Example:**
  ```bash
  aim user rename charlie charlotte
  ```

### `aim user remove`
Remove a user from the database. Note that system default users (`developer`, `unassigned`) are protected.
* **Arguments:**
  * `username` (Required): Username to delete.
* **Example:**
  ```bash
  aim user remove alice
  ```

---

## 4. Structured Documentation

### `aim doc create`
Create a new markdown document inside `.ai-context/docs/`.
* **Arguments:**
  * `title` (Required): Title of the documentation file.
* **Options:**
  * `-f`, `--folder`: Subdirectory folder to organize the file (e.g. `architecture`, `guides`).
  * `-d`, `--desc`: Brief description of the documentation.
* **Example:**
  ```bash
  aim doc create "Database Indexing Guidelines" -f "architecture" -d "Rules for database migrations"
  ```

### `aim doc list`
Recursively list all document files in the project.
* **Usage:** `aim doc list`
* **Example:**
  ```bash
  aim doc list
  ```

### `aim doc view`
Read the content of a document file.
* **Arguments:**
  * `path` (Required): Path to the doc (e.g. `architecture/api-auth` or `@doc/architecture/api-auth`).
* **Example:**
  ```bash
  aim doc view architecture/api-auth
  ```

---

## 5. Persistent Memory

### `aim memory add`
Save a reusable pattern, rule, or architectural decision.
* **Arguments:**
  * `content` (Required): The memory text to remember.
* **Options:**
  * `-c`, `--category`: Categorization keyword (e.g. `decision`, `convention`, `guideline`). Default: `general`.
  * `-l`, `--layer`: Memory scope (`project` or `global`). `global` persists to `~/.aim/memories.json` and follows you across every repo. Default: `project`.
* **Notes:** Memories automatically capture the `author` (`git config user.name`),
  a `reviewedAt` timestamp, and `refs` — file paths / `@`-refs found in the text,
  which `aim doctor` uses to detect staleness. Wrap paths in backticks
  (`` `src/lib/http.ts` ``) so they are picked up as refs.
* **Example:**
  ```bash
  aim memory add "Prefer React Functional Components and Hooks over Class Components" -c convention -l project
  ```

### `aim memory list`
List all recorded memories (project + global), with author column.
* **Usage:** `aim memory list`

### `aim memory edit`
Edit a memory's content, category, or layer. Editing content re-extracts refs.
* **Arguments:** `id` (Required). Optional new `content` as a positional.
* **Options:** `-c`/`--category`, `-l`/`--layer` (moves between project/global).
* **Example:**
  ```bash
  aim memory edit 4 "Auth now uses RS256 as of 2026-06" -c decision
  ```

### `aim memory review`
Mark a memory as freshly verified, resetting its staleness clock (the fix
`aim doctor` suggests for a stale-flagged memory).
* **Arguments:** `id` (Required).
* **Example:**
  ```bash
  aim memory review 4
  ```

### `aim memory rm`
Delete a memory by ID.
* **Arguments:** `id` (Required).
* **Example:**
  ```bash
  aim memory rm 7
  ```

---

## 6. Global Command Suite

### `aim search`
Perform regex and case-insensitive matching across all tasks, docs, and memories.
* **Arguments:**
  * `query` (Required): The search keyword.
* **Example:**
  ```bash
  aim search "jwt"
  ```

### `aim validate`
Scan tasks and documents for broken mentions (e.g. `@task-999` or `@doc/missing` pointing to non-existent files).
* **Options:**
  * `--require-spec`: also fail if any task has no linked spec (spec-driven CI gate).
* **Example:**
  ```bash
  aim validate
  aim validate --require-spec
  ```

### `aim spec`
Spec-driven development helpers built on the task `spec`/`plan` fields.

#### `aim spec import`
Import a [GitHub spec-kit](https://github.com/github/spec-kit) feature directory:
copies `spec.md` (and optional `plan.md`) into `.ai-context/docs/specs|plans` and
creates an umbrella task linked to the spec. Expand it into subtasks with the
`decompose_prd` MCP prompt or `aim task create ... --depends-on`.
* **Arguments:** `dir` (Required) — the spec-kit feature directory.
* **Options:** `--name` — override the spec name (default: directory name).
* **Example:**
  ```bash
  aim spec import specs/001-user-auth
  ```

#### `aim spec coverage`
Report how many tasks have a linked spec, and which do not.
* **Usage:** `aim spec coverage`

### `aim ingest`
Reverse-sync: import rules you already hand-wrote across AI-client files into
AIM, so they become one consolidated source of truth. Scans every sync target
plus `.clinerules` / `.rules` / `.aider.conf.yml`, collects the content outside
the AIM markers (so it never re-imports AIM's own output — safe to re-run), and
writes it to `.ai-context/imported/*.md`. The next `aim sync` re-emits it into
every client file under an "Imported Project Rules" section.
* **Options:**
  * `--dry-run`: preview what would be imported without writing.
  * `--emit`: print the raw content plus an instruction for the connected agent
    to restructure it into `config.json` (zero-dependency "invert the LLM" path).
* **Workflow:**
  ```bash
  aim ingest --dry-run     # see what will be pulled in
  aim ingest               # write to .ai-context/imported/
  aim sync                 # re-emit consolidated rules everywhere
  # then delete the now-redundant originals from the source files
  ```

### `aim doctor`
Diagnose **context drift** — the wedge AIM is built around. Deterministic, no
LLM: it cross-references your memories/docs/tasks against git history and the
workspace to surface context that has likely gone stale.

Checks: broken `@task`/`@doc` references; memories whose referenced files have
changed many commits since last review; memories not reviewed in 90+ days;
duplicate or mismatched task IDs (cross-branch merge artifacts); done tasks
whose spec changed afterward; idle in-progress tasks; spec coverage.

Exits non-zero when there are high/medium findings, so it works as a CI gate.
* **Options:**
  * `--mine`: only show findings for memories you authored.
* **Example:**
  ```bash
  aim doctor
  aim doctor --mine
  ```

### `aim status`
Show the project statistics summary report, including task breakdown, time spent, active timers, and configuration sync status.
* **Usage:** `aim status`
* **Example:**
  ```bash
  aim status
  ```

### `aim board`
Display a lightweight, text-based ASCII Kanban board arrangement of all active tasks in the terminal.
* **Usage:** `aim board`
* **Example:**
  ```bash
  aim board
  ```

---

## 7. Time Tracking

### `aim time start`
Start a time tracking session for a specific task. Only one active timer can run at a time.
* **Arguments:**
  * `id` (Required): Task ID to track.
* **Example:**
  ```bash
  aim time start 1
  ```

### `aim time status`
Show details of the current active timer session.
* **Usage:** `aim time status`
* **Example:**
  ```bash
  aim time status
  ```

### `aim time stop`
Stop the active timer and log the duration.
* **Options:**
  * `-n`, `--note`: Optional comment describing the work session.
* **Example:**
  ```bash
  aim time stop -n "Finished styling navbar components"
  ```

### `aim time log`
Print all log entries recorded for a specific task.
* **Arguments:**
  * `id` (Required): The integer task ID.
* **Example:**
  ```bash
  aim time log 1
  ```

### `aim time report`
Generate a report displaying total accumulated work hours per task.
* **Usage:** `aim time report`
* **Example:**
  ```bash
  aim time report
  ```

---

## 8. Code Generation Templates

### `aim template create`
Create a new directory structure for code-generation templates under `.ai-context/templates/<name>/`.
* **Arguments:**
  * `name` (Required): Name of the template.
* **Example:**
  ```bash
  aim template create react-component
  ```

### `aim template list`
List all templates configured in the workspace.
* **Usage:** `aim template list`
* **Example:**
  ```bash
  aim template list
  ```

### `aim template view`
Inspect the configurations and prompt variables of a template.
* **Arguments:**
  * `name` (Required): Name of the template.
* **Example:**
  ```bash
  aim template view react-component
  ```

### `aim template run`
Execute a template to generate source files. Prompts interactively for missing variables.
* **Arguments:**
  * `name` (Required): Name of the template.
* **Options:**
  * `--dry-run`: Preview files and path calculations without writing to disk.
  * `-v`, `--var`: Variables in `key=value` format (repeatable).
* **Example:**
  ```bash
  aim template run react-component --dry-run -v name="CustomCard"
  ```

---

## 9. AI Assistant Integration

### `aim mcp`
Run the AIM MCP (Model Context Protocol) server over stdio. AI assistants connected to it can query and mutate the workspace directly — no static file reads needed. Zero external dependencies (pure stdlib JSON-RPC).

Exposed tools: `list_tasks`, `get_task`, `create_task`, `search`, `add_memory`, `list_memories`.

* **Usage:** `aim mcp` (intended to be launched by the MCP client, not by hand)
* **Register in Claude Code:**
  ```bash
  claude mcp add aim -- aim mcp
  ```
* **Register in Cursor** (`.cursor/mcp.json`):
  ```json
  { "mcpServers": { "aim": { "command": "aim", "args": ["mcp"] } } }
  ```

### `aim browser`
Launch the AIM Control Hub web dashboard (Kanban board, docs library, memory, time tracking, dependency graph) on a local-only server.
* **Options:**
  * `-p`, `--port`: Port to bind (default `6420`; auto-increments if busy).
  * `--no-open`: Start the server without opening the browser automatically.
* **Example:**
  ```bash
  aim browser -p 7000 --no-open
  ```

---

## 10. Demo Workspace

### `aim demo`
Generate the interactive **AeroMap** demo workspace (users, docs, tasks with subtasks/labels, memories, time logs, and a code-generation template) so you can explore every AIM feature with realistic seed data. `aim generator demo` is an equivalent alias.
* **Usage:** `aim demo`
* **Example:**
  ```bash
  aim demo && aim board && aim browser
  ```
