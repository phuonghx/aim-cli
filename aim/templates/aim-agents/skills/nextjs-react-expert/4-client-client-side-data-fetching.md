# 4. Client-Side Data Fetching

> **Severity:** Medium-high
> **Why it matters:** Deduplicating requests and listeners on the client cuts
> redundant network traffic and keeps interactions smooth.

Four techniques: share a single global listener, mark scroll listeners passive, lean
on SWR for dedup, and version client storage.

---

## 4.1 — Collapse global listeners into one

**Severity:** Low · **Topics:** SWR, event listeners, subscriptions

A hook that attaches a `window` listener registers a new one for every component that
uses it. Use `useSWRSubscription` to keep a single shared listener and fan out to
registered callbacks.

**N components, N listeners:**

```tsx
function useHotkey(combo: string, run: () => void) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey && e.key === combo) run()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [combo, run])
}
```

**N components, one listener:**

```tsx
import useSWRSubscription from 'swr/subscription'

// Registry of callbacks keyed by combo, shared across all hook instances
const registry = new Map<string, Set<() => void>>()

function useHotkey(combo: string, run: () => void) {
  useEffect(() => {
    const set = registry.get(combo) ?? new Set()
    set.add(run)
    registry.set(combo, set)

    return () => {
      set.delete(run)
      if (set.size === 0) registry.delete(combo)
    }
  }, [combo, run])

  // One keydown listener for the whole app, set up once
  useSWRSubscription('app-hotkeys', () => {
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey) registry.get(e.key)?.forEach(cb => cb())
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })
}

function Toolbar() {
  useHotkey('s', save)   // both share the single listener above
  useHotkey('f', focus)
}
```

---

## 4.2 — Make scroll-path listeners passive

**Severity:** Medium · **Topics:** event listeners, scrolling, touch, wheel

By default the browser must wait for a `touch`/`wheel` handler to finish in case it
calls `preventDefault()`, which delays the scroll. Pass `{ passive: true }` to promise
you won't, and scrolling stays immediate.

**Blocks scroll while the handler runs:**

```typescript
useEffect(() => {
  const onTouch = (e: TouchEvent) => track(e.touches[0].clientY)
  const onWheel = (e: WheelEvent) => track(e.deltaY)

  document.addEventListener('touchstart', onTouch)
  document.addEventListener('wheel', onWheel)

  return () => {
    document.removeEventListener('touchstart', onTouch)
    document.removeEventListener('wheel', onWheel)
  }
}, [])
```

**Scroll stays responsive:**

```typescript
useEffect(() => {
  const onTouch = (e: TouchEvent) => track(e.touches[0].clientY)
  const onWheel = (e: WheelEvent) => track(e.deltaY)

  document.addEventListener('touchstart', onTouch, { passive: true })
  document.addEventListener('wheel', onWheel, { passive: true })

  return () => {
    document.removeEventListener('touchstart', onTouch)
    document.removeEventListener('wheel', onWheel)
  }
}, [])
```

**Use passive for** tracking, analytics, and any handler that never prevents the
default. **Don't use passive for** custom swipe, pinch-zoom, or anything that must
call `preventDefault()`.

---

## 4.3 — Let SWR dedupe and cache

**Severity:** Medium-high · **Topics:** SWR, dedup, data fetching

Hand-rolled `useEffect` fetching gives each component its own request and no shared
cache. SWR dedupes identical keys, caches results, and revalidates across instances.

**Every instance fetches independently:**

```tsx
function Members() {
  const [members, setMembers] = useState([])
  useEffect(() => {
    fetch('/api/members').then(r => r.json()).then(setMembers)
  }, [])
}
```

**Instances share one request:**

```tsx
import useSWR from 'swr'

function Members() {
  const { data: members } = useSWR('/api/members', fetcher)
}
```

**Data that never changes:**

```tsx
import { useImmutableSWR } from '@/lib/swr'

function FeatureFlags() {
  const { data } = useImmutableSWR('/api/flags', fetcher)
}
```

**Mutations:**

```tsx
import { useSWRMutation } from 'swr/mutation'

function SaveButton() {
  const { trigger } = useSWRMutation('/api/member', saveMember)
  return <button onClick={() => trigger()}>Save</button>
}
```

Docs: https://swr.vercel.app

---

## 4.4 — Version and slim down `localStorage`

**Severity:** Medium · **Topics:** localStorage, versioning, data minimization

Prefix keys with a version and persist only the fields the UI needs. This avoids
schema clashes after a deploy and keeps tokens or PII out of storage.

**No version, dumps the whole object, no error handling:**

```typescript
localStorage.setItem('prefs', JSON.stringify(fullUser))
const data = localStorage.getItem('prefs')
```

**Versioned, minimal, and guarded:**

```typescript
const SCHEMA = 'v3'

function savePrefs(prefs: { theme: string; locale: string }) {
  try {
    localStorage.setItem(`prefs:${SCHEMA}`, JSON.stringify(prefs))
  } catch {
    // private mode, quota exceeded, or storage disabled
  }
}

function readPrefs() {
  try {
    const raw = localStorage.getItem(`prefs:${SCHEMA}`)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

// upgrade old data once, then drop it
function upgrade() {
  try {
    const old = localStorage.getItem('prefs:v2')
    if (old) {
      const parsed = JSON.parse(old)
      savePrefs({ theme: parsed.dark ? 'dark' : 'light', locale: parsed.lang })
      localStorage.removeItem('prefs:v2')
    }
  } catch {}
}
```

**Persist a narrow slice of a server response:**

```typescript
function cacheUiPrefs(user: FullUser) {
  try {
    localStorage.setItem('ui:v1', JSON.stringify({
      theme: user.settings.theme,
      compact: user.settings.compactMode,
    }))
  } catch {}
}
```

**Always wrap in try/catch** — `getItem`/`setItem` throw in Safari/Firefox private
mode, when the quota is full, or when storage is turned off. Versioning lets the
schema evolve, the minimal payload keeps storage small, and dropping extra fields
keeps secrets and internal flags off the client.
