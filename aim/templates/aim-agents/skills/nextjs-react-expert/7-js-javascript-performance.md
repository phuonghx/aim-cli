# 7. JavaScript Micro-tuning

> **Severity:** Lower
> **Why it matters:** Individually small, these clean-ups add up in hot code — render
> loops, event handlers, and frequently called utilities. Apply them where a profiler
> points, not everywhere.

Twelve techniques.

---

## 7.1 — Don't thrash layout

**Severity:** Medium · **Topics:** DOM, reflow, layout thrashing

Reading a layout property (`offsetWidth`, `getBoundingClientRect()`,
`getComputedStyle()`) after a style write forces the browser into a synchronous
reflow. Interleave reads and writes and you pay for several.

**Fine — consecutive writes get batched:**

```typescript
function paint(el: HTMLElement) {
  el.style.width = '120px'
  el.style.height = '240px'
  el.style.background = 'teal'
  el.style.border = '1px solid black'
}
```

**Bad — each read forces a reflow:**

```typescript
function thrash(el: HTMLElement) {
  el.style.width = '120px'
  const w = el.offsetWidth   // reflow
  el.style.height = '240px'
  const h = el.offsetHeight  // reflow again
}
```

**Good — write everything, then read once:**

```typescript
function paint(el: HTMLElement) {
  el.style.width = '120px'
  el.style.height = '240px'
  el.style.background = 'teal'
  el.style.border = '1px solid black'

  const { width, height } = el.getBoundingClientRect() // single reflow
}
```

**Good — read everything first, then write:**

```typescript
function measureThenStyle(el: HTMLElement) {
  // read phase
  const rect = el.getBoundingClientRect()
  const w = el.offsetWidth
  const h = el.offsetHeight

  // write phase
  el.style.width = '120px'
  el.style.height = '240px'
}
```

**Best — toggle a class:**

```css
.callout {
  width: 120px;
  height: 240px;
  background: teal;
  border: 1px solid black;
}
```

```typescript
function paint(el: HTMLElement) {
  el.classList.add('callout')
  const { width, height } = el.getBoundingClientRect()
}
```

**In React:**

```tsx
// Bad: imperative writes interleaved with a layout read
function Box({ active }: { active: boolean }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (ref.current && active) {
      ref.current.style.width = '120px'
      const w = ref.current.offsetWidth // forces layout
      ref.current.style.height = '240px'
    }
  }, [active])
  return <div ref={ref}>Content</div>
}

// Good: let CSS do it
function Box({ active }: { active: boolean }) {
  return <div className={active ? 'callout' : ''}>Content</div>
}
```

Classes also cache better and keep styling out of the JS. See
https://gist.github.com/paulirish/5d52fb081b3570c81e3a and https://csstriggers.com/.

---

## 7.2 — Index once, look up many times

**Severity:** Low-medium · **Topics:** Map, indexing

Repeated `.find()` calls by the same key are O(n) each. Build a `Map` once and every
lookup becomes O(1).

**O(n) per lookup:**

```typescript
function attachAuthors(posts: Post[], authors: Author[]) {
  return posts.map(post => ({
    ...post,
    author: authors.find(a => a.id === post.authorId),
  }))
}
```

**O(1) per lookup:**

```typescript
function attachAuthors(posts: Post[], authors: Author[]) {
  const byId = new Map(authors.map(a => [a.id, a]))
  return posts.map(post => ({
    ...post,
    author: byId.get(post.authorId),
  }))
}
```

For 1,000 posts against 1,000 authors that's ~1M operations down to ~2K.

---

## 7.3 — Hoist property chains out of loops

**Severity:** Low-medium · **Topics:** loops, caching

Resolving a deep property chain on every iteration is wasted work when it never
changes inside the loop.

**Resolved every iteration:**

```typescript
for (let i = 0; i < rows.length; i++) {
  render(theme.tokens.colors.primary)
}
```

**Resolved once:**

```typescript
const primary = theme.tokens.colors.primary
const n = rows.length
for (let i = 0; i < n; i++) {
  render(primary)
}
```

---

## 7.4 — Memoize repeated calls with a module-level Map

**Severity:** Medium · **Topics:** caching, memoization

When the same pure function runs many times with the same input during render, cache
its results in a module-scoped `Map`.

**Recomputed for every row:**

```tsx
function TagList({ tags }: { tags: Tag[] }) {
  return (
    <ul>
      {tags.map(tag => {
        const slug = slugify(tag.label) // recomputed each render
        return <TagChip key={tag.id} slug={slug} />
      })}
    </ul>
  )
}
```

