# Mobile Decision Trees

> How to choose a framework, a state approach, storage, offline strategy, and auth.
> These are aids to reasoning, not answers to paste in. Every project bends them.

---

## 1. Choosing a framework

```
What are you building?
  │
  ├─ Need to ship fixes without store review?
  │     yes → React Native + Expo
  │             · Expo Go in development
  │             · EAS Update for production OTA
  │             · suits fast iteration and web-leaning teams
  │     no  → ↓
  │
  ├─ Need identical, bespoke UI on both platforms?
  │     yes → Flutter
  │             · its own rendering engine
  │             · one UI for iOS and Android
  │             · suits branded, visual products
  │     no  → ↓
  │
  ├─ Heavy native work (ARKit, HealthKit, specific sensors)?
  │     iOS only     → SwiftUI / UIKit
  │     Android only → Kotlin + Jetpack Compose
  │     both         → native UI with shared logic (Kotlin Multiplatform)
  │
  ├─ Existing web team on TypeScript?
  │     yes → React Native — familiar to React devs, big ecosystem
  │
  └─ Existing Flutter team?
        yes → Flutter — lean on the expertise you have
```

| Factor | React Native | Flutter | Native |
|--------|--------------|---------|--------|
| OTA updates | yes (Expo) | no | no |
| Learning curve | low for React devs | medium | higher |
| Performance | good | excellent | best |
| UI style | platform-native | identical | platform-native |
| Bundle size | medium | larger | smallest |
| Native access | bridges | channels | direct |

**Go native when** raw performance is paramount (games, 3D), OS integration is deep, platform features are the product, the team is native already, or long-term maintenance dominates. **Avoid native when** budget and time are tight, iteration must be fast, the UI should be identical across platforms, or the team is web-focused.

---

## 2. Choosing state management

### React Native

```
How much state, and what kind?
  ├─ small app, little shared state      → Zustand (or useState/Context)
  ├─ mostly server data                  → TanStack Query + Zustand
  ├─ large, many features                → Redux Toolkit + RTK Query
  └─ fine-grained, derived state         → Jotai (atoms)
```

### Flutter

```
How much state, and what kind?
  ├─ small / learning                    → Provider (or setState)
  ├─ modern, typed, testable             → Riverpod 2 (recommended for new work)
  ├─ enterprise, strict patterns         → BLoC (event → state)
  └─ quick prototype                     → GetX (with care; can sprawl)
```

### Patterns to avoid / prefer

Avoid putting everything in global state, mixing approaches, storing server data in local state, skipping normalization, leaning on Context for hot paths, or parking navigation in app state. Prefer a query library for server state, minimal local-first UI state, lifting only when shared, one approach per project, and state kept near where it is used.

---

## 3. Choosing navigation

```
How many top-level destinations?
  ├─ 2          → top tabs or a simple stack
  ├─ 3-5 equal  → tab bar / bottom navigation (most common, discoverable)
  ├─ 6+
  │     all important       → drawer
  │     some secondary      → tab bar + drawer hybrid
  └─ one linear flow         → stack only (onboarding, checkout)
```

| App type | Pattern | Why |
|----------|---------|-----|
| social | tab bar | frequent switching |
| commerce | tab bar + stack | categories as tabs |
| email | drawer + list-detail | many folders |
| settings | stack only | deep drill-down |
| onboarding | stack wizard | linear |
| messaging | tab (chats) + stack | threads |

---

## 4. Choosing storage

```
What kind of data?
  ├─ secrets (tokens, keys)        → secure storage
  │     iOS Keychain · Android EncryptedSharedPreferences · expo-secure-store / react-native-keychain
  ├─ preferences (settings, theme) → key-value
  │     iOS UserDefaults · Android SharedPreferences · AsyncStorage / MMKV
  ├─ structured (entities)         → database
  │     SQLite (expo-sqlite, sqflite) · Realm · WatermelonDB for big datasets
  ├─ large files (media, docs)     → file system
  │     iOS Documents/Caches · Android internal/external · expo-file-system / react-native-fs
  └─ cached API data               → query-library cache
        TanStack Query · Riverpod async · auto-invalidation
```

