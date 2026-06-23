# Touch Interaction Reference

> The deep version of touch design: how fingers differ from cursors, where the thumb can actually reach, how gestures read to users, and when haptics help.
> Read this on every mobile task — it underpins nearly every UI decision.

---

## 1. Fitts' Law, applied to fingers

A mouse pointer is effectively one pixel wide. A fingertip is a soft contact patch roughly 7mm across, and it sits *on top of* the thing being tapped, hiding it. That single difference reshapes the rules.

```
Pointer (desktop)            Finger (mobile)
─────────────────            ───────────────
~1px precise tip             ~7mm soft contact
hover preview before click   no hover, only the tap itself
cheap to miss and retry      a miss feels like a bug
points at the target         covers the target while tapping
```

Fitts' Law says acquisition time grows with distance and shrinks with target width:

```
time ≈ a + b · log2(1 + distance / width)
```

The takeaway for touch: width has to be generous, because the finger's imprecision makes small targets disproportionately slow and error-prone.

### Minimum sizes

| Standard | Floor | Comfortable | Applies to |
|----------|-------|-------------|------------|
| iOS HIG | 44 x 44 pt | 48 pt+ | every tappable element |
| Material | 48 x 48 dp | 56 dp+ | every tappable element |
| WCAG 2.2 | 44 x 44 px | — | accessibility compliance |
| Critical / destructive | — | 56-64 px | primary CTAs, delete |

### Visual size is not hit size

The drawn control can be small as long as the *hit area* meets the floor. Pad the touchable, not the glyph.

```
visible glyph:  ▢ 24px icon
hit area:       ⬚ 48px (12px padding all around)
```

- Right: a 24px icon inside a 48px padded pressable.
- Wrong: a 24px pressable that matches the 24px icon exactly.

| Element | Drawn size | Hit area |
|---------|-----------|----------|
| Icon button | 24-32px | 44-48px via padding |
| Text link | any | 44px tall band |
| List row | full width | 48-56px tall |
| Checkbox / radio | 20-24px | 44-48px tappable |
| Close (X) | 24px | 44px minimum |
| Tab item | 24-28px icon | full tab width, ~49px tall (iOS) |

---

## 2. Where the thumb reaches

About half of phone use is one-handed, so the screen is not uniformly easy to touch. It splits into bands by how far the thumb has to travel.

```
┌───────────────────────────────┐
│  STRETCH  back · menu · settings   │  top — needs a reach
├───────────────────────────────┤
│  COMFORT  content · secondary      │  middle — natural
├───────────────────────────────┤
│  EASY     primary CTA · tab bar    │  bottom — the thumb's home arc
└───────────────────────────────┘
            [ home ]
```

For a right-handed grip the easy region also skews right; a left grip mirrors it. Design for both hands, or assume right-dominant and keep critical actions centered-low.

```
right hand:    stretch  stretch  ok
               stretch  ok       easy
               ok       easy     easy
               easy     easy     easy
```

### Placement guide

| Element | Put it | Because |
|---------|--------|---------|
| Primary CTA | bottom, center or right | easiest thumb arc |
| Tab bar | bottom | where the thumb rests |
| FAB | bottom right | natural for right hand |
| Navigation / settings | top | used less often |
| Destructive action | top, away from the arc | hard to reach = hard to fat-finger |
| Cancel / dismiss | top left | convention plus safety |
| Confirm / done | top right or bottom | convention |

### Tall phones

On screens above ~6 inches the top ~40% becomes a one-handed dead zone. Counter it with reachability gestures, pull-down sheets, bottom-anchored navigation, floating buttons, or gesture alternatives to top-bar actions.

---

## 3. How a tap differs from a click

| Aspect | Click | Tap |
|--------|-------|-----|
| Feedback timing | 100ms is tolerable | feels instant only under ~50ms |
| Pre-feedback | hover then click | nothing until contact |
| Cost of error | retry is trivial | retry feels broken |
| Precision | high | low |
| Secondary menu | right-click | long press |
| Cancel | Esc key | tap outside / swipe away |

### Feedback the tap must produce

```
on press  → respond within ~50ms
            ├─ background/highlight change
            ├─ slight scale-down (0.95-0.98)
            ├─ ripple (Android)
            └─ optional haptic — but never nothing

if the work takes > ~100ms
            ├─ show a spinner or progress
            ├─ disable the control to block double-taps
            └─ use optimistic UI where it is safe
```

### The occlusion problem

Because the finger covers the target, feedback rendered *under* the finger is invisible, which raises the error rate. Counter it by surfacing feedback above the touch point (tooltips), offsetting for precision tasks, using a magnifier for text selection, or simply making targets big enough that exact placement does not matter.

---

## 4. Reading gestures

Gestures are invisible. Nothing on screen announces them, there is no hover hint, and many users never discover them at all. So a gesture is a *shortcut*, never the only route.

```
swipe to delete   → also expose a delete button or menu
pull to refresh   → also offer a refresh control
pinch to zoom     → also provide zoom buttons
```

### Conventional meanings

| Gesture | Common meaning | Typical use |
|---------|----------------|-------------|
| Tap | activate | primary action |
| Double tap | zoom / like | quick action |
| Long press | context menu / select mode | secondary options |
| Horizontal swipe | navigate / reveal actions | list row actions |
| Swipe down | refresh / dismiss | pull-to-refresh, sheets |
| Pinch | zoom | maps, images |
| Two-finger drag | scroll inside a scroll | nested scrolling |

### Make gestures discoverable

