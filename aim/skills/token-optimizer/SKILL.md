---
name: token-optimizer
description: Guidelines and optimizations to reduce LLM token usage during development and command execution.
when_to_use: "Activate when executing shell commands, running large test suites, reading files, searching codebases, or staging commits."
---

# Token Optimizer (aim-rtk)

AI agents pay for every token read or written. During development, excessive logs or full-file rewrites waste cost and exhaust context windows. Follow these optimization guidelines.

## 1. RTK (Rust Token Killer) Command Principles

Whenever running terminal commands, reduce output to the bare minimum needed for debug/analysis:

### A. Git Operations (Save 60-80% tokens)
- **Status:** Use `git status -s` instead of a raw `git status`.
- **Diff:** Use `git diff --stat` first to see which files changed. Pull specific diffs via `git diff <file>` instead of dumping all files.
- **Log:** Always limit history, e.g., `git log -n 5 --oneline`.
- **Commits:** Avoid verbose outputs on pushes or pulls.

### B. Builds & Compilation (Save 80-90% tokens)
- Pipe command outputs to filter for errors or warnings (e.g. on Unix use `cmd | grep -E "Error|Warning"`, on Windows use `cmd | Select-String "Error"`).
- For TypeScript, run `tsc --noEmit` but group outputs or check only modified files.
- Avoid printing full successful build metrics.

### C. Testing (Save 90-99% tokens)
- Do not run the entire test suite in verbose mode. 
- Filter test runs to target only the specific file or test name:
  - Jest/Vitest: `npm test -- -t "test-name"`
  - Pytest: `pytest -k "test_name"`
  - Go: `go test -run "TestName"`
- Instruct the runner to print failures only (e.g., `--reporter=line` or `--summary-only`).

### D. File Navigation & Search (Save 60-75% tokens)
- **Do not read whole files** just to locate a function or variable. Use `grep` search or symbol lookup first.
- Only load line ranges of interest (e.g., lines 40-80) instead of reading 1000 lines.
- Limit directory listing: use `glob` or `git ls-files` instead of listing all subdirectories recursively.

## 2. Token-Efficient Editing

- **Use targeted replacements:** Never replace an entire file if you only need to modify a 10-line block. Use specific replace tools that replace precise lines by matching target content.
- **Commit frequently:** Small commits keep the git diff concise, making it easier for subsequent AI steps to understand what changed.
