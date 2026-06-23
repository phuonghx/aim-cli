---
name: coordinator-mode
description: Orchestrates many worker agents at once, breaking a request into subtasks, running independent reads in parallel, gating writes sequentially, and merging the returns into one answer. Use it when a job spans several domains and benefits from delegated workers plus deliberate synthesis, or when /coordinate or /orchestrate is requested. Not appropriate for narrow single-domain work that one agent can finish alone.
---

# Coordinator Mode

In this mode you stop acting as a builder and start acting as a director. A request arrives, you split it into pieces, hand the pieces to worker agents, and stitch their returns back together. The workers touch the code; you do the thinking, the routing, and the assembly.

Hold that boundary firmly. The moment the coordinator starts editing files directly, the value of orchestration evaporates.

## The Six Moves

A coordinated run cycles through the same six moves every time:

1. **Split** the request into worker-sized subtasks.
2. **Tag** each subtask as research, build, or check.
3. **Send** the workers out — reads concurrently, writes one at a time.
4. **Watch** for the completion signals to arrive.
5. **Merge** the returns into a single coherent result.
6. **Confirm** nothing is missing before you answer the user.

## Phases And Their Concurrency

Group the subtasks into phases. Each phase has its own rule about whether workers may overlap:

| Phase | Goal | Can overlap? | Who runs it |
|-------|------|--------------|-------------|
| Research | Read the codebase, collect facts | Yes, freely | Read-only workers |
| Synthesis | Weigh findings, pick an approach | No — this is you | The coordinator alone |
| Build | Edit files, apply changes | One writer per file group | Write-capable workers |
| Check | Run tests, lint, validate | Yes, when independent | Verification workers |

The Synthesis phase is the one people skip, and skipping it is the most common cause of bad output. Research that flows straight into building means workers act on raw facts nobody reasoned over. Always stop and think between gathering and doing.

## What May Run Together

Reads are cheap to parallelize because they collide with nothing:

- Several workers reading different parts of the tree
- A performance pass and a security pass over the same read-only code
- A linter and a test runner that share no state
- Workers crawling separate folders

Writes and dependencies force a single file:

- Two workers editing the same file — never
- A build step that needs an earlier worker's output first
- A schema migration plus the code that targets the new schema
- An API contract change plus the client that calls it

## Writing The Worker Prompt

### The one rule that matters most

Do the understanding yourself. Do not push it onto the worker.

```
Weak:   "Use what you found to fix the bug."
Weak:   "Read the file and do whatever it needs."
Weak:   "Implement it based on the research."

Strong: "In src/cache/ttl.go, the eviction check on line 88 reads
         `if age > ttl` but should be `if age >= ttl`. Right now an
         entry that hits its TTL exactly survives one extra cycle.
         Change line 88 to use `>=`."
```

Any prompt that leans on "what you found" or "based on the research" is quietly delegating the analysis. A good prompt is proof that you already did it: name the file, name the line, name the change.

### Brief like you're handing off to a peer

Imagine a sharp colleague who just sat down and knows none of the backstory. Tell them:

1. The objective and the reason behind it.
2. What you've already established or eliminated.
3. Enough surrounding context that they can make judgment calls.
4. The exact boundary — what's theirs, what belongs to another worker.
5. The shape of the return you want ("answer in under 200 words").

### Skeletons to adapt

Research worker:
```
Look into [question] within [files or folder].
Why it matters: we're attempting [goal] because [reason].
Already done: I checked [X] and saw [Y].
Return: [the specific deliverable], capped at 200 words.
```

Build worker:
```
Change [file(s)] so that [behavior].
Reason: [why the change is needed].
Today [file:line] does [X]; make it do [Y].
Stay out of: [off-limits files]. [Other worker] owns [neighboring area].
Confirm by: [how to check it worked].
```

Check worker:
```
Confirm [change] behaves correctly.
Run: [commands].
Success looks like: [observable result].
Return: pass or fail, with detail on any failure.
```

## Forking Versus Spawning Fresh

A fork carries your context forward; a fresh spawn starts clean with a named specialist.

| Situation | Pick | Reason |
|-----------|------|--------|
| Open-ended digging | Fork (no type) | Inherits context, prompt stays short |
| Several independent probes | Fork them together | Shared cache across forks |
| Domain-specific build | Spawn a specialist | Clean, focused starting state |
| A sanity check on your own work | Spawn | An untainted second view |

Three habits when forking:

1. **Leave it alone while it runs.** A completion signal will come. Cracking open the live transcript just floods you with tool chatter.
2. **Never guess its output.** Until the signal lands you know nothing; if asked early, say it's still running rather than inventing a result.
3. **Write a directive, not a dossier.** Forks already have your context, so tell them what to do, not what the situation is.

## What Goes Wrong, And The Fix

| Misstep | Cost | Correction |
|---------|------|------------|
| "Read it and fix it" | Workers guess and guess wrong | Hand over paths, lines, exact edits |
| Skipping research | Building blind, then redoing it | Always probe first, even briefly |
| Ten workers in one shot | Synthesis drowns, returns thin out | 2–5 per round, merge, then more |
| Inventing a worker's result | The user gets fiction | Wait for the signal; "still running" is fine |
| Coordinator edits code itself | Throws away the whole point | Route every edit to a worker |

## How To Synthesize

Once the workers return, write up the merge — don't paste their raw text:

```markdown
## Synthesis

### Request
[the original ask]

### Workers
| Worker | Phase | State | Headline |
|--------|-------|-------|----------|
| w1 | Research | done | Found X in Y |
| w2 | Research | done | Spotted pattern Z |

### Combined read
[your reasoning across all returns — your words, not theirs]

### Choice and why
[what you decided, weighing every return]

### Plan
1. [concrete edit with path]
2. [concrete edit with path]

### Open risk
[anything flagged but unresolved]
```

## Continue Or Start Over

| Situation | Do this |
|-----------|---------|
| Worker done, more on the same thread | Continue (message that worker) |
| Worker done, unrelated next step | Spawn a new specialist |
| Worker stumbled, same context still good | Continue with corrected steps |
| Worker stumbled, approach was wrong | Spawn fresh |

## Habits Worth Keeping

1. Open with 2–3 workers; add more only after a merge says you need them.
2. Research precedes building, every time, even when the task looks trivial.
3. Your summary should sharpen the findings, not echo them.
4. Verification workers stay skeptical — they don't take a builder's word.
5. Track each worker's state: pending, done, or failed.
6. Park shared artifacts in one agreed-on directory so workers can reach them.
