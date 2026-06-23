---
name: systematic-debugging
description: Provides a disciplined, evidence-first method for tracking down stubborn defects, moving from reliable reproduction to isolation, then to a proven root cause, and finally to a verified fix. Suited to bugs that resist quick guesses, intermittent or environment-specific failures, and regressions where the cause is not obvious. It replaces trial-and-error edits with a sequence that confirms understanding before any change is made, so fixes address causes rather than symptoms.
---

# Systematic Debugging

Guessing is the slowest way to fix a bug. A method that forces you to reproduce, narrow,
explain, and confirm — in that order — turns a frustrating hunt into a short walk.

## Four stages, in order

Resist the urge to edit code before you reach stage four. Each stage produces evidence
that makes the next one cheaper.

### Stage 1 — Reproduce it on demand

You cannot fix what you cannot trigger. Pin down the exact path to the failure.

- Write the precise sequence: inputs, actions, environment, expected vs. actual result.
- Record how reliably it fires — every time, most of the time, occasionally, or rarely.
- A flaky repro is itself a clue: it points toward timing, ordering, or shared state.

### Stage 2 — Shrink the search space

Cut the problem down until only the culprit remains.

- When did it start? What landed around that time? (`git log`, deploy history.)
- Does it happen everywhere, or only in one environment?
- Strip the scenario down to the smallest snippet that still fails.
- Bisect: find the single smallest change that flips working to broken.

### Stage 3 — Explain the cause, with proof

Chase the *why* until you hit something that, if changed, makes the bug impossible —
not merely something that makes it disappear.

```text
Symptom  : the report endpoint returns an empty list for valid users
  why?   -> the query filters on tenant_id = NULL
  why?   -> tenant_id is never read from the request
  why?   -> the middleware that sets it runs after the handler
  why?   -> route registration order was changed in the last refactor
Root cause: middleware ordering — fix the registration, not the query
```

Each "why" must rest on observed evidence (a log line, a value, a diff), never on a hunch.

### Stage 4 — Fix, then prove the fix

A change is not a fix until you have shown the failure is gone and nothing else broke.

- Confirm the original repro no longer fails.
- Exercise the surrounding behavior to check for collateral damage.
- Add a test that would have caught this, so it cannot quietly return.
- Scan for sibling code with the same mistake.

## A checklist to keep yourself honest

```text
Before you dig in
  [ ] Failure reproduces reliably
  [ ] A minimal reproduction exists
  [ ] Expected behavior is clearly defined

While investigating
  [ ] Recent changes reviewed
  [ ] Logs and error output inspected
  [ ] Extra logging or breakpoints added where the trail goes cold
  [ ] Each conclusion backed by evidence

After the fix
  [ ] Root cause written down
  [ ] Fix verified against the original repro
  [ ] Regression test added
  [ ] Similar code paths checked
```

## Commands that usually help

```bash
git log --oneline -20          # what changed lately
git bisect start               # binary-search to the breaking commit
grep -rn "TimeoutError" src/   # find where a symptom surfaces
journalctl -u myservice -n 200 # recent service logs (systemd)
```

## Habits that waste time

- **Shotgun edits** — changing things hoping one sticks.
- **Dismissing evidence** — "that line couldn't possibly matter."
- **Conviction without proof** — "obviously it's the cache."
- **Fixing before reproducing** — patching in the dark.
- **Quitting at the symptom** — silencing the error instead of curing the cause.
