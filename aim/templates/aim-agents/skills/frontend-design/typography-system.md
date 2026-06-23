# Typography System Reference

> A decision guide for type on the web. The goal is judgment, not recall.
> **Treat every value here as a rule of thumb, not a fixed setting. Reason about the context first.**

---

## 1. Building a Hierarchy

Hierarchy is the reader's map. It answers, at a glance, "where do I start and what matters most?"

### Levers You Can Pull

You rarely need all of these at once. Combining two or three usually reads cleaner than overloading one.

```
                 strongest signal
   Size      ─────────────────────►  big = important
   Weight    ─────────────────────►  bold pulls the eye
   Color     ─────────────────────►  contrast = priority
   Spacing   ─────────────────────►  gaps group & separate
   Placement ─────────────────────►  upper-left reads first
                 subtlest signal
```

### A Workable Default Ladder

| Tier          | Treatment                                  |
|---------------|--------------------------------------------|
| Page title    | Biggest, heaviest, clearly set apart       |
| Section head  | Smaller than the title, still bold         |
| Subsection    | Mid-size; weight alone may carry it        |
| Running text  | Default size and weight                    |
| Meta / labels | Smallest, frequently a muted color         |

### The Squint Test

Blur your eyes (or literally squint) at the layout. If you can still tell the title from the body and one section from the next, the hierarchy holds. If everything turns to grey mush, push the contrast harder.

---

## 2. The Modular Scale

### Idea in One Line

Instead of picking sizes by hand, derive them from one number multiplied by itself:

```
   size(n) = base × ratio ^ n

   base    →  your anchor (usually body copy)
   ratio   →  the step between adjacent sizes
   n       →  how many steps up (+) or down (−)
```

Pick the base, pick the ratio, and the rest of the scale falls out for free — consistent by construction.

### Ratios and the Mood They Carry

| Name           | Ratio | Character     | Reach for it when…            |
|----------------|-------|---------------|-------------------------------|
| Minor second   | 1.067 | Almost flat   | Packed dashboards, tiny viewports |
| Major second   | 1.125 | Restrained    | Tight, utilitarian layouts    |
| Minor third    | 1.2   | Easygoing     | Card grids, native-feel mobile|
| Major third    | 1.25  | Well-balanced | A safe everyday web default   |
| Perfect fourth | 1.333 | Distinct steps| Articles, blogs, reading apps |
| Perfect fifth  | 1.5   | Bold jumps    | Landing pages, big headlines  |
| Golden ratio   | 1.618 | Theatrical    | Hero banners, display moments |

Smaller ratios suit dense, information-heavy screens; larger ratios suit expressive, marketing-style pages.

### Worked Example

Say `base = 1rem` and `ratio = 1.25` (major third):

```
   n = -2   →  1 / 1.25²  =  0.64rem    caption
   n = -1   →  1 / 1.25   =  0.80rem    small
   n =  0   →  1rem                     body  ◄ anchor
   n =  1   →  1 × 1.25   =  1.25rem    lead / h4
   n =  2   →  1 × 1.25²  =  1.563rem   h3
   n =  3   →  1 × 1.25³  =  1.953rem   h2
   n =  4   →  1 × 1.25⁴  =  2.441rem   h1
```

Extend in either direction as far as the design needs.

### Picking the Base

| Situation             | Sensible base | Reason                              |
|-----------------------|---------------|-------------------------------------|
| Mobile-first product  | 16–18px       | Comfortable on small screens        |
| Dense desktop tool    | 14–16px       | Fits more on screen                 |
| Editorial / reading   | 18–21px       | Eases long stretches of text        |
| Accessibility-led     | 18px and up   | Lower reading effort for everyone   |

---

## 3. Line Length (Measure)

### The Comfortable Band

Reading speed and comfort peak when each line holds roughly **45–75 characters**.

```
   |◄── too narrow ──►|◄──── the comfort band ────►|◄── too wide ──►|
   0                 45                            75
        chopped,                relaxed                  eye loses
        jerky rhythm            left-to-right            its place
                                tracking                 on return
```

