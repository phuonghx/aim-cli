---
name: brainstorming
description: A clarify-before-building protocol that turns vague or complex requests into well-scoped work. It defines a questioning gate that pauses implementation to ask decision-focused questions with explicit trade-offs and sensible defaults, then keeps the user informed through progress status boards, plain-language error handling, and structured completion messages. Reach for it before starting any new feature, when requirements are fuzzy, or when a change request needs its scope confirmed.
---

# Pre-Build Questioning & Communication

> Treat this as a checkpoint you must pass through before writing code for anything complex, underspecified, or new.

Two responsibilities live here:
1. **Ask first.** Surface the decisions that shape an implementation before committing to one.
2. **Stay legible.** Report progress, failures, and outcomes in a way the user can act on.

---

## 🛑 The Questioning Gate

### What flips the gate on

| Incoming request | Required move |
|------------------|---------------|
| "Build / create / make X" with thin detail | 🛑 Pose ~3 questions first |
| A sizeable feature or architectural choice | 🛑 Pin down direction before coding |
| "Change / update / tweak X" | 🛑 Lock the scope before touching it |
| Fuzzy or open-ended ask | 🛑 Probe purpose, audience, limits |

### Step 0 — Consult memory first

Before generating any questions, look for accumulated context so you don't re-ask what's already settled:

```
CHECK: Is .aim-agents/memory/MEMORY.md present?
  ├─ Found → Read its index, quietly reuse relevant prior decisions,
  │           and drop any question the memory already answers.
  └─ Absent → Run the full gate below as normal.
```

### The gate, step by step

1. **HALT** — resist the urge to start coding.
2. **RECALL** — scan `.aim-agents/memory/` for anything already decided on this topic.
3. **PROBE** — raise at least three questions (omitting ones memory has covered):
   - 🎯 **Purpose** — which problem does this solve?
   - 👥 **Audience** — who actually uses it?
   - 📦 **Scope** — what's essential versus optional?
4. **PAUSE** — wait for the reply before moving on.
5. **PERSIST** — once the direction is clear, record the calls made with `/remember [decision]`.

This gate is the backbone of the `/brainstorm` workflow.

---

## 🧠 Building Questions on the Fly

**⛔ Canned question lists are off-limits.** Every question is generated from the actual request. The full method lives in `dynamic-questioning.md`; the essentials:

| Guiding idea | What it means in practice |
|--------------|---------------------------|
| **Questions expose consequences** | A question earns its place only by tying to a real architectural fork |
| **Frame before content** | First classify the work — greenfield, addition, refactor, or debug |
| **Fewest questions that matter** | Keep a question only if it rules out an implementation path |
| **Ask, don't presume** | Offer the options and their trade-offs instead of guessing |

### How a question set comes together

```
1. Read the request  → name the domain, the features, the scale signals
2. Spot the forks    → which choices block progress vs. which can wait
3. Rank the asks     → P0 blocking  >  P1 high-leverage  >  P2 optional
4. Dress each one     → state the choice, the stakes, the options, the default
```

### Required shape for every question

```markdown
### [PRIORITY] **[THE DECISION]**

**Question:** [a sharp, answerable question]

**Why it matters:**
- [the architectural consequence it triggers]
- [what it moves: cost / effort / timeline / scale]

**Options:**
| Option | Upside | Downside | Fits when |
|--------|--------|----------|-----------|
| A | [+] | [-] | [scenario] |

**Default if silent:** [the fallback + a one-line reason]
```

Reach for `dynamic-questioning.md` when you need the per-domain question banks and the generation algorithm.

---

## 📊 Reporting Progress

**Why it matters:** visible, actionable status is what earns trust during a long-running task.

Keep a running board:

| Agent | State | Working on | Done |
|-------|-------|------------|------|
| [name] | ✅ 🔄 ⏳ ❌ ⚠️ | [what it's doing] | [% or count] |

Legend:

| Mark | Reads as | When to use |
|------|----------|-------------|
| ✅ | Done | Finished cleanly |
| 🔄 | Active | Currently in flight |
| ⏳ | Held | Stuck on a dependency |
| ❌ | Failed | Broke, needs a look |
| ⚠️ | Caution | A concern, but not a blocker |

---

## ⚠️ When Things Break

**Why it matters:** a failure is a prompt for clear communication, not a dead end.

Walk every error through the same arc:

```
1. Name it        → say plainly that something failed
2. Translate it   → explain the cause in human terms
3. Offer ways out → give concrete fixes, each with its trade-off
4. Hand it back   → let the user pick or supply another route
```

Common cases and how to meet them:

| Situation | How to respond |
|-----------|----------------|
| **Port already in use** | Suggest a free port or offer to stop the squatter |
| **Package not installed** | Install it, or ask first if that's wiser |
| **Build won't compile** | Surface the exact error and a proposed fix |
| **Message is cryptic** | Request specifics — console output, a screenshot, repro steps |

---

## ✅ Wrapping Up a Task

**Why it matters:** a clean finish confirms the win and points the way forward.

Close out in this order:

```
1. A short "it worked" note
2. A concrete recap of what changed
3. A way to check or test it yourself
4. A nudge toward the sensible next step
```

---

## How to Communicate

| Habit | What it looks like |
|-------|--------------------|
| **Brief** | Skip filler, land the point |
| **Scannable** | Lean on icons (✅ 🔄 ⏳ ❌) so status reads at a glance |
| **Concrete** | "~2 minutes," never "give it a moment" |
| **Optioned** | When blocked, lay out more than one road |
| **Forward-looking** | Always close with a suggested next move |

---

## Habits to Avoid

| Trap | Cost |
|------|------|
| Coding before you understand the ask | Effort sunk into the wrong problem |
| Inventing requirements instead of asking | Output nobody wanted |
| Gold-plating version one | Value arrives late |
| Brushing past stated constraints | A solution that can't be used |
| Hedging with "I think…" | Doubt that a question would resolve |

---
