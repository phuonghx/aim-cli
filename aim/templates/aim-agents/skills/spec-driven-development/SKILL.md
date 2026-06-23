---
name: spec-driven-development
description: Drives a feature through three approved artifacts — requirements, design, then tasks — before any code is written, enforcing a left-to-right gate so design is settled before implementation. Use when starting a non-trivial feature, a multi-file change, or anything ambiguous, fuzzy, or risky. Maps the workflow onto AIM's `aim spec new`, `decompose_prd`, and task commands. Skip it for one-line fixes, typos, or fully obvious tweaks.
---

# Spec-Driven Development

> Agree on *what* and *how* before writing a single line of *code*.

Inspired by GitHub spec-kit and AWS Kiro: capture intent in three living
documents, gate each on approval, and let the spec — not memory — be the source
of truth the agent codes against.

## When to write a spec (vs. skip it)

| Write a spec | Skip it |
|---|---|
| New feature or capability | One-line / typo fix |
| Touches 3+ files or modules | Single obvious change |
| Requirements are fuzzy or contested | Behavior is fully clear |
| Cross-cutting (auth, data model, API) | Local refactor with tests already green |
| You'd struggle to write a test for it | You can already name the assertion |

> Rule of thumb: if you can't state the acceptance test in one sentence, you
> need a spec.

## The three artifacts

Each is one file. Keep them short and current; stale specs are worse than none.

1. **`requirements.md` — WHAT & WHY.** Problem statement, user stories
   (`As a <role>, I want <capability>, so that <benefit>`), and numbered
   requirements R1, R2… Each requirement carries **EARS** acceptance criteria
   (see the `ears-acceptance-criteria` skill). No solution detail here.
2. **`design.md` — HOW.** Architecture, components, data model, and the
   trade-offs / alternatives considered. Reference requirements by id (R1, R2)
   so coverage is traceable. Name the risks and open questions.
3. **`tasks.md` — STEPS.** Dependency-ordered, checkable task list derived from
   the design. Mark independent items `[P]` (parallel). Every task should map
   back to a requirement and be independently verifiable.

## The left-to-right approval gate

```
requirements.md ──approve──▶ design.md ──approve──▶ tasks.md ──approve──▶ CODE
      WHAT                       HOW                    STEPS         implement
```

- **Do not move right until the current artifact is approved.** No design
  before requirements are agreed; **no code before design is approved.**
- New information flows **left**: a discovery while coding updates `tasks.md`,
  and if it changes intent, bump `design.md` / `requirements.md` and re-confirm.
- The gate is a checkpoint, not a contract — keep each pass lightweight.

## How it maps to AIM

```bash
# 1. Scaffold the three artifacts + an umbrella task linked via --spec
aim spec new "user profile export"
# → .ai-context/docs/specs/user-profile-export/{requirements,design,tasks}.md
# → umbrella task-N (spec = @doc/.../requirements.md)
```

- Fill `requirements.md` (EARS) → `design.md` → `tasks.md`, getting approval at
  each gate.
- Expand `tasks.md` into tracked tasks two ways:
  - **MCP `decompose_prd` prompt** — feed it the spec; it returns a
    dependency-ordered list and creates tasks via `create_tasks`.
  - **Manually** — `aim task create "<title>" --depends-on <id> --ac "<criterion>"`,
    using `--depends-on` to encode the order from `tasks.md`.
- Check progress with `aim spec coverage` (how many tasks have a linked spec)
  and `aim task next` (next actionable task with deps satisfied).
- Importing an existing spec-kit folder? `aim spec import <dir>`.

## Worked example: dark-mode toggle

```bash
aim spec new "dark mode toggle"
```

**requirements.md (excerpt)**
```
### R1: Toggle theme
As a user, I want a theme toggle, so that I can read comfortably at night.
Acceptance criteria (EARS):
1. WHEN the user clicks the theme toggle THE SYSTEM SHALL switch between light
   and dark within 100ms.
2. THE SYSTEM SHALL persist the selected theme across sessions.
3. WHILE no preference is stored THE SYSTEM SHALL follow the OS color scheme.
```

**design.md (excerpt)** — `ThemeProvider` holds state; persisted to
`localStorage`; default reads `prefers-color-scheme`. Trade-off: CSS variables
over a class-per-component approach (one repaint, smaller diff).

**tasks.md → tracked tasks**
```bash
aim task create "Add ThemeProvider + context"  --ac "exposes theme + toggle()"
aim task create "Wire toggle button to context" --depends-on 41
aim task create "Persist + hydrate from localStorage" --depends-on 41
aim task create "Default to prefers-color-scheme"      --depends-on 43
```

Only after `design.md` is approved do you start task 41. Mark `[x]` in
`tasks.md` and update task status as you go.

## Anti-patterns

| ❌ Don't | ✅ Do |
|---|---|
| Jump straight to code | Pass the requirements → design gate first |
| Put implementation in `requirements.md` | Keep WHAT/WHY pure; HOW lives in design |
| Write a 5-page spec for a small change | Match spec depth to risk; skip when trivial |
| Let the spec rot after coding | Flow discoveries back left and re-confirm |
| One giant task | Decompose into ordered, verifiable tasks |

> The spec is the contract between intent and implementation. Approve left to
> right; code last.
