---
name: skillify
description: Turns a recurring, multi-step way of working into a packaged, reusable SKILL.md that any agent can later discover and follow. Fits when the same kind of request has come up several times, when a procedure has enough stable steps to be worth recording, or when someone explicitly asks to capture a workflow as a skill. It is meant for patterns that repeat across work, not for one-time tasks or project-specific quirks better kept in notes.
---

# Skillify

A procedure you repeat is a procedure worth recording once. The third time you walk the
same path, pave it — write it down as a skill so the path exists for everyone after you.

## Decide whether it deserves a skill

Capture it when **all** of these hold:

- The same flavor of task has shown up roughly three or more times.
- It has a recognizable shape: several steps that stay constant from run to run.
- It would still make sense in a different repository, not just this one.
- A fresh agent with no prior context could act on it.

Skip it when any of these apply:

- It is a single occurrence — just do the task.
- It is glue specific to one codebase — that belongs in project memory, not a shared skill.
- A skill already covers the ground — search the skills directory before adding a duplicate.

## How to extract one

### 1. Name the invariants

Pull the pattern apart into three buckets:

- **Trigger** — what kicks it off (a phrase, a file type, a domain).
- **Constant steps** — the parts that never change between runs.
- **Variable parts** — what differs each time, and the shape of the result.

### 2. Draft the file

Keep the frontmatter to just two keys. The `description` does the heavy lifting: it is
how the skill gets matched later, so write it in the third person and state both *what*
the skill does and *when* to reach for it (and when not to).

```markdown
---
name: kebab-case-name
description: One to a few sentences, third person, describing what the skill does and the
  situations that call for it, plus what it is not for. No first person.
---

# Skill Name

A short framing line — the principle behind the skill.

## When it applies
- Conditions that should trigger it
- Conditions that should rule it out

## Procedure
### 1. First action
Concrete, do-this instructions.

### 2. Next action
...

### N. Confirm it worked
How to tell the procedure succeeded.

## Guidance
A handful of rules worth remembering.
```

### 3. Put it where skills live

```
.aim-agents/skills/<skill-name>/SKILL.md
```

The folder name and the `name` field must match exactly, both in lowercase-hyphen form.

### 4. Review before you commit

- Frontmatter carries only `name` and `description`, both accurate.
- The description makes the triggers *and* the exclusions obvious.
- Every step is something you could actually do — no vague hand-waving.
- Nothing already in the skills directory does the same job.

## Naming that reads well

| Style | Shape | Examples |
|---|---|---|
| Action | `verb-noun` | `verify-changes`, `simplify-code` |
| Subject area | `domain-aspect` | `database-design`, `api-patterns` |
| Around a tool | `tool-patterns` | `tailwind-patterns` |

Conventions: lowercase-hyphen only, two or three words, plainly descriptive rather than
witty, and no abbreviations unless they are universally understood.

## A final pass before it ships

| Check | What "good" looks like |
|---|---|
| Not a duplicate | A search of the skills directory turns up nothing equivalent |
| Portable | Useful beyond the project it was born in |
| Complete | Has framing, applicability, a procedure, and a success check |
| Frontmatter | Exactly `name` and `description`, both correct |
| Self-contained | Readable and actionable with zero outside context |