### Set It in `ch`

The `ch` unit equals the width of the `0` glyph in the current font, so a width set in `ch` tracks the type size automatically — no media queries needed.

```css
.prose {
  max-width: 65ch;
}
```

### Tighten by Context

| Where the text lives | Target characters |
|----------------------|-------------------|
| Desktop article body | 60–75             |
| Phone screen         | 35–50             |
| Narrow sidebar       | 30–45             |
| Ultrawide monitor    | hold the cap near 75ch |

---

## 4. Line Height (Leading)

### What Drives It

```
   line-height responds to:
     • type size      →  bigger type wants a tighter ratio
     • measure        →  longer lines want more breathing room
     • the typeface   →  some designs simply need extra air
     • the role       →  a heading is not a paragraph
```

### Starting Ranges

| Role            | Range     | Why                                |
|-----------------|-----------|------------------------------------|
| Headings        | 1.1 – 1.3 | Few words per line; keep it tight  |
| Body copy       | 1.4 – 1.6 | The everyday comfortable zone      |
| Long-form prose | 1.6 – 1.8 | Maximum ease over many paragraphs  |
| UI chrome       | 1.2 – 1.4 | Conserve vertical space            |

### Nudge It When…

- the **measure runs long** → add leading
- the **type gets larger** → trim the ratio back
- the text is **set in caps** → often wants a touch more
- the **tracking is tight** → may need a little more room

---

## 5. Fluid (Responsive) Type

### Why Fixed Sizes Disappoint

```
   one fixed value across all screens:

   phone   ▏H E A D L I N E▏   ← overflows, feels huge
   laptop  ▏ Headline ▏        ← about right
   desktop ▏ headline ▏        ← looks undersized

   step-based breakpoints fix the extremes but
   snap abruptly at each jump.
```

### `clamp()` Smooths It Out

`clamp()` takes three arguments — a floor, a fluid middle term, and a ceiling — and the browser interpolates the middle as the viewport changes, clipping at the bounds.

```css
/* clamp( MIN , FLUID , MAX ) */
h1 {
  font-size: clamp(1.75rem, 1.2rem + 2.5vw, 3rem);
}
```

The fluid term usually pairs a rem floor with a viewport-relative unit so it grows with the screen.

### How Much Each Role Should Travel

| Element        | Amount of movement              |
|----------------|---------------------------------|
| Body copy      | Gentle (e.g. 1rem → 1.125rem)   |
| Subheadings    | Moderate                        |
| Headings       | Pronounced                      |
| Display type   | The most dramatic of all        |

---

## 6. Pairing Typefaces

### The Balancing Act

```
        too alike                  just right                 too unlike
   ┌──────────────┐          ┌──────────────────┐         ┌──────────────┐
   │ muddy, looks │          │ clear contrast,  │         │ clashing,    │
   │ like a       │   ◄───   │ still feels like │   ───►  │ no shared    │
   │ mistake      │          │ one system       │         │ identity     │
   └──────────────┘          └──────────────────┘         └──────────────┘
```

Aim for enough difference to build hierarchy, enough kinship to feel intentional. A serif-plus-sans or display-plus-neutral split is the classic move.

### Strategies That Tend to Work

| Approach        | What you do                              | Feels like              |
|-----------------|------------------------------------------|-------------------------|
| Play the contrast | Serif headings over a sans body        | Editorial, timeless     |
| Stay in one family| One variable font, vary the weights    | Tidy, modern            |
| Trust the foundry | Two faces from the same designer/foundry| Naturally proportioned  |
| Match the era     | Faces born in the same period           | Period-consistent       |

### What to Actually Compare

```
   line two candidates side by side and check:
     ▸ x-height      lowercase too tall / too short next to each other?
     ▸ width         one condensed, one wide?
     ▸ stroke contrast  flat strokes vs. sharp thick/thin swings?
     ▸ mood          do they agree on formal vs. casual?
```

### Combinations Worth Trying

