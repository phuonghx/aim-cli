---
name: context-engineering
description: Manages what enters an agent's context window — instructions, retrieved knowledge, tools, memory, and history — under a token budget. Use when building agents or RAG features, when long context degrades answer quality, when retrieval pulls in noise, or when deciding what to preload vs fetch on demand. Optimizes the signal-to-noise ratio of every token so the model attends to what matters.
---

# Context Engineering

> The context window is a budget, not a bucket. Every token must earn its place.

## Why it matters

Models do not get smarter with more context — past a point they get worse. Irrelevant, stale, or redundant tokens cause **context rot** (degraded recall) and **distraction** (the model fixates on noise). Curate aggressively: the goal is the *smallest* set of high-signal tokens that lets the model succeed.

## Context types

| Type | What it is | Sourcing strategy |
|---|---|---|
| Instructions | System prompt, role, rules, output format | Preload (stable, always needed) |
| Knowledge | Retrieved docs, facts, code | Just-in-time (fetch per query) |
| Tools | Tool/function schemas available | Scope to the task; don't expose all |
| Memory | Persistent cross-session facts | Ranked recall (importance + recency) |
| History | Prior turns in this session | Compress as it grows |

## Token budgeting

- Set an explicit budget per section before assembling context (e.g. instructions 10%, retrieval 50%, history 25%, headroom 15%).
- Leave headroom for the model's output — a full window leaves no room to answer.
- Measure, don't guess: count tokens of each section; log the breakdown.
- When over budget, cut the lowest-signal section first (usually old history or low-ranked retrieval), never the instructions.

## Retrieval and ranking

Getting the *right* knowledge in matters more than getting *more* in.

- Retrieve a candidate pool, then **rerank** and keep only the top few — precision over recall.
- Deduplicate near-identical chunks before they reach the window.
- Filter by metadata (recency, source, permissions) before semantic ranking.
- Attach provenance (source id/URL) to each chunk so the model can cite and you can debug.
- Tune chunk size to the content: too small loses context, too large wastes budget. Test it.

## Just-in-time vs preloading

| Preload (put it in now) | Just-in-time (fetch when needed) |
|---|---|
| Small, stable, always-relevant | Large, conditional, or rarely needed |
| System rules, output schema, key conventions | Document bodies, search results, file contents |
| Core tool schemas | Niche tools gated behind a router |

Default to just-in-time. Preloading large content "to be safe" is the most common cause of context bloat. Give the agent the *ability to fetch* (a search tool, file reader) rather than the *fetched payload*.

## Memory feeding working context

Persistent project memory is the long-term store; working context is the active window. A memory store ranked by **importance and recency** decides what surfaces:

- Each memory carries an importance weight and a last-used timestamp.
- On a new task, retrieve memories by relevance, then rank by `importance × recency` and inject only the top entries — not the whole store.
- Promote facts that prove useful (bump importance/recency); let stale, unused facts decay out of recall.
- Keep a lightweight index in context and fetch full memory files just-in-time.
- This is exactly the recall pattern the `memory-system` skill implements — load its ranked index, not every topic file.

## Compression and summarization

As history grows, replace verbose spans with dense summaries that preserve decisions and references.

- Summarize *completed* phases; keep the active task verbatim.
- Preserve the "why" (decisions, constraints) and concrete handles (file paths, ids); drop step-by-step tool chatter.
- Compress large tool outputs at the source: a 300-line grep becomes a 5-line finding.
- Checkpoint at phase transitions (research → implementation) — a natural compaction point.
- See the `context-compression` skill for the phase-summary and checkpoint formats.

## Avoiding context rot and distraction

| Problem | Cause | Fix |
|---|---|---|
| Model ignores buried instruction | Lost in the middle of long context | Put critical rules at start AND end |
| Answers degrade as context grows | Context rot from accumulated noise | Compress history; prune low-signal tokens |
| Model fixates on irrelevant detail | Distraction from off-topic chunks | Rerank harder; drop low-score retrieval |
| Stale fact used as current | Outdated memory/cache in window | Recency-filter; expire and refresh |
| Tool misuse / wrong tool | Too many tools exposed at once | Scope tools to the task; route to a subset |
| Contradictory guidance | Conflicting sources in context | Deduplicate; establish source precedence |

## Structuring long context

- Wrap each section in named tags or headers (`<instructions>`, `<retrieved_docs>`, `<history>`) so the model can tell them apart.
- Order by attention: most important first and last; bury nothing critical in the middle.
- Label retrieved chunks with source and date inline.
- Keep one consistent structure across requests — stable layout improves reliability and caching.

## Assembly loop

```
1. Start with the budget and the fixed instructions.
2. Pull relevant memory → rank by importance × recency → inject top-N.
3. Retrieve knowledge → rerank → dedupe → keep top-K within budget.
4. Add compressed history (summaries for old phases, verbatim for active).
5. Expose only the tools this task needs.
6. Check token count vs budget; if over, trim lowest-signal section.
7. Verify critical rules sit at the edges, not the middle.
```

## Checklist

- [ ] Explicit token budget per section, with output headroom.
- [ ] Retrieval reranked and deduplicated, not raw top-k.
- [ ] Just-in-time fetching preferred over bulk preloading.
- [ ] Memory injected by importance × recency ranking, not wholesale.
- [ ] Old history compressed; active task kept verbatim.
- [ ] Tools scoped to the task.
- [ ] Sections delimited; critical rules at start and end.