| Storage | Speed | Security | Capacity | For |
|---------|-------|----------|----------|-----|
| secure | medium | high | small | tokens, secrets |
| key-value | fast | low | medium | settings |
| SQLite | fast | low | large | structured data |
| file system | medium | low | very large | media, documents |
| query cache | fast | low | medium | API responses |

---

## 5. Choosing an offline strategy

```
How critical is offline?
  ├─ nice to have      → cache last data, show it stale
  │                       TanStack Query staleTime, a "last updated" label
  ├─ essential         → offline-first
  │                       local DB is the source of truth, sync when online,
  │                       conflict resolution, queued actions
  └─ real-time         → socket + local queue
                          optimistic updates, eventual consistency, careful conflicts
```

Implementation shapes:

```
cache-first             request → check cache → if stale, fetch → update
stale-while-revalidate  return cache now → fetch → refresh UI
offline-first           write local → queue → sync when online
sync engine             Firebase / Realm Sync / Supabase handle conflicts for you
```

---

## 6. Choosing an auth flow

```
What kind of auth?
  ├─ email + password   → JWT
  │                         refresh token in secure storage, access token in memory, silent refresh
  ├─ social login       → OAuth 2.0 + PKCE
  │                         platform SDKs, deep-link callback, Apple Sign-In required on iOS
  ├─ enterprise / SSO   → OIDC / SAML
  │                         system browser or web view, handle the redirect cleanly
  └─ biometric          → local auth unlocking a stored token
                            not a server-auth replacement; fall back to PIN/password
```

Never store tokens in AsyncStorage, in app state alone, in any plain local store, or in logs. Always store them in Keychain (iOS) / EncryptedSharedPreferences (Android) / SecureStore (Expo), biometric-gated where available.

---

## 7. Starter stacks by project

**Commerce** — React Native + Expo (OTA for pricing); tabs (Home, Search, Cart, Account); TanStack Query for products, Zustand for cart; SecureStore for auth, SQLite for cart cache; cache products and queue cart actions; email + social + Apple Pay. Lazy-load and cache product images, sync the cart across devices, keep checkout short, plan share deep links.

**Social / content** — RN or Flutter; tabs (Feed, Search, Create, Activity, Profile); TanStack Query for the feed, Zustand for UI; SQLite for feed cache and drafts; cache the feed, queue posts; social login (Apple required). Infinite scroll with memoized rows, background upload queue, deep-link push to content, sockets for live notifications.

**Productivity / SaaS** — Flutter (consistent UI) or RN; drawer or tabs; Riverpod/BLoC or Redux Toolkit; SQLite offline plus SecureStore; full offline editing with sync; SSO/OIDC. Decide a conflict-resolution policy, real-time vs eventual collaboration, large-file handling, and enterprise needs like MDM and compliance.

---

## 8. Checklists

**Before any project** — platforms defined, framework chosen against criteria, state approach picked, navigation chosen, storage mapped per data type, offline requirements set, auth designed, deep links planned.

**Questions to ask a vague brief:**

1. Do you need OTA updates without store review? → affects the framework (Expo = yes)
2. Must iOS and Android look identical? → affects the framework (Flutter = identical)
3. What is the offline requirement? → affects architectural complexity
4. Is there an existing backend or auth system? → affects auth and API design
5. Phones only, or tablets too? → affects navigation and layout
6. Enterprise or consumer? → affects auth (SSO), security, compliance

---

## 9. Decision anti-patterns

| Anti-pattern | Why it is bad | Instead |
|--------------|---------------|---------|
| Redux for a tiny app | huge overkill | Zustand or context |
| native for an MVP | slow to build | cross-platform MVP |
| drawer for 3 sections | hides navigation | tab bar |
| AsyncStorage for tokens | insecure | SecureStore |
| no offline thought | breaks on a train | plan from the start |
| one stack for every project | ignores context | evaluate each time |

---

## 10. Quick picks

```
Framework      OTA → RN+Expo · identical UI → Flutter · max perf → native · web team → RN
State          simple → Zustand/Provider · server → TanStack/Riverpod · enterprise → Redux/BLoC · atomic → Jotai
Storage        secrets → SecureStore · settings → AsyncStorage · structured → SQLite · API → query lib
```

---

> These trees are scaffolding for thought, not commandments. Each project has its own constraints. When the brief is vague, ask; then decide from real needs, not from habit.
