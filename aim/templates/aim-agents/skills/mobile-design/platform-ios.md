# iOS Platform Guidelines

> The Human Interface Guidelines distilled: iOS conventions, SF Pro type, system colors, and native components.
> Read this whenever the target is iPhone or iPad.

---

## 1. The HIG mindset

Apple's design language rests on three ideas.

- **Clarity** — text stays legible at any size, icons are precise, decoration is restrained, and function drives the form.
- **Deference** — the interface helps without competing; content fills the screen and translucency hints at what lies beyond.
- **Depth** — layers and transitions convey hierarchy, and touch reveals function while content sits above the chrome.

These show up as concrete values: aesthetic integrity (the design suits the task — a game is not a spreadsheet), consistency through system controls, direct manipulation of content, prompt feedback, real-world metaphors, and user control (the user initiates and can always cancel).

---

## 2. Typography

### The SF families

```
SF Pro Text     body copy below 20pt
SF Pro Display  large titles, 20pt and up
SF Pro Rounded  friendly, softer contexts
SF Mono         code, tabular figures
SF Compact      watchOS and tight layouts
```

### The type scale

| Style | Size | Weight | Use |
|-------|------|--------|-----|
| Large Title | 34pt | Bold | nav bar, collapses on scroll |
| Title 1 | 28pt | Bold | page titles |
| Title 2 | 22pt | Bold | section headers |
| Title 3 | 20pt | Semibold | subsection headers |
| Headline | 17pt | Semibold | emphasized body |
| Body | 17pt | Regular | primary content |
| Callout | 16pt | Regular | secondary content |
| Subhead | 15pt | Regular | tertiary content |
| Footnote | 13pt | Regular | captions, timestamps |
| Caption 1 | 12pt | Regular | annotations |
| Caption 2 | 11pt | Regular | fine print |

### Dynamic Type is mandatory

```swift
// Wrong — fixed, will not scale
Text("Hello").font(.system(size: 17))

// Right — scales with the user's setting
Text("Hello").font(.body)
```

```jsx
// React Native: avoid hardcoded sizes; drive from a scalable token
<Text style={styles.body}>Hello</Text>
```

Weights map as: regular (400) for body, medium (500) for buttons and emphasis, semibold (600) for subheadings, bold (700) for titles and key facts, heavy (800) only rarely.

---

## 3. Color

Reach for semantic colors so light and dark modes adapt automatically.

```
Text       .label · .secondaryLabel · .tertiaryLabel · .quaternaryLabel
Surfaces   .systemBackground · .secondarySystemBackground · .tertiarySystemBackground
Fills      .systemFill · .secondarySystemFill · .tertiarySystemFill · .quaternarySystemFill
```

### System accents

| Color | Light | Dark | Use |
|-------|-------|------|-----|
| Blue | #007AFF | #0A84FF | links, default tint |
| Green | #34C759 | #30D158 | success |
| Red | #FF3B30 | #FF453A | destructive, errors |
| Orange | #FF9500 | #FF9F0A | warnings |
| Yellow | #FFCC00 | #FFD60A | attention |
| Purple | #AF52DE | #BF5AF2 | special features |
| Pink | #FF2D55 | #FF375F | favorites |
| Teal | #5AC8FA | #64D2FF | information |

Dark mode is a deliberate palette, not an inversion: backgrounds go to true or near black, colors desaturate, text becomes light, and shadows give way to glows or nothing. Semantic colors handle the switch for you.

---

## 4. Layout and spacing

Keep interactive content inside the safe area — clear of the status bar at the top and the home indicator at the bottom.

```
┌─────────────────────────────┐
│ ░░░ status bar ░░░           │  top inset
├─────────────────────────────┤
│        safe content         │
├─────────────────────────────┤
│ ░░░ home indicator ░░░       │  bottom inset
└─────────────────────────────┘
```

Standard spacing:

| Spot | Value |
|------|-------|
| screen edge → content | 16pt |
| grouped section top/bottom | 16pt |
| list cell horizontal padding | 16pt |
| card inner padding | 16pt |
| button padding | 12pt vertical, 16pt horizontal |

Work in multiples of 8pt on iPhone (16pt margins, 8pt minimum gaps), tighten to 4/8 in compact layouts, and widen to 20pt-plus margins with multi-column layouts on iPad.

---

## 5. Navigation

| Pattern | Use | Form |
|---------|-----|------|
| Tab bar | 3-5 top-level sections | bottom, always visible |
| Navigation controller | hierarchical drill-down | stack with a back button |
| Modal | a focused, interrupting task | sheet or full screen |
| Sidebar | iPad multi-column | left sidebar |

### Tab bar