| Heading face   | Body face       | Resulting tone        |
|----------------|-----------------|-----------------------|
| Geometric sans | Humanist sans   | Modern and approachable |
| Display serif  | Plain sans      | Refined, magazine-like  |
| Neutral sans   | The same sans   | Stripped-back, techy    |
| Heavy geometric| Light geometric | Current, fashion-forward|

### Steer Clear Of

- ❌ two attention-grabbing display faces fighting each other
- ❌ near-identical faces that read as an error
- ❌ stacking four or more families on one page
- ❌ pairs whose x-heights are wildly mismatched

---

## 7. Weight & Emphasis

### Reading the Weight Scale

| Range   | Common name   | Put it to work on        |
|---------|---------------|--------------------------|
| 300–400 | Light/Regular | Paragraphs, running text  |
| 500     | Medium        | Quiet emphasis            |
| 600     | Semibold      | Labels, minor headings    |
| 700     | Bold          | Headings, strong stress   |
| 800–900 | Heavy/Black   | Display and hero type     |

### Make the Jump Count

```
   pick weights that are clearly apart:

   400  ▏regular body▏        and  700 ▏Bold Heading▏   ✓ reads instantly
   400  ▏regular body▏        and  500 ▏medium stress▏  ~ whispered
   600  ▏Semibold head▏       and  700 ▏Bold sub▏        ✗ too close to tell
```

Leave at least two steps between levels you want to contrast.

### Hold Back On

- ❌ piling on weights — three or four per page is plenty
- ❌ neighboring weights (400 vs 500) to signal hierarchy
- ❌ heavy weights stretched across long passages

---

## 8. Letter-Spacing (Tracking)

### The Core Rule

```
   big display type          →  pull it in
      large glyphs make default gaps look loose;
      a slight negative value tightens it up

   small body type           →  leave alone or open slightly
      a touch of extra space aids legibility;
      never go negative on body text

   ALL-CAPS RUNS             →  always open it up
      caps lack the up/down strokes that space lowercase,
      so they need extra room to breathe
```

### Suggested Adjustments

| Context          | Tracking         |
|------------------|------------------|
| Display / hero   | −2% to −4%       |
| Headings         | −1% to −2%       |
| Body text        | 0% (leave it)    |
| Fine print       | +1% to +2%       |
| ALL CAPS         | +5% to +10%      |

---

## 9. How People Actually Read

### The F-Shaped Scan

On text-dense pages, eyes trace a rough **F**: a sweep across the top, a shorter sweep lower down, and a vertical skim down the left edge.

```
   ████████████████████  ← full sweep across the first line
   ██████████
   ███████████████       ← shorter sweep (a subhead grabs them)
   ██████
   ████                  ┐
   ████                  │ skim straight down the left margin
   ████                  ┘
```

**Takeaway:** load the left edge and your headings with the words that matter.

### Chunk It Down

- cap paragraphs around three or four lines
- break the page with honest subheadings
- turn series into bulleted lists
- let white space separate one block from the next

### Lower the Effort

- conventional, familiar letterforms read faster
- strong text-to-background contrast reduces strain
- repeated, predictable patterns let readers stop thinking about the layout

---

## 10. Pre-Ship Checklist

Run through this before locking type down:

- [ ] Did you **ask about font preferences** up front?
- [ ] Does the choice **fit the brand and context**?
- [ ] Have you **settled on a scale ratio**?
- [ ] Are you **holding to two or three families**?
- [ ] Did you **check legibility at every size**?
- [ ] Is the **measure inside 45–75ch**?
- [ ] Does **contrast meet accessibility needs**?
- [ ] Is this **a fresh take, not a repeat of last time**?

### Things to Avoid

- ❌ reaching for the same fonts on every project
- ❌ letting the family count creep up
- ❌ trading away readability for looks
- ❌ hard-coded sizes with no responsive plan
- ❌ decorative faces carrying body copy

---

> **Bottom line:** type exists to make meaning land clearly — let the content and the audience pick the settings, not habit or taste.
