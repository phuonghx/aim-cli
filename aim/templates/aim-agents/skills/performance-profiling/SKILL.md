---
name: performance-profiling
description: A measurement-first approach to finding and fixing performance problems in web apps, covering Core Web Vitals targets, a baseline-isolate-fix-verify loop, bundle and runtime/memory analysis, and prioritized quick wins. Use it when diagnosing slow loads or interactions, running Lighthouse audits, inspecting bundle size, or improving LCP, INP, and CLS.
---

# Performance Profiling

> Measure, then analyze, then change -- in that order. Optimizing on a hunch wastes effort.

## Automation

| Script | What it does | How to run |
|--------|--------------|------------|
| `scripts/lighthouse_audit.py` | Runs a Lighthouse audit and extracts scores | `python scripts/lighthouse_audit.py https://example.com` |

---

## Core Web Vitals

### What "good" looks like

| Metric | Good | Poor | What it captures |
|--------|------|------|------------------|
| **LCP** | under 2.5s | over 4.0s | How fast the main content paints |
| **INP** | under 200ms | over 500ms | How responsive interactions feel |
| **CLS** | under 0.1 | over 0.25 | How much the layout jumps around |

### Where to measure each stage

- **While developing** -- local Lighthouse runs.
- **In CI** -- Lighthouse CI to catch regressions before merge.
- **In production** -- real-user monitoring (RUM), because lab numbers miss field reality.

---

## The profiling loop

1. **Baseline** -- record where things stand today.
2. **Isolate** -- find the single biggest bottleneck.
3. **Fix** -- make one focused change aimed at it.
4. **Verify** -- re-measure and confirm the change actually helped.

### Matching the tool to the problem

- Whole-page load -> Lighthouse
- Shipping too much JavaScript -> a bundle analyzer
- Sluggish runtime behavior -> the Performance panel in DevTools
- Climbing memory -> the Memory panel
- Slow requests -> the Network panel

---

## Reading the bundle

### Red flags
- A heavy dependency sitting near the top of the bundle.
- The same code duplicated across multiple chunks.
- Large stretches of code the page never executes (low coverage).
- One giant chunk with no splitting.

### Corresponding moves
- Heavy library -> import only the pieces you use.
- Duplicate dependency -> dedupe and align versions.
- Route bundled into the entry point -> split it out.
- Dead exports -> rely on tree-shaking, or delete them.

---

## Runtime and memory

### Performance panel cues
- Long tasks over ~50ms block the main thread and hurt responsiveness.
- A flood of tiny tasks often means work that could be batched.
- Heavy layout/paint activity points at a rendering bottleneck.
- Big script blocks point at expensive JavaScript.

### Memory panel cues
- A heap that only grows suggests a leak.
- Large retained objects mean something is holding references too long.
- Detached DOM nodes are elements that were removed but never released.

---

## Common bottlenecks by symptom

- **Slow first load** -> oversized JavaScript or render-blocking resources.
- **Laggy interactions** -> expensive event handlers doing too much synchronously.
- **Jank while scrolling** -> layout thrashing from interleaved reads and writes.
- **Memory creeping up** -> leaks or references that are never cleaned up.

---

## Quick wins, ranked by payoff

1. Turn on compression (gzip/brotli) -- high impact.
2. Lazy-load below-the-fold images -- high impact.
3. Code-split by route -- high impact.
4. Cache static assets aggressively -- medium impact.
5. Compress and right-size images -- medium impact.

---

## Habits to drop

- Guessing at the cause -> profile before touching anything.
- Polishing micro-details -> fix the largest issue first.
- Optimizing prematurely -> wait until there is a measured need.
- Trusting lab numbers alone -> let RUM tell you what users actually feel.

---

> The fastest code is the code that never runs. Remove work before you try to speed it up.
