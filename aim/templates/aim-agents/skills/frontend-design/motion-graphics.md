# Advanced Web Motion Graphics

> A working reference for high-end web animation: scroll effects, GSAP, Lottie, SVG, 3D, and particles.
> **Master the trade-offs first; the wow follows.**

---

## Choosing a Technique (start here)

Match the *need* to the lightest tool that satisfies it. Walk the branches top to bottom and stop at the first match.

```
NEED ──┐
       ├─[ entrance / hover / focus ]──────────► CSS @keyframes  (or Framer Motion)
       │
       ├─[ tied to scroll position ]──────────► native scroll-timeline  →  GSAP ScrollTrigger
       │
       ├─[ multi-step, brand-authored ]───────► Lottie  (authored in After Effects)
       │
       ├─[ logo draw / icon swap / morph ]─────► SVG  (dashoffset or path tween)
       │
       ├─[ depth, flips, tilt ]────────────────► CSS 3D  →  Three.js if it gets heavy
       │
       └─[ ambient background texture ]────────► tsParticles / Canvas
```

Rule of thumb: reach for a library only after CSS can't express it. Every dependency you add is weight the user downloads.

---

## Performance: the constraint behind every choice

Animation cost is dominated by *which properties* you touch, not how many elements move.

```
  budget-friendly                 budget-busting
  (compositor, GPU)               (forces layout/paint)
  ───────────────────             ───────────────────────
  transform  ──► ✔                width / height      ──► ✘
  opacity    ──► ✔                top / left / right  ──► ✘
  filter*    ──► ~ (sparingly)    margin / padding    ──► ✘
                                  box-shadow (heavy)  ──► ✘
```

Animate `transform` and `opacity` whenever you can — they skip reflow entirely. Anything that changes box geometry re-runs layout on every frame.

**Pre-ship checklist**

- [ ] Movement expressed through `transform` / `opacity` only
- [ ] `prefers-reduced-motion` honored with a calm fallback
- [ ] Heavy libraries (GSAP, Three.js, particle engines) loaded lazily
- [ ] Scroll handlers throttled (see scroll section)
- [ ] `will-change` flipped on just before a costly run, then cleared
- [ ] Verified on a low-spec phone, not just the dev machine

> `will-change` is a promise, not a free pass — leaving it on permanently keeps layers in memory and backfires.

---

## Scroll-Driven Animation

### Native CSS first

The platform now drives animation straight from scroll, no JavaScript loop required.

| Property | Drives from | Notes |
|----------|-------------|-------|
| `animation-timeline: scroll()` | the scroll container's progress | whole-page progress bars, etc. |
| `animation-timeline: view()` | an element passing through the viewport | per-element reveals |
| `animation-range` | entry / exit thresholds | bound the active window |

### Picking thresholds

| Marker | Fires when the element is… |
|--------|----------------------------|
| `entry 0%` | just touching the viewport edge |
| `entry 50%` | halfway in |
| `cover 50%` | dead center |
| `exit 100%` | fully gone |

**Guidelines**

- Trigger reveals around the **25% entry** mark — content is on screen before it animates.
- Parallax should track scroll *continuously*, not snap at a point.
- Pin sticky sections against the `cover` range.
- For any JS fallback, gate work behind `requestAnimationFrame` so you never run more than once per frame.

---

## GSAP (GreenSock)

A timeline engine for choreography that CSS can't sequence cleanly.

```
GSAP toolkit
  • Tween ........ one value, A → B
  • Timeline ..... many tweens, sequenced or overlapped
  • ScrollTrigger  scroll position scrubs playback
  • MorphSVG ..... one shape interpolated into another
  • easing ....... physics-flavored, beyond CSS cubic-beziers
  works on: any DOM node, plus SVG
```

### Core pieces

| Piece | Does |
|-------|------|
| **Tween** | animates a single A→B change |
| **Timeline** | orders and overlaps multiple tweens |
| **ScrollTrigger** | links scroll position to playback |
| **Stagger** | ripples one animation across a set of elements |

### Reach for GSAP when

- ✅ several animations must fire in a precise order
- ✅ reveals are scrubbed by scroll position
- ✅ exact, repeatable timing matters
- ✅ you need true SVG shape morphing

### Skip it when

- ❌ it's a plain hover or focus state → CSS
- ❌ you're on a tight mobile budget → it's not the lightest option

**Guidelines**

- Orchestrate with a Timeline; resist a pile of loose tweens.
- Stagger spacing: **0.05–0.15s** between items reads as a clean cascade.
- Start ScrollTrigger reveals at **70–80%** of viewport entry.
- **Kill timelines and triggers on unmount** — orphaned instances leak memory in SPAs.

---

## Lottie

### What it is

Vector animation shipped as JSON.

```
Lottie (.json)
  ↳ authored in After Effects, exported via Bodymovin
  ↳ tiny on the wire — beats GIF and video
  ↳ vector, so it stays crisp at any size
  ↳ playable: scrub, segment, pause from code
  ↳ runs on web, iOS, Android, React Native alike
```

### Good fits

