---
name: architecture
description: A framework for making and recording architecture decisions. Covers gathering requirements and context, weighing trade-offs, picking suitable patterns, and writing decision records (ADRs). Reach for it when deciding how to structure a system, comparing options, capturing the reasoning behind a choice, or reviewing an existing design. It is a thinking and documentation aid, not a tool for writing implementation code.
---

# Making Architecture Decisions

Three ideas anchor everything below:

- **Requirements come first.** The shape of the system follows from what it actually needs to do.
- **Trade-offs justify choices.** No option is free; name the cost before committing.
- **Decision records preserve the "why".** Future maintainers inherit the reasoning, not just the result.

---

## Read Only What the Task Needs

This skill is split across several reference files. Don't load all of them. Look at the map, decide what the current request calls for, and open just those.

| File | What it holds | Open it when |
|------|---------------|--------------|
| `context-discovery.md` | The questions to ask up front and a way to classify the project | You're at the very start of a design |
| `trade-off-analysis.md` | Templates for decision records plus a method for weighing options | You're capturing a decision in writing |
| `pattern-selection.md` | Branching guides for picking patterns and a list of traps to avoid | You're deciding which pattern fits |
| `examples.md` | Three fully worked designs (MVP, SaaS, enterprise) | You want a concrete reference to compare against |
| `patterns-reference.md` | A compact catalog of patterns side by side | You need a fast lookup or comparison |

---

## Companion Skills

Architecture touches neighboring concerns. Hand off to these where they fit:

| Skill | Reach for it when |
|-------|-------------------|
| `@[skills/database-design]` | The decision is about how to model and structure data |
| `@[skills/api-patterns]` | The focus shifts to designing the API surface |
| `@[skills/deployment-procedures]` | You're working out how the system ships and runs |

---

## The Guiding Principle

**Begin with the smallest design that works, and let complexity earn its place.**

- Default to the simple option.
- Reach for heavier patterns only after a real need shows up — not in anticipation of one.
- Layering a pattern on later is straightforward.
- Tearing one out once code depends on it is painful. Adding is cheap; removing is expensive.

---

## Check Before You Commit

Run through this list before treating an architecture as settled:

- [ ] The requirements are genuinely understood, not assumed
- [ ] Constraints (scale, team, timeline, budget) are written down
- [ ] Every meaningful decision is backed by a trade-off comparison
- [ ] A simpler alternative was considered and consciously rejected
- [ ] Significant decisions have an ADR recording the rationale
- [ ] The chosen patterns line up with what the team already knows how to operate
