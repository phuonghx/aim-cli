---
name: chrome-extension
description: Guiding principles for a Chrome extension starter — Manifest V3, React, TypeScript.
---

# Chrome Extension Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology |
|-------|------------|
| Manifest | V3 |
| UI | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Bundler | Vite with CRXJS (@crxjs/vite-plugin v2) |
| Storage | Chrome Storage API |

---

## Folder Layout

> With CRXJS and Vite, `manifest.config.ts` is the single source of truth and Vite resolves the entries from it.

```
project-name/
├── src/
│   ├── popup/           # { index.html, main.tsx, Popup.tsx }
│   ├── options/         # { index.html, main.tsx, Options.tsx }
│   ├── background/      # service-worker.ts (the MV3 service worker)
│   ├── content/         # { content-script.ts, content.css }
│   ├── components/      # Shared React
│   └── lib/
│       ├── storage.ts   # Chrome storage helpers
│       └── messaging.ts # Message passing
├── public/              # Static assets (icons)
├── manifest.config.ts   # defineManifest() — the typed manifest
├── vite.config.ts       # crx({ manifest }) + react + tailwind
└── package.json
```

---

## The Manifest V3 Pieces

| Piece | Role |
|-------|------|
| Service worker | background work |
| Content scripts | injected into pages |
| Popup | the user-facing UI |
| Options page | settings |

---

## Permissions

| Permission | What it grants |
|------------|----------------|
| storage | saving user data |
| activeTab | access to the current tab |
| scripting | injecting scripts |
| host_permissions | access to specific sites |

---

## Getting Set Up

1. `npm create vite@latest {{name}} -- --template react-ts`
2. Add CRXJS: `npm install -D @crxjs/vite-plugin@latest`
3. Add Chrome types: `npm install -D @types/chrome`
4. Write `manifest.config.ts` with `defineManifest`, then wire `crx({ manifest })` into `vite.config.ts`
5. `npm run dev` (HMR for popup, options, and content)
6. Load it in Chrome: `chrome://extensions` → Load unpacked → pick `dist/`

---

## Debugging Tips

| Task | How |
|------|-----|
| Debug the popup | right-click the icon → Inspect |
| Debug the background | Extensions page → Service worker |
| Debug content scripts | the page's DevTools console |
| Hot reload | `npm run dev` (CRXJS HMR) |

---

## Practices Worth Following

- Keep messaging type-safe
- Wrap Chrome APIs in promises
- Treat the MV3 background as a throwaway service worker — keep state in `chrome.storage` rather than module globals, and rely on event listeners and alarms instead of long-lived timers
- Ask for as few permissions as possible
- Scope content-script styles so they don't bleed into the host page