| Scenario | Why Lottie earns its place |
|----------|----------------------------|
| **Loaders** | on-brand, smooth, featherweight |
| **Empty states** | turns a blank screen into something inviting |
| **Onboarding** | carries complex, multi-beat sequences |
| **Success / error cues** | a small moment of delight on feedback |
| **Animated icons** | identical motion across every platform |

**Guidelines**

- Aim for files under **100KB**.
- Loop only with intent — perpetual motion pulls focus.
- Ship a **static frame** for reduced-motion users.
- Defer the JSON load until it's actually needed.

**Where to get them:** the LottieFiles library, a custom After Effects + Bodymovin pipeline, or a Figma export plugin.

---

## SVG Animation

### Four techniques

| Technique | How | Typical use |
|-----------|-----|-------------|
| **Line draw** | animate `stroke-dashoffset` | logo reveals, signatures |
| **Morph** | interpolate one path into another | icon-to-icon transitions |
| **Transform** | `rotate` / `scale` / `translate` | interactive icons |
| **Color** | tween `fill` / `stroke` | state changes |

### How the line-draw trick works

```
   path length = L
   ┌───────────────────────────────┐
1) stroke-dasharray  = L      ─── one dash spanning the whole path
2) stroke-dashoffset = L      ─── push the dash off-screen (invisible)
3) animate offset → 0         ─── dash slides into view, "drawing" the line
   └───────────────────────────────┘
```

### Use SVG animation for

- ✅ logo reveals and brand moments
- ✅ icon state swaps (hamburger ↔ close)
- ✅ infographics and data viz
- ✅ interactive illustrations

### Avoid it for

- ❌ photoreal content → use video
- ❌ very dense scenes → performance suffers

**Guidelines**

- Read the path length **at runtime** (`getTotalLength()`) so the dash math is exact.
- Full draws land well at **1–3s**.
- `ease-out` feels the most natural.
- Keep fills understated so they support the line, not fight it.

---

## 3D with CSS Transforms

### The properties that matter

```
       viewer's eye
            ▲
            │  perspective: 500–1500px  (depth of the scene)
   ┌────────┴────────┐
   │  preserve-3d    │  children live in real 3D space
   │  rotateX/Y/Z    │  spin around each axis
   │  translateZ     │  push toward / away from the eye
   │  backface:hidden│  hide the reverse side on flips
   └─────────────────┘
```

### Patterns worth knowing

| Pattern | Where it shines |
|---------|-----------------|
| **Card flip** | reveals, flashcards, product fronts/backs |
| **Hover tilt** | interactive cards with a sense of depth |
| **Parallax layers** | hero sections, immersive scroll |
| **3D carousel** | galleries and sliders |

**Guidelines**

- Perspective dialing: **800–1200px** reads subtle, **400–600px** reads dramatic.
- Combine just `rotate` + `translate`; over-stacking transforms muddies the result.
- Set `backface-visibility: hidden` on anything that flips.
- **Check it in Safari** — its 3D rendering diverges from other engines.

---

## Particle Effects

### Pick a mood

| Style | Reads as | Fits |
|-------|----------|------|
| **Geometric** | technical, networked | SaaS and tech |
| **Confetti** | celebratory | success beats |
| **Snow / rain** | atmospheric | seasonal, moody |
| **Dust / bokeh** | dreamy | photography, luxury |
| **Fireflies** | magical | games, fantasy |

### Pick an engine

| Library | Sweet spot |
|---------|-----------|
| **tsParticles** | highly configurable, still light |
| **particles.js** | quick, simple backgrounds |
| **Canvas API** | hand-rolled, total control |
| **Three.js** | full 3D particle systems |

### Use particles for

- ✅ atmospheric hero backgrounds
- ✅ confetti bursts on success
- ✅ connected-node "network" visuals

### Keep them away from

- ❌ dense, content-first pages → distraction
- ❌ weak devices → battery and frame-rate hit

**Guidelines**

- Start near **30–50** particles — more reads as noise.
- Drift slowly and organically (**speed 0.5–2**).
- Hold opacity at **0.3–0.6** so they sit behind the content.
- Faint connector lines sell the "network" look.
- ⚠️ Cut the count hard, or disable entirely, on mobile.

---

## Anti-Patterns

| ✅ Do | ❌ Don't |
|-------|----------|
| Stagger and sequence | fire everything simultaneously |
| Begin with CSS | pull in a heavy lib for a trivial effect |
| Always ship a reduced-motion path | ignore `prefers-reduced-motion` |
| Hold 60fps | jam work onto the main thread |
| Tune particles to the brand | reuse the same field everywhere |
| Feature-detect on mobile | run desktop-grade effects on phones |

---

## Quick Reference

| Effect | Reach for | Weight |
|--------|-----------|--------|
| Loading spinner | CSS or Lottie | light |
| Staggered reveal | GSAP or Framer | medium |
| SVG line draw | CSS `stroke` | light |
| 3D card flip | CSS transforms | light |
| Particle backdrop | tsParticles | heavy |
| Scroll parallax | GSAP ScrollTrigger | medium |
| Shape morph | GSAP MorphSVG | medium |

---

> **Takeaway:** motion is a tool for meaning — feedback, wayfinding, delight, story — so spend it only where it earns its keep and its frames.
