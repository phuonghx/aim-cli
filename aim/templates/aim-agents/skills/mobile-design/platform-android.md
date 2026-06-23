# Android Platform Guidelines

> Material Design 3 distilled: Android conventions, Roboto type, the color system, and native components.
> Read this whenever the target is Android.

---

## 1. The Material 3 mindset

Material treats the interface as physical surfaces in a lit, layered space — shadow and light convey hierarchy, motion provides continuity, and the look is bold and intentional. It is adaptive (one design across form factors, color drawn from the wallpaper) and accessible by default (large targets, clear hierarchy, semantic colors, motion that respects user preferences).

In practice that means: dynamic color from the user's wallpaper, per-user personalization, accessibility baked into every component, responsiveness across screen sizes, and a single consistent language.

---

## 2. Typography

### The Roboto families

```
Roboto            default sans-serif
Roboto Flex       variable font (API 33+)
Roboto Serif      serif option
Roboto Mono       monospace
Google Sans       Google products (special license)
```

### The Material type scale

| Role | Size | Weight | Line | Use |
|------|------|--------|------|-----|
| Display Large | 57sp | Regular | 64sp | hero, splash |
| Display Medium | 45sp | Regular | 52sp | large headers |
| Display Small | 36sp | Regular | 44sp | medium headers |
| Headline Large | 32sp | Regular | 40sp | page titles |
| Headline Medium | 28sp | Regular | 36sp | section headers |
| Headline Small | 24sp | Regular | 32sp | subsections |
| Title Large | 22sp | Regular | 28sp | dialogs, cards |
| Title Medium | 16sp | Medium | 24sp | lists, nav |
| Title Small | 14sp | Medium | 20sp | tabs, secondary |
| Body Large | 16sp | Regular | 24sp | primary content |
| Body Medium | 14sp | Regular | 20sp | secondary content |
| Body Small | 12sp | Regular | 16sp | captions |
| Label Large | 14sp | Medium | 20sp | buttons, FAB |
| Label Medium | 12sp | Medium | 16sp | navigation |
| Label Small | 11sp | Medium | 16sp | chips, badges |

### Use sp for text

```
sp = scale-independent pixels — it tracks the user's font setting,
display density, and accessibility options.

Rule: sp for text, dp for everything else.
```

Weights: regular (400) for body and display, medium (500) for buttons, labels, and emphasis, bold (700) only for strong emphasis.

---

## 3. Color

### Material You dynamic color

```
wallpaper → extracted palette → app theme

You automatically get primary (wallpaper-derived), secondary, tertiary,
derived surfaces, and matching on-colors. Wire it up for a personalized feel.
```

### Semantic roles

```
Surfaces   Surface · SurfaceVariant · SurfaceTint · InverseSurface
On-surface OnSurface · OnSurfaceVariant · Outline · OutlineVariant
Primary    Primary · OnPrimary · PrimaryContainer · OnPrimaryContainer
(secondary and tertiary follow the same shape)
```

### Error / success colors

| Role | Light | Dark | Use |
|------|-------|------|-----|
| Error | #B3261E | #F2B8B5 | errors, destructive |
| OnError | #FFFFFF | #601410 | text on error |
| ErrorContainer | #F9DEDC | #8C1D18 | error backgrounds |

### Dark theme

```
background #121212 (not pure black by default)
surfaces   #1E1E1E, #232323 ... lighter as elevation rises
colors     desaturated; check contrast

elevation overlay (dark)
  0dp 0% · 1dp 5% · 3dp 8% · 6dp 11% · 8dp 12% · 12dp 14%
```

---

## 4. Layout and spacing

```
8dp baseline grid; spacing in multiples of 8
  4dp  component internal (half-step)
  8dp  minimum gap
  16dp standard
  24dp section
  32dp large

margins: phone 16dp · small tablet 24dp · large 24dp+ or columns
```

Window size classes drive layout:

```
Compact  (< 600dp)    phone portrait → single column, bottom nav
Medium   (600-840dp)  tablet/foldable → consider 2 columns, navigation rail
Expanded (> 840dp)    large tablet/desktop → multi-column, drawer
```

Canonical layouts: list-detail (email, messages; medium/expanded), feed (all sizes), supporting pane (reference content; medium/expanded).

---

## 5. Navigation

| Component | Use | Position |
|-----------|-----|----------|
| Bottom navigation | 3-5 top destinations | bottom |
| Navigation rail | tablets, foldables | left, vertical |
| Navigation drawer | many destinations, large screens | left, hidden or fixed |
| Top app bar | context and actions | top |

### Bottom navigation

```
┌─────────────────────────────┐
│         content             │
├─────────────────────────────┤
│  🏠   🔍   ➕   ❤️   👤      │  ~80dp tall
│ Home Search FAB Saved You    │
└─────────────────────────────┘
```

