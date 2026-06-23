---
name: ears-acceptance-criteria
description: Writes acceptance criteria in EARS notation (Easy Approach to Requirements Syntax) so each one states a single atomic, testable behavior using the five patterns — ubiquitous, event-driven WHEN, state-driven WHILE, unwanted-behavior IF/THEN, and optional WHERE. Use when authoring a spec's requirements, defining what "done" means for a task, or turning a vague request into verifiable criteria. Includes how to attach criteria to AIM tasks via `aim task create --ac`.
---

# EARS Acceptance Criteria

> One criterion, one behavior, one test.

EARS (Easy Approach to Requirements Syntax) constrains free-text requirements
to a few keyword-driven templates. The result is unambiguous, reviewable, and
maps 1:1 to a test case.

## The five patterns

| Pattern | Keyword shape | Use for |
|---|---|---|
| **Ubiquitous** | `THE SYSTEM SHALL <response>.` | Always-true invariants |
| **Event-driven** | `WHEN <trigger> THE SYSTEM SHALL <response>.` | A reaction to an event |
| **State-driven** | `WHILE <state> THE SYSTEM SHALL <response>.` | Behavior during a state |
| **Unwanted behavior** | `IF <condition> THEN THE SYSTEM SHALL <response>.` | Errors, faults, abuse |
| **Optional feature** | `WHERE <feature included> THE SYSTEM SHALL <response>.` | Behavior gated on a feature/config |

Keywords combine. Compound: `WHILE <state> WHEN <trigger> THE SYSTEM SHALL
<response>.` Keep `SHALL` (the obligation) in every line.

## Template

```
<pattern keywords> THE SYSTEM SHALL <single observable response>
[within <measurable bound>].
```

- **Trigger / condition / state** — the precondition, in user-visible terms.
- **SHALL <response>** — exactly one behavior you can observe and assert.
- **Bound (optional)** — a number a test can check (time, count, size, %).

## One atomic, verifiable behavior per criterion

- If a line contains **"and"** joining two behaviors, split it into two.
- If you can't picture the assertion, it's too vague — rewrite it.
- Responses must be **observable** (output, state change, status code), not
  internal ("the system processes the data correctly").
- Prefer measurable bounds over adjectives ("fast", "large", "secure").

## Good vs. bad

| ❌ Bad | ✅ Good (EARS) |
|---|---|
| The system should be fast. | WHEN a user submits the form THE SYSTEM SHALL return a response within 500ms. |
| Handle invalid input gracefully. | IF the email field is malformed THEN THE SYSTEM SHALL reject the submission and show a field-level error. |
| Users can log in and see their dashboard. | WHEN valid credentials are submitted THE SYSTEM SHALL authenticate the user. *(then a second criterion for the dashboard)* |
| The app supports offline mode. | WHERE offline mode is enabled THE SYSTEM SHALL queue writes and sync them WHEN connectivity returns. |
| Keep the session secure. | WHILE a session is idle for 15 minutes THE SYSTEM SHALL log the user out. |

## Pattern picker

```
Always true, no trigger? ............... Ubiquitous (THE SYSTEM SHALL …)
Reaction to a discrete event? .......... Event-driven (WHEN …)
Only while in a mode/state? ............ State-driven (WHILE …)
Error / fault / disallowed case? ....... Unwanted behavior (IF … THEN …)
Only when a feature/flag is present? ... Optional (WHERE …)
```

## Attaching criteria to AIM tasks

Each EARS line becomes one `--ac` item (repeatable):

```bash
aim task create "Add login endpoint" \
  --ac "WHEN valid credentials are submitted THE SYSTEM SHALL return a session token." \
  --ac "IF credentials are invalid THEN THE SYSTEM SHALL respond 401 with no token." \
  --ac "WHILE 5+ failures occurred in 10 min THE SYSTEM SHALL rate-limit the account."
```

- Add one later: `aim task edit <id> --add-ac "WHEN …"`.
- Tick a criterion off (1-based index) as it's met:
  `aim task edit <id> --check-ac 2`.
- In a spec, these same lines live under each requirement in
  `requirements.md` (see the `spec-driven-development` skill); the MCP
  `create_task` / `create_tasks` tools accept them via the `ac` field.

## Checklist before you commit a criterion

- [ ] Uses an EARS keyword (`WHEN` / `WHILE` / `IF…THEN` / `WHERE` / bare SHALL).
- [ ] Exactly one behavior (no hidden "and").
- [ ] Response is observable and assertable.
- [ ] Trigger/state/condition is concrete, not vague.
- [ ] Measurable bound included where it matters.
- [ ] You could hand it to a tester and they'd write the same test.

> If a criterion can't fail a test, it isn't acceptance criteria — it's a wish.
