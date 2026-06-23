---
description: Initialize AIM project context and rules. Use this when starting a project or setting up AIM.
---

# /aim-init - Initialize AIM Workspace

Initialize and synchronize the AIM project workspace context.

---

## 🔴 CRITICAL RULES

1. **Workspace Root** - Initialize in the correct project root where the code is located.
2. **Setup Config** - Run `aim init` to select agents and set up `config.json` correctly.
3. **Synchronize** - Run `aim sync` after initialization or configuration updates.
4. **Agent Alignment** - Ensure guidelines such as `CLAUDE.md`, `ANTIGRAVITY.md` (or Cursor/Windsurf rules) are generated.

---

## Task

Verify the status of the AIM workspace and initialize it:

1. **Check Context Directory**:
   - Check if `.ai-context` directory exists in the workspace.
   - If not initialized, run `aim init --all-agents` in the terminal to initialize all agents non-interactively, or run `aim init` and respond to options.
2. **Synchronize Workspace**:
   - If already initialized or after `aim init` finishes, run `aim sync` to make sure rules, modular skills, and commands are fully synchronized.
3. **Inspect Rules**:
   - Read the generated `CLAUDE.md`, `ANTIGRAVITY.md` (or the rule file of the active editor) to understand the project technology stack, core commands, and coding conventions.
4. **List Backlog**:
   - Run `aim task list` to view the current backlog tree and identify the next actionable task.

---

## Expected Output

| Action | Result / Deliverable |
|--------|----------------------|
| Setup | `.ai-context/config.json` containing project metadata, tech stack, and agent selections. |
| Skills | Modular skills in `.ai-context/skills/` and `.aim-agents/` directories. |
| Guidelines | Updated client files like `CLAUDE.md`, `ANTIGRAVITY.md`, `.cursor/rules/aim.mdc` or `.cursorrules`. |
| Sync Status | All rule files compiled and synchronized with the latest skills index. |

---

## Usage

```bash
/aim-init
```
