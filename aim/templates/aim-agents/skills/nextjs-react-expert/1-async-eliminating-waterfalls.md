# 1. Killing Request Waterfalls

> **Severity:** Highest
> **Why it matters:** A waterfall is any place where one async call waits on another
> that didn't need to come first. Every link in that chain costs a full network round
> trip, so collapsing waterfalls is usually the single biggest speed-up available.

This file collects six techniques, from deferring an `await` to the Next.js 16
`after()` and `connection()` primitives.

---

## 1.1 — Push `await` into the branch that uses it

**Severity:** High · **Topics:** async, conditional fetching, early exit

If a function can return without touching some fetched value, don't fetch that value
up front. Awaiting before a branch decision makes the fast path pay for the slow
path's data.

**Slower — every caller waits, even the ones that bail out early:**

```typescript
async function loadDashboard(accountId: string, previewOnly: boolean) {
  const metrics = await fetchMetrics(accountId)

  if (previewOnly) {
    // We already paid for metrics we are about to throw away.
    return { preview: true }
  }

  return renderDashboard(metrics)
}
```

**Faster — fetch only on the path that needs the data:**

```typescript
async function loadDashboard(accountId: string, previewOnly: boolean) {
  if (previewOnly) {
    return { preview: true }
  }

  const metrics = await fetchMetrics(accountId)
  return renderDashboard(metrics)
}
```

The same idea applies to validation gates. Check the cheap condition first and only
reach for the expensive lookup once you know you'll use it:

```typescript
// Slower: permissions fetched before we even know the order exists
async function cancelOrder(orderId: string, actorId: string) {
  const grants = await loadGrants(actorId)
  const order = await loadOrder(orderId)

  if (!order) return { error: 'missing' }
  if (!grants.canCancel) return { error: 'denied' }

  return await markCancelled(order, grants)
}

// Faster: short-circuit on the missing order before touching permissions
async function cancelOrder(orderId: string, actorId: string) {
  const order = await loadOrder(orderId)
  if (!order) return { error: 'missing' }

  const grants = await loadGrants(actorId)
  if (!grants.canCancel) return { error: 'denied' }

  return await markCancelled(order, grants)
}
```

The payoff grows when the early exit is common or the deferred work is heavy.

---

## 1.2 — Parallelize partial dependencies

**Severity:** Highest · **Topics:** async, dependency graph, `better-all`

When some tasks depend on others but not all of them, a flat `Promise.all` leaves
gaps. The goal is to let every task start the instant its own inputs are ready.

**Leaves the table on the floor — the dependent fetch waits for *both* roots:**

```typescript
const [account, settings] = await Promise.all([
  fetchAccount(),
  fetchSettings(),
])
const usage = await fetchUsage(account.id) // started too late
```

**Tighter — `better-all` schedules each task as early as possible:**

```typescript
import { all } from 'better-all'

const { account, settings, usage } = await all({
  async account() { return fetchAccount() },
  async settings() { return fetchSettings() },
  async usage() {
    // `usage` only needs `account`, so it starts as soon as that resolves
    return fetchUsage((await this.$.account).id)
  },
})
```

**No-dependency version** — kick off every promise first, then await together:

```typescript
const accountP = fetchAccount()
const usageP = accountP.then(a => fetchUsage(a.id))

const [account, settings, usage] = await Promise.all([
  accountP,
  fetchSettings(),
  usageP,
])
```

Library: https://github.com/shuding/better-all

---

## 1.3 — Don't serialize work inside route handlers

**Severity:** Highest · **Topics:** route handlers, server actions, parallelism

In a Route Handler or Server Action, fire off every independent call immediately.
Capture the promise now and await it only when you genuinely need the value.

**Serial — settings wait on auth, payload waits on both:**

```typescript
export async function GET() {
  const session = await getSession()
  const settings = await getSettings()
  const payload = await getPayload(session.user.id)
  return Response.json({ payload, settings })
}
```

