---
name: taste-skill
description: A taste filter for marketing-style web work (landing pages, portfolios, and redesigns) that fights generic, machine-generated "design" output. The agent reads the brief first, commits to a deliberate direction, and ships interfaces that look authored rather than templated. It reaches for genuine design systems when the brief warrants one, audits before redesigning, and runs a strict checklist before any code leaves the door. Not intended for dashboards, data tables, or multi-step product flows.
---

# taste-skill — A Filter Against Generic Frontend Output

> Scope: landing pages, portfolios, marketing sites, and redesigns of those. **Out of scope:** dashboards, dense data tables, admin panels, multi-step wizards, native mobile.
> Nothing here is a default that fires on its own. Read the brief, then pull in only the rules that fit it.

## How to use this skill

1. Work through **Step 1 — Read the brief** and state a one-line direction.
2. Set the **three dials** (Step 2). They gate every layout, motion, and density call below.
3. Decide foundation: a real design system, or a hand-built aesthetic (Step 3 → `design-systems.md` for the lookup table, install lines, and source links).
4. Build against the **principles** (Steps 4–7), avoiding the **tells** catalogued in `tells.md`.
5. For scroll-driven and physics motion, follow the patterns in `motion-recipes.md`.
6. Clear the **pre-flight checklist** (Step 8) before you ship a single line.

| Reference file | Open it when |
|---|---|
| [design-systems.md](design-systems.md) | Choosing a foundation; need official package names, install lines, or canonical docs |
| [tells.md](tells.md) | Auditing output for machine-generated signatures; the full ban list |
| [motion-recipes.md](motion-recipes.md) | Implementing sticky-stack, horizontal-pan, or scroll-reveal motion |

---

## Step 1 — Read the brief before anything else

Most weak design output comes from jumping straight to a house aesthetic instead of listening. Resist that.

**Signals to extract:**
- **Surface type** — SaaS / consumer / agency / event landing; developer / designer / studio portfolio; redesign (keep the brand vs. replace it); editorial or blog.
- **Mood language** the person actually used — "calm", "minimal", "premium", "playful", "brutalist", "editorial", "dark/technical", and so on.
- **References** — links, screenshots, named products, competitors.
- **Who reads it** — a procurement committee, a design-literate shopper, and a recruiter skimming a portfolio each want a different language. Their context picks the aesthetic, not your preference.
- **Existing brand material** — logo, colors, type, photography. On a redesign these are inputs, not suggestions (Step 7).
- **Hard constraints** — accessibility-critical, regulated, public-sector, children's products, trust-first commerce. These override any aesthetic instinct.

**Then commit out loud, in one line, before writing code:**
> "Reading this as a `<surface>` for `<audience>`, in a `<mood>` language, built on `<system or aesthetic>`."

Worked examples:
- "Reading this as a developer-tooling landing for technical buyers, in a restrained/precise language, built on Tailwind utilities with measured motion."
- "Reading this as a one-person studio portfolio for art directors, in a kinetic-editorial language, built on hand-rolled CSS with scroll-driven type."
- "Reading this as a redesign of a clinic booking site, in a trust-first language, built on a government/accessible component system."

**When the brief is genuinely split**, ask exactly one question — never a questionnaire — and only when the direction truly forks ("Closer to quiet-and-precise, or loud-and-experimental?"). If context lets you infer confidently, skip the question and declare the read.

**Refuse the autopilot palette.** Violet-to-blue gradients, a centered headline floating on a dark mesh, three identical feature cards, glass on every surface, looping micro-animation everywhere, the same neutral-grey sans on every project — these are the reflexes to climb past on purpose.

---

## Step 2 — Set three dials

After the read, fix three values. Treat them as named globals the rest of this skill refers to; do not invent aliases. Overrides happen in conversation, never by editing this file.