**Computed once per unique input:**

```tsx
const slugCache = new Map<string, string>()

function memoSlugify(label: string): string {
  const cached = slugCache.get(label)
  if (cached !== undefined) return cached
  const slug = slugify(label)
  slugCache.set(label, slug)
  return slug
}

function TagList({ tags }: { tags: Tag[] }) {
  return (
    <ul>
      {tags.map(tag => (
        <TagChip key={tag.id} slug={memoSlugify(tag.label)} />
      ))}
    </ul>
  )
}
```

**Single-value variant** with manual invalidation:

```typescript
let cachedFlag: boolean | null = null

function hasConsent(): boolean {
  if (cachedFlag !== null) return cachedFlag
  cachedFlag = document.cookie.includes('consent=')
  return cachedFlag
}

function onConsentChange() {
  cachedFlag = null // clear when it changes
}
```

A plain `Map` (not a hook) works in utilities and event handlers too, not just
components.

Background: https://vercel.com/blog/how-we-made-the-vercel-dashboard-twice-as-fast

---

## 7.5 — Cache storage reads in memory

**Severity:** Low-medium · **Topics:** localStorage, caching

`localStorage`, `sessionStorage`, and `document.cookie` are synchronous and slow.
Read them once and keep the value in memory.

**Reads storage on every call:**

```typescript
function getTheme() {
  return localStorage.getItem('theme') ?? 'light'
}
// ten calls → ten reads
```

**Backed by a Map:**

```typescript
const cache = new Map<string, string | null>()

function readLocal(key: string) {
  if (!cache.has(key)) cache.set(key, localStorage.getItem(key))
  return cache.get(key)
}

function writeLocal(key: string, value: string) {
  localStorage.setItem(key, value)
  cache.set(key, value) // keep the cache consistent
}
```

**Cookies:**

```typescript
let cookieJar: Record<string, string> | null = null

function readCookie(name: string) {
  if (!cookieJar) {
    cookieJar = Object.fromEntries(
      document.cookie.split('; ').map(pair => pair.split('=')),
    )
  }
  return cookieJar[name]
}
```

**Invalidate on outside changes** — another tab or a server-set cookie can make the
cache stale:

```typescript
window.addEventListener('storage', e => {
  if (e.key) cache.delete(e.key)
})

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') cache.clear()
})
```

---

## 7.6 — Fold multiple passes into one loop

**Severity:** Low-medium · **Topics:** arrays, loops

Chaining several `.filter()`/`.map()` calls walks the array once per call. One loop
does it all in a single pass.

**Three passes:**

```typescript
const admins = members.filter(m => m.isAdmin)
const beta = members.filter(m => m.inBeta)
const dormant = members.filter(m => !m.active)
```

**One pass:**

```typescript
const admins: Member[] = []
const beta: Member[] = []
const dormant: Member[] = []

for (const m of members) {
  if (m.isAdmin) admins.push(m)
  if (m.inBeta) beta.push(m)
  if (!m.active) dormant.push(m)
}
```

---

## 7.7 — Compare array lengths before the expensive part

**Severity:** Medium-high · **Topics:** arrays, comparison

Before sorting, deep-comparing, or serializing two arrays, compare lengths. Different
lengths mean they can't be equal, so you skip all the heavy work.

**Always sorts and joins, even on a length mismatch:**

```typescript
function changed(next: string[], prev: string[]) {
  return next.sort().join() !== prev.sort().join()
}
```

Two O(n log n) sorts run even when one array has 5 items and the other 100 — plus the
cost of joining and string comparison.

**O(1) length check first:**

```typescript
function changed(next: string[], prev: string[]) {
  if (next.length !== prev.length) return true

  const a = next.toSorted()
  const b = prev.toSorted()
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return true
  }
  return false
}
```

This skips sorting/joining when lengths differ, allocates no joined strings, leaves
the inputs unmutated, and bails on the first difference.

---

## 7.8 — Return as soon as the answer is known

**Severity:** Low-medium · **Topics:** functions, early return

Don't keep iterating after the result is settled.

**Checks every item even after a failure is found:**

```typescript
function validate(rows: Row[]) {
  let bad = false
  let message = ''

  for (const row of rows) {
    if (!row.email) { bad = true; message = 'email required' }
    if (!row.name) { bad = true; message = 'name required' }
    // keeps looping
  }

  return bad ? { ok: false, message } : { ok: true }
}
```

**Returns on the first failure:**

```typescript
function validate(rows: Row[]) {
  for (const row of rows) {
    if (!row.email) return { ok: false, message: 'email required' }
    if (!row.name) return { ok: false, message: 'name required' }
  }
  return { ok: true }
}
```

