---
name: nextjs-saas
description: Guiding principles for a Next.js SaaS starter (2026) — React 19, Server Actions, Auth.js v5.
---

# Next.js SaaS Starter (2026)

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology | Version / Notes |
|-------|------------|-----------------|
| Framework | Next.js | v16+ (App Router, React Compiler) |
| Runtime | Node.js | v24 (Krypton LTS) |
| Auth | Auth.js | v5 (`next-auth@beta`, the former NextAuth). Or Clerk |
| Payments | Stripe API | latest |
| Database | PostgreSQL | Prisma v7+ (serverless driver) |
| Email | Resend | with React Email |
| UI | Tailwind CSS | v4 (Oxide engine, no config file) |

---

## Folder Layout

```
project-name/
├── prisma/
│   └── schema.prisma    # Database schema
├── src/
│   ├── actions/         # Server Actions — these replace API routes for mutations
│   │   ├── auth-actions.ts
│   │   ├── billing-actions.ts
│   │   └── user-actions.ts
│   ├── app/
│   │   ├── (auth)/      # Route group: login, register
│   │   ├── (dashboard)/ # Route group: protected app shell
│   │   ├── (marketing)/ # Route group: landing, pricing
│   │   └── api/         # Reserved for webhooks and edge cases
│   │       └── webhooks/stripe/
│   ├── components/
│   │   ├── emails/      # React Email templates
│   │   ├── forms/       # Client components on useActionState (React 19)
│   │   └── ui/          # Shadcn UI
│   ├── lib/
│   │   ├── auth.ts      # Auth.js v5 config
│   │   ├── db.ts        # Prisma singleton
│   │   ├── data/        # Data Access Layer (server-only reads)
│   │   └── stripe.ts    # Stripe singleton
│   └── styles/
│       └── globals.css  # Tailwind v4 imports (CSS only)
└── package.json
```

---

## What Ships With It

| Capability | How it's done |
|------------|---------------|
| Auth | Auth.js v5 with passkeys and OAuth |
| Mutations | Server Actions, no API routes |
| Subscriptions | Stripe Checkout plus the Customer Portal |
| Webhooks | Stripe events processed asynchronously |
| Email | Transactional sends through Resend |
| Validation | Zod, run on the server |

---

## Data Model

| Model | Notable fields |
|-------|----------------|
| User | id, email, stripeCustomerId, subscriptionId, plan |
| Account | OAuth provider records (Google, GitHub, …) |
| Session | user sessions (database strategy) |

---

## Environment Variables

| Variable | What it's for |
|----------|---------------|
| DATABASE_URL | Prisma's Postgres connection string |
| AUTH_SECRET | the Auth.js v5 successor to NEXTAUTH_SECRET |
| STRIPE_SECRET_KEY | payments, server-side |
| STRIPE_WEBHOOK_SECRET | verifying webhooks |
| RESEND_API_KEY | sending email |
| NEXT_PUBLIC_APP_URL | the app's canonical URL |

---

## Getting Set Up

1. Create the project (Node 24):
   ```bash
   npx create-next-app@latest {{name}} --typescript --eslint
   ```

2. Pull in the core libraries:
   ```bash
   npm install next-auth@beta stripe resend @prisma/client
   ```

3. Wire up Tailwind v4 (in globals.css):
   ```css
   @import "tailwindcss";
   ```

4. Fill in `.env.local`.

5. Push the schema:
   ```bash
   npx prisma db push
   ```

6. Forward webhooks locally:
   ```bash
   npm run stripe:listen
   ```

7. Start it up:
   ```bash
   npm run dev
   ```
