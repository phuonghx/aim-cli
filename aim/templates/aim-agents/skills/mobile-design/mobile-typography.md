# Mobile Typography Reference

> Type scale, system fonts, dynamic text, accessibility, and dark-mode text.
> Bad typography is the leading cause of unreadable mobile apps.

---

## 1. Why phone type is its own problem

```
desktop                         mobile
───────                         ──────
viewed at 20-30 inches          viewed at 12-15 inches
wide viewport                   narrow viewport
hover for detail                tap or scroll for detail
controlled lighting             outdoors, glare, dark
fixed sizes                     user controls the size
long reading sessions           quick scanning
```

| Rule | Desktop | Mobile |
|------|---------|--------|
| minimum body | 14px | 16px (14pt/14sp) |
| max line length | ~75 chars | 40-60 chars |
| line height | 1.4-1.5 | 1.4-1.6 (more generous) |
| weight | varied | regular-dominant, bold sparingly |
| contrast | AA (4.5:1) | AA minimum, AAA preferred |

---

## 2. System fonts

### iOS — SF Pro

```
SF Pro Display  large text (20pt+)
SF Pro Text     body (< 20pt)
SF Pro Rounded  friendly contexts
SF Mono         monospace
SF Compact      watch, tight UI

optical sizing, dynamic tracking, tabular/proportional figures, high legibility
```

### Android — Roboto

```
Roboto · Roboto Flex (variable) · Roboto Serif · Roboto Mono · Roboto Condensed

screen-optimized, wide language coverage, many weights, holds up at small sizes
```

**Use system fonts when** the brand does not mandate otherwise, reading efficiency matters, a native feel is important, performance is critical, or you need broad language support. **Reach for a custom font when** brand identity demands it, you need visual differentiation, or the style is editorial — but still support accessibility.

If you do go custom: include every weight you use, subset the file, test across all Dynamic Type sizes, provide a system fallback, check rendering quality, and confirm language coverage.

---

## 3. Type scale

### iOS (built in)

| Style | Size | Weight | Line |
|-------|------|--------|------|
| Large Title | 34pt | Bold | 41pt |
| Title 1 | 28pt | Bold | 34pt |
| Title 2 | 22pt | Bold | 28pt |
| Title 3 | 20pt | Semibold | 25pt |
| Headline | 17pt | Semibold | 22pt |
| Body | 17pt | Regular | 22pt |
| Callout | 16pt | Regular | 21pt |
| Subhead | 15pt | Regular | 20pt |
| Footnote | 13pt | Regular | 18pt |
| Caption 1 | 12pt | Regular | 16pt |
| Caption 2 | 11pt | Regular | 13pt |

### Android (Material 3)

| Role | Size | Weight | Line |
|------|------|--------|------|
| Display Large | 57sp | 400 | 64sp |
| Display Medium | 45sp | 400 | 52sp |
| Display Small | 36sp | 400 | 44sp |
| Headline Large | 32sp | 400 | 40sp |
| Headline Medium | 28sp | 400 | 36sp |
| Headline Small | 24sp | 400 | 32sp |
| Title Large | 22sp | 400 | 28sp |
| Title Medium | 16sp | 500 | 24sp |
| Title Small | 14sp | 500 | 20sp |
| Body Large | 16sp | 400 | 24sp |
| Body Medium | 14sp | 400 | 20sp |
| Body Small | 12sp | 400 | 16sp |
| Label Large | 14sp | 500 | 20sp |
| Label Medium | 12sp | 500 | 16sp |
| Label Small | 11sp | 500 | 16sp |

### Rolling your own

Build a custom scale on a modular ratio:

```
1.125 major second   dense UI
1.200 minor third    compact
1.250 major third    balanced (common)
1.333 perfect fourth spacious
1.500 perfect fifth  dramatic

base 16px at 1.25:
  xs 10 · sm 13 · base 16 · lg 20 · xl 25 · 2xl 31 · 3xl 39 · 4xl 49
```

---

## 4. Dynamic / scalable text

iOS — Dynamic Type is mandatory:

```swift
// Wrong — fixed
Text("Hello").font(.system(size: 17))

// Right — scales
Text("Hello").font(.body)

// Custom font, still scaling
Text("Hello").font(.custom("MyFont", size: 17, relativeTo: .body))
```

Android — always size text in sp:

