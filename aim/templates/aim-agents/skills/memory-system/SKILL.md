---
name: memory-system
description: Gives agents a durable memory that outlives a single session, storing user preferences, project conventions, and prior decisions in a slim MEMORY.md index backed by per-topic files. It lets an agent recall what was already learned instead of re-asking. Use it when the user says to remember, save, or not forget something, when a fresh session needs earlier context, or when the /remember workflow runs.
---

# Memory System

Without memory, every session starts from zero — preferences re-explained, conventions re-discovered, decisions re-litigated. This skill fixes that by keeping a small, searchable record on disk. A short index points to detailed topic files, so the agent can pull back exactly what it needs.

The trade is favorable: loading the index costs roughly a thousand tokens, while skipping the re-discovery it replaces saves several thousand.

## How It's Laid Out

```
.aim-agents/memory/
├── MEMORY.md                 ← the index — a thin set of pointers, ≤200 lines
├── user-preferences.md       ← who the user is: role, style, tooling
├── project-conventions.md    ← how this project does things
├── tech-decisions.md         ← architectural calls already made
├── feedback-history.md       ← what landed well or badly
└── <topic>.md                ← more topic files as the need arises
```

## The Index File

`MEMORY.md` is a directory, not a database. Each line is a one-glance summary that names the topic file holding the full story.

Keep it disciplined:
- Cap the whole file at **200 lines**.
- Hold each entry to about **150 characters**.
- Use the shape: `- [type] summary → topic-file.md`.
- Stick to four tags: `[user]`, `[feedback]`, `[project]`, `[reference]`.

A worked example:
```markdown
# Memory Index

## User
- [user] Works on macOS, lives in the terminal, prefers fish → user-preferences.md
- [user] Staff backend engineer, ~10 yrs in distributed systems → user-preferences.md
- [user] Writes in English; occasional German → user-preferences.md

## Project
- [project] pnpm only — never npm or yarn → project-conventions.md
- [project] React 19 with the compiler on → tech-decisions.md
- [project] Trunk-based; short-lived branches off main → project-conventions.md

## Feedback
- [feedback] Wants answers tight, no preamble → feedback-history.md
- [feedback] Finds long walkthroughs tedious → feedback-history.md
- [feedback] Reaches for tables over bullet lists → feedback-history.md

## Reference
- [reference] Staging gateway listens on 8443 → infrastructure-notes.md
- [reference] Release flow: tag, then CI promotes → project-conventions.md
```

## A Topic File

Every topic file opens with frontmatter and then holds organized prose:

```markdown
---
type: user | feedback | project | reference
created: 2026-05-02
updated: 2026-05-02
---

# User Preferences

## Environment
- OS: macOS
- Shell: fish
- Editor: Neovim
- Package manager: pnpm (never npm)

## Style
- Wants concise answers
- Prefers tables for comparisons
- Avoids long-winded explanations
```

## What Belongs In Memory

| Tag | Holds | For instance |
|-----|-------|-------------|
| user | Role, preferences, tools, how they like to communicate | "Staff engineer, terminal-first" |
| feedback | Reactions to the agent's output | "Called a reply 'too long', wanted a table" |
| project | Standards, stack choices, conventions | "pnpm only, React 19" |
| reference | Non-secret infra notes, public URLs, config facts | "Staging gateway port" |

## What Stays Out

| Keep out | Because |
|----------|---------|
| Secrets — keys, tokens, passwords, private keys | The store persists and may travel between sessions |
| Anything the code already states | Read `package.json`; don't memorize the dep list |
| Throwaway debug context | It clutters the store and ages out fast |
| Literal code snippets | Code drifts; the note goes stale |
| Paths that might move | Prefer a glob or a description |
| Whole transcripts | Memory holds distilled insight, not logs |

## The Four Operations

### Save — when the user says "remember", "save", "don't forget"

1. Decide the type: user, feedback, project, or reference.
2. See whether a fitting topic file already exists.
3. If it does, append to it.
4. If not, create one with frontmatter.
5. Add a one-line pointer to the index.
6. Acknowledge: "Saved: [summary]".

### Recall — at session start, or "what do you know about X"

1. Read `.aim-agents/memory/MEMORY.md`.
2. Scan for entries relevant to the task at hand.
3. Open the topic file behind any match.
4. Apply what you find quietly — don't recite it unless asked.

### Search — "do I have notes on X"

1. Grep `.aim-agents/memory/*.md` for the term.
2. List the hits with their file references.
3. Offer to open the full topic file on request.

### Prune — when the index passes 200 lines

1. Flag it: "The index is at X lines — worth a tidy-up."
2. Propose merging related entries.
3. Propose moving stale ones to `memory/archive/`.
4. Never delete on your own; always ask first.

## Starting A Session

Every session begins the same way:

```
Is there a .aim-agents/memory/MEMORY.md?
  yes → read it, apply what's relevant, silently
  no  → carry on; create one the first time "remember" comes up

Apply memory without reading it aloud.
  Avoid:  "I recall you use pnpm and prefer terse replies..."
  Prefer: (just use pnpm in commands, keep replies terse)

The exception: if asked "what do you remember?", recite the relevant bits.
```

## Three Artifacts, Three Jobs

| Artifact | Holds | Lives | Lives in |
|----------|-------|-------|----------|
| Memory | Knowledge across sessions | Until pruned | `.aim-agents/memory/` |
| Plan | The breakdown of a project | Until the project ships | Project root |
| Task | Progress within a session | Until the session ends | Artifact directory |

Memory is what you know. A plan is what you intend to do. A task is what you're doing right now.
