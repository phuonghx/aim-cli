---
name: lint-and-validate
description: A discipline for running linters, formatters, type checkers, and security audits after every edit so code stays syntactically sound and consistent with project standards. Covers the Node/TypeScript and Python toolchains plus a tight edit-check-fix loop. Use it after changing code, before marking work done, or whenever linting, formatting, type, or static-analysis questions come up.
---

# Lint and Validate

> Treat validation as part of writing the code, not a separate chore. Code is not "done" while a checker still complains.

## Toolchain by ecosystem

### Node.js / TypeScript
1. **Style + autofix** -- `npm run lint`, or `npx eslint "<path>" --fix` when there is no script
2. **Type safety** -- `npx tsc --noEmit`
3. **Dependency audit** -- `npm audit --audit-level=high`

### Python
1. **Lint + autofix** -- `ruff check "<path>" --fix` (fast, covers most rules)
2. **Static security** -- `bandit -r "<path>" -ll`
3. **Type safety** -- `mypy "<path>"`

## The validation loop

1. Make the edit.
2. Run the relevant checks, e.g. `npm run lint && npx tsc --noEmit`.
3. Read the output carefully -- look at the final summary, not just the exit code.
4. Fix what it reports and re-run. Repeat until clean. Reporting code as finished while the summary shows failures is not acceptable.

## When a step fails

- **Linter complains** -- resolve the style or syntax problem right away; many issues autofix.
- **Type check complains** -- reconcile the type mismatch before moving on.
- **No tooling configured** -- look for `.eslintrc`, `tsconfig.json`, or `pyproject.toml` in the project root and propose adding the missing config rather than skipping the check.

---
**Non-negotiable:** nothing gets committed or called complete until these checks pass.

---

## Scripts

| Script | What it does | How to run |
|--------|--------------|------------|
| `scripts/lint_runner.py` | Detects the stack and runs its linters/type checks | `python scripts/lint_runner.py <project_path>` |
| `scripts/type_coverage.py` | Estimates type-annotation coverage | `python scripts/type_coverage.py <project_path>` |
