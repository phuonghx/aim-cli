# AIM 🎯

**AIM** (AI Memory / Mind) is a centralized, unified memory, task tracker, and instruction synchronizer for modern AI coding assistants including **Claude Code**, **Antigravity**, and **Codex (Cursor / Windsurf / GitHub Copilot)**.

It compiles a single source-of-truth configuration file (`.ai-context/config.json`) and project directory into client-specific instruction files (`CLAUDE.md`, `ANTIGRAVITY.md`, `.cursorrules`, etc.), exposes custom slash commands, and installs AIM's 20 specialist agents, 45 skills, and 13 workflows.

---

## 🏗️ Folder Structure

```plaintext
aim/
├── templates/
│   ├── config.json.template      # Baseline configuration skeleton
│   ├── aim-agents/               # Full suite of AIM specialist agents, skills, and workflows
│   └── commands/                 # Custom slash commands for Claude Code
│       ├── commit.md             # Conventional commit messages helper
│       ├── pr.md                 # Pull Request checks & description assembler
│       ├── optimize.md           # Space/Time efficiency optimization
│       ├── review.md             # Code quality and security checklist
│       ├── test.md               # Unit test coverage expander
│       └── docs.md               # Code comments & API documentation generator
├── setup.py                      # Installer script (delegates to aim_cli.py init)
├── setup.bat                     # Windows batch wrapper for quick installation
├── sync.py                       # Standalone synchronizer script
├── aim_cli.py                    # Core AIM CLI engine
└── README.md                     # This documentation
```

---

## 🚀 Installation & Initialization

To initialize AIM in your workspace:

### On Windows
Simply double-click the `setup.bat` file or run:
```powershell
.\aim\setup.bat
```

This will also create:
- `aim.bat`: Windows wrapper at the root, allowing you to run `aim <command>` directly.
- `aim.sh`: Bash wrapper at the root for Unix-like shells.

---

## 🔄 Synchronization

If you modify project settings, conventions, or add custom instructions in `.ai-context/config.json`, propagate the updates to all AI runtimes by running:

```bash
aim sync
# or: python aim/sync.py
```

This updates:
* **Claude Code**: `CLAUDE.md` (project commands, style constraints, and active skills references).
* **Antigravity**: `ANTIGRAVITY.md` (agent planning flow, Knowledge Items policy, validation).
* **Codex (Cursor / Windsurf)**: `.cursorrules` & `.windsurfrules` (custom rules, UI design requirements).
* **GitHub Copilot**: `.github/copilot-instructions.md` (metadata context).

---

## 🛠️ CLI Reference

### 1. Task & Workflow Management
Manage project tasks and let your AI follow progress and check off acceptance criteria.

```bash
# Create a task
aim task create "Title" -d "Description" --ac "AC 1" --ac "AC 2" -p high -a "user"

# List tasks
aim task list

# View task details
aim task view <id>

# Edit task status or complete acceptance criteria
aim task edit <id> -s in-progress
aim task edit <id> --check-ac 1     # Check off AC index 1 (1-based)
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