```
┌──────────────────────────────────────┐
│ ⠿  List row with hidden actions   →  │  edge peek + drag handle
└──────────────────────────────────────┘
```

- Good: a sliver of color peeking at the edge, a drag handle for reordering, a one-time onboarding hint.
- Bad: a hidden gesture with no affordance at all.

### Platform gesture differences

| Gesture | iOS | Android |
|---------|-----|---------|
| Back | left edge swipe | system back button / gesture |
| Share | action sheet | share sheet |
| Context menu | long press | long press |
| Dismiss modal | swipe down | back button or swipe |
| Delete in list | swipe, then tap delete | swipe with immediate undo |

---

## 5. Haptics

Done well, haptics confirm an action without the user looking, add a sense of quality, aid blind users, and lower error rates. Done poorly (too often) they become noise and fatigue.

### iOS feedback types

| Type | Strength | When |
|------|----------|------|
| selection | light | picker scrub, toggle |
| light | light | minor actions |
| medium | medium | standard tap confirm |
| heavy | strong | important completion, drop |
| success | pattern | task succeeded |
| warning | pattern | needs attention |
| error | pattern | action failed |

### Android feedback types

| Type | When |
|------|------|
| CLICK | standard tap |
| HEAVY_CLICK | important action |
| DOUBLE_CLICK | confirmation |
| TICK | scrub / scroll detents |
| LONG_PRESS | long-press trigger |
| REJECT | invalid action |

### When to fire, when to stay quiet

```
fire haptics for          stay silent for
────────────────          ───────────────
button taps               every scroll tick
toggles                   every list row
picker / slider steps     background events
pull-to-refresh trigger   passive displays
successful completion      anything high-frequency
errors and warnings        (haptic fatigue)
crossing a swipe threshold
significant state changes
```

### Match intensity to weight

| Action weight | Haptic | Example |
|---------------|--------|---------|
| browsing | light or none | scrolling |
| standard | medium / selection | tap, toggle |
| significant | heavy / success | confirm, complete |
| critical / destructive | heavy / warning | delete, pay |
| failure | error pattern | failed action |

---

## 6. Cognitive load on mobile

| Factor | Desktop | Mobile | What to do |
|--------|---------|--------|------------|
| Attention | focused sessions | constant interruption | design for micro-sessions |
| Environment | controlled | anywhere | survive glare and noise |
| Multitasking | many windows | one app visible | finish the task in-app |
| Input speed | fast typing | slow tapping | minimize input, smart defaults |
| Recovery | easy undo | harder | prevent errors, ease recovery |

### Lowering the load

- One clear primary action per screen.
- Progressive disclosure — show only what is needed now.
- Smart defaults — prefill whatever you can.
- Chunking — break long forms into steps.
- Recognition over recall — show choices, do not make users remember.
- Persist state across interruptions and backgrounding.

### Miller and Hick, on a phone

Working memory is tighter on mobile (call it 5±1 rather than 7±2) because of distraction, so cap tab bars at five, menu levels around five, and visible progress steps around five. And because more choices slow decisions — worse on a small screen where scrolling hides options — start with three to five, push the rest behind "More," order by frequency, and remember prior selections.

---

## 7. Touch accessibility

Users with motor impairments may have tremors, use assistive input, have limited reach, need more time, or trigger accidental touches. Respond with generous targets (48dp+), adjustable gesture timing, undo for destructive actions, and switch- and voice-control support.

### Spacing (WCAG 2.2, SC 2.5.8)

```
each target: ≥ 44px wide, ≥ 44px tall, ≥ 8px from its neighbours
unless it is inline in text, user-resizable, or essential with no alternative
```

### Accessible equivalents

| Gesture pattern | Accessible alternative |
|-----------------|------------------------|
| swipe actions | a menu of the same actions |
| drag and drop | select, then move |
| pinch zoom | zoom buttons |
| force touch | long press |
| shake | a button |

---

## 8. The feel of quality

Touch reads as "premium" when response is instant (<50ms), haptics are appropriate, animations hold 60fps, physics feel right, and (where fitting) sound reinforces the action.

| Emotion | Touch response |
|---------|----------------|
| success | success haptic + check / confetti |
| error | error haptic + shake |
| warning | warning haptic + attention color |
| delight | an unexpected, smooth motion |
| weight | a heavy haptic on a big action |

Trust is built when the same action always produces the same response, feedback never fails silently, sensitive actions feel secure, motion is never janky, and destructive actions ask first.

---

## 9. Checklists

**Every screen**
- [ ] All targets at least 44-48px
- [ ] Primary CTA in the thumb arc
- [ ] Destructive actions confirmed
- [ ] Visible alternative for every gesture
- [ ] Haptic on the important actions
- [ ] Visual response on tap
- [ ] Loading state for anything over ~100ms

**Before release**
- [ ] Tested on the smallest supported device
- [ ] Tested one-handed on a large phone
- [ ] Every gesture has a visible alternative
- [ ] Haptics verified on a real device
- [ ] Targets checked with accessibility settings on
- [ ] No tiny close buttons or icons

---

## 10. Quick card

```
Minimum target:   iOS 44pt · Android 48dp · WCAG 44px
Spacing:          ≥ 8 everywhere

Reach bands:      top = infrequent · middle = content · bottom = primary

Haptics:          light = select/toggle · medium = tap · heavy = confirm
                  success / error / warning = outcomes
```

---

> Every touch is a small exchange between a person and a device. Make it feel responsive and forgiving of real fingers — not built for a pixel-perfect pointer.
