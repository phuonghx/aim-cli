---
description: Extract reusable knowledge, patterns, schemas, or decisions from the current session into AIM memories or documentation.
---

# /aim-extract - Extract Project Memory & Patterns

Analyze the current session, recent modifications, or code files, and extract reusable rules, schemas, decisions, or architectural patterns into AIM's persistent context.

---

## 🔴 CRITICAL RULES

1. **No Duplicate Documentation** - Do not copy large blocks of code/documentation into memories. Summarize the rule and reference the file path instead.
2. **Context Enrichment** - Check recent commits or chat logs to identify patterns, recurring bugs, or design decisions.
3. **Cross-Referencing** - Tag memories and docs with relevant `@task-N` or `@doc/<path>` references.
4. **Appropriate Layer** - Use the `project` layer for repository-specific rules, and the `global` layer for general user preferences or cross-project conventions.

---

## Task

Extract knowledge and save it to the memory layer:

1. **Scan Context**:
   - Inspect files modified in the current session (e.g. using `git status -s` or reviewing diffs).
   - Review recent errors, lessons learned, or choices made during implementation.
2. **Determine Format**:
   - For **micro-rules, decisions, or conventions**: Add to memories.
   - For **detailed guides, architectural designs, or API references**: Create a documentation file using `aim doc create`.
3. **Execute Extraction**:
   - Run the appropriate `aim memory add` command:
     - Project-specific rule: `aim memory add "Rule/Decision description" -c [decision|syntax|pattern] -l project --importance [1-10]`
     - Global rule: `aim memory add "Preference description" -c [decision|syntax|pattern] -l global`
   - Create documentation if needed:
     - `aim doc create "Title" -d "Summary description" -f [folder]`
4. **Sync**:
   - Run `aim sync` after modifying config or adding custom rules to make sure all guidelines are updated.

---

## Expected Output

| Output | Command / Action |
|--------|------------------|
| Project Memory | Added memory statement in local `memories.json` via `aim memory add ... -l project` |
| Global Memory | Added memory statement in global `~/.aim/memories.json` via `aim memory add ... -l global` |
| Document | Markdown file in `.ai-context/docs/` via `aim doc create ...` |

---

## Usage

```bash
/aim-extract
```
