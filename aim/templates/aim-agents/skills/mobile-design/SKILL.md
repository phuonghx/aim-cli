---
name: mobile-design
description: Guidance for designing and building mobile app interfaces on iOS and Android, including React Native and Flutter projects. Covers touch interaction, on-device performance, platform conventions, navigation, and offline behavior, and emphasizes reasoning about constraints over copying fixed values. Use it when creating native or cross-platform mobile UI, not when working on web apps.
---

# Mobile Design System

> Build for thumbs, not cursors. Respect the battery, respect the platform, survive offline.
> A phone is its own medium, not a shrunken desktop. Reason about the constraints first, then confirm the platform before you commit to anything.

---

## Validation script

There is one helper script. Run it; you do not need to read its source.

| Script | What it does | How to run |
|--------|--------------|------------|
| `scripts/mobile_audit.py` | Scans RN/Flutter source for touch, performance, and platform issues | `python scripts/mobile_audit.py <project_path>` |

---

## Read the reference files first

Do not begin coding until you have opened the references that apply to the work in front of you. Each one goes deeper than the summaries below.

### Read on every mobile task

| File | Focus |
|------|-------|
| [mobile-design-thinking.md](mobile-design-thinking.md) | **Start here.** Breaks the habit of reaching for memorized defaults |
| [touch-psychology.md](touch-psychology.md) | Fitts' Law, reach zones, gestures, haptics |
| [mobile-performance.md](mobile-performance.md) | 60fps lists and animations, memory, RN + Flutter |
| [mobile-backend.md](mobile-backend.md) | Push, offline sync, mobile-shaped APIs |
| [mobile-testing.md](mobile-testing.md) | Test pyramid, E2E on devices, platform splits |
| [mobile-debugging.md](mobile-debugging.md) | JS vs native crashes, DevTools, Logcat |
| [mobile-navigation.md](mobile-navigation.md) | Tabs, stacks, drawers, deep links |
| [mobile-typography.md](mobile-typography.md) | System fonts, dynamic text, readability |
| [mobile-color-system.md](mobile-color-system.md) | OLED, dark mode, sunlight, battery |
| [decision-trees.md](decision-trees.md) | Choosing framework, state, storage |

> The thinking guide comes before everything else. It is what keeps the output tailored to the project instead of generic.

### Read the one that matches your target

| Target | File | Covers |
|--------|------|--------|
| iPhone / iPad | [platform-ios.md](platform-ios.md) | HIG, SF Pro, SwiftUI conventions |
| Android | [platform-android.md](platform-android.md) | Material 3, Roboto, Compose conventions |
| Cross-platform | both of the above | Where the two diverge |

> iOS build? Open the iOS file. Android build? Open the Android file. Shipping both? Read both and branch on platform where it matters.

---

## Ask before you assume

When the request is vague, resist filling the gaps with your personal favorites. Surface the open questions instead.

| Unknown | Question to ask | Why it matters |
|---------|-----------------|----------------|
| Platform | iOS, Android, or both? | Touches nearly every decision |
| Framework | React Native, Flutter, or native? | Sets tooling and patterns |
| Navigation | Tabs, drawer, or pure stack? | Foundational UX shape |
| State | Zustand, Redux, Riverpod, BLoC, something else? | Architecture backbone |
| Offline | Must it work without a connection? | Drives the whole data layer |
| Devices | Phone only, or tablets too? | Changes layout complexity |

### Patterns to avoid

These are the failure modes that show up most often in generated mobile code.

**Performance**

| Avoid | Reason | Do instead |
|-------|--------|------------|
| `ScrollView` holding a long list | Mounts every row at once; memory balloons | `FlatList` / `FlashList` / `ListView.builder` |
| Inline `renderItem` | Fresh closure each render re-renders all rows | `useCallback` + `React.memo` |
| No `keyExtractor` | Index keys corrupt state on reorder | Stable unique id from the data |
| Skipping `getItemLayout` | Layout runs async, scroll stutters | Supply it for fixed-height rows |
| `setState` for everything (Flutter) | Rebuilds far more than needed | Scoped state, `const` constructors |
| `useNativeDriver: false` | Animation stuck behind the JS thread | Keep it `true` |
| `console.log` shipped to prod | Stalls the JS thread | Strip before release |

**Touch and UX**

| Avoid | Reason | Do instead |
|-------|--------|------------|
| Hit area under 44px | Misses and mis-taps | 44pt (iOS) / 48dp (Android) minimum |
| Targets crammed together | Neighbors get tapped | 8-12px of breathing room |
| Gesture as the only path | Locks out motor-impaired users | Always pair with a visible control |
| No loading feedback | Reads as frozen | Show progress for anything slow |
| No error recovery | User is stranded | Error state with a retry |
| Network failure ignored | Crash or hang offline | Degrade gracefully, serve cache |

