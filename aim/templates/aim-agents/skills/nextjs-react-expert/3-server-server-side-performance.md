# 3. Server-Side Performance

> **Severity:** High
> **Why it matters:** Tightening server rendering and data access removes server-side
> waterfalls, shrinks the data crossing the RSC boundary, and gets bytes to the
> browser sooner.

Seven techniques covering server-action security, RSC payload size, request-scoped
and cross-request caching, parallel server fetching, and post-response work.

---

## 3.1 — Guard Server Actions like public endpoints

**Severity:** Highest · **Topics:** server actions, auth, authorization

A `"use server"` function is reachable from the network exactly like a route handler.
Anyone can invoke it directly, so authentication and authorization must live *inside*
the action — middleware, layout guards, and page checks do not protect it.

The Next.js docs are explicit: treat Server Actions with the same scrutiny as
public-facing API endpoints and confirm the caller is allowed to perform the
mutation.

**Wide open — no check at all:**

```typescript
'use server'

export async function removeProject(projectId: string) {
  await db.project.delete({ where: { id: projectId } })
  return { ok: true }
}
```

**Locked down — verify identity, then permission:**

```typescript
'use server'

import { getSession } from '@/lib/session'
import { Forbidden } from '@/lib/errors'

export async function removeProject(projectId: string) {
  const session = await getSession()
  if (!session) throw Forbidden('sign in required')

  const project = await db.project.findUnique({ where: { id: projectId } })
  if (!project) throw Forbidden('not found')

  // owners and admins only
  if (project.ownerId !== session.user.id && session.user.role !== 'admin') {
    throw Forbidden('not your project')
  }

  await db.project.delete({ where: { id: projectId } })
  return { ok: true }
}
```

**Validate the payload too** — never trust the shape of incoming data:

```typescript
'use server'

import { getSession } from '@/lib/session'
import { z } from 'zod'

const RenameInput = z.object({
  projectId: z.string().uuid(),
  name: z.string().min(1).max(120),
})

export async function renameProject(raw: unknown) {
  const input = RenameInput.parse(raw)          // 1. validate

  const session = await getSession()             // 2. authenticate
  if (!session) throw new Error('unauthorized')

  const project = await db.project.findUnique({ where: { id: input.projectId } })
  if (project?.ownerId !== session.user.id) {    // 3. authorize
    throw new Error('forbidden')
  }

  await db.project.update({                       // 4. mutate
    where: { id: input.projectId },
    data: { name: input.name },
  })
  return { ok: true }
}
```

Docs: https://nextjs.org/docs/app/guides/authentication

---

## 3.2 — Don't serialize the same data twice across the RSC boundary

**Severity:** Low · **Topics:** RSC, serialization, props

Serialization from server to client dedupes by *object reference*, not by value. Pass
the same reference and it's encoded once; create a new one and it's encoded again. So
do reshaping (`.toSorted()`, `.filter()`, `.map()`) on the client, not the server.

**Sends the list twice:**

```tsx
// six strings on the wire (two arrays of three)
<TagCloud tags={tags} tagsSorted={tags.toSorted()} />
```

**Sends it once:**

```tsx
<TagCloud tags={tags} />

// client side, derive locally
'use client'
const sorted = useMemo(() => [...tags].sort(), [tags])
```

**How nesting behaves** — the cost depends on the element type:

- `string[]` / `number[]` / `boolean[]`: **expensive** — the array and every
  primitive get duplicated.
- `object[]`: **cheap** — the array shell duplicates, but the nested objects are
  shared by reference.

```tsx
// primitives: everything duplicates
tags={['a','b']} sorted={tags.toSorted()}        // 4 strings sent

// objects: only the array shell duplicates
rows={[{id:1},{id:2}]} sorted={rows.toSorted()}  // 2 arrays + 2 shared objects, not 4
```

**Operations that mint a new reference** (and thus break dedup):

- Arrays: `.toSorted()`, `.filter()`, `.map()`, `.slice()`, `[...arr]`
- Objects: `{...obj}`, `Object.assign()`, `structuredClone()`, JSON round-trips

**Exception:** send derived data when the transform is expensive or the client never
needs the original.

---

## 3.3 — Cache across requests with an LRU

**Severity:** High · **Topics:** caching, LRU, cross-request

`React.cache()` only lives for one request. When the same data is needed across
sequential requests — a user clicks A, then clicks B seconds later — back it with an
in-memory LRU.

```typescript
import { LRUCache } from 'lru-cache'

const accountCache = new LRUCache<string, Account>({
  max: 500,
  ttl: 1000 * 60 * 5, // five minutes
})

export async function getAccount(id: string) {
  const hit = accountCache.get(id)
  if (hit) return hit

  const account = await db.account.findUnique({ where: { id } })
  if (account) accountCache.set(id, account)
  return account
}

// first request: hits the DB and stores the result
// follow-up request: served from memory, no query
```

On **Vercel Fluid Compute**, an LRU is especially effective because concurrent
requests can share one function instance and its cache — no Redis required. On
**classic serverless**, each invocation is isolated, so reach for Redis when you need
cross-process sharing.

