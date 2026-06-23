# Working With Color in UI

> A reasoning guide for choosing color in web interfaces.
> **Don't memorize palettes — build the judgment to pick them.**

The aim here is decision-making, not a lookup table. Every project carries its
own audience, mood, and constraints, so the "right" colors shift each time. What
stays constant is the process below.

---

## 1. Reading the Context First

Color should fall out of the problem, not lead it. Before touching a single
value, work through these prompts.

**Map the project type**

```
project
  ├─ shop / checkout ........ pair confidence with a nudge to act
  ├─ dashboard / SaaS ....... easy on the eyes for long sessions, data-first
  ├─ wellness / health ...... soft, organic, reassuring
  ├─ premium / boutique ..... restrained, quiet luxury
  ├─ portfolio / creative ... distinctive, leaves an impression
  └─ anything else .......... ask the person you're building for
```

**Then narrow the hue family**

```
pick exactly one starting point
  • blues / teals .... credibility
  • greens ........... renewal, balance
  • warm tones ....... liveliness
  • neutrals ......... refinement
  • (still unsure? get the user's preference)
```

**Settle mode, then confirm.** Will this run light, dark, or both? Reading-heavy
screens tend to favor light surfaces; an app used at night benefits from a dark
option. Sector habits and personal taste both feed this call.

> Whenever the brief leaves color open, **ask before committing**. A confirmed
> preference beats a clever guess every time.

---

## 2. Color Psychology by Use Case

Hues carry meaning, and that meaning should match the work.

| When the product is...         | Reach for...              | Because it signals...        |
|--------------------------------|---------------------------|------------------------------|
| Banking, software, healthcare  | Blue, teal                | trust, steadiness, calm      |
| Sustainability, wellness       | Green, earthy tones       | health, renewal, the natural |
| Cuisine, sports, youth brands  | Orange, yellow, warm reds | appetite, energy, warmth     |
| High-end, cosmetics, design    | Deep teal, gold, black    | refinement, exclusivity      |
| Clearance, warnings, deadlines | Red, orange               | urgency, motion, intensity   |

**Emotional read of each family** — handy when you're torn between options:

| Family | Works for | Watch out for |
|--------|-----------|---------------|
| Blue   | dependable, composed, businesslike | reads cold or generic if overdone |
| Green  | flourishing, wholesome, affirming | dull when it's the whole story |
| Red    | bold, pressing, full of drive | very loud — a little goes far |
| Orange | approachable, lively, inventive | turns gaudy at full intensity |
| Yellow | upbeat, eye-catching, sunny | poor legibility; best as a spark |
| Purple | inventive, opulent, dreamlike | the lazy default — spend it on purpose, or swap in deep teal, maroon, emerald |
| Black  | refined, commanding, current | can sit heavy on a layout |
| White  | tidy, spare, airy | drifts toward clinical |

A quick sequence to lock the lead hue: **industry → trims the families → emotion
→ fixes the hue → contrast goal → settles light vs. dark → confirm with user.**

---

## 3. The Color Wheel and Its Relationships

With a lead hue chosen, the wheel tells you what else can join it.

```
        ·  ·  ·
     ·   YELLOW   ·
   YEL-GRN     YEL-ORG
  ·                   ·
GREEN  - - - O - - -  ORANGE
  ·                   ·
   BLU-GRN     RED-ORG
   ·  (center)    ·
     ·  BLUE   RED ·
        VIO-BLU
          ·
       VIOLET
          ·
      RED-VIOLET
```

Step around the ring and you pass each hue family; cut straight across the
center and you land on a hue's opposite. Those two moves generate every scheme
below.

| Scheme | Recipe | Best suited to |
|--------|--------|----------------|
| **Monochromatic** | one hue; shift only saturation and lightness | clean, unified, businesslike looks |
| **Analogous** | two or three neighbors on the ring | gentle, easygoing, organic feels |
| **Complementary** | a hue plus the one opposite it | punchy contrast that grabs the eye |
| **Split-complementary** | a hue plus the two flanking its opposite | lively yet still grounded |
| **Triadic** | three hues spaced evenly around the ring | spirited, expressive, imaginative |

**Choosing among them:**

- Mood — relaxed leans analogous; assertive leans complementary.
- Count — a lean palette wants monochromatic; a rich one can carry triadic.
- Audience — buttoned-up favors monochromatic; younger skews triadic.

---

## 4. Building a Palette With HSL

Skip hex memorization. Reason in **HSL** instead — it lets you dial color by hand.

```
HSL = Hue · Saturation · Lightness

Hue  (0–360)      which family
   0 / 360 red · 60 yellow · 120 green
   180 cyan · 240 blue · 300 purple

Saturation (0–100%)   how intense
   low  → restrained, mature
   high → punchy, energetic

Lightness (0–100%)    how bright
   0% black · 50% the true hue · 100% white
```

**Stretch one hue into a full scale.** Hold the hue steady and vary lightness to
produce a 50→900 ramp:

