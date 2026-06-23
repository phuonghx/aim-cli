# Thinking Before Building (Mobile)

> A guard against autopilot. The goal is to reason about the project in front of you instead of replaying the most common answer from memory.
> Treat this the way a frontend specialist treats layout decomposition: a deliberate pause before the first line of code.

---

## The reasoning pass

Run this loop before any mobile project. It is short on purpose; the point is to interrupt reflex, not to produce paperwork.

1. **Name your assumptions.** What have you already decided without being told? Write them down, then challenge each one.
2. **Spot the autopilot.** Is this choice a memorized default? If so, is it actually the best fit here, or just the most familiar?
3. **Split by platform.** Did you think about iOS and Android as separate problems, or blur them into one?
4. **Walk each interaction.** Did you examine taps and gestures one at a time, applying reach and target-size reasoning?
5. **Weigh the cost.** What does each component cost in memory, CPU, and battery? Is the obvious solution actually cheap?

---

## Defaults to distrust

The patterns below are the ones models reach for automatically because they dominate training data. None of them are wrong in general; all of them are wrong *sometimes*. Before using any of them, pause and name an alternative.

**Navigation reflexes**
- Tab bar for every app — would a drawer or a plain stack serve this better?
- Exactly five tabs — would three do? Past six, is a drawer the honest answer?
- "Home" pinned to the far left — does observed usage support that?
- Hamburger menu — is it hiding things users actually need often?

**State reflexes**
- Redux by default — would Zustand or Jotai cover it with less ceremony?
- Global store for everything — is most of this really local state?
- Nested context providers — would atoms re-render less?
- BLoC on every Flutter screen — is Riverpod a lighter fit?

**List reflexes**
- FlatList as the automatic pick — is FlashList faster for this data?
- A big `windowSize` "just in case" — is it justified?
- `removeClippedSubviews` everywhere — always, or only some screens?
- `ListView.builder` — would `ListView.separated` read cleaner with dividers?

**UI reflexes**
- FAB locked to bottom-right — is bottom-left kinder to left-handed reach?
- Pull-to-refresh on every list — does this list even need it?
- Swipe-to-delete from one side only — which side actually fits?
- Bottom sheet for every modal — would a full screen suit heavy content better?

---

## Decomposing a screen

Before designing a screen, answer the questions below for it. If you cannot, you do not understand the screen well enough yet.

- **Main action** — what is the one thing the user came to do, and is it within thumb reach?
- **Tap targets** — list each tappable element, its size, and the spacing between them. Any mis-tap risk?
- **Scrolling content** — is there a list? Which virtualized component, and why that one? Roughly how many items? Fixed height (so `getItemLayout`/`itemExtent` helps)?
- **State** — is local state enough, do you need to lift it, or is something genuinely global? Justify global.
- **Platform splits** — anything that should differ on iOS vs Android?
- **Offline** — should this screen function without a connection? What gets cached?
- **Cost** — any heavy components, anything that needs memoization, any animation worth profiling?

---

## Interrogating a pattern

For each default you are tempted by, run the matching question.

**Navigation**

| Tempted to... | Ask | Consider instead |
|---------------|-----|------------------|
| Use a tab bar | How many destinations? | 3 → few tabs; 6+ → drawer |
| Ship five tabs | Are they equally important? | A "More" tab, or a drawer hybrid |
| Use bottom nav | Tablet support? | Navigation rail |
| Lean on stack nav | Did you plan deep links? | Make the URL shape mirror the nav shape |

**State**

| Tempted to... | Ask | Consider instead |
|---------------|-----|------------------|
| Reach for Redux | How complex is this really? | Zustand (simple), TanStack Query (server) |
| Make it global | Is it truly global? | Lift locally, or a context selector |
| Add a provider | Will re-renders bite? | Atom-based (Zustand/Jotai) |
| Use BLoC | Is the boilerplate earning its keep? | Riverpod |

**Lists**

