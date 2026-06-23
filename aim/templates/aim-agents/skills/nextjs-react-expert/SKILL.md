---
name: nextjs-react-expert
description: A performance playbook for React and Next.js covering data-fetching waterfalls, bundle weight, server rendering, re-render hygiene, paint cost, and hot-path micro-tuning, plus Next.js 16 Cache Components. Use it while authoring components, profiling slow pages, trimming JavaScript shipped to the browser, or reviewing a pull request for performance regressions.
---

# React & Next.js Performance Playbook

The fastest wins almost always come from the same two places: stop fetching data
one request at a time, and stop shipping JavaScript the user never runs. Work the
list below in roughly that order — structural fixes first, micro-optimizations last.

## How to use these notes

The detail lives in the numbered reference files, not here. Open only the file that
matches the problem in front of you. Each file is self-contained and groups a set of
concrete rules with before/after code.

## Reference index

| File | Severity | Reach for it when |
| --- | --- | --- |
| `1-async-eliminating-waterfalls.md` | Highest | Pages stall on chained `await`s; requests run in series |
| `2-bundle-bundle-size-optimization.md` | Highest | First-load JS is heavy; interactivity arrives late |
| `3-server-server-side-performance.md` | High | SSR is slow, server actions need hardening, RSC payloads bloat |
| `4-client-client-side-data-fetching.md` | Medium-high | Duplicate client requests, SWR, storage, listener sharing |
| `5-rerender-re-render-optimization.md` | Medium | Components render too often; memoization questions |
| `6-rendering-rendering-performance.md` | Medium | Long lists, hydration flashes, image and SVG cost |
| `7-js-javascript-performance.md` | Lower | Tight-loop and algorithmic clean-ups in hot code |
| `8-advanced-advanced-patterns.md` | Situational | One-time init, callback refs, effect-event hooks |
| `9-cache-components.md` | Next.js 16+ | `use cache`, `cacheLife`, `cacheTag`, PPR |

## Picking the right file fast

```
Symptom                          Start here
------------------------------   ----------------------------
Long time-to-interactive    →    Files 1 and 2
First-load bundle too big   →    File 2 (splitting, deep imports)
Server response is slow     →    File 3 (parallel RSC, streaming)
UI janks / renders too much →    File 5 (render hygiene)
Scrolling / paint is rough  →    File 6 (virtualization, layout)
Redundant client requests   →    File 4 (SWR, dedupe)
On Next.js 16 caching       →    File 9 (Cache Components)
```

## Suggested order for a full pass

1. **Structural (do first).** File 1 removes request waterfalls — each one it kills
   saves a full network round trip. File 2 cuts the bytes that delay interactivity.
2. **Server (do next).** File 3 parallelizes server work and shrinks the
   server-to-client boundary.
3. **Render layer (do after).** Files 4, 5, and 6 reduce repeated work in the
   browser once the big wins are banked.
4. **Polish (do last).** Files 7 and 8 are incremental; spend time here only where a
   profiler points you.
5. **Modern caching.** On Next.js 16+, File 9 replaces most older revalidation knobs.

## Review checklist

Must hold before shipping:

- [ ] Independent fetches run together, not in sequence
- [ ] Main bundle stays lean; heavy widgets are split out
- [ ] No whole-library imports where a deep import would do
- [ ] Data-heavy subtrees sit behind `Suspense`
- [ ] Server actions validate input and check auth internally

Worth confirming:

- [ ] Server Components used wherever interactivity isn't required
- [ ] No N+1 queries in route handlers
- [ ] Static generation applied where the data allows it
- [ ] Costly computations are memoized
- [ ] Lists past ~100 rows are virtualized or use `content-visibility`
- [ ] Images go through `next/image`

Nice to have:

- [ ] Hot loops avoid repeated property/storage reads
- [ ] Regular expressions are hoisted out of render
- [ ] Membership checks use `Set`/`Map`, not `Array.includes`

## Habits that pay off

- **Profile before you change anything.** React DevTools and the browser
  performance panel tell you where the time actually goes.
- **Fix the expensive thing first.** Waterfalls and bundle size dwarf most
  micro-optimizations.
- **Lean on the framework.** `next/image`, `next/font`, automatic `fetch`
  memoization, and `optimizePackageImports` solve common problems for free.
- **Default to the server.** Code that runs in a Server Component is code the
  browser never downloads.
- **Don't optimize on a hunch.** If a profiler can't see the problem, your users
  probably can't either.

## Mental shortcuts

- A chain of `await`s is a chain of round trips.
- Every import is a candidate for bundle bloat.
- An unnecessary re-render is wasted CPU.
- Moving work to the server removes JavaScript from the client.

## Tooling

Run a quick automated scan with the bundled auditor:

```
python scripts/react_performance_checker.py <project_path>
```

It flags likely waterfalls, barrel imports, un-split heavy components,
`useEffect` fetching, missing memoization, and raw `<img>` usage, then prints a
prioritized report. `scripts/convert_rules.py` is a maintenance helper that
rebuilds the numbered reference files from a per-rule source tree.

## Adjacent skills

| For | Use |
| --- | --- |
| API design | `@[skills/api-patterns]` |
| Database tuning | `@[skills/database-design]` |
| Test design | `@[skills/testing-patterns]` |
| UI and UX | `@[skills/frontend-design]` |
| TypeScript | `@[skills/typescript-expert]` |
| Deploy and ops | `@[skills/deployment-procedures]` |
