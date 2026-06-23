---
name: express-api
description: Guiding principles for an Express.js REST API starter — TypeScript, Prisma, JWT.
---

# Express.js API Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology |
|-------|------------|
| Runtime | Node.js 24 (Krypton LTS) |
| Framework | Express 5 (stable, the npm default) |
| Language | TypeScript |
| Database | PostgreSQL with Prisma |
| Validation | Zod |
| Auth | JWT plus bcrypt |

---

## Folder Layout

```
project-name/
├── prisma/
│   └── schema.prisma
├── src/
│   ├── app.ts           # Express app + middleware wiring (no listen)
│   ├── server.ts        # Bootstrap that calls listen() — split out for tests
│   ├── config/          # Environment
│   ├── routes/          # Route definitions, nothing more
│   ├── controllers/     # HTTP layer (req/res, calls into services)
│   ├── services/        # Business logic
│   ├── middlewares/
│   │   ├── auth.ts      # JWT verification
│   │   ├── error.ts     # Error handler
│   │   └── validate.ts  # Zod validation
│   ├── schemas/         # Zod schemas
│   └── utils/
├── tests/
└── package.json
```

---

## Middleware, In Order

| Order | Middleware |
|-------|------------|
| 1 | helmet (security headers) |
| 2 | cors |
| 3 | compression |
| 4 | body parsing |
| 5 | morgan (request logging) |
| 6 | routes |
| 7 | error handler (last, with the 4-argument signature) |

---

## Response Shape

| Outcome | JSON |
|---------|------|
| Success | `{ success: true, data: {...} }` |
| Failure | `{ error: "message", details: [...] }` |

---

## Getting Set Up

1. Make the project folder
2. `npm init -y`
3. Install: `npm install express prisma zod bcrypt jsonwebtoken`
4. Configure Prisma
5. `npm run db:push`
6. `npm run dev`

---

## Practices Worth Following

- Keep `app.ts` (wiring) separate from `server.ts` (`listen`) so tests can import the app cleanly
- Stick to the layered flow: routes → controllers → services
- Validate every input with Zod at the route boundary
- Register one central error handler last (Express 5 forwards rejected promises on its own, so you don't need a manual catch wrapper)
- Drive config from the environment
- Let Prisma give you type-safe DB access