---

## 7.9 — Hoist or memoize `RegExp` creation

**Severity:** Low-medium · **Topics:** regexp, memoization

Constructing a `RegExp` in render rebuilds it every time. Hoist a constant pattern to
module scope; memoize a dynamic one with `useMemo`.

**New regex every render:**

```tsx
function Mark({ text, term }: Props) {
  const re = new RegExp(`(${term})`, 'gi')
  const parts = text.split(re)
  return <>{parts.map((p, i) => /* ... */ null)}</>
}
```

**Hoisted constant / memoized dynamic:**

```tsx
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function Mark({ text, term }: Props) {
  const re = useMemo(() => new RegExp(`(${escapeRegex(term)})`, 'gi'), [term])
  const parts = text.split(re)
  return <>{parts.map((p, i) => /* ... */ null)}</>
}
```

**Watch out:** a global (`/g`) regex carries mutable `lastIndex` state across calls:

```typescript
const re = /foo/g
re.test('foo') // true,  lastIndex = 3
re.test('foo') // false, lastIndex = 0
```

---

## 7.10 — Find min/max with a loop, not a sort

**Severity:** Low · **Topics:** arrays, algorithms

Picking the smallest or largest element is one linear pass. Sorting the whole array
for it is O(n log n) wasted work.

**O(n log n) — sorts to grab the newest:**

```typescript
interface Build { id: string; finishedAt: number }

function newest(builds: Build[]) {
  return [...builds].sort((a, b) => b.finishedAt - a.finishedAt)[0]
}
```

**O(n) — one pass:**

```typescript
function newest(builds: Build[]) {
  if (builds.length === 0) return null
  let best = builds[0]
  for (let i = 1; i < builds.length; i++) {
    if (builds[i].finishedAt > best.finishedAt) best = builds[i]
  }
  return best
}

function span(builds: Build[]) {
  if (builds.length === 0) return { first: null, last: null }
  let first = builds[0]
  let last = builds[0]
  for (let i = 1; i < builds.length; i++) {
    if (builds[i].finishedAt < first.finishedAt) first = builds[i]
    if (builds[i].finishedAt > last.finishedAt) last = builds[i]
  }
  return { first, last }
}
```

**For small numeric arrays**, `Math.min`/`Math.max` with spread is fine — but spread
has an argument-count ceiling (roughly 124K in Chrome, 638K in Safari; see
https://jsfiddle.net/qw1jabsx/4/) and can throw on very large arrays. The loop is the
reliable choice.

```typescript
const xs = [5, 2, 8, 1, 9]
const lo = Math.min(...xs)
const hi = Math.max(...xs)
```

---

## 7.11 — Use a `Set`/`Map` for repeated membership tests

**Severity:** Low-medium · **Topics:** Set, Map, data structures

`Array.includes` is O(n) per check. Convert to a `Set` for O(1) lookups when you test
membership repeatedly.

**O(n) each check:**

```typescript
const allowed = ['read', 'write', 'share']
actions.filter(a => allowed.includes(a.scope))
```

**O(1) each check:**

```typescript
const allowed = new Set(['read', 'write', 'share'])
actions.filter(a => allowed.has(a.scope))
```

---

## 7.12 — Prefer `toSorted()` over `sort()` for immutability

**Severity:** Medium-high · **Topics:** arrays, immutability, React state

`.sort()` mutates in place, which corrupts React props and state. `.toSorted()`
returns a new sorted array and leaves the original alone.

**Mutates the prop array:**

```typescript
function Names({ people }: { people: Person[] }) {
  const sorted = useMemo(
    () => people.sort((a, b) => a.name.localeCompare(b.name)),
    [people],
  )
  return <ul>{sorted.map(renderName)}</ul>
}
```

**Leaves the prop untouched:**

```typescript
function Names({ people }: { people: Person[] }) {
  const sorted = useMemo(
    () => people.toSorted((a, b) => a.name.localeCompare(b.name)),
    [people],
  )
  return <ul>{sorted.map(renderName)}</ul>
}
```

Mutating props/state violates React's read-only model and can produce stale-closure
bugs when the mutated array is captured in a callback or effect.

**Support:** `.toSorted()` works in Chrome 110+, Safari 16+, Firefox 115+, and
Node 20+. For older targets, spread first:

```typescript
const sorted = [...items].sort((a, b) => a.value - b.value)
```

Companion immutable methods: `.toReversed()`, `.toSpliced()`, and `.with()`.
