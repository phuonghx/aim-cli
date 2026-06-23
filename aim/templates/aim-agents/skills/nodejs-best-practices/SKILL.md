---
name: nodejs-best-practices
description: Guides decision-making for modern Node.js backend work, covering framework choice, async modeling, validation, error handling, and security trade-offs rather than fixed snippets. It frames each choice around deployment target, concurrency shape, and team context. Use it when standing up a Node.js service, weighing Express vs. Fastify vs. Hono vs. NestJS, or designing async and validation layers.
---

# Node.js Backend Decisions

The aim here is judgment, not recipes. Identical projects rarely exist, so resist reaching for the same stack and layout every time. When the requirements leave a choice open, surface the trade-off and ask before committing.

## Picking a framework

Start from where the code will run and how much structure the team needs, then narrow:

- Functions at the edge (Vercel, Cloudflare, Netlify) reward tiny footprints and fast cold starts -- reach for **Hono**.
- Throughput-sensitive HTTP services where every millisecond counts favor **Fastify** (its schema-driven serialization is a real edge; still measure against your own routes).
- Teams that want opinionated structure, dependency injection, and decorators out of the box lean toward **NestJS**.
- Brownfield systems or cases needing the widest middleware catalog stay on **Express**.
- A frontend already in play (Next.js) often makes **route handlers or tRPC** the path of least resistance.

Questions worth answering before you decide: Where does this deploy? Does cold-start latency show up in the SLO? What has the team shipped before? Is there existing code that constrains the choice?

## Choosing the runtime layer

**TypeScript without a build step.** Recent Node LTS strips types from `.ts` files on the fly, so `node server.ts` runs directly. The catch: only erasable syntax works -- `enum`, runtime `namespace`, and constructor parameter properties will throw. When you need those, run through `tsx` instead. This is handy for one-off scripts and lean services.

**Modules.** New code should be ESM (`import`/`export`) -- it tree-shakes better and is the direction the ecosystem is moving. Stick with CommonJS (`require`) only when an existing codebase or a stubborn dependency forces it.

**Which runtime.** Node remains the safe default with the deepest ecosystem. Bun is worth a look when raw speed and an integrated toolchain matter; Deno appeals when you want TypeScript and a permissions model built in.

## Shaping the architecture

For anything that will grow, separate concerns into layers so each has one job:

```
HTTP handler   -> parses the request, validates input, returns the response
   |
Service        -> business rules, framework-agnostic, orchestrates the work
   |
Repository     -> talks to the database or external store, nothing else
```

The payoff is real: layers can be tested in isolation, the data store can be swapped without rewriting logic, and responsibilities stay legible. That said, a 40-line script or a throwaway prototype does not need this -- before adding structure, ask whether the thing is likely to outlive the week.

## Handling errors

Centralize it. Define your own error classes, throw them from wherever the problem is detected, and catch them once at the top (an error-handling middleware). The client and the logs see different things on purpose:

- **To the caller:** the right status code, a stable error code for programmatic handling, and a message safe to display -- never a stack trace or internal detail.
- **To the logs:** the full trace, request context, the acting user when known, and a timestamp.

Map situations to status codes deliberately:

| Situation | Code |
|-----------|------|
| Malformed or invalid input | 400 |
| Missing/invalid credentials | 401 |
| Authenticated but not permitted | 403 |
| Resource absent | 404 |
| State or uniqueness conflict | 409 |
| Schema-valid but breaks a business rule | 422 |
| Our fault -- log everything | 500 |

## Modeling async work

Match the construct to the shape of the work:

- `await` in sequence when each step depends on the last.
- `Promise.all` to fan out independent calls and wait for all.
- `Promise.allSettled` when some of those calls are allowed to fail.
- `Promise.race` for timeouts or first-wins responses.

Keep the event loop in mind. Async buys you nothing for CPU-bound work -- it only helps while the process waits on I/O:

```
Helped by async (waiting):    DB queries, HTTP calls, disk reads, sockets
Not helped (computing):       hashing, image work, heavy math
                              -> move these to worker threads or a separate service
```

Two rules that prevent most stalls: never call the synchronous variants (`readFileSync` and friends) on a hot path, and stream large payloads instead of buffering them whole.

## Validating input

Validate at every boundary where untrusted data enters: incoming request bodies and params, anything about to hit the database, responses from third-party APIs, uploaded files, and environment variables at startup. Treat "internal" data as untrusted too.

For the validator itself: **Zod** is the TypeScript-first default with strong inference; **Valibot** wins when bundle size is tight thanks to tree-shaking; **ArkType** targets the performance-critical path; **Yup** fits when it already lives in a React form. Whatever you pick, fail early and return messages specific enough to act on.

## Security baseline

Walk this list on every service:

- [ ] Every input validated at its boundary
- [ ] Parameterized queries only -- no string-built SQL
- [ ] Passwords hashed with argon2 or bcrypt
- [ ] JWTs verified for signature and expiry on every request
- [ ] Rate limiting in front of abusable endpoints
- [ ] Security headers applied (e.g. Helmet)
- [ ] HTTPS everywhere in production
- [ ] CORS scoped to known origins
- [ ] Secrets in environment variables, never in the repo
- [ ] Dependencies audited on a schedule

The underlying stance: trust nothing crossing the boundary -- query strings, bodies, headers, cookies, uploads, and external API responses all get checked.

## Testing

Spend effort where failure hurts:

| Layer | Focus | Typical tools |
|-------|-------|---------------|
| Unit | business logic | `node:test`, Vitest |
| Integration | endpoints end to end | Supertest |
| E2E | full user flows | Playwright |

Prioritize critical paths (auth, payments, core flows), then edge cases (empty inputs, boundaries), then failure handling. Skip the trivia -- framework internals and one-line getters do not need tests. Node's built-in runner (`node --test`) covers most unit needs with no extra dependency, plus watch mode and coverage.

## Common traps

Avoid: defaulting Express onto a fresh edge project, synchronous I/O in production, business logic stuffed into handlers, skipped validation, hard-coded secrets, trusting external data unchecked, and blocking the loop with CPU work.

Prefer: choosing the framework for the situation at hand, asking about preferences when they are unclear, layering anything that will grow, validating everywhere input arrives, sourcing secrets from the environment, and profiling before you optimize.

## Before you write code

- [ ] Confirmed the user's stack preference?
- [ ] Picked the framework for *this* context, not by habit?
- [ ] Accounted for the deployment target?
- [ ] Settled on an error-handling approach?
- [ ] Located every validation boundary?
- [ ] Weighed the security requirements?

Every project earns a fresh look. The patterns are scaffolding for thinking, not answers to copy.