```
┌─────────────────────────────┐
│         content             │
├─────────────────────────────┤
│  🏠   🔍   ➕   ❤️   👤      │  ~49pt tall
│ Home Search New Saved You    │
└─────────────────────────────┘
```

Keep it to 3-5 items, use SF Symbols (~25pt), always label them, mark the active one with a filled glyph plus the tint, and do not hide the bar on scroll.

### Navigation bar

```
┌─────────────────────────────┐
│ ‹ Back    Page Title   Edit  │  ~44pt
├─────────────────────────────┤
│         content             │
└─────────────────────────────┘
```

The back control is a chevron with the previous title (or "Back"), the title centers and uses dynamic type, the right side holds at most two actions, a large title may collapse on scroll, and text buttons read more clearly than icons.

### Modals

| Style | Use | Look |
|-------|-----|------|
| Sheet (default) | secondary tasks | a card over the dimmed parent |
| Full screen | immersive tasks | covers everything |
| Popover | iPad quick info | an arrowed bubble |
| Alert | critical interruption | centered dialog |
| Action sheet | contextual choices | options from the bottom |

### Gestures

| Gesture | Meaning |
|---------|---------|
| left edge swipe | go back |
| pull down (sheet) | dismiss |
| long press | context menu |
| two-finger swipe | scroll within a nested scroll |

---

## 6. Components

### Buttons

```
Tinted     filled, the primary action
Bordered   outlined, secondary
Plain      text only, tertiary
```

Sizes run mini, small, medium, large; primary CTAs want at least a 44pt tap height.

### Lists and tables

```
styles    .plain · .insetGrouped (default since iOS 14) · .grouped · .sidebar (iPad)

accessories
  ›  disclosure → navigates to detail
  ⓘ  detail button → info without navigating
  ✓  checkmark → selection
  ☰  reorder handle
  −  delete (edit/swipe)
```

### Text fields

```
┌─────────────────────────────┐
│ 🔍 Search...            ✕   │
└─────────────────────────────┘
 leading icon          clear button
```

Rounded rectangle, at least 36pt tall, placeholder in secondary text color, clear button when there is content.

### Segmented controls

```
┌──────┬────────┬──────┐
│ All  │ Active │ Done │
└──────┴────────┴──────┘
```

Two to five equal-width segments, text or icons but not a mix, max five — past that, prefer tabs.

---

## 7. Distinctive patterns

- **Pull to refresh** — use the native `UIRefreshControl`: pull past the threshold shows the spinner, release triggers the refresh, completion hides it. Do not hand-build this.
- **Swipe actions** — a left swipe reveals destructive actions (Archive, Delete, Flag), a right swipe reveals constructive ones (Pin, Star, Mark as Read); a full swipe fires the first action.
- **Context menus** — a long press opens a preview plus related actions, with any destructive item last and in red, scrolling past roughly eight.
- **Sheets (iOS 15+)** — a draggable grabber over a dimmed parent, with detents `.medium`, `.large`, or a custom height.

---

## 8. SF Symbols

```
Apple's icon set (thousands of glyphs).
weight: match the adjacent text weight
scale:  .small (inline) · .medium (standard) · .large (emphasis)
```

```swift
Image(systemName: "star.fill").font(.title2).foregroundStyle(.yellow)
Image(systemName: "heart.fill").symbolRenderingMode(.multicolor)
Image(systemName: "checkmark.circle").symbolEffect(.bounce)   // iOS 17+
```

Best practice: match symbol weight to font weight, prefer standard symbols users recognize, use multicolor only when it carries meaning, and check availability on older iOS.

---

## 9. Accessibility

Every interactive element needs a label, an optional hint, the right traits, and a value when it has state.

```swift
.accessibilityLabel("Play")
.accessibilityHint("Plays the selected track")
```

```jsx
accessibilityLabel="Play"
accessibilityHint="Plays the selected track"
accessibilityRole="button"
```

Support Dynamic Type across the whole range (roughly 14pt up to 53pt at accessibility sizes), and honor Reduce Motion:

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion
// reduceMotion ? instant : animated
```

```jsx
import { AccessibilityInfo } from 'react-native';
AccessibilityInfo.isReduceMotionEnabled();
```

---

## 10. Checklists

**Each iOS screen** — SF Pro / SF Symbols, Dynamic Type supported, safe areas respected, HIG navigation (back gesture works), tab bar ≤ 5, targets ≥ 44pt.

**Before iOS release** — dark mode tested, all text sizes checked, VoiceOver tested, edge-back working everywhere, keyboard avoidance in place, notch / Dynamic Island handled, home-indicator area clear, native components used where they fit.

---

> iOS users carry strong expectations from every other iOS app. Stray from HIG patterns and it reads as broken. When unsure, reach for the native component.
