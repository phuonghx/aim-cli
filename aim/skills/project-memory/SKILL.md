---
name: project-memory
description: Rules for managing tasks, project documentation, cross-referencing, and cross-session memory. Activate when resolving project tasks, creating documentation, referencing files, or logging persistent session memories.
---

# Project Memory (aim-memory)

Memory is the cognitive backbone of AI-native development. Because LLMs are stateless by default, project context must be stored deterministically in the codebase.

## 1. Directory Structure

Memory is organized under the `.ai-context/` directory:
- `.ai-context/config.json`: The single source of truth for project metadata, stack, and commands.
- `.ai-context/skills/`: Holds the active AIM skills.
- `.ai-context/docs/`: Directory for Markdown documentation files.

## 2. Tasks & Progress (Task Mode)

During execution, use planning tools to log tasks:
- Maintain a structured task list in your brain directory (`task.md`).
- Mark tasks with `[ ]` (todo), `[/]` (in-progress), and `[x]` (completed).
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`) when finalizing task items.

## 3. Documentation & Cross-Referencing

Keep documentation clean, modular, and cross-referenced:
- **Task Mentions:** Refer to tasks in files or commit messages using `@task-<id>`.
- **Doc Mentions:** Link to Markdown docs using `@doc/<path>`.
- **Code Line Links:** Reference specific lines using `@doc/<path>:12` or ranges using `@doc/<path>:10-25`.
- **Anchors:** Reference markdown sections using `@doc/<path>#section-slug`.

## 4. Session memory policy

At the end of a session or task:
- Evaluate whether any new design decision, architecture pattern, user preference, or recurring error should be saved as persistent memory.
- Store project-specific rules in local docs or `.ai-context/config.json`.
- Store global user preferences in global files so they carry across sessions.
- Default to saving durable rules automatically without waiting for explicit user instructions.
- Never duplicate full documentation code blocks into memory; summarize and reference the file path instead.
