# AIM AI Agent Integration Guide 🤖

**AIM** serves as the central orchestration and context synchronization layer for modern AI coding assistants. By editing a single file (`.ai-context/config.json`), you instantly propagate project tech stacks, style guidelines, safety constraints, custom commands, and workflows to all client configurations.

---

## 🔄 Compilation & Propagation

When you execute:
```bash
aim sync
```
AIM compiles your project settings and writes client-specific instruction files into your workspace root. 

Below is an overview of how each AI client reads and utilizes these configurations:

---

## 1. Claude Code (`CLAUDE.md`)
Claude Code automatically scans and reads the `./CLAUDE.md` file at startup. It uses this context to learn how to compile, build, test, and format your project, and imports style guidelines.

### Custom Slash Commands
AIM installs custom actions in Claude Code via `.claude/commands/`. You can trigger these actions directly using slash commands in the Claude Code terminal:
* **`/commit`**: Automatically analyzes git status and stages diffs, formatting a professional, standardized conventional commit message for approval.
* **`/pr`**: Assembles git differences, runs QA checks, and compiles a clean, structured Pull Request description markdown.
* **`/optimize`**: Audits targeted files or functions for space/time complexity bottlenecks and generates optimized alternatives.
* **`/review`**: Executes a comprehensive, multi-perspective code quality and security audit check.
* **`/test`**: Scans files and writes unit tests to maximize test coverage.
* **`/docs`**: Generates high-quality JSDoc, docstrings, or markdown API documentation.

---

## 2. Antigravity (`ANTIGRAVITY.md`)
Antigravity (Google DeepMind's Advanced Agentic Coding environment) reads `ANTIGRAVITY.md` to adopt strict workflow rules.

### Planning Mode Workflow
When given a complex task, the agent is forced to run through these phases:
1. **Planning Phase:** Research the task and create `implementation_plan.md` in the brain conversation directory. It cannot write code or run modifying commands until you review the plan and approve it by setting `request_feedback = false` or via chat.
2. **Execution Phase:** Create `task.md` in the conversation directory to list all tasks as checkbox items. The agent checks off items dynamically as progress is made.
3. **Verification & Walkthrough Phase:** Run build and automated test suites. Write a summary of changes and validation results in `walkthrough.md` with embedded screenshots or recordings.

### Knowledge Items (KI) System
`ANTIGRAVITY.md` instructs the agent to check the localized repo memory snapshots (`<appDataDir>/knowledge/`) first to prevent duplicate research efforts.

---

## 3. Cursor & Windsurf (`.cursorrules` & `.windsurfrules`)
Cursor and Windsurf read `.cursorrules` and `.windsurfrules` at the workspace root to guide their autocomplete (tab-completion) and chat behavior.

### Visual Styling Constraints
AIM instructs Cursor and Windsurf to prioritize high-level visual excellence:
* **Premium Design:** Avoid browser default styles. Use sleek dark-glassmorphism layouts, harmonious HSL tailored palettes, and rounded corners.
* **Micro-animations:** Implement subtle transitions and interactive hover effects.
* **No Placeholders:** Prohibit blank elements, static mockup text, or TODO placeholders. Use actual working logic or assets.

---

## 4. GitHub Copilot (`.github/copilot-instructions.md`)
GitHub Copilot reads `.github/copilot-instructions.md` to align inline code completions and chat responses with your project's technology stack and file conventions.
* **Contextual Suggestions:** Helps Copilot autocomplete functions matching your project's naming conventions (e.g. repository pattern, clean code guidelines).
* **Dependency Alignment:** Prevents Copilot from suggesting outdated package versions or incorrect API usages by declaring your active tech stack.