| Tempted to... | Ask | Consider instead |
|---------------|-----|------------------|
| Use FlatList | Is perf critical here? | FlashList |
| Write a plain renderItem | Is it memoized? | useCallback + React.memo |
| Key by index | Does order change? | Key by `item.id` |
| Use ListView | Need dividers? | ListView.separated |

**UI**

| Tempted to... | Ask | Consider instead |
|---------------|-----|------------------|
| Pin a FAB bottom-right | Which hand? | Respect handedness / a11y settings |
| Add pull-to-refresh | Does this list need it? | Only where it earns its place |
| Use a bottom sheet | How much content? | Full-screen modal for a lot |
| Add a swipe action | Will users find it? | Pair it with a visible control |

---

## The honesty test

Ask yourself the following before committing to a solution. A "yes" to any first clause means stop and rethink.

- Did I pick this because "that is how I always do it"? → Stop; list alternatives.
- Is this a pattern I have simply seen a lot? → Is it genuinely right *here*?
- Did I write it on reflex without thinking? → Step back and decompose.
- Did I weigh an alternative at all? → If not, find two, then choose.
- Did I reason per platform? → If not, separate iOS and Android.
- Did I consider the runtime cost? → If not, estimate memory/CPU/battery.
- Does this actually fit this project's context? → If not, adapt it.

---

## Let context drive the shape

Different app categories pull toward different defaults. Use these as starting hypotheses, not rules.

**Commerce** — tabs (Home, Search, Cart, Account); memoized, image-heavy product grids; aggressive image caching; persisted cart and cached catalog; a secure, short checkout.

**Social / content** — tabs (Feed, Search, Create, Activity, Profile); infinite scroll with rich, memoized rows; feed render speed is the bottleneck; cached feed and draft posts; real-time updates and heavy media handling.

**Productivity / SaaS** — drawer or an adaptive shell (tabs on phone, rail on tablet); data tables and forms; reliable sync; full offline editing; conflict resolution and background sync.

**Utility** — minimal navigation, sometimes a single stack; few or no lists; fast cold start; core function works offline; widgets and shortcuts matter.

**Media / streaming** — tabs (Home, Search, Library, Profile); horizontal carousels over vertical feeds; preloading and buffering; download management for offline; background playback and casting.

---

## Walking a gesture

Before adding any gesture, answer these.

- **Discoverability** — how will users find it? Is there a visual hint, an onboarding cue, and (always) a button equivalent?
- **Convention** — what does this gesture mean on iOS, on Android, and are you fighting either platform's meaning?
- **Accessibility** — can a motor-impaired user perform it? Is there a VoiceOver/TalkBack path and switch-control support?
- **Conflicts** — does it clash with system gestures (iOS edge-back, Android back, home-indicator swipe)? Is it consistent with your other gestures?
- **Feedback** — is haptic defined, is the visual response enough, is sound warranted?

---

## Substance over a checked box

Ticking a box is not the same as getting it right.

| Looks done | Actually ask |
|------------|--------------|
| "Target is 44px" (but jammed in a corner) | Can a thumb reach it one-handed? |
| "I used FlatList" (but never memoized) | Is the scroll genuinely smooth? |
| "Platform-specific nav" (only the icons changed) | Does iOS feel iOS, and Android feel Android? |
| "Offline supported" (generic error toast) | What can the user actually *do* offline? |
| "Loading state exists" (bare spinner) | Does the user know how long to wait? |

> Passing the checklist is not the objective. A good mobile experience is.

---

## A short commitment

Fill this in at the start of a project. If you cannot, you do not yet understand it — go back and ask.

- One default I will deliberately *not* use here, and why.
- The single thing this project most needs me to get right.
- One concrete iOS/Android difference I will implement.
- The area I will profile and optimize.
- The hardest or most unusual constraint in this project.

---

## Gate before coding

A final pass before writing anything:

- Decomposed the screen?
- Interrogated the patterns I reached for?
- Passed the honesty test?
- Let context, not habit, drive decisions?
- Walked each gesture?
- Written the commitment above?

---

> A choice made "because that is how it is always done" is a choice made without thinking. Every project, context, and user is specific. Reason first; then write code.
