# AIM 🎯

**AIM** (AI Memory / Mind) is a centralized, unified memory, task tracker, and instruction synchronizer for modern AI coding assistants including **Claude Code**, **Antigravity**, and **Codex (Cursor / Windsurf / GitHub Copilot)**.

It compiles a single source-of-truth configuration file (`.ai-context/config.json`) and project directory into client-specific instruction files (`CLAUDE.md`, `ANTIGRAVITY.md`, `.cursorrules`, etc.), exposes custom slash commands, and installs AIM's 20 specialist agents, 45 skills, and 13 workflows.

---

## 🏗️ Folder Structure

```plaintext
aim-cli/
├── .github/
│   └── workflows/
│       └── release.yml           # GitHub Actions release pipeline
├── aim/                          # Module directory
│   ├── templates/                # Full suite of AIM specialist agents, skills, and workflows
│   ├── skills/                   
│   ├── __init__.py
│   ├── aim_cli.py                # Core AIM CLI engine
│   ├── browser_server.py         # Dashboard web server
│   └── sync.py                   # Standalone synchronizer script
├── .gitignore
├── install.ps1                   # One-line installer for Windows PowerShell
├── install.sh                    # One-line installer for macOS/Linux Bash
├── MANIFEST.in                   # Packaging manifest file
├── setup.py                      # Package installation config
├── setup.bat                     # Windows batch installer helper
├── aim.bat                       # Windows CLI wrapper (development)
├── aim.sh                        # Bash CLI wrapper (development)
└── README.md                     # This documentation
```

---

## 🚀 Installation & Initialization

### One-line install

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/phuonghx/aim-cli/main/install.ps1 | iex
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/phuonghx/aim-cli/main/install.sh | bash
```

**Or directly via pip:**
```bash
pip install git+https://github.com/phuonghx/aim-cli.git
# optional: embeddings for `aim search --semantic` + doctor similar-memory check
pip install "aim-cli[semantic] @ git+https://github.com/phuonghx/aim-cli.git"
```

Then initialize AIM in your project:
```bash
aim init          # set up .ai-context/, skills, and agent suite
aim --version     # verify the installed version
```

Re-running `aim init` on an existing workspace will not overwrite your
customized skills/agents — use `aim init --force` to reinstall (a timestamped
`.bak` backup is kept).

**Already have rules scattered across files?** Pull your existing CLAUDE.md /
`.cursorrules` / `.clinerules` / AGENTS.md into AIM in one step:
```bash
aim ingest --dry-run     # preview
aim ingest && aim sync   # consolidate, then re-emit everywhere
```

### From a repository checkout (development)
Run via the included wrappers without installing:
- `aim.bat` (Windows) / `aim.sh` (Unix-like shells) at the repo root.

---

## 🔄 Synchronization

If you modify project settings, conventions, or add custom instructions in `.ai-context/config.json`, propagate the updates to all AI runtimes by running:

```bash
aim sync
# or: python aim/sync.py
```

Generated content is written between `<!-- AIM:BEGIN -->` / `<!-- AIM:END -->` markers — anything you write outside the markers in these files is preserved on every re-sync (pre-existing files without markers are backed up to `.bak` once).

This updates:
* **Claude Code**: `CLAUDE.md` (project commands, style constraints, and active skills references).
* **Cross-tool agents** (OpenAI Codex, Jules, etc.): `AGENTS.md` (the shared agent-instructions convention).
* **Gemini CLI / Code Assist**: `GEMINI.md`.
* **Antigravity**: `ANTIGRAVITY.md` (agent planning flow, Knowledge Items policy, validation).
* **Cursor**: `.cursor/rules/aim.mdc` (modern project-rules format) plus legacy `.cursorrules`.
* **Windsurf**: `.windsurfrules`.
* **GitHub Copilot**: `.github/copilot-instructions.md` (metadata context).

---

## 🔌 MCP Server (Live AI Integration)

Beyond static instruction files, AIM can serve the workspace live over the **Model Context Protocol**, so assistants query tasks/docs/memories directly:

```bash
# Claude Code
claude mcp add aim -- aim mcp
```

```json
// Cursor (.cursor/mcp.json)
{ "mcpServers": { "aim": { "command": "aim", "args": ["mcp"] } } }
```

Exposed tools: `list_tasks`, `get_task`, `create_task`, `create_tasks`, `next_task`, `search`, `add_memory`, `list_memories`, `record_correction`, `review_memory`, `doctor`. Plus a `decompose_prd` prompt that turns a PRD into dependency-ordered tasks via `create_tasks`. Zero external dependencies — pure stdlib JSON-RPC over stdio.

When the user corrects the agent mid-session, the agent can call
`record_correction(...)` to persist the lesson as a memory — it then syncs to
every tool, so the next session (in any client) does not repeat the mistake.

---

## 🐙 GitHub sync (`aim github`)

Project AIM tasks onto GitHub Issues + Projects so your team gets a familiar
board, while AIM stays the agent's working layer. Zero-dependency — it shells out
to the `gh` CLI (requires `gh auth login`).

```bash
aim github create-project "AIM Roadmap"   # create a Project (v2)
aim github push --all --project 3         # create/update an issue per task, add to the project, sync Status
aim github pull --all                     # two-way: reconcile tasks from issue state/title
aim github status --check                 # report drift between AIM and GitHub
```

Issues are idempotent (the issue number is stored back in each task); a `done`
task closes its issue, and `push --project` sets each card's Status field. Sync
is two-way: `pull` brings issue state/title changes back into AIM (GitHub is
canonical for state/title; AIM stays canonical for acceptance criteria,
dependencies, and spec links).

---

## 🩺 Context Health (`aim doctor`)

AIM's wedge is fighting **context drift** — stale rules and decisions that make
agents confidently wrong. `aim doctor` detects it deterministically (no LLM):

```bash
aim doctor          # full report; exits non-zero on high/medium findings (CI-friendly)
aim doctor --mine   # only memories you authored
```

It cross-references each memory's `refs` against git history (e.g. "this decision
mentions `aim/auth.py`, which changed 23 commits since you last reviewed it →
likely stale → run `aim memory review 4`"), and flags broken references,
duplicate task IDs, and spec drift.

---

## 🛠️ CLI Reference

### 1. Task & Subtask Hierarchy Management
Manage project tasks, build parent-child subtask relationships, and categorize with labels.

```bash
# Create a task (supports parent ID, labels, spec, and plan)
aim task create "Implement landing page SEO" -d "SEO optimization" --ac "Add tags" -p high -a "alice" --parent 1 -l bug -l seo --spec "@doc/sdd/seo.md"

