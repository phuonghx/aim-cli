# 8. Advanced Patterns

> **Severity:** Situational
> **Why it matters:** Narrow patterns for specific problems. Each needs care, so reach
> for them when the situation actually calls for it.

Three techniques: run app init exactly once, keep callbacks stable in effects, and use
effect-event hooks.

---

## 8.1 — Initialize the app once, not on every mount

**Severity:** Low-medium · **Topics:** initialization, app startup

App-wide setup that must run a single time per load does not belong in a component's
`useEffect([])`. Components remount — and Strict Mode double-invokes effects in dev —
so the work runs more than once. Guard it at module scope, or run it in the entry
module.

**Runs twice in dev and again on every remount:**

```tsx
function App() {
  useEffect(() => {
    restoreSession()
    primeAnalytics()
  }, [])

  // ...
}
```

**Runs once per load:**

```tsx
let initialized = false

function App() {
  useEffect(() => {
    if (initialized) return
    initialized = true
    restoreSession()
    primeAnalytics()
  }, [])

  // ...
}
```

Reference: https://react.dev/learn/you-might-not-need-an-effect#initializing-the-application

---

## 8.2 — Keep handlers in a ref so effects don't re-subscribe

**Severity:** Low · **Topics:** refs, event handlers

When an effect attaches a listener and depends on a callback, the listener tears down
and re-attaches every time the callback's identity changes. Store the callback in a
ref so the subscription stays put while still calling the latest version.

**Re-subscribes whenever `handler` changes:**

```tsx
function useWindowEvent(type: string, handler: (e: Event) => void) {
  useEffect(() => {
    window.addEventListener(type, handler)
    return () => window.removeEventListener(type, handler)
  }, [type, handler])
}
```

**Subscribes once per event type:**

```tsx
function useWindowEvent(type: string, handler: (e: Event) => void) {
  const handlerRef = useRef(handler)
  useEffect(() => {
    handlerRef.current = handler // always points at the latest
  }, [handler])

  useEffect(() => {
    const proxy = (e: Event) => handlerRef.current(e)
    window.addEventListener(type, proxy)
    return () => window.removeEventListener(type, proxy)
  }, [type])
}
```

**Cleaner on recent React** — `useEffectEvent` gives you a stable function that always
runs the newest handler:

```tsx
import { useEffectEvent } from 'react'

function useWindowEvent(type: string, handler: (e: Event) => void) {
  const onEvent = useEffectEvent(handler)

  useEffect(() => {
    window.addEventListener(type, onEvent)
    return () => window.removeEventListener(type, onEvent)
  }, [type])
}
```

---

## 8.3 — Read latest values without re-running the effect

**Severity:** Low · **Topics:** useEffectEvent, refs

`useEffectEvent` lets a callback see the latest props and state without listing them as
dependencies, so the effect doesn't re-run on every change while still avoiding stale
closures.

**Effect restarts whenever `onSubmit` changes:**

```tsx
function Debounced({ onSubmit }: { onSubmit: (v: string) => void }) {
  const [value, setValue] = useState('')

  useEffect(() => {
    const id = setTimeout(() => onSubmit(value), 300)
    return () => clearTimeout(id)
  }, [value, onSubmit])
}
```

**Effect depends only on `value`:**

```tsx
import { useEffectEvent } from 'react'

function Debounced({ onSubmit }: { onSubmit: (v: string) => void }) {
  const [value, setValue] = useState('')
  const submit = useEffectEvent(onSubmit)

  useEffect(() => {
    const id = setTimeout(() => submit(value), 300)
    return () => clearTimeout(id)
  }, [value])
}
```
