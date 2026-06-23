---
name: plan-writing
description: Turns multi-step work into a short, concrete task list where each item names a specific action and how to confirm it is done. It favors a handful of verifiable steps over sprawling outlines and tailors content to whether the work is a new build, a feature, or a fix. Use it when planning a feature, a refactor across files, or any non-trivial change, typically alongside a /plan workflow.
---

# Writing Plans

A good plan is a thinking tool, not paperwork. It exists to make the next actions obvious and to tell you when you are finished. Each plan is shaped to its task -- there is no master template to fill in.

## What makes a task good

- **Bite-sized.** A step should be completable in a couple of minutes and produce one clear result.
- **Checkable.** You should be able to say exactly how you would confirm it worked -- a command to run, output to see, a value to inspect.
- **Ordered sensibly.** Note what depends on what, run independent steps in parallel, and call out the critical path. The verification step always comes last.

## Where the file lives

Save the plan in the **project root** as `{task-slug}.md`, with the slug pulled from the task itself -- "add billing webhooks" becomes `billing-webhooks.md`. Do not bury it in `.aim-agents/`, `docs/`, or a scratch directory.

## Five habits to keep

These are habits, not boilerplate. Every plan is unique to its task.

### Keep it short

A handful of meaningful steps beats an exhaustive tree of sub-sub-tasks. List only things you will actually do, one line each. If the plan runs past a single page, it is doing too much -- cut it down or split it.

### Be concrete

Vague steps stall; specific ones move.

| Too vague | Concrete |
|-----------|----------|
| "Set up the project" | "Run `npm create vite@latest`" |
| "Add login" | "Install Lucia, add `src/lib/auth.ts` and the session middleware" |
| "Polish the UI" | "Apply spacing + dark-mode classes to `Sidebar.tsx`" |

The test: does the step have an outcome you could point at and verify?

### Let the task type drive the content

**New project:** decide the stack first, define the smallest shippable slice, sketch the file layout.

**Adding a feature:** identify which files change, list new dependencies, decide how you will confirm it works.

**Fixing a bug:** pin down the root cause, name the exact file and line to change, state the test that proves it is fixed.

### Reference only the tooling you actually touch

Do not staple every helper script onto every plan. Pick the ones that fit the work.

| Working on... | Likely scripts |
|---------------|----------------|
| Frontend / React | `ux_audit.py`, `accessibility_checker.py` |
| Backend / API | `api_validator.py`, `security_scan.py` |
| Mobile | `mobile_audit.py` |
| Database | `schema_validator.py` |
| Full-stack | whichever of the above match what you changed |

### Make verification something you can run

"Make sure it works" is not verification. Name the concrete check.

| Hand-wavy | Runnable |
|-----------|----------|
| "Verify the component" | "Start `npm run dev`, click Submit, confirm the toast appears" |
| "Test the endpoint" | "`curl localhost:3000/api/orders` returns 200 with a JSON array" |
| "Check the theme" | "Open the page, toggle dark mode, confirm contrast holds" |

## A flexible skeleton

Use this as a starting shape and bend it to fit -- skip sections you do not need.

```
# <Task name>

## Goal
One sentence: what gets built or fixed.

## Tasks
- [ ] <specific action>  ->  Verify: <how you check>
- [ ] <specific action>  ->  Verify: <how you check>
- [ ] <specific action>  ->  Verify: <how you check>

## Done when
- [ ] <the headline success condition>

## Notes
<anything worth flagging>
```

Resist adding phases and nested headings unless the work genuinely calls for them. Start minimal; layer in structure only when it earns its place.

## Quick reference

1. Open with the goal -- what is being built or fixed.
2. Cap it around ten tasks; beyond that, split into separate plans.
3. Give every task a clear "done" condition.
4. Tailor it to this project; no copy-pasted templates.
5. Tick `[x]` as you go and keep the plan current.

## When to reach for this

- Spinning up a project from nothing
- Adding a feature of any real size
- Untangling a bug that is not a one-liner
- Refactoring that touches several files