# List tasks (prints an indented tree view showing subtasks and tags)
aim task list

# View task details
aim task view <id>

# Edit task properties, add/remove tags, set spec/plan paths
aim task edit <id> -s in-progress --parent 2 --add-label frontend --remove-label bug -d "Updated description"
aim task edit <id> --check-ac 1     # Check off AC index 1 (1-based)
```

### 1.5. User Database & Assignment (CRUD)
Manage project team members and assign tasks.

```bash
# List all registered users
aim user list

# Register a new user
aim user add <username>

# Rename an existing user (automatically propagates assignee updates to all active tasks)
aim user rename <old_username> <new_username>

# Remove a user (system default users are protected)
aim user remove <username>
```

### 1.6. Project Status & ASCII Kanban Board
Check project health statistics and view your tasks in a lightweight ASCII Kanban board right inside the terminal.

```bash
# View project status summary (stats for tasks, docs, memories, time tracking, and sync health)
aim status

# Display the tasks arranged as an ASCII Kanban board (columns: TODO, IN-PROGRESS, IN-REVIEW, DONE)
aim board
```

### 1.7. Task Time Tracking
Track the exact time spent working on specific tasks directly from your CLI.

```bash
# Start timer for a task
aim time start <task_id>

# Check current active timer status
aim time status

# Stop active timer and optionally add a note
aim time stop -n "Implemented feature X"

# View time log entries for a specific task
aim time log <task_id>

# Generate a project time tracking report
aim time report
```

### 1.8. Code Generation Templates
Scaffold, view, and execute reusable code generation templates with dynamic variables and case-helpers:

```bash
# List all available templates
aim template list

# Create a new template scaffold (creates folder under .ai-context/templates/<name>/)
aim template create <template_name>

# View the configuration of a specific template
aim template view <template_name>

# Run a template (prompts for missing variables)
aim template run <template_name>

# Run with predefined variables
aim template run <template_name> -v name="MyComponent"

# Dry-run execution to preview output files without writing to disk
aim template run <template_name> --dry-run -v name="MyComponent"
```

### 2. Structured Documentation
Scaffold, list, and read Markdown docs inside `.ai-context/docs/`.

```bash
# Create a doc
aim doc create "API Auth" -f "architecture" -d "JWT auth guide"

# List docs
aim doc list

# View a doc
aim doc view architecture/api-auth
```

### 3. Persistent Memory
Save reusable patterns, decisions, or rules that AI should recall between sessions.

```bash
# Save a decision or rule
aim memory add "We use repository pattern for database transactions" -c decision -l project

# List saved memories
aim memory list
```

### 4. Semantic Search
Perform keyword and regex matching across all tasks, docs, and memories:

```bash
aim search "auth"
```

### 5. Link Validation
Scan tasks and documents for broken mentions (e.g. `@task-X` or `@doc/path` linking to non-existent resources):

```bash
aim validate
```

---

## 🤖 Supported Clients & How They Use It

### 1. Claude Code
Claude Code automatically loads `./CLAUDE.md` to learn about compile commands, test runs, code styling, and safety constraints.
- Trigger custom actions directly via slash commands:
  - `/commit`: Inspects git status/diff and formats conventional commit messages.
  - `/pr`: Standardizes PR titles, description layouts, and verification steps.
  - `/optimize`: Performs time/space complexity audits on targeted functions.
  - `/review`: Executes QA/Security code review checklists.
  - `/test`: Writes targeted tests based on the project's runner.
  - `/docs`: Automates writing docstrings, JSDoc, or markdown references.

### 2. Antigravity (Advanced Agentic Coding)
Antigravity reads `ANTIGRAVITY.md` which instructs it on:
- **Planning Mode**: Forcing the agent to write and get approval on `implementation_plan.md` before coding, track checklist tasks in `task.md`, and summarize verification in `walkthrough.md`.
- **Knowledge Items (KI) System**: Directing the agent to read workspace-specific memory snapshots in the local AppData knowledge folder first, preventing duplicated efforts.

### 3. Codex (Cursor & Windsurf)
Cursor and Windsurf read `.cursorrules` and `.windsurfrules` to:
- Adopt specific frameworks guidelines (e.g. Next.js App Router rules).
- Apply high-level visual styling rules (Harmonious palettes, glassmorphism, micro-animations, no placeholders).

### 4. GitHub Copilot
Copilot parses `.github/copilot-instructions.md` to align autocomplete recommendations with the project's tech stack and code conventions.
