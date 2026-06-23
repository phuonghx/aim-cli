# Mobile Testing Patterns

> Mobile testing is not web testing — different environment, different strategy.
> The focus here is *which* approach to use *when*, and why. Code is deliberately minimal.

---

## What makes mobile testing different

```
· real devices matter — emulators hide hardware-specific bugs
· iOS and Android behave differently — test both
· network conditions swing wildly
· performance and battery are under test
· the app lifecycle is real — backgrounded, killed, restored
· permissions and system dialogs interrupt
· interactions are touches, not clicks
```

---

## Common missteps

| Reflex | Why it misses | Better |
|--------|---------------|--------|
| Jest only | skips the native layer | Jest + on-device E2E |
| Enzyme | deprecated, web-shaped | React Native Testing Library |
| Cypress E2E | cannot drive native features | Detox / Maestro |
| mock everything | hides integration bugs | test on a real device |
| no platform tests | iOS and Android diverge | platform-specific cases |
| skip performance | mobile perf is critical | profile on a low-end device |
| only the happy path | mobile has more edges | offline, permissions, interrupts |
| chase 100% coverage | false confidence | a balanced pyramid |
| copy web patterns | wrong environment | mobile-specific tooling |

---

## 1. Choosing a tool

```
What are you testing?
  ├─ pure functions, helpers          → Jest (no mobile setup)
  ├─ a component in isolation
  │     React Native → React Native Testing Library
  │     Flutter      → flutter_test (widget tests)
  ├─ a component with hooks/context/nav
  │     React Native → RNTL + mocked providers
  │     Flutter      → integration_test
  ├─ a full user flow (login, checkout)
  │     Detox (RN, fast, reliable)
  │     Maestro (cross-platform, YAML)
  │     Appium (legacy, slow, last resort)
  └─ performance, memory, battery
        Flashlight (RN) · Flutter DevTools · device profiling (Xcode / Android Studio)
```

| Tool | Platform | Speed | Reliability | When |
|------|----------|-------|-------------|------|
| Jest | RN | high | high | unit, logic |
| RNTL | RN | high | medium | component |
| flutter_test | Flutter | high | high | widget |
| Detox | RN | medium | high | E2E, critical flows |
| Maestro | both | medium | medium | E2E, cross-platform |
| Appium | both | low | low | legacy fallback |

---

## 2. The pyramid

```
        E2E            10%   slow, expensive, essential (real device)
     Integration       20%   component + context
      Component        30%   isolated UI
        Unit           40%   pure logic, fastest, most stable
```

| Level | Why this share |
|-------|----------------|
| E2E 10% | slow and flaky, but catches integration bugs |
| Integration 20% | exercises real flows without the whole app |
| Component 30% | fast feedback on UI |
| Unit 40% | fastest and most stable, covers logic |

> 90% unit tests and 0% E2E means you are testing the wrong layer.

---

## 3. What belongs at each level

**Unit (Jest)** — test utility functions, reducers/stores, response transformers, validation, business rules. Do not test rendering, navigation, native modules (mock them), or third-party libraries.

**Component (RNTL / flutter_test)** — test that it renders, user interactions (tap, type, swipe), loading/error/empty states, accessibility labels, and prop-driven behavior. Do not test internal details, snapshot everything (reserve it for key components), brittle styling, or third-party internals.

**Integration** — test form submission, navigation between screens, state persisting across screens, API integration against a mocked server, and provider interactions. Do not test every path (push that to unit tests), real third-party services, or backend logic.

**E2E** — test the critical journeys (login, purchase, signup), offline→online transitions, deep links, push navigation, permission flows, and payments. Do not test every edge case (too slow), visual regression (use snapshots), non-critical features, or backend-only logic.

---

## 4. Platform differences

| Area | iOS | Android | Test both? |
|------|-----|---------|------------|
| back navigation | edge swipe | system back | yes |
| permissions | ask once, then settings | ask each time, with rationale | yes |
| keyboard | different look | different behavior | yes |
| date picker | wheel/modal | Material dialog | if custom |
| push format | APNs payload | FCM payload | yes |
| deep links | universal links | app links | yes |
| gestures | some unique | Material gestures | if custom |

```
per platform:
  unit + component tests (shared)
  E2E on a REAL device
    iOS:     a real iPhone, not just the simulator
    Android: a mid-range device, not a flagship
  platform-specific features tested separately
```

---

## 5. Offline and network

| Scenario | Verify |
|----------|--------|
| launch offline | shows cache or an offline message |
| drop mid-action | the action queues, nothing lost |
| reconnect | the queue syncs with no duplicates |
| slow (2G) | loading states and timeouts behave |
| flaky | retry and error recovery work |

```
how to exercise it
  unit         mock NetInfo, test the logic
  integration  mock API responses, test the UI
  E2E (Detox)  device.setURLBlacklist()
  E2E (Maestro) network conditions
  manual       Charles Proxy / Network Link Conditioner
```

---

## 6. Performance

| Metric | Target | How |
|--------|--------|-----|
| startup | < 2s | profiler, Flashlight |
| screen transition | < 300ms | DevTools |
| list scroll | 60fps | profiler + feel |
| memory | flat, no leaks | Instruments / Android Profiler |
| bundle size | minimize | bundler analysis |

```
when:  before release (required), after heavy features,
       after dependency upgrades, on slowness reports, optionally in CI

where: a real device (required), a low-end device (budget Android, old iPhone),
       never an emulator (it lies about performance), with production-scale data
```

---

## 7. Accessibility

| Element | Check |
|---------|-------|
| interactive elements | have an accessibilityLabel |
| images | alt text or a decorative flag |
| forms | labels linked to inputs |
| buttons | role = button |
| touch targets | ≥ 44 (iOS) / 48 (Android) |
| contrast | WCAG AA minimum |

```
automated  RN: jest-axe · Flutter: accessibility checks in tests · lint for missing labels
manual     navigate the whole app with VoiceOver / TalkBack ·
           test with enlarged text · test with reduced motion
```

---

## 8. CI/CD

| Stage | Tests | Devices |
|-------|-------|---------|
| PR | unit + component | none (fast) |
| merge to main | + integration | simulator/emulator |
| pre-release | + E2E | real devices (farm) |
| nightly | full suite | device farm |

| Service | Pros | Cons |
|---------|------|------|
| Firebase Test Lab | free tier, Google devices | Android-leaning |
| AWS Device Farm | wide selection | expensive |
| BrowserStack | good UX | expensive |
| local devices | free, reliable | limited variety |

---

## Checklists

**Before a PR** — unit tests for new logic, component tests for new UI, no stray logs in tests, green CI.

**Before release** — E2E on a real iOS device, E2E on a real Android device, tested on a low-end device, offline scenarios verified, performance acceptable, accessibility verified.

**Skip on purpose** — chasing 100% coverage (aim for meaningful coverage), every visual permutation (snapshots sparingly), third-party internals, backend logic (test it separately).

---

## Questions to ask first

1. What could break? → test that.
2. What is critical for users? → E2E that.
3. What is complex logic? → unit-test that.
4. What is platform-specific? → test both platforms.
5. What happens offline? → test that scenario.

> Good mobile testing is about testing the *right* things, not *everything*. A flaky E2E test is worse than none. One unit test that catches a real bug beats a hundred trivial passing ones.
