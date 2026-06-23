# Motion & Animation Playbook

> A thinking guide for UI motion — reason about each choice instead of pasting presets.
> **There are no magic numbers here. Internalize the *forces* behind good timing.**

---

## 1. The Decision Filter

Run every animation idea through one gate before you build it. If it clears all three, proceed; otherwise cut it.

- [ ] **Does it serve a job?** (confirm an action / point the eye / spark a moment of delight)
- [ ] **Is the speed honest?** (neither sluggish nor twitchy for what it does)
- [ ] **Did easing match intent?** (arriving vs. leaving vs. holding attention)
- [ ] **Will it stay smooth?** (lean on `transform` and `opacity`)
- [ ] **Does it bow to reduced-motion?** (a11y is non-negotiable)
- [ ] **Does it rhyme with the rest of the UI?** (shared timing language)
- [ ] **Is it a deliberate value, not your habitual default?**
- [ ] **If the visual style is ambiguous, did you ask first?**

### Habits to break

| Smell | Why it hurts |
|-------|--------------|
| Reusing identical durations on every project | Reads as generic, no craft |
| Motion with no message | Noise that taxes the user |
| Skipping `prefers-reduced-motion` | Excludes and nauseates people |
| Tweening layout-shifting properties | Jank on real hardware |
| A dozen things moving together | Chaos, nothing readable |
| Front-loaded delays before feedback | Feels broken, frustrates |

---

## 2. Duration: What Actually Sets the Clock

A duration is never a constant — it's a function of the situation. Five inputs push it up or down:

```
        slower  <───────────────────────────────>  faster
DISTANCE   long travel ........................... short hop
SIZE       big surface ........................... tiny element
COMPLEXITY many moving parts ..................... single change
WEIGHT     critical / must-notice ............... trivial / ambient
MOOD       calm, luxurious ...................... urgent, snappy
```

### Ballpark ranges per job

Treat these as starting brackets, not laws — nudge within them using the forces above.

| Job of the motion | Typical window | Rationale |
|-------------------|----------------|-----------|
| Tap/press acknowledgement | 50–100 ms | Under the eye's notice threshold |
| Micro-interactions | 100–200 ms | Felt, but never in the way |
| Everyday transitions | 200–300 ms | The comfortable default zone |
| Multi-part / involved moves | 300–500 ms | Long enough to track |
| Whole-page handoffs | 400–600 ms | Smooth scene change |
| **Signature / "wow" moments** | 800 ms+ | Layered, spring-driven, theatrical |

### Three questions that pick the number

1. What distance does the element cover?
2. How badly does the user *need* to register this change?
3. Is someone actively waiting on it, or is it happening in the background?

---

## 3. Easing: Shaping the Velocity Curve

Easing controls how speed evolves across the animation's lifetime. Get this wrong and even a well-timed move feels off.

```
LINEAR        ●━━━━━━━━━━●     even pace — robotic, mechanical
EASE-OUT      ●━━━━━━━─ ─●     bursts in, eases down — entrances
EASE-IN       ●─ ─━━━━━━━●     creeps then bolts — exits
EASE-IN-OUT   ●─ ━━━━━━ ─●     gentle on both ends — loops, accents
```

### Pairing easing to the moment

| Curve | Reach for it when… | Reads as |
|-------|--------------------|----------|
| **Ease-out** | something is coming on screen | landing, coming to rest |
| **Ease-in** | something is leaving | pulling away, vanishing |
| **Ease-in-out** | accenting or repeating | considered, fluid |
| **Linear** | nonstop motion (spinners, marquees) | steady, machine-like |
| **Bounce / elastic** | playful, characterful UI | lively, fun |

### The core rule, in CSS

```css
/* On the way in — decelerate into place */
.is-entering {
  animation-timing-function: ease-out;
}

/* On the way out — accelerate away */
.is-leaving {
  animation-timing-function: ease-in;
}

/* Looping or holding focus — smooth at both ends */
.is-looping {
  animation-timing-function: ease-in-out;
}
```

---

## 4. Micro-Interactions & Interactive States

### The four jobs a micro-interaction can do

```
( FEEDBACK )  "yes, that registered"
( GUIDANCE )  "here's what you can do"
( STATUS   )  "this is where things stand"
( DELIGHT  )  "a tiny spark of personality"
```

### Mapping states on an interactive control

```
  HOVER     →  gentle invitation   (raise, brighten, grow a touch)
  ACTIVE    →  tactile press       (shrink slightly, flatten shadow)
  FOCUS     →  unmistakable marker (ring / outline for keyboard users)
  LOADING   →  work in progress    (spinner or skeleton)
  SUCCESS   →  it worked           (checkmark, color flip)
```

### Rules of thumb

1. **React inside 100 ms** — past that, it stops feeling instant.
2. **Echo the gesture** — a tap might `scale(0.95)`; a hover might `translateY(-4px)` plus a soft glow.
3. **Confident yet smooth** — aim for "intentionally crafted," not flashy.
4. **Stay predictable** — the same action should always trigger the same response.

