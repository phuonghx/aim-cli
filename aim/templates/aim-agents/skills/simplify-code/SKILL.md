---
name: simplify-code
description: Cuts away accidental complexity from working code by deleting dead branches, collapsing needless layers of indirection, un-nesting control flow, and reducing parameter lists, all while keeping observable behavior identical. Applies when a file feels over-built, more abstract than its single use justifies, or harder to follow than the problem warrants, or when someone asks to clean up, slim down, or make a piece of code simpler. It is a refactoring aid, not a place to introduce new functionality.
---

# Simplify Code

Code costs more to read than to write. Treat every extra layer, branch, and clever
trick as a debt that future readers pay interest on. Remove it unless it earns its keep.

## The one rule that governs the rest

Simplicity is not a style preference; it is the absence of structure that does not pull
its weight. Keep an abstraction only when you can name the concrete benefit it provides
right now. "We might need it later" is not a benefit you have today.

## What to hunt for

### Indirection that adds nothing

| You see | You probably want |
|---|---|
| A class that forwards every call to another object | The inner object, used directly |
| A factory that only ever builds one concrete type | A plain constructor call |
| An interface with exactly one implementer | The concrete class, interface deleted |
| A "strategy" with a single strategy | An ordinary function |
| A base class extended by one subclass | The two folded together |
| An options struct holding two fields | Two positional arguments |

### Code nothing reaches

- Imports referenced nowhere
- Branches that can never be true (confirm via tests before deleting)
- Old code left behind in comments — version control already remembers it
- Variables assigned but never read; functions called from nowhere
- Stale `TODO` notes — act on them or file a ticket, then delete
- Toggles guarding a feature that already shipped to everyone

### Pyramids of nesting

Flatten with guard clauses and pipeline-style collection methods.

```python
# Tangled: four levels before any real work happens
def notify_active(payload):
    if payload:
        if payload.get("recipients"):
            for r in payload["recipients"]:
                if r.get("subscribed"):
                    send(r)

# Flat: bail early, then express the intent in one chain
def notify_active(payload):
    recipients = (payload or {}).get("recipients") or []
    for r in recipients:
        if r.get("subscribed"):
            send(r)
```

### Functions that ask for too much

```python
# Hard to call correctly: positional soup
def register(name, email, plan, region, trial, referral, locale): ...

# One cohesive argument the caller can read at a glance
def register(signup: Signup): ...
```

### Speed tricks bought before they were needed

| You see | Default move |
|---|---|
| A bespoke cache for a few dozen entries | Drop it; profile before re-adding |
| Memoization wrapped around a trivial computation | Remove the wrapper |
| Lazy-loading a module that is tiny | Import it normally |
| A state machine modeling three states | A short `if`/`match` |

## A safe order of operations

Work in small, reversible steps and lean on the test suite between each.

1. **Measure before you cut.** Note nesting depth, argument counts, function length, and
   how many abstractions stand between a feature and the work it does.
2. **Understand the intent.** Be sure you know what the code *accomplishes* and *why* it
   was shaped this way — there may be a constraint that the shape encodes.
3. **Delete dead code first.** It is the lowest-risk change and shrinks the surface area
   for everything that follows.
4. **Un-nest, then inline.** Apply guard clauses, then fold away one-line wrappers and
   merge functions that always run together.
5. **Re-run everything.** Tests and the build must stay green; behavior must not drift.

```bash
pytest -q        # behavior unchanged?
ruff check .     # nothing newly broken?
```

## Leave it alone when

| Situation | Why the complexity stays |
|---|---|
| A genuine hot path tuned for speed | The shape is a deliberate performance trade |
| A structure a framework or library forces on you | The constraint is external |
| An architecture the team deliberately chose | Respect the decision; ask before undoing it |
| Growth is imminent and concrete | A seam being added for known, near-term work |

When unsure, surface it instead of silently rewriting: *"This layer looks heavier than
the use case needs — is there a reason to keep it, or should I collapse it?"*
