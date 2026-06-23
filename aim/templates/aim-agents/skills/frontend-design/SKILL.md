---
name: frontend-design
description: A reasoning framework for web UI design decisions — components, layout, color, type, effects, and motion. Use it when composing interfaces, picking palettes or fonts, structuring page layouts, or pushing a design past generic defaults. It teaches the principles and trade-offs behind each choice rather than prescribing fixed values, and prompts asking the user when intent is unclear. Scope is web; it is not aimed at native mobile apps.
---

# Frontend Design System

> **Premise:** Nothing on the page is accidental. Space is a feature. Decisions trace back to the person using the product.
> **Working rule:** Reason it out, don't recite it. When in doubt, ask.

---

## Read Files Deliberately

One file is mandatory; the rest are a reference shelf, pulled in only when the work calls for them.

| File | Priority | Open it for |
|------|----------|-------------|
| [ux-psychology.md](ux-psychology.md) | **Read every time** | The behavioral foundation behind all of this |
| [color-system.md](color-system.md) | As needed | Palette and color decisions |
| [typography-system.md](typography-system.md) | As needed | Choosing and pairing type |
| [visual-effects.md](visual-effects.md) | As needed | Shadows, blur, gradients, glow |
| [animation-guide.md](animation-guide.md) | As needed | Interface motion |
| [motion-graphics.md](motion-graphics.md) | As needed | Lottie, GSAP, SVG, 3D, particles |
| [decision-trees.md](decision-trees.md) | As needed | Context-driven starting points |

## Audit Helpers

Run these against a project; they are tools, not reading material.

| Command | What it inspects |
|---------|------------------|
| `python scripts/ux_audit.py <project_path>` | Broad sweep across UX, color, type, motion, and a11y heuristics |
| `python scripts/accessibility_checker.py <project_path>` | Targeted a11y checks: labels, ARIA, focus, contrast hints |

---

## Resist the Reflex to Default

> When a brief is loose, the easy move is to fall back on the same handful of "tasteful" choices. Don't.

If the brief leaves it open, **ask**: a color direction (cool / warm / neutral / bolder?), a style cue (pared-back / loud / retro / futuristic / organic?), a layout hint (single column / grid / asymmetric / edge-to-edge?).

| The reflex | The problem | The better question |
|------------|-------------|---------------------|
| Bento grid for everything | The house style of every AI mockup | Does this content actually want a grid? |
| Left-text / right-image hero | Seen a thousand times | What about oversized type, or a vertical scroll story? |
| Aurora / mesh gradient backdrop | The new lazy "wow" | What's a color pairing nobody expects here? |
| Frosted glass panels | A stand-in for "premium" | Would flat, high-contrast blocks read stronger? |
| Safe fintech blue | The escape hatch once purple was off-limits | Why not black, a deep red, an acid green? |
| "Orchestrate," "empower," "seamless" | Copy that smells generated | How would an actual person phrase this? |
| Dark canvas + neon glow | The signature "AI look" | What does the *brand* genuinely call for? |
| Everything rounded | Soft by default, not by intent | Where would a hard, squared edge hit harder? |

> Each "safe" pick nudges the result closer to a template. Choose the braver option more often than feels comfortable.

---

## 1. Pin Down the Constraints First

No visual decisions until these are answered (or asked):

| Dimension | Ask | Why it steers the work |
|-----------|-----|------------------------|
| Time | How much runway? | Caps the ambition |
| Content | Real or lorem ipsum? | Decides layout flexibility |
| Brand | Existing guidelines? | May lock color and type |
| Stack | Which technologies? | Bounds what's buildable |
| Audience | Who, precisely? | Drives every aesthetic call |

**Audience cues:** Gen Z → loud, quick, mobile-native; Millennials → tidy, values-forward; Gen X → familiar, legible; Boomers → large type, strong contrast; B2B → credible, data-forward; Luxury → quiet confidence, lots of air.

---

## 2. Behavioral Foundations

