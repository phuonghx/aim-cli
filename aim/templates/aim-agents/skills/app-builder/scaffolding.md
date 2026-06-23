# Scaffolding a Project

The folder layout and anchor files to lay down for a new project.

---

## Next.js Full-Stack Layout (tuned for Next.js 16)

```
project-name/
├── src/
│   ├── app/                        # Routing only — keep it thin
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css             # Tailwind v4 config (@theme) goes here
│   │   ├── (auth)/                 # Route group — auth screens
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (dashboard)/            # Route group — dashboard shell
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   └── api/                    # Route Handlers (webhooks / external only)
│   │       └── [resource]/route.ts
│   │
│   ├── components/                 # UI components
│   │   ├── ui/                     # Reusable primitives (Button, Input)
│   │   └── forms/                  # Client forms (useActionState)
│   │
│   ├── lib/                        # Shared helpers and server-only code
│   │   ├── db.ts                   # Prisma singleton client
│   │   ├── dal.ts                  # Data Access Layer (server-only, returns DTOs)
│   │   └── utils.ts                # Misc helpers
│   │
│   ├── actions/                    # Server Actions (mutations)
│   │
│   └── types/                      # Project-wide TypeScript types
│
├── prisma/
│   ├── schema.prisma
│   ├── migrations/
│   └── seed.ts
│
├── public/
├── proxy.ts                        # Network boundary (auth, redirects)
├── .env.example
├── .env.local
├── package.json
├── next.config.ts
├── tsconfig.json
└── README.md
```

---

## Why It's Laid Out This Way

| Idea | How it shows up |
|------|-----------------|
| **Routes stay thin** | `app/` does routing and layouts only; the real logic sits in `actions/` and `lib/` |
| **Server vs. client split** | Server-only code lives in `lib/dal.ts`, which stops it from sneaking into client bundles |
| **One data layer** | `lib/dal.ts` is the single place DB access happens, returning DTOs that are safe to reuse |
| **Mutations as Server Actions** | `actions/` holds the Server Actions that forms call through `useActionState` |
| **Route groups** | `(groupName)/` shares a layout without changing the URL |
| **Reusable UI** | `components/ui/` for primitives, `components/forms/` for client forms |

---

## The Anchor Files

| File | What it's for |
|------|---------------|
| `proxy.ts` | Next.js 16 network-boundary logic (auth, redirects). The old `middleware.ts`, now on the Node.js runtime |
| `package.json` | Dependencies |
| `next.config.ts` | Next.js config, written in TypeScript |
| `tsconfig.json` | TypeScript settings plus path aliases (`@/*`) |
| `.env.example` | A template for environment variables |
| `README.md` | Project notes |
| `.gitignore` | Files Git should skip |
| `prisma/schema.prisma` | The database schema |
| `src/app/globals.css` | Tailwind v4 theme via `@theme` — no `tailwind.config.js` |

---

## Path Aliases (tsconfig.json)

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/actions/*": ["./src/actions/*"]
    }
  }
}
```

---

## Where Each Thing Goes

| You're adding | Put it in |
|---------------|-----------|
| A new page or route | `app/(group)/page.tsx` |
| A reusable button or input | `components/ui/` |
| A client form | `components/forms/` |
| A mutation (server action) | `actions/` |
| A DB query / data fetch | `lib/dal.ts` |
| The Prisma client | `lib/db.ts` |
| A helper function | `lib/utils.ts` |
| Auth or redirect logic | `proxy.ts` |