```
sp scales with the user's font preference; dp does not (never size text in dp).
Users scale 85% → 200%:
  default (100%): 14sp = 14dp
  largest (200%): 14sp = 28dp
Test at 200%.
```

Large sizes break naive layouts — text overflows, buttons grow too tall, icons look small, layouts crack. Counter with flexible (not fixed-height) containers, allowed wrapping, icons that scale with text, scrollable containers for long copy, and testing at the extremes during development.

---

## 5. Accessibility

| Element | Minimum | Recommended |
|---------|---------|-------------|
| body | 14 | 16 |
| secondary | 12 | 13-14 |
| caption | 11 | 12 |
| buttons | 14 | 14-16 |
| nothing below | 11 | — |

Contrast (WCAG):

```
normal text (< 18pt, or < 14pt bold)   AA 4.5:1 · AAA 7:1
large text  (≥ 18pt, or ≥ 14pt bold)   AA 3:1   · AAA 4.5:1
decorative / logos                      no requirement
```

Spacing (WCAG SC 1.4.12): line height ≥ 1.5x, paragraph spacing ≥ 2x the font size, letter spacing ≥ 0.12x, word spacing ≥ 0.16x. On mobile, aim for body 1.4-1.6, headings 1.2-1.3, never below 1.2.

---

## 6. Dark-mode text

```
light mode                 dark mode
──────────                 ─────────
black text (#000)          light gray (#E0E0E0)
high contrast              slightly reduced contrast
full saturation            desaturated
dark = emphasis            light = emphasis
```

Do not use pure white (#FFF) on dark — soften to off-white (#E0E0E0 to #F0F0F0) to cut eye strain.

| Level | Light | Dark |
|-------|-------|------|
| primary | #000000 | #E8E8E8 |
| secondary | #666666 | #A0A0A0 |
| tertiary | #999999 | #707070 |
| disabled | #CCCCCC | #505050 |

Text reads thinner on dark backgrounds because light bleeds into the dark (halation). Compensate by using medium weight for body, nudging letter-spacing up slightly, testing on real OLED panels, and going one step bolder than in light mode.

---

## 7. Anti-patterns

| Mistake | Problem | Fix |
|---------|---------|-----|
| fixed sizes | ignores accessibility | dynamic sizing |
| tiny text | unreadable | minimum 14pt/sp |
| low contrast | invisible in sun | minimum 4.5:1 |
| long lines | hard to track | max ~60 chars |
| cramped line height | hard to read | minimum 1.4x |
| too many sizes | visual chaos | 5-7 sizes |
| all-caps body | hard to read | headlines only |
| pale gray on white | fails in bright light | raise contrast |

Frequent generated-code slips: px values instead of pt/sp, skipping Dynamic Type, 12-14px body text, ignoring line height, low-contrast "aesthetic" grays, reusing the desktop scale, and never testing at large sizes. Typography must *scale* — test at the smallest and largest settings.

---

## 8. Loading and performance

```
file sizes matter on mobile
  full font     100-300KB per weight
  Latin subset  15-40KB per weight
  variable      100-200KB (all weights)

subset to needed glyphs · WOFF2 · 2-3 files max · consider variable fonts · cache them
```

Loading strategy: show a system fallback and swap when the custom font loads, use `font-display: swap`, preload above-the-fold fonts, and never block rendering on font load.

---

## 9. Checklists

**Any text design** — body ≥ 16px/pt/sp, line height ≥ 1.4, line length ≤ 60 chars, scale defined (5-7 sizes), using pt (iOS) or sp (Android).

**Before release** — Dynamic Type tested (iOS), font scaling tested at 200% (Android), dark-mode contrast checked, sunlight readability checked, clear hierarchy, custom fonts have fallbacks, long text scrolls.

---

## 10. Quick reference

```
iOS tokens        .largeTitle 34 Bold · .title 28 Bold · .title2 22 Bold ·
                  .title3 20 Semibold · .headline 17 Semibold · .body 17 Regular ·
                  .subheadline 15 · .footnote 13 · .caption 12

Material tokens   displayLarge 57 · headlineLarge 32 · titleLarge 22 ·
                  bodyLarge 16 · labelLarge 14

minimum sizes     body 14-16 · secondary 12-13 · caption 11-12 · never < 11
line height       headings 1.1-1.3 · body 1.4-1.6 · long text 1.5-1.75
```

---

> If users cannot read the text, the app is broken. Typography is not decoration — it is the primary interface. Test on real devices, in real light, with accessibility settings on.