- **`VARIANCE` (1–10)** — 1 is rigid symmetry, 10 is deliberate asymmetry/chaos.
- **`MOTION` (1–10)** — 1 is fully static, 10 is cinematic and physics-driven.
- **`DENSITY` (1–10)** — 1 is gallery-airy, 10 is packed and instrument-dense.

**Starting point: `7 / 6 / 4`.** Shift from there based on the read:

| Read | VARIANCE | MOTION | DENSITY |
|---|---|---|---|
| Minimal / calm / precise / editorial | 5–6 | 3–4 | 2–3 |
| Premium consumer / luxury / brand-forward | 7–8 | 5–7 | 3–4 |
| Playful / experimental / agency / showcase | 9–10 | 8–10 | 3–4 |
| Trust-first / regulated / accessibility-critical | 3–4 | 2–3 | 4–5 |
| Developer portfolio | 6 | 5 | 4 |
| Redesign — keep the brand | match existing | existing +1 | match existing |
| Redesign — replace it | existing +2 | existing +2 | match existing |

---

## Step 3 — Pick the foundation honestly

With the read and dials set, choose what you build on. Two paths:

1. **The brief maps to a real product system** (enterprise SaaS, a Material-flavored app, a government service, a Shopify surface, a GitHub-style devtool, etc.). Install and use the *official* package. Do not rebuild its CSS by hand, and do not import its tokens only to override most of them. One system per project — never blend two component libraries in one tree. The full mapping, package names, install commands, and doc links live in **[design-systems.md](design-systems.md)**.