**Security** — keep tokens out of `AsyncStorage` (use SecureStore / Keychain / EncryptedSharedPreferences); never hardcode API keys or log secrets; pin certificates in production.

**Architecture** — keep logic out of the view (service layer), default to local state and lift only when shared, plan deep links up front, and tear down every subscription and timer.

---

## Unify or diverge by platform

Share what users never see; honor platform habits for what they touch.

```
Share across platforms          Split per platform
──────────────────────          ──────────────────
Business logic                  Back navigation (edge swipe vs system back)
Data + networking layer         Gesture feel
Core feature set                Iconography (SF Symbols vs Material)
                                Pickers (native date/time)
                                Sheets and dialogs
                                Type (SF Pro vs Roboto)
                                Alert conventions
```

### Platform defaults at a glance

| Element | iOS | Android |
|---------|-----|---------|
| Default font | SF Pro / SF Compact | Roboto |
| Minimum target | 44 x 44 pt | 48 x 48 dp |
| Back | Left edge swipe | System back |
| Tab icons | SF Symbols | Material Symbols |
| Choice menu | Action sheet | Bottom sheet / dialog |
| Progress | Spinner | Linear (Material) |
| Refresh | UIRefreshControl | SwipeRefreshLayout |

---

## Reach and touch, in brief

Fingers are blunt where cursors are sharp. A fingertip covers roughly 7mm, so targets need real size and primary actions belong where the thumb naturally lands.

```
┌─────────────────────────────┐
│   stretch zone              │  back, menu, settings
├─────────────────────────────┤
│   comfortable zone          │  secondary actions, content
├─────────────────────────────┤
│   easy zone (thumb arc)     │  primary CTA, tab bar
└─────────────────────────────┘
          [ home ]
```

Mobile attention is also different: one task at a time, no hover state, frequent interruptions, slow text entry. Design for the interrupted user with one free hand. Full detail in [touch-psychology.md](touch-psychology.md).

---

## Performance, in brief

Only animate `transform` and `opacity` (GPU-composited). Animating width, height, margin, padding, or top/left forces layout and drops frames.

React Native lists, the short version:

```tsx
const Row = React.memo(({ item }: { item: Item }) => (
  <View style={styles.row}><Text>{item.title}</Text></View>
));

const renderRow = useCallback(({ item }: { item: Item }) => <Row item={item} />, []);

<FlatList
  data={rows}
  renderItem={renderRow}
  keyExtractor={(item) => item.id}     // stable id, never the index
  getItemLayout={(_, i) => ({ length: ROW_H, offset: ROW_H * i, index: i })}
  removeClippedSubviews
  maxToRenderPerBatch={10}
  windowSize={5}
/>
```

Flutter, the short version: mark anything static `const`, prefer builder lists, and rebuild narrowly with `ValueListenableBuilder` or a provider `.select`. Full guide in [mobile-performance.md](mobile-performance.md).

---

## Before you write code

Answer these in your head (or out loud) first. If you cannot, you have not read enough of the references yet.

- Platform: iOS / Android / both?
- Framework: RN / Flutter / SwiftUI / Kotlin?
- Which reference files did you actually open?
- Three principles you will apply here.
- Two anti-patterns you will steer clear of.

---

## Picking a framework

```
What is the project?
   ├── OTA updates + fast iteration + web-leaning team  → React Native + Expo
   ├── Bespoke pixel-perfect UI, performance-sensitive  → Flutter
   ├── Deep native, single platform
   │      ├── iOS only      → SwiftUI
   │      └── Android only  → Kotlin + Jetpack Compose
   ├── Already on React Native                          → React Native (bare)
   └── Already on Flutter                               → Flutter
```

Fuller trees (state, storage, offline, auth) live in [decision-trees.md](decision-trees.md).

---

## Checklists

**Project kickoff** — platform confirmed, framework chosen, navigation shape decided, state approach picked, offline needs understood, deep links planned, target devices defined.

**Per screen** — targets at least 44-48px, primary action within thumb reach, loading state present, error state with retry, offline behavior handled, platform conventions followed.

**Pre-release** — debug logs removed, secrets in secure storage, certificate pinning on, lists memoized with stable keys, listeners and timers cleaned up, verified on a low-end device, accessibility labels on every interactive element.

---

> Picture the worst case: weak signal, one hand, glaring sun, a dying battery, a user who is already distracted. Build for that, and the easy cases take care of themselves.