| Step | Lightness | Typical role |
|------|-----------|--------------|
| 50   | ~97%      | faint tints, hover washes |
| 100  | ~94%      | subtle fills |
| 200  | ~86%      | borders, dividers |
| 300  | ~74%      | muted / disabled states |
| 400  | ~66%      | secondary emphasis |
| 500  | ~50–60%   | the base hue |
| 600  | ~48%      | hover on the base |
| 700  | ~38%      | pressed / active |
| 800  | ~30%      | strong text on light |
| 900  | ~20%      | deepest shade |

**Tune saturation to the situation:**

| Situation | Saturation |
|-----------|------------|
| Corporate, serious | dial down (40–60%) |
| Playful, youthful | push up (70–90%) |
| Dark mode | trim 10–20% off |
| Accessibility | adjust as needed to hold contrast |

---

## 5. Distributing Color: 60-30-10

A palette still needs proportion. The classic split keeps a layout balanced:
one dominant tone, one supporting tone, one small jolt of emphasis.

```
╭──────────────────────────────────────────────╮
│ ░░░░░░░░░░░░░  60% DOMINANT  ░░░░░░░░░░░░░░░░░ │
│ ░ page background, broad surfaces            ░ │
│ ░ neutral or quiet — sets the overall tone   ░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
├───────────────────────────────────┬──────────┤
│ ▒▒▒▒▒▒▒ 30% SUPPORTING ▒▒▒▒▒▒▒▒▒▒ │ ███ 10% █│
│ ▒ cards, panels, headers          │ █ pop:   █│
│ ▒ present but never competes       │ █ CTAs,  █│
│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │ █ links █│
╰───────────────────────────────────┴──────────╯
       60 ─────────────  30 ────────  10
```

Sketched as tokens:

```css
:root {
  /* 60% — chosen for mode + mood */
  --color-bg:        /* neutral: white, off-white, or deep gray */;
  --color-surface:   /* a half-step away from the background */;

  /* 30% — chosen for brand or context */
  --color-secondary: /* a softened primary, or a neutral */;

  /* 10% — chosen for the action you want */
  --color-accent:    /* saturated, made to stand out */;
}
```

---

## 6. Designing for Dark Mode

Dark mode is its own discipline — not a simple inversion of the light theme.

1. **Avoid true black.** A near-black gray, tinted faintly toward the brand hue,
   reads softer than `#000000`.
2. **Avoid true white text.** Sit body copy around 87–92% lightness so it doesn't
   buzz against the background.
3. **Pull saturation back.** Colors that sing in light mode can fatigue the eye
   on dark; ease them down.
4. **Brighter means higher.** Lift surfaces a touch as they rise in the stack —
   brightness reads as elevation.

```
elevation, base → top (each layer a shade lighter):

  popovers   ▓▓▓▓▓▓▓▓   lightest dark
  modals     ▓▓▓▓▓▓
  cards      ▓▓▓▓
  page base  ▓▓         darkest
```

**Porting light values over:**

| Light mode | Dark-mode move |
|------------|----------------|
| Punchy accent | shave 10–20% saturation |
| Plain white background | dark gray carrying a hint of the brand hue |
| Near-black text | light gray, never pure white |
| Bright color fills | darker, desaturated counterparts |

---

## 7. Contrast and Accessibility

Color only works if people can read it. WCAG sets the bar.

| Level | Body text | Large text |
|-------|-----------|------------|
| AA (baseline) | 4.5:1 | 3:1 |
| AAA (stronger) | 7:1 | 4.5:1 |

**How the ratio is figured:**

1. Convert both colors to relative luminance.
2. Divide: `(lighter + 0.05) / (darker + 0.05)`.
3. Nudge lightness until the result clears the level you need.

**Reliable starting points:**

| Pairing | Rule of thumb |
|---------|---------------|
| Text over a light surface | keep lightness at 35% or below |
| Text over a dark surface | keep lightness at 85% or above |
| Brand color on white | lean on a deep enough shade |
| Buttons | wide gap between fill and label |

---

## 8. Anti-Patterns

**Steer clear of:**

- Recycling the same hex values on every project.
- Defaulting to purple/violet without a reason — spend it deliberately.
- Reflexively pairing dark mode with neon.
- True-black (`#000000`) backgrounds.
- Pure-white (`#FFFFFF`) text floating on dark.
- Treating every industry the same.
- Shipping color without asking the user.

**Lean into:**

- A purpose-built palette each time out.
- Asking what the user actually wants.
- Weighing audience and sector.
- HSL, so adjustments stay fluid.
- Verified contrast and accessibility.
- Offering both a light and a dark route.

---

## 9. Pre-Ship Checklist

Run through this before locking color in:

- [ ] Asked the user when nothing was specified?
- [ ] Fits the industry and audience?
- [ ] Proportions follow 60-30-10?
- [ ] Contrast meets WCAG?
- [ ] Holds up in both modes (if dark is in play)?
- [ ] Not just your usual go-to?
- [ ] Distinct from the last thing you built?

---

> **Bottom line:** treat color as a choice you can justify per project, never a
> setting you reuse out of habit.
