# Mobile Navigation Reference

> Choosing between tabs, stacks, and drawers; deep linking; back handling; transitions.
> Navigation is the skeleton of the app — get it wrong and everything else feels broken.

---

## 1. Picking a structure

```
What shape is the app?
  ├─ 3-5 equal top-level sections   → tab bar / bottom nav   (social, commerce, utility)
  ├─ deep, hierarchical content     → stack                  (settings, email folders)
  ├─ more than 5 destinations       → drawer                 (Gmail, complex enterprise)
  ├─ a single linear flow           → stack only             (checkout, onboarding)
  └─ tablet / foldable              → navigation rail + list-detail   (mail, notes on iPad)
```

---

## 2. Tab bar

**Use it when** there are 3-5 destinations of roughly equal importance, users switch between them often, each tab owns an independent stack, and sessions are short. **Avoid it when** there are more than five destinations, the destinations form a clear hierarchy, usage would be lopsided, or the content is sequential.

```
iOS tab bar
  49pt (83pt with home indicator) · max 5 · SF Symbols 25pt · always-on labels · tint indicator

Android bottom nav
  80dp · 3-5 items · Material Symbols 24dp · always-on labels · pill + filled-icon indicator
```

### Preserve each tab's stack

Every tab keeps its own navigation history. A user who drills from Home into an item, jumps to Profile, then returns to Home should land back on that item — not the Home root.

```
implementation: React Navigation gives each tab its own navigator;
                Flutter uses IndexedStack to retain state.
Never reset a tab's stack on switch.
```

---

## 3. Stack

A stack is a pile of cards: push adds one on top, pop removes the top (back), replace swaps the current one, reset clears to a new root. New screens slide in from the trailing edge; back slides them out.

| Pattern | Use | How |
|---------|-----|-----|
| simple stack | linear flow | push each step |
| nested stack | a section with its own sub-navigation | a stack inside a tab |
| modal stack | a focused task | present modally |
| auth stack | login vs main app | conditional root |

### Back, by platform

```
iOS      left-edge swipe (system), optional nav-bar back, interactive pop;
         do not override the swipe without strong reason

Android  system back button/gesture, optional toolbar up, predictive back (14+);
         handle back at the Activity/Fragment level

Both     back always moves up the stack, never repurpose it,
         confirm before discarding unsaved data,
         deep links must allow a full back traversal
```

---

## 4. Drawer

**Use it when** there are more than five destinations, some are accessed infrequently, the app is feature-dense, you need branding or user info in the nav, or a large screen can keep the drawer pinned. **Avoid it when** there are five or fewer destinations, all are equally important, the app is simple and mobile-first, or discoverability is critical (a drawer is hidden by default).

```
modal drawer      slides over content with a scrim; edge-swipe or ☰; common on phones
permanent drawer  always visible on large screens; content shifts beside it
navigation rail   a narrow vertical strip of icons (+ optional labels), 80dp, for tablets
```

---

## 5. Modals

```
push (stack)                  modal
────────────                  ─────
slides horizontally           slides up (sheet)
part of the hierarchy         a separate task
back returns                  close (X) returns
same nav context              its own nav context
"drill in"                    "focus on a task"
```

Use a modal to create content, change settings, complete a transaction, run a self-contained flow, or perform a quick action.

| Type | iOS | Android | Use |
|------|-----|---------|-----|
| sheet | `.sheet` | bottom sheet | quick tasks |
| full screen | `.fullScreenCover` | full activity | complex forms |
| alert | Alert | Dialog | confirmations |
| action sheet | action sheet | menu / bottom sheet | choose an option |

Users expect to dismiss a modal via a close button, a swipe down (sheet), a tap on the scrim (for non-critical ones), or system back on Android. Only block dismissal to protect unsaved data.

---

## 6. Deep linking

Plan deep links from the start. They power push navigation, content sharing, marketing campaigns, search/Spotlight integration, widgets, and inter-app handoffs. Retrofitting them is painful — it forces a navigation refactor, exposes unclear screen dependencies, and complicates parameter passing.

```
scheme://host/path?params

myapp://product/123
https://myapp.com/product/123          (universal / app link)
myapp://checkout?promo=SAVE20
myapp://tab/profile/settings

the URL path should mirror the navigation path:
  myapp://home
  myapp://home/product/123
  myapp://home/product/123/reviews
```

Rules:

1. **Build the full stack.** A link to `myapp://product/123` should seat Home at the root, push Product on top, so back returns to Home.
2. **Respect auth.** If the target needs login, save the intent, route to login, then continue to the destination.
3. **Handle invalid links.** Fall back to home with a message; never crash or blank out.
4. **Be stateful.** During an active session, do not blow away the current stack — push on top, or ask first.

---

## 7. State persistence

```
persist            current tab, list scroll positions, form drafts,
                   recent stack, user preferences

do not persist     modal/dialog state, transient UI, stale data (refresh on return),
                   auth state (use secure storage)
```

```jsx
const [ready, setReady] = useState(false);
const [initialState, setInitialState] = useState();

useEffect(() => {
  (async () => {
    const saved = await AsyncStorage.getItem('NAV_STATE');
    if (saved) setInitialState(JSON.parse(saved));
    setReady(true);
  })();
}, []);

<NavigationContainer
  initialState={initialState}
  onStateChange={(state) => AsyncStorage.setItem('NAV_STATE', JSON.stringify(state))}
/>
```

---

## 8. Transitions

```
iOS       push → slide from trailing edge · modal → slide up or fade ·
          tab switch → cross-fade · interactive swipe-back

Android   push → fade + slide · modal → slide up ·
          tab switch → cross-fade or none · shared-element hero animations
```

Use defaults most of the time — for standard drill-downs, platform consistency, and hot paths. Reach for custom transitions only when brand identity calls for it, for shared-element connections, or for special reveals; keep them subtle and under ~300ms.

Shared-element transitions connect the same element across screens — a product image grows from its card into the detail view. Implement with a shared-element library (React Navigation), the Hero widget (Flutter), `matchedGeometryEffect` (SwiftUI), or shared-element transitions (Compose).

---

## 9. Anti-patterns

| Anti-pattern | Problem | Fix |
|--------------|---------|-----|
| inconsistent back | users cannot predict it | always pop the stack |
| hidden navigation | features go undiscovered | a visible tab/drawer trigger |
| deep nesting | users get lost | cap at 3-4 levels, add breadcrumbs |
| breaking swipe-back | frustrates iOS users | never override the gesture |
| no deep links | cannot share, weak notifications | plan from the start |
| resetting a tab stack | work lost on switch | preserve tab state |
| modal for a primary flow | cannot backtrack | use a stack |

Common generated-code mistakes: leaning on modals for everything, forgetting tab-state preservation, skipping deep links, overriding platform back, resetting stacks on tab switch, and ignoring predictive back (Android 14+). Use the platform's navigation patterns; do not reinvent them.

---

## 10. Checklists

**Architecture** — app shape decided, destination count known, deep-link scheme planned, auth integrated with navigation, large screens considered.

**Each screen** — back works (no dead end), deep link planned, state preserved across navigation, transition fits the relationship, auth handled.

**Before release** — all deep links tested, back works everywhere, tab state preserved, edge-back works (iOS), predictive back works (Android 14+), universal/app links configured, push deep links work.

---

> Done right, navigation is invisible — users do not think about *how* to get somewhere, they just arrive. If they notice the navigation at all, something is wrong.
