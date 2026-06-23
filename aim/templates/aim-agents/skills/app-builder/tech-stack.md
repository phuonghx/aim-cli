# Choosing a Tech Stack (2026)

The go-to stack for web apps, plus the substitutes worth reaching for when requirements differ.

## Recommended Web Stack (2026)

```yaml
Frontend:
  framework: Next.js 16 (stable)
  language: TypeScript 5.7+
  styling: Tailwind CSS v4
  state: React 19 Actions / Server Components
  caching: Next.js 16 Cache Components (stable)
  bundler: Turbopack (stable for both dev and build)

Backend:
  runtime: Node.js 24 (Krypton LTS)
  framework: Next.js Route Handlers / Hono (when targeting the edge)
  validation: Zod / TypeBox

Database:
  primary: PostgreSQL
  orm: Prisma / Drizzle
  hosting: Supabase / Neon

Auth:
  provider: Auth.js (v5) / Clerk

Monorepo:
  tool: Turborepo 2.0
```

## When to Swap Something In

| Requirement | Go-to choice | Other solid picks |
|-------------|--------------|-------------------|
| Real-time | Supabase Realtime | Socket.io, Ably |
| File storage | Supabase Storage | Cloudinary, AWS S3 |
| Payments | Stripe | LemonSqueezy, Paddle |
| Email | Resend | SendGrid, Postmark |
| Search | Algolia | Typesense, Orama |
