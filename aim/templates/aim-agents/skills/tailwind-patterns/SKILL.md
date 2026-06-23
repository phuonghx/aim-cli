---
name: tailwind-patterns
description: Captures the way Tailwind CSS v4 is meant to be used, where configuration lives in CSS through the @theme directive, the Rust-based engine compiles utilities, and tokens surface as CSS custom properties. Useful when setting up or migrating a v4 project, defining a design-token system, reaching for container queries and other native features, or choosing between viewport and component-level responsiveness. Covers theming, dark mode, layout, color, type, motion, and the anti-patterns to avoid.
---

# Tailwind CSS v4 Patterns

Version 4 moves Tailwind's center of gravity into CSS itself. Configuration, tokens, and
modern features all live in your stylesheet, and the JavaScript config file becomes optional.

## What is different in v4

| Topic | v3 | v4 |
|---|---|---|
| Where config lives | `tailwind.config.js` | `@theme` block in CSS |
| Compiler | PostCSS-based | A faster, Rust-based engine |
| On-demand generation | JIT mode you enabled | Always on, built in |
| Extending the system | JS plugins | Native CSS features |
| Tokens | Internal | Emitted as `--*` custom properties |

The mental shift: describe your design system *in CSS*, lean on real CSS variables, and
prefer the platform's own capabilities (nesting, container queries) over plugins.

## Theme tokens in CSS

Declare your scales once inside `@theme`; Tailwind turns each into both a utility and a
custom property you can read anywhere.

```css
@theme {
  /* semantic colors, expressed in OKLCH for even perceptual steps */
  --color-brand:        oklch(0.72 0.16 255);
  --color-canvas:       oklch(0.99 0 0);
  --color-canvas-night: oklch(0.16 0 0);

  /* a deliberate spacing rhythm */
  --spacing-tight: 0.25rem;
  --spacing-snug: 0.5rem;
  --spacing-base: 1rem;
  --spacing-loose: 2rem;

  /* type families */
  --font-body: "Inter", system-ui, sans-serif;
  --font-code: "JetBrains Mono", ui-monospace, monospace;
}
```

Add tokens alongside the defaults when you want to *grow* the system; replace a whole
scale only when you intend to *retire* Tailwind's defaults for it. Reach for semantic
names (`brand`, `canvas`) so intent survives a redesign.

## Two kinds of responsiveness

Viewport breakpoints answer the question "how wide is the screen?" Container queries
answer "how wide is *this component's* box?" Reusable components should usually depend on
the latter, so they adapt wherever they are dropped.

| Tool | Reacts to | Best for |
|---|---|---|
| `sm:` `md:` `lg:` | The viewport | Page-level layout decisions |
| `@container` + `@sm:` `@md:` | The nearest sized ancestor | Self-contained, reusable components |

Mark a parent with `@container`, then size its children with the `@`-prefixed variants;
name a container (`@container/card`) when nesting makes targeting ambiguous.

Default breakpoint stops: `sm` 640px, `md` 768px, `lg` 1024px, `xl` 1280px, `2xl` 1536px.
Style the smallest screen with no prefix, then layer wider overrides on top —
`w-full md:w-1/2 lg:w-1/3`.

## Dark mode

Pick the strategy that matches how much control the user gets.

| Strategy | How it triggers | Reach for it when |
|---|---|---|
| Class | a `.dark` ancestor toggles it | You ship a manual theme switch |
| Media | follows the OS setting | The OS decides, no in-app toggle |
| Custom selector | any selector you choose | Theming logic is non-standard |

Pair each surface across both modes: `bg-white dark:bg-zinc-900`,
`text-zinc-900 dark:text-zinc-100`, `border-zinc-200 dark:border-zinc-700`.

## Layout recipes

Flexbox for one-dimensional arrangements:

| Goal | Utilities |
|---|---|
| Center on both axes | `flex items-center justify-center` |
| Stack vertically | `flex flex-col gap-4` |
| Row with spacing | `flex gap-4` |
| Push ends apart | `flex justify-between items-center` |
| Wrapping row | `flex flex-wrap gap-4` |

Grid for two-dimensional structure:

| Goal | Utilities |
|---|---|
| Fluid card wall | `grid grid-cols-[repeat(auto-fit,minmax(16rem,1fr))]` |
| Editorial / bento layout | `grid grid-cols-3 grid-rows-2` plus span utilities |
| Content + rail | `grid grid-cols-[1fr_auto]` |

Asymmetric, bento-style grids tend to read as more intentional than an evenly split
three-column row.

## Color architecture

Layer your tokens so each level has one job:

| Layer | Example | Holds |
|---|---|---|
| Primitive | `--blue-500` | Raw, named color values |
| Semantic | `--color-brand` | Meaning, decoupled from the hex |
| Component | `--btn-bg` | One component's local choice |

OKLCH is the preferred space — its lightness steps look uniform to the eye, which makes
generated shades and accessible contrast far easier to reason about than HSL or RGB.

## Typography

Stack a preferred face ahead of robust fallbacks: body `"Inter", system-ui, sans-serif`;
code `"JetBrains Mono", ui-monospace, monospace`; display `"Outfit", "Poppins", sans-serif`.

Lean on the default type scale for hierarchy — `text-xs` for captions, `text-sm` for
secondary copy, `text-base` for body, `text-lg` for lead-ins, `text-xl` and up for headings.

## Motion

Built-in loops cover the common cases: `animate-spin` (loaders), `animate-pulse` (skeletons),
`animate-ping` (attention), `animate-bounce` (playful nudges).

For interaction feedback, combine a transition with the property you are changing and an
easing curve: `transition-colors duration-150`, or
`hover:scale-105 transition-transform ease-out`.

## Knowing when to extract a component

When the same long class list appears three or more times, or a piece carries several
state variants, lift it into a real component (React, Vue, etc.) rather than copying the
string around. Reserve `@apply` for the rare case where a component boundary is not
available — it is a fallback, not the default.

## Patterns to avoid

| Don't | Instead |
|---|---|
| Sprinkle arbitrary values everywhere | Stay on the design scale |
| Reach for `!important` | Resolve the specificity conflict properly |
| Drop back to inline `style=` | Express it with utilities |
| Copy a giant class string repeatedly | Extract a component |
| Blend a v3 JS config with v4 | Commit fully to the CSS-first model |
| Build class names from template strings | Write them statically so they survive compilation |

## Keeping builds fast

Unused utilities are pruned automatically, and the v4 engine compiles quickly out of the
box. The one thing you control is *predictability*: never assemble class names dynamically,
since the compiler can only keep what it can see in the source. Cache build artifacts in CI
to skip repeat work.

The throughline: in v4, CSS is the source of truth. Embrace custom properties, container
queries, and native features, and let the config file fade away.
