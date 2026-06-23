---
name: nextjs-fullstack
description: Guiding principles for a Next.js full-stack starter — App Router, Prisma, Tailwind v4.
---

# Next.js Full-Stack Starter (2026)

> The versions below track the stable line as of 2026-05. When you scaffold, pin to whatever the current stable release is.

## Stack

| Piece | Technology | Version / Notes |
|-------|------------|-----------------|
| Framework | Next.js | v16+ (App Router, Turbopack) |
| Runtime | Node.js | v24 (Krypton LTS) |
| Language | TypeScript | v5+ (strict mode) |
| Database | PostgreSQL | via Prisma ORM (serverless-friendly) |
| Styling | Tailwind CSS | v4.0 (zero-config, CSS-first) |
| Auth | Auth.js v5 (`next-auth@beta`) or Clerk | route protection through `proxy.ts` |
| UI logic | React 19 | Server Actions, useActionState |
| Validation | Zod | shared across APIs and forms |

---

## Folder Layout

```
project-name/
├── prisma/
│   └── schema.prisma       # Database schema
├── src/
│   ├── app/
│   │   ├── (auth)/         # Route groups for login / register
│   │   ├── (dashboard)/    # Protected area
│   │   ├── api/            # Route Handlers — webhooks / external only
│   │   ├── layout.tsx      # Root layout (metadata, providers)
│   │   ├── page.tsx        # Landing page
│   │   └── globals.css     # Tailwind v4 config (@theme) lives here
│   ├── components/
│   │   ├── ui/             # Reusable UI (Button, Input)
│   │   └── forms/          # Client forms built on useActionState
│   ├── lib/
│   │   ├── db.ts           # Prisma singleton client
│   │   ├── utils.ts        # Helpers
│   │   └── dal.ts          # Data Access Layer (server-only)
│   ├── actions/            # Server Actions (mutations)
│   └── types/              # Project-wide TS types
├── public/
├── next.config.ts          # Config in TypeScript
└── package.json
```

---

## Core Ideas

| Idea | What it means here |
|------|--------------------|
| Server Components | The default; they run on the server and hit Prisma directly, no API layer needed |
| Server Actions | Handle form mutations and stand in for the API routes you'd otherwise write; call them from `action={}` |
| React 19 hooks | `useActionState`, `useFormStatus`, and `useOptimistic` manage form state |
| Data Access Layer | Keeps DB logic in one place and hands back DTOs that are safe to reuse |
| Tailwind v4 | No `tailwind.config.js` — the theme is declared straight in CSS |

---

## Environment Variables

| Variable | What it's for |
|----------|---------------|
| DATABASE_URL | Postgres connection string for Prisma |
| NEXT_PUBLIC_APP_URL | The app's public URL |
| AUTH_SECRET | Auth.js v5 session secret (default auth path) |
| NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY | Auth, if you go with Clerk instead |
| CLERK_SECRET_KEY | Clerk's server-side secret (Clerk path only) |

---

## Getting Set Up

1. Spin up the project:
   ```bash
   npx create-next-app@latest my-app --typescript --tailwind --eslint
   # Answer Yes to App Router
   # src directory is optional — this starter uses it
   ```

2. Add the database and validation packages:
   ```bash
   npm install prisma @prisma/client zod
   npm install -D ts-node # needed for seed scripts
   ```

3. Set up Tailwind v4 if it isn't already:
   Confirm `src/app/globals.css` uses the import syntax rather than a config file:
   ```css
   @import "tailwindcss";

   @theme {
     --color-primary: oklch(0.5 0.2 240);
     --font-sans: "Inter", sans-serif;
   }
   ```

4. Bring up the database:
   ```bash
   npx prisma init
   # edit schema.prisma
   npm run db:push
   ```

5. Start the dev server:
   ```bash
   npm run dev --turbo
   # --turbo turns on Turbopack
   ```

---

## Practices Worth Following (2026)

- **Reading data**: await Prisma right inside Server Components. Skip `useEffect` for the first load.
- **Writing data**: pair Server Actions with React 19's `useActionState` so loading and error states come for free, instead of hand-rolling `useState`.
- **Type safety**: reuse the same Zod schema for a Server Action's input check and its client form.
- **Safety**: run input through Zod before it ever reaches Prisma.
- **Styling**: lean on Tailwind v4's CSS variables to make theming dynamic.
