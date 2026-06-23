---
description: Initialize and sync the AIM project workspace context
---

# Initialize AIM Workspace

Initialize and synchronize the AIM project workspace context to get up to speed.

Instructions:
1. Check if the `.ai-context` directory exists.
2. If the project is not yet initialized with AIM, run `aim init --all-agents` in the terminal to initialize all agents non-interactively.
3. If it is already initialized, or immediately after running `aim init`, run `aim sync` to make sure all rule files, modular skills, and command shims are fully synchronized.
4. Read the generated project guidelines (e.g. `CLAUDE.md`, `ANTIGRAVITY.md`, `.cursorrules` or `.cursor/rules/aim.mdc` depending on the active editor context).
5. Check the list of tasks via `aim task list` to understand the backlog.
