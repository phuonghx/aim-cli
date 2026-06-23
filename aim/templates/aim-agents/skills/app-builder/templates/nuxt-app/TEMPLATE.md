---
name: nuxt-app
description: A Nuxt 4 full-stack starter — Vue 3, Pinia, Tailwind v4, Prisma.
---

# Nuxt 4 Full-Stack Starter (2026)

> A current full-stack base for Nuxt 4. Versions track the stable line as of 2026-05; pin to the current stable release when you scaffold.

## Stack

| Piece | Technology | Version / Notes |
|-------|------------|-----------------|
| Framework | Nuxt | v4+ (the app/ srcDir layout) |
| UI engine | Vue | v3 (stable) |
| Language | TypeScript | v5+ (strict mode) |
| State | Pinia | v3+ (setup-store syntax) |
| Database | PostgreSQL | via Prisma ORM |
| Styling | Tailwind CSS | v4 (@tailwindcss/vite plugin) |
| UI library | Nuxt UI | v3 (built for Tailwind v4) |
| Validation | Zod | schema validation |

---

## Folder Layout (Nuxt 4 convention)

Nuxt 4 points `srcDir` at `app/` by default, which keeps client code apart from `server/` and the root config.

```
project-name/
├── app/                  # App source (Nuxt 4 srcDir)
│   ├── assets/css/
│   │   └── main.css      # Tailwind v4 import
│   ├── components/       # Auto-imported
│   ├── composables/      # Auto-imported logic
│   ├── layouts/
│   ├── middleware/
│   ├── pages/            # File-based routing
│   ├── plugins/
│   ├── stores/           # Pinia stores
│   ├── app.vue           # Root component
│   └── app.config.ts     # Reactive runtime config
├── server/               # Nitro server
│   ├── api/              # API routes (e.g. /api/users)
│   ├── routes/           # Server routes
│   └── utils/            # Server-only helpers (Prisma client)
├── shared/               # Isomorphic code (types, Zod schemas)
├── prisma/
│   └── schema.prisma
├── public/
├── nuxt.config.ts
└── package.json
```

---

## Core Ideas (2026)

| Idea | What it means here |
|------|--------------------|
| **app/ srcDir** | Client code sits under `app/`, kept clear of `server/` and config |
| **shared/** | Isomorphic code — types and Zod validators usable by both the Vue app and Nitro |
| **Server engine** | Nitro-powered: API routes go in `server/api/`, the Prisma client in `server/utils/` |
| **Tailwind v4** | CSS-first; the theme lives in CSS via `@theme`, no `tailwind.config.js` |
| **Vapor mode** | An experimental VDOM-free renderer (not GA in 2026). Once it ships, opt in per component with `<script setup vapor>` |

---

## Environment Variables

| Variable | What it's for |
|----------|---------------|
| DATABASE_URL | Prisma's Postgres connection string |
| NUXT_PUBLIC_APP_URL | the canonical URL |
| NUXT_SESSION_PASSWORD | the session encryption key |

---

## Getting Set Up

1. Create the project:
   ```bash
   npx nuxi@latest init my-app
   ```

2. Add the core dependencies:
   ```bash
   npm install @pinia/nuxt @prisma/client zod
   npm install -D prisma
   ```

3. Set up Tailwind v4 with the first-party Vite plugin (not @nuxtjs/tailwindcss):
   ```bash
   npm install tailwindcss @tailwindcss/vite
   ```

   Then add to `nuxt.config.ts`:
   ```ts
   import tailwindcss from '@tailwindcss/vite'
   export default defineNuxtConfig({
     vite: { plugins: [tailwindcss()] },
     css: ['~/assets/css/main.css']
   })
   ```

4. Set the CSS in `app/assets/css/main.css`:
   ```css
   @import "tailwindcss";
   @theme {
     --color-primary: oklch(0.6 0.15 150);
   }
   ```

5. Run it:
   ```bash
   npm run dev
   ```

---

## Practices Worth Following

- **Fetching**: reach for `useFetch` / `useAsyncData` so data is SSR-friendly; keep `server: false` for client-only work.
- **State**: Pinia (`defineStore`) for global state; Nuxt's `useState` for small shared SSR values.
- **Validation**: write Zod schemas in `shared/` and reuse them on client forms and Nitro routes alike.
- **Type safety**: `$fetch` infers your API route types automatically.
- **Server-only**: create the Prisma client in `server/utils/` so it can't leak into the client bundle.
