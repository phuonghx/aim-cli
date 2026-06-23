---
name: electron-desktop
description: Guiding principles for an Electron desktop starter — cross-platform, React, TypeScript.
---

# Electron Desktop App Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology |
|-------|------------|
| Framework | Electron 42+ |
| UI | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Bundler | electron-vite plus electron-builder |
| IPC | type-safe, through contextBridge |

---

## Folder Layout

> The electron-vite layout — splitting main / preload / renderer — is the 2026 norm.

```
project-name/
├── src/
│   ├── main/            # Main process (lifecycle, windows, IPC handlers)
│   │   └── index.ts
│   ├── preload/         # contextBridge — the type-safe IPC surface
│   │   ├── index.ts
│   │   └── index.d.ts   # Ambient types shared with the renderer
│   └── renderer/        # React app
│       ├── index.html
│       └── src/
│           ├── main.tsx
│           ├── App.tsx
│           └── components/
├── resources/           # App icons / static assets (build time)
├── build/               # Builder assets (entitlements, icons)
├── electron.vite.config.ts
├── electron-builder.yml
└── package.json         # scripts: electron-vite dev | build | preview
```

---

## The Three Processes

| Process | Role |
|---------|------|
| Main | Node.js, system access |
| Renderer | Chromium, the React UI |
| Preload | the bridge, with context isolation |

---

## Core Ideas

| Idea | Why it matters |
|------|----------------|
| contextBridge | exposes APIs safely |
| ipcMain / ipcRenderer | talk between processes |
| nodeIntegration: false | security |
| contextIsolation: true | security |

---

## Getting Set Up

1. `npm create @quick-start/electron@latest {{name}} -- --template react-ts`
2. `cd {{name}} && npm install`
3. Add Tailwind v4: `npm install tailwindcss @tailwindcss/vite`
4. Declare your IPC types in `src/preload/index.d.ts`
5. `npm run dev`

---

## Build Targets

| Platform | Outputs |
|----------|---------|
| Windows | NSIS, Portable |
| macOS | DMG, ZIP |
| Linux | AppImage, DEB |

---

## Practices Worth Following

- Keep the secure defaults: `contextIsolation: true` (default since v12), `sandbox: true` (default since v20), `nodeIntegration: false` (default since v5) — never turn Node on for remote content
- Expose a tight API through `contextBridge.exposeInMainWorld`, never the raw `ipcRenderer`
- Check each IPC `sender` against an allowlist and set a strict CSP (`script-src 'self'`)
- Keep IPC type-safe by sharing types from `preload/index.d.ts` into the renderer
- Ship auto-updates via electron-updater
