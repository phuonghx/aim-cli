---
name: context-compression
description: A technique for keeping long working sessions sharp by condensing finished work while keeping the decisions that still matter. It covers when to compress, three levels of compression from single tool outputs to full checkpoints, and a step-by-step protocol. Useful once a session stretches long, turns get repetitive, or earlier context starts slipping.
---

# Context Compression for Long Sessions

Over a long session the context window fills with finished work, and the assistant starts repeating itself or losing the thread. The fix is to summarize what's done — preserving the decisions, discarding the transcript — so attention stays on what's still active.

## Overview

Extended sessions (roughly 30+ turns) degrade: earlier work fades, suggestions repeat, decisions get forgotten. Compressing completed phases as you go keeps the window focused on live work.

**Payoff:** reclaiming on the order of 5,000–15,000 tokens in a long session by swapping bulky tool output for tight semantic summaries.

---

## When to Compress

| Signal | Response |
|--------|----------|
| Past ~20 turns | Consider compressing proactively |
| Suggestions start repeating | Window is saturated — compress now |
| User notes "we covered this already" | Compress right away |
| Moving into a new phase | Summarize the phase you're leaving |
| A tool dumps 500+ lines | Compact that output on the spot |

---

## Three Levels

### Level 1 — Compact a Tool Output

Shrink a single noisy result down to its meaning.

```
Before — raw search dump (~200 lines, ~4,000 tokens):
src/auth/jwt.ts:15: import { verify } from 'jsonwebtoken'
src/auth/jwt.ts:23: export function validateToken(token: string) {
src/auth/jwt.ts:24:   try {
... (and so on)

After — the gist (~5 lines, ~100 tokens):
Searched "jwt": 8 files, 42 hits. Core: src/auth/jwt.ts (JWT logic),
src/middleware/auth.ts (guard), src/api/login.ts (issues tokens).
Validation lives at jwt.ts:23-40, error handling at 42-55, secret read from env at line 8.
```

### Level 2 — Summarize a Phase

Collapse a whole stretch of exploration into its conclusions.

```
Before — full research trail (~3,000 tokens):
[turn 1] read package.json
[turn 2] read src/index.ts
[turn 3] searched "auth"
... (a dozen more exploration turns)

After — phase summary (~200 tokens):
## Research done
- Stack: Next.js 15 app, JWT-based auth
- Auth code: 8 files across src/auth, src/middleware, src/api
- Flow: login -> mint JWT -> httpOnly cookie -> verified in middleware
- Defect: src/auth/jwt.ts:45 — expiry test uses `<` where it needs `<=`
- Plan: fix the operator, add a boundary test
```

### Level 3 — Checkpoint the Session

For long-running work, write a complete status snapshot.

```markdown
## Checkpoint — turn 35

Done
- [x] Mapped the auth system (8 files, JWT flow)
- [x] Fixed expiry bug at jwt.ts:45
- [x] Added boundary test in jwt.test.ts
- [x] Full suite green (42 tests)

Open
- [ ] Update the API docs
- [ ] Re-read the surrounding middleware

Decisions
1. Stay on httpOnly cookies, not localStorage
2. Use `<=` so an exact-moment expiry still counts
3. Allow a 5-minute clock-skew grace window

Touched
- src/auth/jwt.ts (line 45 operator)
- tests/auth/jwt.test.ts (+3 boundary tests)
```

---

## The Protocol

### Step 1 — Spot finished phases

```
Which work is settled and won't be reopened?
- research already distilled
- changes already verified
- decisions already made and applied
```

### Step 2 — Pull out what matters

```
Keep:
- decisions, and the reasoning behind them
- file paths and line numbers of edits
- findings that still steer the work
- error text and test outcomes (condensed)

Drop:
- step-by-step tool calls
- full contents of files that were read
- dead-end explorations
- long stack traces (keep the message)
```

### Step 3 — Write it down

```
Use the phase-summary shape above.
Budget ~100-300 tokens per finished phase.
Include enough to resume cold, without re-reading.
```

---

## Practices

1. **Compress phases, keep facts** — individual decisions stay; the blow-by-blow goes.
2. **Favor the "why"** — the reason behind a choice outlives the exact commands.
3. **Announce it** — tell the user "I'm condensing the finished research phase to keep us focused"; don't do it silently.
4. **Hold onto references** — paths and line numbers always survive the cut.
5. **Compress at the seams** — phase transitions (research → implementation) are the natural moment.
