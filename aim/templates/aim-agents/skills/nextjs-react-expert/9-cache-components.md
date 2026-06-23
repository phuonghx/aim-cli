# 9. Cache Components — `use cache`, `cacheLife`, `cacheTag`, PPR

> [!IMPORTANT]
> Next.js 16+ only. Do not retrofit these onto Next.js 15 or earlier without
> confirming compatibility first.

## The shift in mental model

Next.js 16 moves caching from the route segment down to individual components and
functions. Instead of a blanket `export const revalidate = 3600`, you opt specific
pieces into caching and describe how fresh each one needs to be.

## 1. The `use cache` directive

Add `'use cache'` to a Server Component or an async function to cache its result.

### Keep it tight

Cache the smallest unit that needs it — a single data loader or one component — rather
than a whole page.

```tsx
// Cache one data-access function
async function loadArticle(slug: string) {
  'use cache'
  return db.article.findUnique({ where: { slug } })
}

// Cache one component
export default async function ArticleHeader({ slug }: { slug: string }) {
  'use cache'
  const article = await loadArticle(slug)
  return <h1>{article.title}</h1>
}
```

## 2. Freshness with `cacheLife`

`cacheLife` sets how long a cached value stays fresh and how long it may be served
stale, via a named profile.

```tsx
import { cacheLife } from 'next/cache'

async function loadExchangeRate() {
  'use cache'
  cacheLife('minutes') // refresh on a minute-ish cadence
  return fetchRate()
}
```

### Built-in profiles

| Profile | Use for |
| --- | --- |
| `seconds` | Rapidly changing data |
| `minutes` | Ordinary dynamic content |
| `hours` | Fairly stable content (articles) |
| `days` | Slow-moving content |
| `weeks` | Nearly static content |
| `max` | Cache until explicitly invalidated |
| `default` | Baseline (~1 year stale window) |

## 3. Targeted invalidation with `cacheTag`

Tag cached data so you can purge exactly that data later.

```tsx
import { cacheTag } from 'next/cache'

async function loadProfile(handle: string) {
  'use cache'
  cacheTag(`profile:${handle}`)
  return db.user.findUnique({ where: { handle } })
}
```

### Invalidate from a Server Action

```tsx
import { revalidateTag, updateTag } from 'next/cache'

export async function saveProfile(handle: string, patch: ProfilePatch) {
  await db.user.update({ where: { handle }, data: patch })

  // Option A — stale-while-revalidate: refresh in the background
  revalidateTag(`profile:${handle}`)

  // Option B — read-your-writes: update immediately so the author sees the change
  updateTag(`profile:${handle}`)
}
```

## 4. Partial Pre-Rendering (PPR)

PPR is stabilized in Next.js 16 behind the `cacheComponents` flag in `next.config.ts`.
The static shell is served instantly while dynamic, cached pieces stream in.

### Wrap dynamic cache components in `<Suspense>`

A `<Suspense>` boundary around each dynamic cache component is what lets PPR send the
static part first.

```tsx
import { Suspense } from 'react'
import { Skeleton } from '@/components/ui/skeleton'

export default function Page() {
  return (
    <main>
      <h1>Catalog</h1>
      <Suspense fallback={<Skeleton />}>
        <RecommendedForYou />
      </Suspense>
    </main>
  )
}
```
