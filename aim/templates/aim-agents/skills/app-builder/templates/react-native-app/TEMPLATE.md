---
name: react-native-app
description: Guiding principles for a React Native mobile starter — Expo, TypeScript, navigation.
---

# React Native App Starter (2026)

> A current mobile base, set up for the New Architecture and React 19. Versions track the stable line as of 2026-05; NativeWind v5 is still pre-release, so pin it on purpose when you scaffold.

## Stack

| Piece | Technology | Version / Notes |
|-------|------------|-----------------|
| Core | React Native + Expo | SDK 56+ (New Architecture on) |
| Language | TypeScript | v5+ (strict mode) |
| UI logic | React | v19 (React Compiler, automatic memoization) |
| Navigation | Expo Router | file-based, universal links |
| Styling | NativeWind | v5 (pre-release, Tailwind v4 CSS-first) |
| State | Zustand + React Query | v5+ (async state) |
| Storage | Expo SecureStore | encrypted local storage |

---

## Folder Layout

Expo Router keeps `app/` for routes alone; everything else sits under `src/` behind the `@/*` alias.

```
project-name/
├── src/
│   ├── app/             # Expo Router — file-based routing ONLY
│   │   ├── _layout.tsx  # Root layout (Stack/Tabs config)
│   │   ├── index.tsx    # Main screen
│   │   ├── (tabs)/      # Route group for the tab bar
│   │   │   ├── _layout.tsx
│   │   │   ├── home.tsx
│   │   │   └── profile.tsx
│   │   ├── +not-found.tsx
│   │   └── [id].tsx     # Dynamic route (typed)
│   ├── components/
│   │   ├── ui/          # Primitives (Button, Text)
│   │   └── features/    # Larger composite components
│   ├── hooks/           # Custom hooks
│   ├── lib/
│   │   ├── api.ts       # Axios / fetch client
│   │   └── storage.ts   # SecureStore wrapper
│   ├── store/           # Zustand stores
│   └── constants/       # Colors, theme config
├── assets/              # Fonts, images
├── global.css           # NativeWind v5 entry: @import "tailwindcss"
├── babel.config.js      # NativeWind Babel preset
├── metro.config.js      # withNativeWind wrapper
└── app.json             # Expo config
```

---

## Navigation Patterns (Expo Router)

| Pattern | What it does | How |
|---------|--------------|-----|
| Stack | push/pop hierarchical navigation | `<Stack />` in `_layout.tsx` |
| Tabs | bottom tab bar | `<Tabs />` in `(tabs)/_layout.tsx` |
| Drawer | side slide-out menu | `expo-router/drawer` |
| Modals | overlay screens | `presentation: 'modal'` on a Stack screen |

---

## The Key Packages

| Package | Why it's here |
|---------|---------------|
| expo-router | file-based routing, Next.js style |
| nativewind | Tailwind classes inside React Native |
| react-native-reanimated | smooth animations that run on the UI thread |
| @tanstack/react-query | server state, caching, prefetching |
| zustand | lightweight global state (lighter than Redux) |
| expo-image | faster, cache-aware image rendering |

---

## Getting Set Up (2026)

1. Create the project:
   ```bash
   npx create-expo-app@latest my-app --template default
   cd my-app
   ```

2. Add the core dependencies:
   ```bash
   npx expo install expo-router react-native-safe-area-context react-native-screens expo-link expo-constants expo-status-bar
   ```

3. Add NativeWind v5 (pre-release, Tailwind v4 CSS-first):
   ```bash
   npm install nativewind@next tailwindcss react-native-reanimated
   ```

4. Wire up NativeWind across Babel, Metro, and CSS:
   - In `babel.config.js`: `presets: [["babel-preset-expo", { jsxImportSource: "nativewind" }], "nativewind/babel"]`.
   - In `metro.config.js`: wrap with `withNativeWind(config, { input: './global.css' })`.
   - Create `global.css` containing `@import "tailwindcss";` (theme via `@theme`, no `tailwind.config.js`).
   - Import `global.css` from `src/app/_layout.tsx`.

5. Run it:
   ```bash
   npx expo start -c
   # press 'i' for the iOS simulator or 'a' for the Android emulator
   ```

---

## Practices Worth Following

- **New Architecture**: set `newArchEnabled: true` in `app.json` to get TurboModules and the Fabric renderer.
- **Typed routes**: turn on Expo Router's typed routes so navigation like `router.push('/path')` is checked.
- **React 19**: with the Compiler on, you can drop most `useMemo` / `useCallback` calls.
- **Components**: build primitives (Box, Text) with NativeWind `className` so they're reusable.
- **Assets**: prefer `expo-image` over the default `<Image />` for caching and speed.
- **API**: always go through TanStack Query; don't fire calls straight from `useEffect`.
