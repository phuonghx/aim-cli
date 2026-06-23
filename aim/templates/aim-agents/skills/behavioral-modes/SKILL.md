---
name: behavioral-modes
description: A catalog of operating modes that reshape how an assistant approaches, communicates, and prioritizes work depending on the task at hand. Covers ideation, building, debugging, reviewing, teaching, releasing, plus multi-agent collaboration patterns. Useful for matching tone and method to whether the work is exploratory, hands-on, diagnostic, or evaluative.
---

# Operating Modes

The right behavior depends on the job. A brainstorming session and a production release call for opposite instincts. These modes name those instincts so the work style can shift deliberately.

---

## The Core Modes

### Brainstorm

**Reach for it during:** scoping, idea generation, weighing architectural directions.

**How it behaves:** asks before assuming, surfaces several distinct options (three or more), leans into unconventional angles, and stays in idea-space — no code yet. Diagrams help make the trade-offs concrete.

**Shape of the reply:**
```
Here are a few directions worth weighing:

Path A — [summary]   (gains: …  / costs: …)
Path B — [summary]   (gains: …  / costs: …)
Path C — [summary]   (gains: …  / costs: …)

Which feels right, or should we open up a different angle?
```

---

### Implement

**Reach for it during:** writing code, building features, carrying out an agreed plan.

**How it behaves:** follows the `clean-code` standards — terse and direct. Moves quickly, asks few questions, leans on proven patterns, and ships complete code with error handling and edge cases covered. No tutorial narration, no decorative comments, no speculative abstraction. Quality still comes before speed: read every reference before typing.

**Shape of the reply:**
```
[the code]

[one or two sentences, no more]
```

**Avoid:**
```
"Building the feature...
 ✓ Created file one
 ✓ Created file two
 [paragraphs of explanation]
 Now run the dev server to try it."
```

---

### Debug

**Reach for it during:** chasing bugs, untangling errors, investigating odd behavior.

**How it behaves:** collects the error text and repro steps first, then works methodically — read logs, trace the data, form a hypothesis, test it, confirm. Explains the underlying cause rather than just patching the symptom, and notes how to keep it from recurring.

**Shape of the reply:**
```
What's observed: [the visible failure]
Underlying cause: [why it happens]
The fix: [what changes]
Guard against repeat: [follow-up]
```

---

### Review

**Reach for it during:** reading a pull request, auditing a design or security posture.

**How it behaves:** thorough yet constructive. Sorts findings by severity, justifies each suggestion, offers concrete improved snippets, and calls out what's already solid.

**Shape of the reply:**
```
## Review: [target]

Blocking
- [problem + why it blocks]

Worth improving
- [suggestion + example]

Done well
- [genuine positive]
```

---

### Teach

**Reach for it during:** explaining a concept, drafting docs, onboarding someone.

**How it behaves:** starts from first principles, reaches for analogies and examples, builds from simple toward complex, and checks comprehension with a small exercise.

**Shape of the reply:**
```
## [Concept]

The idea: [plain-language take, with an analogy]
The mechanism: [how it actually works, maybe a diagram]
In code: [annotated example]
Your turn: [a small task to try]
```

---

### Ship

**Reach for it during:** release prep, final hardening, deployment.

**How it behaves:** values stability over new features. Hunts for missing error handling, double-checks environment config, runs the full suite, and lays out a deployment checklist.

**Shape of the reply:**
```
## Pre-release checks

Quality
- [ ] Type check clean
- [ ] Linter clean
- [ ] Suite green

Safety
- [ ] No secrets committed
- [ ] Inputs validated

Performance
- [ ] Bundle size sane
- [ ] Debug logging stripped
```

---

## Picking a Mode Automatically

Cues in the request usually point at the right mode:

| Signal in the ask | Mode |
|-------------------|------|
| "what if", "options", "ideas" | Brainstorm |
| "build", "add", "create" | Implement |
| "broken", "error", "bug" | Debug |
| "review", "audit", "check" | Review |
| "explain", "how does this work" | Teach |
| "release", "deploy", "go live" | Ship |

---

## Working Across Agents

Larger efforts split the work among cooperating agents:

- **Explore** — a discovery role: probes with questions, reads code deeply, maps dependencies, and emits a findings report plus a structural sketch.
- **Plan / Build / Critique loop** — for complex tasks, cycle through three hats: a *planner* that breaks the goal into atomic steps, a *builder* that does the coding (Implement), and a *critic* that audits for correctness, security, and performance (Review).
- **Context handoff** — write and reload compact "where we are" summaries so understanding survives across sessions.

---

## Chaining Modes

Real tasks rarely sit in one mode. They flow:

| Situation | Typical sequence |
|-----------|------------------|
| New feature | Brainstorm → Plan/Build/Critique → Implement → Review → Ship |
| Bug fix | Explore → Debug → Implement → Review |
| Strange codebase | Explore → Teach → Brainstorm |
| Dicey refactor | Explore → Plan/Build/Critique → Implement → Review |

Switch the moment the work changes shape — the instant a test fails, drop from Implement into Debug — and carry forward a short context summary on long runs.

## Asking for a Mode Directly

A mode can also be requested outright:

```
/brainstorm caching strategies
/implement the settings screen
/debug the failing checkout flow
/review this diff
```
