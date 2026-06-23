---
name: conventional-commits
description: Writes commit messages that follow the Conventional Commits 1.0 spec — `type(scope): subject` with an imperative subject, optional body, and breaking-change markers (`!` and `BREAKING CHANGE:`). Use when committing changes, reviewing a commit message, or wiring automated changelogs and semantic versioning. Backs AIM's `/commit` slash command and feeds changelog generation, and includes a pre-commit sanity checklist.
---

# Conventional Commits

> A structured commit history that humans skim and tools parse.

Conventional Commits 1.0 gives every commit a machine-readable prefix so
changelogs and version bumps can be generated automatically.

## Format

```
<type>[optional scope][!]: <subject>

[optional body]

[optional footer(s)]
```

Example:
```
feat(auth): add passkey login

Adds WebAuthn registration and assertion flows behind a feature flag.

Closes #142
```

## Common types

| Type | Use for | Version impact |
|---|---|---|
| `feat` | A new feature | MINOR |
| `fix` | A bug fix | PATCH |
| `docs` | Docs only | — |
| `refactor` | Code change, no behavior change | — |
| `perf` | Performance improvement | PATCH |
| `test` | Adding / fixing tests | — |
| `build` | Build system or dependencies | — |
| `ci` | CI configuration | — |
| `chore` | Maintenance, no src/test change | — |
| `revert` | Reverts a previous commit | — |
| `style` | Formatting / whitespace only | — |

- **Scope** (optional): the area touched, e.g. `fix(parser):`, `feat(api):`.
  Keep it a short noun; stay consistent across the repo.

## Subject rules

- **Imperative mood**: "add", "fix", "remove" — not "added" / "adds" / "fixing".
  (It should complete: "If applied, this commit will _add passkey login_".)
- **≤ 72 characters**, ideally ≤ 50.
- **No trailing period.** Lowercase first word (unless a proper noun).
- Describe **what/why**, not how. Put detail in the body, wrapped at ~72 cols.

## Breaking changes

Two equivalent signals — use one or both:

```
feat(api)!: drop support for v1 tokens
```
and/or a footer (always uppercase, in the footer block):
```
BREAKING CHANGE: v1 tokens are rejected; clients must migrate to v2.
```

A breaking change triggers a **MAJOR** bump regardless of type.

## Footers

- `BREAKING CHANGE: <description>`
- Issue refs: `Closes #123`, `Refs #98`
- `Co-Authored-By: Name <email>`

## Pre-commit sanity checklist

Run through this before every commit:

- [ ] **No leftover debug**: no stray `console.log`, `print`, `debugger`,
      `dd()`, commented-out blocks.
- [ ] **No unresolved markers**: no `TODO` / `FIXME` / `XXX` you intended to
      finish in this change.
- [ ] **No secrets**: no keys, tokens, passwords, `.env` values, or private
      URLs in the diff.
- [ ] **Tests pass** and lint/format/type checks are green.
- [ ] **Diff is focused**: one logical change per commit; unrelated edits split out.
- [ ] **Type & scope are accurate**; subject is imperative and ≤ 72 chars.
- [ ] **Breaking change flagged** with `!` and/or `BREAKING CHANGE:` if behavior
      or API changed incompatibly.

## How it backs AIM

- The **`/commit`** slash command reads `git status` / `git diff` / branch /
  recent log, then writes a commit message in this exact format (`feat`, `fix`,
  `docs`, `refactor`, `test`, `chore`). Pass a message as the argument to
  override the generated one.
- A consistent, typed history **feeds changelog generation**: tools group
  `feat`/`fix` under "Features"/"Bug Fixes", surface `BREAKING CHANGE:` footers,
  and derive the next semantic version (PATCH / MINOR / MAJOR) automatically.
  Junk subjects produce junk changelogs — the discipline above is what makes the
  automation work.

## Good vs. bad

| ❌ Bad | ✅ Good |
|---|---|
| `fixed bug` | `fix(parser): handle empty input lines` |
| `Update code.` | `refactor(core): extract token loader` |
| `feat: Added new login and also fixed a typo` | `feat(auth): add passkey login` *(typo → separate commit)* |
| `feat: remove v1 API` | `feat(api)!: remove v1 endpoints` + `BREAKING CHANGE:` footer |
| `WIP` | *(don't commit WIP to shared history; squash first)* |

> One logical change, one well-typed commit. Your future changelog writes itself.
