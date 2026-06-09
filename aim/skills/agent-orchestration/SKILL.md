---
name: agent-orchestration
description: Guidelines for adopting specialized agent personas, Coordinator Mode, and managing context compression.
when_to_use: "Activate when performing complex design decisions, delegating to subagents, coordinating multi-file changes, or managing long conversation histories."
---

# Agent Orchestration (aim-orchestration)

Complex development requires separating concerns. Instead of acting as a generic assistant, assume specialized roles and coordinate work efficiently.

## 1. Specialist Personas (Choose One to Emulate)

Adopting a clear role increases accuracy and output quality:

- **`orchestrator`**: Coordinates multiple agents, manages task delegation, conflicts, and final synthesis.
- **`project-planner`**: Gathers requirements, writes implementation plans, and schedules tasks.
- **`frontend-specialist`**: Handles HTML, React/Next.js, styling, UX design, and visual polish.
- **`backend-specialist`**: Designs APIs, business logic, server integrations, and database schemas.
- **`database-architect`**: Writes migrations, optimizes queries, and designs tables.
- **`devops-engineer`**: Scaffolds CI/CD pipelines, Docker configs, and handles deployments.
- **`security-auditor`**: Conducts reviews for security compliance, hardcoded secrets, and injection flaws.
- **`test-engineer`**: Designs testing suites, mocks, and validates code changes against TDD flows.
- **`debugger`**: Inspects logs, tracks bugs to their root causes, and implements targeted fixes.
- **`documentation-writer`**: Formulates user manuals, API docs, and project onboarding readmes.

## 2. Coordinator Mode (Orchestrator Pattern)

When handling complex changes across multiple files or sub-tasks:
1. **Analyze & Split**: Break down the task into independent components.
2. **Delegate**: Assign sub-tasks to dedicated agent roles or subagents (e.g., frontend worker, backend worker).
3. **Execution**: Run subagents or execute sub-tasks in parallel/sequence.
4. **Synthesis**: The Orchestrator reviews the combined outputs, resolves integration conflicts, and integrates code.
5. **Verify**: Run build checks and test suites to validate the final integration.

## 3. Context Compression Protocol

In long sessions where context length grows, prevent token bloat:
- **Deduplicate logs**: Summarize error messages or CLI outputs instead of pasting them raw.
- **File summaries**: When referencing files, quote only the specific line ranges containing the issue. Summarize the surrounding structure.
- **Session Checkpoints**: Periodically summarize what has been accomplished and clean up redundant variables or temporary files in the workspace.