---

## 5. Loading & Waiting States

Pick your loading treatment by how long the wait runs and whether you can measure it.

| Wait length | What to show |
|-------------|--------------|
| Snappy (< 1 s) | Nothing — don't flash an indicator |
| Short (1–3 s) | A spinner or light animation |
| Drawn-out (3 s+) | A progress bar or skeleton |
| Length unknown | An indeterminate indicator |

### Skeletons — why they win

```
GOAL: shrink the *perceived* wait
  1. paint the layout's silhouette right away
  2. keep it alive with a faint shimmer or pulse
  3. swap in real content the moment it's ready
  →  reads faster than a bare spinner
```

### Determinate progress — when it earns its place

```
SHOW it for:                 SKIP it for:
  • actions the user kicked off    • near-instant work
  • up/downloads                   • silent background jobs
  • step-by-step flows             • first page paint (skeleton wins)
  • genuinely long operations
```

---

## 6. Page & View Transitions

### The governing principle

```
RULE: usher the old out quickly, bring the new in with care
  ── outgoing view dissolves fast
  ── incoming view animates in deliberately
  ── never let "everything move at once"
```

### Pattern picker

| Pattern | Best fit |
|---------|----------|
| **Fade** | The dependable default — works anywhere |
| **Slide** | Linear flows (next / previous) |
| **Scale** | Modals opening and closing |
| **Shared element** | Carrying a visual thread between views |

### Let direction echo navigation

```
where the user is going  →  which way it moves
  advancing           →  slides in from the right
  going back          →  slides in from the left
  drilling down       →  scales up out of center
  popping up a level  →  scales back down
```

---

## 7. Scroll-Triggered Motion

### Reveal as you go

```
WHY stagger content into view on scroll:
  + eases the upfront mental load
  + makes scrolling feel rewarding
  − it must never lag or stutter
  − always offer an off switch (a11y)
```

### Choosing the trigger line

| Fire when the element is… | Resulting feel |
|---------------------------|----------------|
| just touching the viewport | standard reveal |
| centered on screen | spotlight / emphasis |
| only partly in view | reveals sooner |
| fully in view | reveals later |

### What to animate, and how to keep it fast

- Compose from a small set: fade (`opacity`), rise (`transform`), grow (`transform`), or blends of these.
- Detect visibility with the **Intersection Observer** API — not scroll-event math.
- Restrict animated properties to **`transform` / `opacity`**.
- Dial it back on phones when needed.

---

## 8. Hover Feedback

### Fit the effect to the element

| Element | Effect | Message |
|---------|--------|---------|
| **Tappable card** | raise + shadow | "I'm interactive" |
| **Button** | shift color / brightness | "Click me" |
| **Image** | scale / zoom | "Look closer" |
| **Text link** | underline / recolor | "Go somewhere" |

### Keep in mind

1. **Advertise interactivity** — hover should announce "clickable."
2. **Restraint reads as polish** — small shifts usually beat big ones.
3. **Scale with weight** — a more important target can move more.
4. **Plan for no-hover** — touch devices never fire `:hover`, so don't hide essentials behind it.

---

## 9. Feedback Animations (Success & Error)

### Confirming success

```
celebrate in proportion:
  small action     →  quiet check or color nudge
  meaningful action →  a more visible flourish
  full completion  →  a satisfying, finished beat
  ...always in your brand's voice
```

### Surfacing errors

```
alert without alarming:
  • flip to a semantic red
  • a *brief* shake — keep it short
  • move focus to the offending field
  • say plainly what went wrong
```

### Timing temperament

- **Success** — let it breathe a touch; the user gets to enjoy it.
- **Error** — keep it brisk; never stall the path to fixing it.
- **Loading** — runs continuously until the work resolves.

---

## 10. Performance

### Cheap vs. expensive to animate

```
┌─ COMPOSITOR / GPU — cheap, buttery ───────────┐
│   transform : translate · scale · rotate      │
│   opacity   : 0 ──► 1                          │
└───────────────────────────────────────────────┘
┌─ FORCES LAYOUT/PAINT — costly, janky ─────────┐
│   width · height                              │
│   top · left · right · bottom                 │
│   margin · padding                            │
│   border-radius  (when animated)              │
│   box-shadow     (when animated)              │
└───────────────────────────────────────────────┘
```

### How to stay fast

1. **Prefer `transform` / `opacity`** wherever the effect allows.
2. **Steer clear of layout-triggering props** (anything resizing or repositioning the box).
3. **Apply `will-change` only as needed** — it's a hint, not a free pass; overuse backfires.
4. **Profile on weak hardware**, not just your dev box.

### Honor the user's motion setting

```css
@media (prefers-reduced-motion: reduce) {
  /* respect the request: trim or kill decorative motion */
  /* keep only what's essential to understanding */
}
```

---

> **Bottom line:** motion is a message — if a movement isn't saying something useful to the user, it shouldn't ship.
