---
name: clean-code
description: Pragmatic coding standards favoring concise, direct, well-named code over verbose tutorials, needless comments, or speculative abstraction. Covers core principles, naming, function shape, anti-patterns, pre-edit dependency checks, and a discipline for handling validation-script output. Applies to essentially all code-writing work.
---

# Pragmatic Coding Standards

The aim is working software written plainly. Be concise, be direct, and solve the actual problem — nothing more.

---

## Guiding Principles

- **One job per unit** — a function or class should do a single thing.
- **No duplication** — when logic repeats, lift it out and share it.
- **Simplest thing that works** — favor the obvious solution over the clever one.
- **Build only what's needed** — skip features no one asked for yet.
- **Leave it tidier** — every file you touch should come out a little cleaner.

---

## Naming

| Thing | Convention | Good |
|-------|------------|------|
| Variables | Say what they hold | `retryCount`, not `n` |
| Functions | Action + subject | `fetchOrder()`, not `order()` |
| Booleans | Phrase as a yes/no | `isReady`, `hasAccess`, `canDelete` |
| Constants | Upper snake case | `DEFAULT_TIMEOUT_MS` |

If a name needs a comment to be understood, the name is wrong — rename it.

---

## Functions

- **Short** — aim for 5–10 lines, treat 20 as a ceiling.
- **Focused** — one responsibility, done well.
- **Single altitude** — don't mix high-level orchestration with low-level detail in the same body.
- **Lean signatures** — zero to two parameters ideally, three at most.
- **No surprise mutations** — don't quietly alter the caller's data.

---

## Structure

- Use **guard clauses** to handle edge cases up front and return early.
- Keep nesting **shallow** — two levels deep is plenty.
- Prefer **small pieces composed together** over one sprawling block.
- Keep **related code physically close**.

---

## How to Respond While Coding

- Feature requested → write it, skip the preamble.
- Bug reported → fix it; don't narrate the fix.
- Requirement unclear → ask, rather than guessing.

---

## Anti-Patterns to Avoid

| Don't | Do instead |
|-------|-----------|
| Annotate every line | Drop comments that restate the code |
| Wrap a one-liner in a helper | Inline it |
| Build a factory for two cases | Construct them directly |
| Create `utils.ts` for a lone function | Put it where it's used |
| Open with "First we import…" | Just write the code |
| Nest four levels deep | Flatten with guard clauses |
| Sprinkle magic numbers | Name the constant |
| Write a 200-line god function | Split it by responsibility |

---

## Think Before Editing a File

Changing one file can ripple outward. Before you edit, answer:

- **Who imports this?** Those callers may break.
- **What does this import?** A signature change here can cascade.
- **Which tests exercise it?** They may need updating too.
- **Is it shared?** If so, several call sites are in play.

A quick trace:

```
Editing: OrderService.ts
  imported by → OrderController.ts, CheckoutController.ts
  signature changing? → update both call sites in this same task
```

> Edit the file and every dependent file together. Never leave a half-applied change or a dangling import behind.

---

## Self-Check Before Declaring Done

Don't call it finished until each holds:

- **Goal met** — did exactly what was asked, no more, no less.
- **All files touched** — every file the change required is updated.
- **Verified** — the change was actually run or tested.
- **Clean** — linter and type checker pass.
- **Edges covered** — no obvious case left unhandled.

If any fails, fix it first.

---

## Handling Validation Scripts

Some skills ship validation scripts. Each agent runs only the scripts that belong to its own skill — a frontend agent runs the UX and accessibility checkers, a backend agent runs the API validator, and so on. Running another skill's script is a misuse.

When you do run one, follow a strict read-then-report loop:

1. **Run it** and capture the complete output.
2. **Parse it** into errors, warnings, and passes.
3. **Summarize** for the user, for example:

```markdown
## Results: api_validator.py

Errors (2)
- routes/users.ts:40 — missing input validation
- routes/auth.ts:12 — unhandled rejection

Warnings (1)
- routes/items.ts:88 — response not typed

Passed (5)
- ... five checks green

Want me to fix the 2 errors?
```

4. **Wait** for the user to confirm before changing anything.
5. **Re-run** the script after fixing to confirm it's clean.

Two things count as failures: running a script and ignoring what it reported, and auto-fixing without first asking. Always read the output, summarize it, ask, then fix.

---

> **Bottom line:** the user wants code that runs, not a lecture about it. Let clear names and small functions carry the explanation.