Library: https://github.com/isaacs/node-lru-cache

---

## 3.4 — Send only the fields the client uses

**Severity:** High · **Topics:** RSC, serialization, props

Everything you hand a Client Component gets serialized into the HTML and into later
RSC payloads. That weight lands directly on page size and load time, so pass the
narrowest slice the client renders.

**Serializes all 40 fields to use one:**

```tsx
async function ProfilePage() {
  const user = await loadUser() // 40 fields
  return <Greeting user={user} />
}

'use client'
function Greeting({ user }: { user: User }) {
  return <h1>Hi, {user.firstName}</h1>
}
```

**Serializes one field:**

```tsx
async function ProfilePage() {
  const user = await loadUser()
  return <Greeting firstName={user.firstName} />
}

'use client'
function Greeting({ firstName }: { firstName: string }) {
  return <h1>Hi, {firstName}</h1>
}
```

---

## 3.5 — Parallelize server fetches through composition

**Severity:** Highest · **Topics:** RSC, parallel fetching, composition

Server Components in a single subtree resolve top-down. If a parent awaits before
rendering a child, the child's fetch can't begin until the parent's finishes.
Restructure so siblings fetch side by side.

**Nav waits for the parent's fetch:**

```tsx
export default async function Page() {
  const banner = await loadBanner()
  return (
    <div>
      <div>{banner}</div>
      <Nav />
    </div>
  )
}

async function Nav() {
  const links = await loadNav()
  return <nav>{links.map(renderLink)}</nav>
}
```

**Both fetch at once:**

```tsx
async function Banner() {
  const banner = await loadBanner()
  return <div>{banner}</div>
}

async function Nav() {
  const links = await loadNav()
  return <nav>{links.map(renderLink)}</nav>
}

export default function Page() {
  return (
    <div>
      <Banner />
      <Nav />
    </div>
  )
}
```

**With a `children` slot** so a layout doesn't block its content:

```tsx
function Shell({ children }: { children: ReactNode }) {
  return (
    <div>
      <Banner />
      {children}
    </div>
  )
}

export default function Page() {
  return (
    <Shell>
      <Nav />
    </Shell>
  )
}
```

---

## 3.6 — Dedupe per request with `React.cache()`

**Severity:** Medium · **Topics:** caching, request dedup

Wrap server functions in `React.cache()` so repeated calls within one request run
once. Auth checks and database reads benefit most.

```typescript
import { cache } from 'react'

export const getViewer = cache(async () => {
  const session = await getSession()
  if (!session?.user?.id) return null
  return db.user.findUnique({ where: { id: session.user.id } })
})
```

Call `getViewer()` from five components in the same request and the query still runs
exactly once.

**Pass primitives, not inline objects.** `React.cache()` compares arguments with
`Object.is`. A fresh object literal is a new reference every call, so it never hits.

```typescript
// never hits — new object each time
const loadOne = cache(async (q: { id: number }) =>
  db.row.findUnique({ where: { id: q.id } }),
)
loadOne({ id: 7 })
loadOne({ id: 7 }) // miss, runs again

// hits — primitives compare by value
const loadById = cache(async (id: number) =>
  db.row.findUnique({ where: { id } }),
)
loadById(7)
loadById(7) // hit
```

If you must pass an object, reuse the same reference:

```typescript
const key = { id: 7 }
loadById2(key) // runs
loadById2(key) // hit, same reference
```

**Next.js note:** `fetch` is already memoized per request — identical URL and options
are deduped automatically, so you don't need `React.cache()` for `fetch`. You still
need it for everything else: ORM queries (Prisma, Drizzle), heavy computation, auth
checks, filesystem reads — any non-`fetch` async work.

Docs: https://react.dev/reference/react/cache

---

## 3.7 — Move side effects past the response with `after()`

**Severity:** Medium · **Topics:** server, logging, analytics

Use `after()` to run work once the response has been sent, so logging, analytics, and
cleanup never delay the reply.

**Logging blocks the response:**

```tsx
export async function POST(request: Request) {
  await persist(request)

  const agent = request.headers.get('user-agent') ?? 'unknown'
  await writeAuditLog({ agent }) // user waits on this

  return Response.json({ status: 'ok' })
}
```

**Logging happens after the reply:**

```tsx
import { after } from 'next/server'
import { headers, cookies } from 'next/headers'

export async function POST(request: Request) {
  await persist(request)

  after(async () => {
    const agent = (await headers()).get('user-agent') ?? 'unknown'
    const sid = (await cookies()).get('sid')?.value ?? 'anon'
    writeAuditLog({ sid, agent })
  })

  return Response.json({ status: 'ok' })
}
```

Good fits: analytics, audit trails, notifications, cache invalidation, cleanup.
Notes: `after()` still runs when the response errors or redirects, and it works in
Server Actions, Route Handlers, and Server Components.

Docs: https://nextjs.org/docs/app/api-reference/functions/after