The full treatment lives in [ux-psychology.md](ux-psychology.md); the shortlist:

| Law | The idea | How it shows up |
|-----|----------|-----------------|
| Hick's | More options slow the decision | Trim choices; reveal complexity gradually |
| Fitts's | Big and near is easy to hit | Scale targets to their importance |
| Miller's | Working memory holds only a few items | Group things into small clusters |
| Von Restorff | The odd one out is remembered | Let the primary action look different |
| Serial position | Ends of a list stick | Anchor key items first and last |

Emotion runs on three layers — **visceral** (the gut reaction: color, imagery, vibe), **behavioral** (the using: speed, feedback, smoothness), **reflective** (the afterthought: "this says something about me"). Earn trust with security cues where stakes are high, real proof from others, easy access to help, consistency, and honest policies.

---

## 3. Layout, Color, Type, Effects, Motion — the Essentials

Each has a dedicated reference file; the load-bearing rules to keep in mind:

- **Layout** — Lean on the golden ratio (~62/38 splits) for balance and an 8px spacing rhythm. Keep text columns to 45–75 characters; size tap targets to be hit without precision.
- **Color** — Split roughly 60 / 30 / 10 (base / support / accent). Pick by industry then emotion, decide a light or dark base, and ask if it's unspecified. → [color-system.md](color-system.md)
- **Type** — Choose a modular scale (1.25 is the safe general pick; 1.5–1.618 for display). Pair faces that are distinct enough for hierarchy yet related enough to cohere. Body ≥ 16px, line height 1.4–1.6, contrast meets WCAG. → [typography-system.md](typography-system.md)
- **Effects** — Use frosted glass, gradients, and shadows only with intent: shadows imply elevation (vertical offset, layered), gradients stay coherent (analogous or one hue), and the stock looks are clichés. → [visual-effects.md](visual-effects.md)
- **Motion** — Time it to distance, size, stakes, and mood. Ease-out to enter, ease-in to leave, ease-in-out for emphasis. Animate transform and opacity only, honor reduced-motion, test on weak hardware. → [animation-guide.md](animation-guide.md), [motion-graphics.md](motion-graphics.md)

---

## 4. Signals of a Standout Result

- **Premium:** real breathing room, quiet depth, smooth purposeful motion, tight alignment, a coherent rhythm, bespoke (not all-stock) touches.
- **Trustworthy:** security cues where they matter, genuine proof, one clear value proposition, quality imagery, a single consistent design language.
- **Emotional:** a hero that hits the intended note, a human presence, visible progress, small deliberate delights.

---

## 5. What to Avoid

- **Phoned-in:** default system fonts, mismatched stock photos, wandering spacing, clashing colors, undifferentiated walls of text, failing contrast.
- **The generated look:** the same palette every time, dark-plus-neon by reflex, purple as the automatic accent, bento grids on simple pages, mesh-gradient-plus-glow pileups, recycled layouts, never asking the user.
- **Dishonest (never):** hidden costs, fabricated urgency, inescapable actions, deceptive interfaces, guilt-tripping the exit.

---

## 6. The Loop, Condensed

```
On every design task:

1. CONSTRAINTS — time, brand, stack, audience? Unclear → ask.
2. CONTENT     — what exists, and what ranks highest?
3. DIRECTION   — what suits this context? Unclear → ask, don't default.
4. BUILD       — apply the principles; check against the anti-patterns.
5. REVIEW      — Does it serve the user? Is it different from my usual?
                 Would I put my name on it?
```

---

## Where This Fits

| Skill | When |
|-------|------|
| **frontend-design** (here) | Before building — reason through color, type, and UX |
| **[web-design-guidelines](../web-design-guidelines/SKILL.md)** | After building — audit a11y, performance, and practices |

After it's coded, run the `web-design-guidelines` skill to check accessibility, focus states, motion, and performance.

> **The throughline:** design is reasoning, not duplication. Every project earns a fresh look at its own context and people. Steer wide of the default SaaS template.