**Overlapped — auth and settings travel together:**

```typescript
export async function GET() {
  const sessionP = getSession()
  const settingsP = getSettings()

  const session = await sessionP
  const [settings, payload] = await Promise.all([
    settingsP,
    getPayload(session.user.id),
  ])

  return Response.json({ payload, settings })
}
```

For knottier dependency chains, reach for `better-all` (see 1.2).

---

## 1.4 — `Promise.all` for fully independent calls

**Severity:** Highest · **Topics:** async, parallelism, promises

If three calls share no data, running them one after another triples your latency
for no reason.

**Three sequential round trips:**

```typescript
const profile = await fetchProfile()
const orders = await fetchOrders()
const reviews = await fetchReviews()
```

**One round trip's worth of waiting:**

```typescript
const [profile, orders, reviews] = await Promise.all([
  fetchProfile(),
  fetchOrders(),
  fetchReviews(),
])
```

---

## 1.5 — Place `Suspense` boundaries deliberately

**Severity:** High · **Topics:** Suspense, streaming, layout stability

Rather than awaiting data at the top of a component and blocking everything below it,
let the shell render immediately and stream the data-dependent part in behind a
boundary.

**Blocks the whole page on one query:**

```tsx
async function ReportPage() {
  const rows = await fetchReport() // nothing renders until this resolves

  return (
    <Shell>
      <Toolbar />
      <ReportTable rows={rows} />
      <Footer />
    </Shell>
  )
}
```

**Shell paints right away; only the table waits:**

```tsx
function ReportPage() {
  return (
    <Shell>
      <Toolbar />
      <Suspense fallback={<TableSkeleton />}>
        <ReportTable />
      </Suspense>
      <Footer />
    </Shell>
  )
}

async function ReportTable() {
  const rows = await fetchReport() // scoped to this subtree only
  return <Table rows={rows} />
}
```

**Sharing one fetch across siblings** — start the request once, pass the promise
down, and unwrap it with `use`:

```tsx
function ReportPage() {
  const reportP = fetchReport() // begins immediately, not awaited here

  return (
    <Shell>
      <Toolbar />
      <Suspense fallback={<TableSkeleton />}>
        <ReportTable reportP={reportP} />
        <ReportTotals reportP={reportP} />
      </Suspense>
      <Footer />
    </Shell>
  )
}

function ReportTable({ reportP }: { reportP: Promise<Report> }) {
  const report = use(reportP)
  return <Table rows={report.rows} />
}

function ReportTotals({ reportP }: { reportP: Promise<Report> }) {
  const report = use(reportP) // same promise, no second fetch
  return <Totals value={report.total} />
}
```

**Skip this pattern when:** the data drives layout decisions, the content is
above-the-fold and SEO-critical, the query is tiny and fast, or a late-arriving chunk
would shift the page and annoy the user. The trade is earlier paint against possible
layout shift — pick based on the screen.

---

## 1.6 — `after()` and `connection()` on Next.js 16+

**Severity:** High · **Topics:** Next.js 16, runtime hints

### Defer side effects with `after()`

Work that doesn't shape the first render — analytics, audit logs, outbound email —
shouldn't be awaited inline. Schedule it for after the response goes out.

```tsx
import { after } from 'next/server'

export default async function ProductPage({ id }: { id: string }) {
  const product = await loadProduct(id) // needed for the response

  after(() => {
    // runs once the response is already on its way
    recordView(product.id)
  })

  return <ProductView product={product} />
}
```

### Mark dynamic intent with `connection()`

Call `connection()` to tell the framework a component is genuinely dynamic, so it
won't be pre-rendered statically and the rest of the page can stream around it.

```tsx
import { connection } from 'next/server'

async function LivePrice({ ticker }: { ticker: string }) {
  await connection() // explicitly dynamic
  return <Price value={await fetchQuote(ticker)} />
}
```