2. **The brief is an aesthetic, not a system** (glass, bento tiles, brutalist, editorial, mesh-gradient, kinetic type). No single package owns these. Build with native CSS plus a utility framework and one maintained component set, and say plainly in comments what is borrowed inspiration versus official material. (Note: Apple's "Liquid Glass" is an Apple-platform material — there is no official web package for it. Any web version is a labeled frosted-glass approximation.) See **[design-systems.md](design-systems.md)** for honest implementation notes.

---

## Step 4 — Default stack and conventions

When the brief does *not* call for a product system (path 1 above), default to:

- **Framework:** React / Next.js, Server Components by default. Anything using motion, scroll, or pointer input is an isolated `'use client'` leaf; server components stay static. Global state lives only in client components — wrap providers in a client boundary.
- **Styling:** Tailwind v4. (v3 only if the existing project forces it. For v4, wire up the dedicated PostCSS or Vite plugin, not the old `tailwindcss` PostCSS entry.)
- **Motion library:** Motion, imported from `motion/react`. The legacy `framer-motion` alias still resolves; prefer `motion/react` in new code.
- **Fonts:** load via the framework's font pipeline or self-host with `font-display: swap`. No production `<link>` to a font CDN.
- **Continuous values** (cursor position, scroll progress, drag, magnetic hover) go through Motion's `useMotionValue` / `useTransform` / `useScroll` — never `useState`, which re-renders the tree every frame and stutters on phones. Plain `useState` / `useReducer` is fine for discrete UI; reach for a store (Zustand, Jotai, context) only to escape deep prop-drilling.
- **Icons:** one family per project from a real set (Phosphor, Hugeicons, Radix, Tabler are all good). Avoid Lucide unless asked or already present. Never draw icon paths by hand — if a glyph is missing, add a second library. Lock a single `strokeWidth` globally.
- **Emoji:** off by default in code and visible text; use icon glyphs instead. Allow them only for an explicitly playful/social brief, and even then sparingly.
- **Layout mechanics:** standard breakpoints; cap page width (`max-w-7xl mx-auto` or similar). Full-height sections use `min-h-[100dvh]`, never `h-screen` (the mobile address bar will jump it). Reach for CSS Grid over hand-computed flex percentages.
- **Dependencies:** before importing any third-party package, confirm it is in `package.json`; if not, emit the install command first. Never assume a library is present.

---

## Step 5 — Build with taste (the core principles)

The model's instinct trends toward cliché. Correct it deliberately. Each rule has an override path when the brief earns it.

### Type
- Headlines: tight tracking, controlled leading; large but not screaming. Body: comfortable measure (~`65ch`), relaxed leading.
- **Default to a sans display face.** A neutral workhorse sans as the *default* is a tell — pick a more characterful sans (geometric, grotesk, or a brand-fit face) first. The neutral sans is acceptable when the brief explicitly wants plain/standard, or for accessibility-first and public-sector work.
- **Serif is not the reflex for "creative".** "Feels premium/editorial" is not a reason. A serif is justified only when the brand names one, or the family is genuinely editorial/luxury/heritage *and* you can say why this specific serif fits. The two LLM-favorite display serifs in particular should not be your default reach; if a serif is warranted, rotate your choice between projects rather than reusing one.
- **Emphasis stays in one family.** To stress a word in a headline, use italic or bold of the *same* face. Splicing a serif word into a sans headline (or the reverse) is amateur.
- **Italic descenders clip.** Any italic display word containing `g j p q y` needs at least `leading-[1.1]` plus a little bottom reserve (`pb-1`). Check every italic headline word before shipping.

### Color
- One accent, kept under ~80% saturation by default. Neutral base (zinc/slate/stone) with a single confident accent (emerald, electric blue, deep rose, burnt orange…).
- **No reflex violet/blue glow.** No automatic purple button auras, no random neon gradients. If the brand genuinely wants violet, commit to it with a coherent, restrained palette — not generic gradient mush.
- **Lock the accent across the whole page.** A warm-grey site does not sprout a cool-blue CTA in a later section. Pick one accent, hold it everywhere, audit before shipping.
- **Avoid the premium-consumer autopilot palette.** For cookware/wellness/artisan/luxury briefs the reflex is *warm cream background + brass/clay/oxblood accent + espresso near-black text*. It makes every such brand look identical. Reach instead for something with intent — cold metallic luxury, deep forest + bone + amber, true-black + warm tan, saturated cobalt on one neutral, terracotta on cool slate, or pure monochrome with a single bright pop — and rotate so two consecutive premium briefs don't share a palette. The cream/brass family is fine only when the brand names those colors or is genuinely vintage-craft and you can justify it.

### Layout
- **Resist the centered hero** above `VARIANCE 4`. Prefer split layouts, left-content/right-asset, asymmetric whitespace, or scroll-pinned structure. Centered is fine for a manifesto/announcement where the words *are* the design.
- **Vary the page.** A layout family (three-up cards, full-bleed quote, image+text split…) appears at most once per page; an 8-section page uses at least four families. Never stack three consecutive image+text "zigzag" rows — break the third with a full-bleed, a stack, a grid, or a marquee.
- **Section headers stack, they don't split.** The "huge left headline + small floating explainer on the right" pattern is banned as a default; put the explainer under the headline at a sane measure. Use a true two-column header only when the right side carries a real visual, not filler text.
- **Eyebrows are rare.** The small uppercase wide-tracked label above a heading should appear at most once per three sections (the hero counts). Most sections need only the headline; the section's position already tells the reader what it is.

### Cards, shape, surface
- Use a card only when elevation reflects real hierarchy; otherwise separate with a hairline, a divider, or space. At high `DENSITY`, drop card containers entirely and let numbers breathe in plain layout.
- Tint shadows toward the background hue — no pure-black drop shadow on a light surface.
- **One radius system per page** (all-sharp, all-soft, or all-pill for interactive). A mixed scale is allowed only with a documented rule followed everywhere (e.g. pill buttons / 16px cards / 8px inputs). Round buttons on a square page is broken.

### Interactive states
LLMs ship only the happy, static state. Always cover the full cycle:
- **Loading:** skeletons shaped like the final content, not a generic spinner.
- **Empty:** composed, and it tells the user how to fill it.
- **Error:** inline for forms, contextual toasts only for transient events.
- **Press feedback:** a small `:active` nudge (`scale-[0.98]` or a 1px lift).
- **Button contrast (a11y):** every CTA's text must clear WCAG AA against its own background (4.5:1 body, 3:1 for 18px+). No white-on-white, no borderless transparent button floating on a photo — add a scrim or stroke.
- **Form contrast (a11y):** inputs, placeholders, focus rings, helper and error text all clear AA against the section background.
- **One CTA label per intent.** "Get in touch" / "Let's talk" / "Start a project" are the same intent — pick one wording and use it in nav, hero, and footer. Same for sign-up variants and portfolio-view variants.
- **CTA text fits one line** at desktop. If a label wraps, shorten it (3 words max, ideally 1–2) or widen the button.
- Labels go **above** inputs; never use a placeholder as the label.

### Theme
One theme per page. A dark page stays dark in every section — no warm-paper section dropped into a dark scroll (or the reverse); the reader should never feel they changed sites mid-page. Tints within one family are fine (`zinc-950` beside `zinc-900`); flipping to a light cream block mid-dark-page is not. A deliberate single full-theme switch with a strong transition is allowed once, only if the brief asks for it.

**Design dual-mode from the start.** Pick one token strategy (Tailwind `dark:` variant, or CSS variables swapped under a theme attribute / `prefers-color-scheme`) and stick to it. Don't hardcode mode-specific colors here — the brief decides — but keep WCAG AA contrast, hierarchy, and brand recognition intact in both modes, avoid pure `#000`/`#fff` (use off-black/off-white for depth), and never desaturate the brand into oblivion in dark mode. Respect the system preference unless the brand insists on one mode. View the page in both before calling it done.

---

## Step 6 — Content, copy, and visual assets

### Real images, not stand-ins
Marketing pages and portfolios are visual products. A text-only page with fake-screenshot `<div>`s is unfinished.
1. **If an image-generation tool exists in the environment, use it** to make section-specific assets at the right aspect ratio — hero, product, texture, mood.
2. **Otherwise pull real photography** — a seeded placeholder service with descriptive seeds, brand/stock URLs the brief supplies, or an open-license source if allowed.
3. **If neither is possible, leave labeled placeholder slots** and tell the person at the end exactly which images the page needs. Do not paper over it with hand-drawn SVG scenes or `<div>` "screenshots."

Even a restrained, minimal site needs a few real images (hero plus a couple of supporting shots) — generate quiet black-and-white photography rather than skipping imagery because the dials are low. The hero specifically needs a real visual; a gradient blob is a placeholder, not a hero.

**Logo walls use real marks.** For "trusted by / used by", render real SVG brand logos (an icon CDN or package) rather than styled text wordmarks. For an invented brand, generate a simple monogram or glyph as inline SVG in the page style. Ensure logos work in both modes. Logos only — no industry/category caption under each one.

**Banned visual reflexes:** hand-drawn decorative SVG illustrations as a default (fine only for an explicitly requested simple geometric mark); and `<div>`-built fake product UI (fake task lists, fake terminals, fake dashboards) — the single biggest tell. Show a product with a real screenshot, a generated image, an actual mini-component, or not at all.

### Hero discipline (hard rules — failing these is shipping broken work)
- The hero **fits the first viewport**: headline ≤ 2 lines, subtext ≤ 20 words *and* ≤ 3–4 lines, CTA visible without scrolling. If the value prop won't fit in 20 words, the prop is unclear — that's not the rule being strict.
- **Plan font scale with the asset.** A four-line hero headline is a font-size mistake, not a copy-length one. Big asset + long headline means a smaller starting scale.
- **Top padding caps at ~`pt-24`** on desktop; more makes the hero float halfway down and read as a bug. Need more air? Increase scale or asset size, not padding.
- **At most four text elements:** an optional eyebrow *or* brand strip (pick zero or one), the headline, the subtext, and the CTAs (one primary + at most one secondary). A trust micro-strip, a tagline under the CTAs, a pricing teaser, a feature bullet list, an avatar row — all move to their own sections below. The "used by" logo wall is a *separate* section beneath the hero, never inside it.

### Navigation
- One line at desktop. If items don't fit at `lg`, shorten labels, drop secondary items, or collapse to a menu. A two-line desktop nav is broken.
- Height caps around 64–80px. No oversized bar eating the viewport.

### Density and copy
- **Default section shape:** short headline (≤ ~8 words) + short paragraph (≤ ~25 words) + one asset *or* one CTA. More needs a reason.
- **No data dumps.** A 20-row table or 30-item award list on a marketing page is the wrong component. Show the top few with a "see all" link, use a marquee/carousel for breadth, or move the data to its own page if it *is* the product.
- **Long lists want a different component, not a longer list.** Past ~5 items, reach for a grouped two-column split, a card grid, tabs/accordion, scroll-snap pills, or a marquee. A 10-row spec sheet with a hairline under every row is the laziest possible layout — group into a few clusters, or give each spec a card.
- **Audit every visible string before shipping.** Re-read headlines, subheads, labels, buttons, body, captions, alt text, footer, errors. Cut anything grammatically broken, with a dangling referent, or that reads like the model trying to sound profound (forced metaphor, mock-humble craftsman voice, cute-but-wrong wordplay). When unsure, replace it with a plain functional sentence — boring beats wrong.
- **No faked precision.** Oddly specific stats (`92%`, `4.1×`, `5.8mm`) are fine only if they come from real data or are explicitly marked as sample. Don't invent engineering precision the brand doesn't claim.
- **One copy register per page** unless the brand voice deliberately mixes them.
- **Quotes are snippets:** ≤ 3 lines of body, cut longer ones down. Attribution is name + role (+ company optionally), never a bare first name. Use real typographic quote marks or none.

---

## Step 7 — Redesigns

Greenfield and redesign are different jobs; misreading which one you're in is the top cause of bad redesign output. First, classify:

- **Greenfield** — nothing exists, or a full overhaul is approved. Use Step 2 baselines.
- **Redesign, keep the brand** — modernize without breaking identity. Audit first, extract the brand tokens, evolve gradually.
- **Redesign, replace it** — new visual language over existing content. Treat visuals as greenfield but preserve the content and information architecture.

If it's ambiguous, ask once: keep the existing brand, or start visually fresh?

**Audit before changing anything.** Document the current brand tokens (color, type, logo, radii), the information architecture and conversion paths, which content is doing real work versus filler, the signature patterns worth keeping, the slop/breakage worth retiring, an inferred dial reading of the current site (your starting point, not the baseline), and the SEO baseline. **SEO regression is the number-one redesign risk.**

**Hold these stable unless explicitly told otherwise:** URL/route slugs and anchor IDs, primary nav labels, form field names and order (renaming them breaks analytics and autofill), the logo/wordmark, and existing legal/consent copy. Preserve the copy voice unless a rewrite is requested, and don't regress existing accessibility wins.

**Apply changes in rising order of risk, stopping when the brief is satisfied:** type refresh (most lift per unit risk) → spacing and rhythm → color recalibration (desaturate, unify neutrals, keep the brand accent) → a motion layer appropriate to the `MOTION` dial → hero/key-section recomposition → full block replacement (only when a block is unsalvageable). A brand that is already purple stays purple — that's the override path for the no-reflex-violet rule.

Rule of thumb: if IA, content, and SEO are sound, targeted evolution (the first few levers) buys most of the value at a fraction of the risk. Go to a full redesign only when the debt is structural. If the brand itself is changing, it's greenfield.

---

## Step 8 — Pre-flight checklist (run before any code ships)

Not optional. Walk every line. If one can't be ticked honestly, the page isn't done.

**Direction**
- [ ] One-line read declared (Step 1).
- [ ] Dials set and justified from the brief, not silently left at baseline.
- [ ] Foundation chosen from `design-systems.md`, or the aesthetic labeled honestly; one system only.
- [ ] If a redesign: mode classified and audit done (Step 7).

**Consistency locks**
- [ ] One theme for the whole page — no section inverts.
- [ ] One accent color across every section.
- [ ] One radius system throughout.
- [ ] One copy register; one icon family; one font strategy.

**Hero & layout**
- [ ] Hero fits the first viewport (≤ 2-line headline, ≤ 20-word/≤ 4-line subtext, CTA visible, scale planned with the asset).
- [ ] Hero top padding ≤ ~`pt-24`; content not floating mid-viewport.
- [ ] ≤ 4 hero text elements; no tagline/trust-strip/pricing-teaser crammed in.
- [ ] Eyebrow count ≤ ceil(sections / 3), hero included.
- [ ] No split-header (big-left-headline + small-right-paragraph) pattern.
- [ ] No 3+ consecutive image+text zigzag sections; ≥ 4 layout families across 8 sections.
- [ ] Nav on one line at desktop, height ≤ ~80px.
- [ ] Any grid has exactly as many cells as content, with real visual variety (not all text-on-blank), and rhythm rather than one repeated row.

**Type, color, contrast**
- [ ] Serif (if any) is justified and rotated from the last project; not a reflex creative-serif.
- [ ] Premium-consumer palette is not the cream/brass/oxblood/espresso autopilot (or it's justified and differs from the last such project).
- [ ] Italic display words with descenders have leading + bottom reserve.
- [ ] Every CTA and form element clears WCAG AA contrast.
- [ ] No CTA label wraps at desktop; one label per intent.

**Content & assets**
- [ ] Real images present (generated → seeded placeholder → labeled slot); no `<div>` fake screenshots, no default hand-drawn SVG scenes, no pure-text "minimalism."
- [ ] Logo wall sits under the hero, uses real/generated SVG marks, logos only.
- [ ] No overlaid pills/labels or decorative photo-credit captions on images.
- [ ] No data-dump sections; long lists use a real component; sane density.
- [ ] Quotes ≤ 3 lines with clean attribution.
- [ ] Every visible string re-read; nothing broken, dangling, or mock-profound.
- [ ] **Zero em-dashes (`—`) and zero en-dash separators (`–`) anywhere visible.** See `tells.md` — this is binary, not "use sparingly."
- [ ] None of the catalogued tells in `tells.md` (autopilot palette, generic names like "John Doe"/"Acme", fake-perfect numbers, scroll cues, version/locale/weather strips, section-number eyebrows, decorative dots, "Quietly trusted by," etc.).

**Motion, performance, a11y**
- [ ] If `MOTION > 4`, the page actually moves (entry, scroll-reveal, hover) — claimed motion is shown; if you can't ship it cleanly, drop the dial and ship static.
- [ ] Every animation is justifiable in one sentence (hierarchy / sequence / feedback / state).
- [ ] At most one horizontal marquee on the page.
- [ ] Sticky-stack / horizontal-pan follow `motion-recipes.md` (pin at viewport top, correct scrub).
- [ ] No `window` scroll listeners or per-frame React state for scroll/pointer — Motion values, ScrollTrigger, IntersectionObserver, or CSS scroll-driven animation only.
- [ ] Everything above `MOTION 3` honors `prefers-reduced-motion`; infinite loops, parallax, and physics collapse to static.
- [ ] Animate only `transform`/`opacity`; `useEffect` motion has cleanup; motion isolated in `'use client'` leaves.
- [ ] Grain/noise only on a fixed `pointer-events-none` overlay, never a scrolling container.
- [ ] Dark mode tokens defined and verified in both modes.
- [ ] High-variance layouts collapse explicitly to single-column under 768px; `min-h-[100dvh]` not `h-screen`.
- [ ] Empty / loading / error states provided.
- [ ] Core Web Vitals plausibly met (LCP < 2.5s with a prioritized hero image, INP < 200ms, CLS < 0.1); z-index used only for real layering contexts.
