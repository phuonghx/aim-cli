# Mobile Color System Reference

> OLED behavior, dark mode, battery-aware color, outdoor legibility.
> On a phone, color is not only aesthetics — it is battery life and usability.

---

## 1. Why phone color is its own problem

```
desktop                         mobile
───────                         ──────
backlit LCD                     OLED is common (self-emissive)
controlled lighting             bright sun, outdoors
steady power                    battery matters
personal preference             system-wide dark mode
static viewing                  shifting angles, motion
```

Priority order on mobile: readability first (variable light), then battery efficiency (OLED), then system integration (dark/light mode), then semantics (error/success/warning), and brand last — after the functional needs are met.

---

## 2. OLED behavior

```
LCD                              OLED
───                              ────
backlight always on              each pixel emits its own light
black = filtered backlight       black = pixel off (zero power)
constant energy use              brighter pixels cost more
dark mode saves nothing          dark mode saves real power
```

Relative energy by color:

```
#000000 true black    ░░░░░░░░░░  ~0%
#1A1A1A near black     █░░░░░░░░░  ~15%
#333333 dark gray      ███░░░░░░░  ~30%
#666666 medium gray    █████░░░░░  ~50%
#FFFFFF white          ██████████  100%
```

Saturation costs power too: blue subpixels are most efficient, green middling, red least — so desaturated colors save more.

True black versus near black:

```
#000000        maximum savings, but can smear on scroll and feels harsh; Apple's pure dark mode
#121212-#1A1A1A still saves well, scrolls smoothly, easier on the eyes; Material's recommendation

A common split: #000000 for backgrounds, #0D0D0D-#1A1A1A for surfaces.
```

---

## 3. Dark mode

People enable dark mode for OLED battery savings, less eye strain in low light, personal taste, the AMOLED look, and light sensitivity.

```
                light          dark
background      #FFFFFF   →    #000000 or #121212
surface         #F5F5F5   →    #1E1E1E
surface 2       #EEEEEE   →    #2C2C2C
primary         #1976D2   →    #90CAF9 (lighter)
text            #212121   →    #E0E0E0 (not pure white)
secondary       #757575   →    #9E9E9E

elevation in dark = a slightly lighter surface (overlay), not a shadow:
  0dp 0% · 4dp 9% · 8dp 12%
```

Text colors:

| Role | Light | Dark |
|------|-------|------|
| primary | #000000 | #E8E8E8 |
| secondary | #666666 | #B0B0B0 |
| disabled | #9E9E9E | #6E6E6E |
| links | #1976D2 | #8AB4F8 |

Do not simply invert: saturated colors become harsh, semantic colors lose meaning, brand colors may break, and contrast shifts unpredictably. Build an intentional dark palette instead — desaturate the primaries, use lighter tints for emphasis, keep semantic meanings, and recheck contrast on its own.

---

## 4. Outdoor legibility

Bright sun washes out low contrast, glare cuts readability, polarized sunglasses interfere, and users end up shielding the screen. The casualties are light gray text on white, subtle color differences, low-opacity overlays, and pastels.

```
minimum contrast
  normal text  4.5:1 (AA)
  large text   3:1   (AA)
  aim for      7:1+  (AAA)

avoid    #999 on #FFF (fails AA) · #BBB on #FFF · pale on light · subtle gradients for key info
do       system semantic colors · test in bright light · offer a high-contrast mode · solid colors for critical UI
```

---

## 5. Semantic colors

| Semantic | Meaning | iOS | Android |
|----------|---------|-----|---------|
| error | problem, destruction | #FF3B30 | #B3261E |
| success | done, positive | #34C759 | #4CAF50 |
| warning | caution | #FF9500 | #FFC107 |
| info | information | #007AFF | #2196F3 |

Never use semantic colors for branding (it muddies meaning), decoration (it dilutes impact), arbitrary styling, or status shown by color alone. Always pair them with icons (for colorblind users), keep them consistent across light and dark, hold them steady through the app, and follow platform conventions.

Error states specifically need a red-ish semantic color, high contrast against the background, an icon, and a clear text explanation:

```
iOS      light #FF3B30 · dark #FF453A
Android  light #B3261E · dark #F2B8B5 (on error container)
```

---

## 6. Dynamic color (Android)

```
Material You: wallpaper → extracted palette → app theme
you receive primary (dominant), secondary, tertiary, derived neutral surfaces, and on-colors
```

```kotlin
MaterialTheme(
    colorScheme = dynamicColorScheme() ?: staticColorScheme()  // fallback for older Android
)
```

Provide a static scheme for when dynamic color is unavailable (Android < 12, user-disabled, non-supporting launchers): define your brand colors, test in both modes, map them onto the dynamic-color roles, and support light and dark.

---

## 7. Accessibility

```
~8% of men and ~0.5% of women are colorblind
types: protanopia (red) · deuteranopia (green) · tritanopia (blue) · monochromacy (rare)

rules: never rely on color alone · add patterns, icons, text ·
       test with simulators · avoid red/green-only distinctions
```

Verify with the Xcode accessibility inspector, Android's Accessibility Scanner, contrast calculators, colorblind simulation, and real devices in sunlight.

```
AA   normal 4.5:1 · large 3:1 · UI components 3:1
AAA  normal 7:1   · large 4.5:1
mobile: meet AA, aim for AAA
```

---

## 8. Anti-patterns

| Mistake | Problem | Fix |
|---------|---------|-----|
| light gray on white | invisible outdoors | minimum 4.5:1 |
| pure white in dark mode | eye strain | #E0E0E0-#F0F0F0 |
| same saturation in dark | garish, glowing | desaturate |
| red/green-only indicator | colorblind users miss it | add icons |
| semantic colors for brand | confuses meaning | neutral brand colors |
| ignoring system dark mode | jarring | support both |

Frequent generated-code slips: reusing one palette for light and dark, ignoring OLED implications, skipping contrast math, leaning on a single default accent regardless of brand, low-contrast "aesthetic" grays, never testing outdoors, and forgetting colorblind users. Design for the worst case — bright sun, tired eyes, colorblindness, a dying battery.

---

## 9. Checklists

**Choosing colors** — light and dark variants defined, contrast checked (4.5:1+), OLED battery considered, semantic colors follow conventions, no color-only indicators.

**Before release** — tested in bright sun, tested in dark mode on an OLED device, system dark mode respected, dynamic color supported (Android), error/success/warning consistent, all text meets contrast.

---

## 10. Quick reference

```
dark backgrounds   #000000 (OLED max) · #121212 (Material) · #1E1E1E · #2C2C2C · #3C3C3C
text on dark       primary #E0E0E0-#ECECEC · secondary #A0A0A0-#B0B0B0 · disabled #606060-#707070
contrast           small 4.5:1 · large 3:1 · UI 3:1 · ideal 7:1
```

---

> Mobile color has to survive the worst conditions — bright sun, tired eyes, colorblindness, low battery. Pretty colors that fail those tests are useless colors.