3-5 destinations, Material Symbols (24dp), always-visible labels, active state as a filled icon in a pill indicator, badges for notifications, an optional integrated FAB.

### Top app bar

```
types: center-aligned · small (scrolls away) · medium (collapses) · large (collapses to small)

┌─────────────────────────────┐
│ ☰  App Title         🔔 ⋮   │  ~64dp (small)
├─────────────────────────────┤
│         content             │
└─────────────────────────────┘
```

Up to three action icons; overflow goes behind ⋮.

### Navigation rail (tablets)

```
┌──────┬──────────────────────┐
│ ≡    │                      │
│ 🏠   │      content         │
│ Home │                      │
│ 🔍   │                      │
│Search│                      │
└──────┴──────────────────────┘
80dp wide, 24dp icons, labels below, optional FAB at the top
```

### Back navigation

Android provides system back via button, edge gesture, and predictive back (Android 14+). Your app must pop the stack correctly, support the predictive-back animation, never hijack back unexpectedly, and confirm before discarding unsaved work.

---

## 6. Components

### Buttons

```
Filled    primary action
Tonal     secondary, less emphasis
Outlined  tertiary, lower emphasis
Text      lowest emphasis

heights ~40dp standard, 56dp large; minimum 48dp touch target even when the visual is smaller
```

### Floating action button

```
standard 56dp · small 40dp · large 96dp · extended (icon + text)
position bottom right, 16dp inset, elevated above content

┌─────────────────────────────┐
│         content             │
│                      ┌────┐ │
│                      │ ➕ │ │
│                      └────┘ │
├─────────────────────────────┤
│      bottom navigation      │
└─────────────────────────────┘
```

### Cards

```
elevated (shadow) · filled (color, no shadow) · outlined (border)

┌─────────────────────────────┐
│        header image         │  optional
├─────────────────────────────┤
│ Title                       │
│ Supporting text             │
├─────────────────────────────┤
│   [ Action ]   [ Action ]   │  optional
└─────────────────────────────┘
12dp corners, 16dp padding (M3 default)
```

### Text fields

```
filled (fill + underline) or outlined (full border)

┌─────────────────────────────┐
│ Label (floats up on focus)  │
│ [ input text ............. ]│
│ supporting or error text    │
└─────────────────────────────┘
56dp tall; the label animates from placeholder to top; errors show red + icon + message
```

### Chips

```
assist · filter · input · suggestion
~32dp tall, 8dp corners; states unselected / selected / disabled
```

---

## 7. Distinctive patterns

- **Snackbars** — one short message above the bottom nav, 4-10 seconds, at most one text action, dismissible by swipe; queue them rather than stacking.
- **Bottom sheets** — standard (interactive) or modal (with a scrim), 28dp top corners, an optional drag handle.
- **Dialogs** — centered over a scrim, up to two right-aligned actions (a destructive one may sit left); basic, full-screen, picker, and confirmation variants.
- **Pull to refresh** — a Material circular indicator that pulls down from the top center (SwipeRefreshLayout pattern).
- **Ripple** — every touchable must ripple from the touch point on press and fade on release; roughly 12% opacity (black on light, white on dark). This is non-negotiable for the Android feel.

---

## 8. Material Symbols

```
styles  Outlined (default) · Rounded (softer) · Sharp (angular)
axes    FILL 0→1 · wght 100-700 · GRAD -25→200 · opsz 20/24/40/48

sizes   20dp dense · 24dp standard · 40dp larger target · 48dp emphasis
states  default · disabled 38% · hover/focus container · selected = filled + tint
        inactive = outlined, active = filled + indicator
```

---

## 9. Accessibility

Every interactive element needs a content description, correct semantics, state announcements, and logical grouping.

```kotlin
Modifier.semantics { contentDescription = "Play button"; role = Role.Button }
```

```jsx
accessibilityLabel="Play button"
accessibilityRole="button"
accessibilityState={{ disabled: false }}
```

Touch targets are 48 x 48dp minimum (pad up from smaller visuals; 8dp between targets). Support font scaling all the way to 200% — use sp and avoid fixed heights, then test at 200%. Respect reduced motion:

```kotlin
val reduceMotion = Settings.Global.getFloat(
    contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f
) == 0f
```

---

## 10. Checklists

**Each Android screen** — Material 3 components, targets ≥ 48dp, ripple on every touchable, Roboto / Material type scale, semantic colors (dynamic-color ready), back navigation correct.

**Before Android release** — dark theme tested, dynamic color tested where supported, font scaling checked at 200%, TalkBack tested, predictive back (14+), edge-to-edge (15+), multiple screen sizes, platform-matching navigation.

---

> Android users expect Material. Designs that ignore it feel foreign and broken. Start from Material components and customize with intent.
