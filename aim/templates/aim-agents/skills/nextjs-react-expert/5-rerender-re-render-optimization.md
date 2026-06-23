# 5. Taming Re-renders

> **Severity:** Medium
> **Why it matters:** Every render the component doesn't need is CPU spent for
> nothing. Cutting wasted renders keeps the UI responsive.

Twelve techniques covering derived values, narrow subscriptions, careful memoization,
functional updates, lazy init, transitions, and refs.

> **React Compiler:** If your project runs the React Compiler, much of the manual
> `memo`/`useMemo`/`useCallback` advice below is handled automatically. The
> correctness items — functional updates, lazy init, derived state — still apply.

---

## 5.1 — Compute derived values during render

**Severity:** Medium · **Topics:** derived state, useEffect

If a value follows from current props or state, just compute it in the render body.
Storing it in state and syncing it from an effect adds a render and invites drift.

**Redundant state plus an effect:**

```tsx
function NameCard() {
  const [first, setFirst] = useState('Ada')
  const [last, setLast] = useState('Lovelace')
  const [full, setFull] = useState('')

  useEffect(() => {
    setFull(`${first} ${last}`)
  }, [first, last])

  return <p>{full}</p>
}
```

**Derive it inline:**

```tsx
function NameCard() {
  const [first, setFirst] = useState('Ada')
  const [last, setLast] = useState('Lovelace')
  const full = `${first} ${last}`

  return <p>{full}</p>
}
```

Reference: https://react.dev/learn/you-might-not-need-an-effect

---

## 5.2 — Read volatile state at the point of use

**Severity:** Medium · **Topics:** searchParams, localStorage

Don't subscribe to constantly changing state (search params, storage) if you only
read it inside a callback. The subscription re-renders the component on every change
for no benefit.

**Subscribes to all search-param changes:**

```tsx
function CopyLink({ docId }: { docId: string }) {
  const params = useSearchParams()

  const onCopy = () => {
    copyShareUrl(docId, { source: params.get('source') })
  }

  return <button onClick={onCopy}>Copy link</button>
}
```

**Reads on demand, no subscription:**

```tsx
function CopyLink({ docId }: { docId: string }) {
  const onCopy = () => {
    const source = new URLSearchParams(window.location.search).get('source')
    copyShareUrl(docId, { source })
  }

  return <button onClick={onCopy}>Copy link</button>
}
```

---

## 5.3 — Skip `useMemo` for cheap primitive expressions

**Severity:** Low-medium · **Topics:** useMemo

When an expression is a couple of operators returning a primitive (boolean, number,
string), wrapping it in `useMemo` costs more than just recomputing it — the hook and
its dependency comparison aren't free.

**Pointless memo:**

```tsx
function Banner({ feed, alerts }: Props) {
  const busy = useMemo(
    () => feed.pending || alerts.pending,
    [feed.pending, alerts.pending],
  )

  if (busy) return <Spinner />
}
```

**Just compute it:**

```tsx
function Banner({ feed, alerts }: Props) {
  const busy = feed.pending || alerts.pending

  if (busy) return <Spinner />
}
```

---

## 5.4 — Hoist non-primitive default props of memoized components

**Severity:** Medium · **Topics:** memo, default props

A memoized component with a default value for an object/array/function prop breaks its
own memoization when rendered without that prop: the default is a fresh instance every
render and fails the strict-equality check in `memo()`. Move the default to a module
constant.

**`onSelect` differs on every render:**

```tsx
const Row = memo(function Row({ onSelect = () => {} }: { onSelect?: () => void }) {
  // ...
})

<Row /> // default recreated each render → memo defeated
```

**Stable default:**

```tsx
const NOOP = () => {}

const Row = memo(function Row({ onSelect = NOOP }: { onSelect?: () => void }) {
  // ...
})

<Row /> // NOOP is the same reference every time
```

---

## 5.5 — Move expensive work behind a memoized child

**Severity:** Medium · **Topics:** memo, useMemo, early return

Pulling costly work into its own memoized component lets the parent bail out before
the work happens at all.

**Builds the thumbnail even while loading:**

```tsx
function Card({ photo, loading }: Props) {
  const thumb = useMemo(() => {
    const url = buildThumbUrl(photo)
    return <Thumb src={url} />
  }, [photo])

  if (loading) return <Skeleton />
  return <div>{thumb}</div>
}
```

**Skips the work entirely when loading:**

```tsx
const PhotoThumb = memo(function PhotoThumb({ photo }: { photo: Photo }) {
  const url = useMemo(() => buildThumbUrl(photo), [photo])
  return <Thumb src={url} />
})

function Card({ photo, loading }: Props) {
  if (loading) return <Skeleton />
  return (
    <div>
      <PhotoThumb photo={photo} />
    </div>
  )
}
```

---

## 5.6 — Depend on primitives, not whole objects

**Severity:** Low · **Topics:** useEffect, dependencies

List the specific primitive an effect reads so it re-runs only when that value moves,
not on every change to the parent object.

**Re-runs on any field of `account`:**

```tsx
useEffect(() => {
  track(account.id)
}, [account])
```

**Re-runs only when the id changes:**

```tsx
useEffect(() => {
  track(account.id)
}, [account.id])
```

**Compute boolean thresholds outside the effect** so it fires on the transition, not
on every intermediate value:

```tsx
// runs at width 1024, 1023, 1022, ...
useEffect(() => {
  if (width < 1024) collapseSidebar()
}, [width])

// runs only when the boolean flips
const isNarrow = width < 1024
useEffect(() => {
  if (isNarrow) collapseSidebar()
}, [isNarrow])
```

---

## 5.7 — Put user-action logic in the handler, not an effect

**Severity:** Medium · **Topics:** useEffect, events

When a side effect is caused by a concrete action (submit, click, drag), run it in
that event handler. Modeling the action as state plus an effect makes the effect
re-run on unrelated changes and can fire the action more than once.

**Action smuggled through state + effect:**

```tsx
function SignupForm() {
  const [submitted, setSubmitted] = useState(false)
  const theme = useContext(ThemeContext)

  useEffect(() => {
    if (submitted) {
      register()
      notify('Welcome', theme)
    }
  }, [submitted, theme])

  return <button onClick={() => setSubmitted(true)}>Join</button>
}
```

**Run it directly in the handler:**

```tsx
function SignupForm() {
  const theme = useContext(ThemeContext)

  function onSubmit() {
    register()
    notify('Welcome', theme)
  }

  return <button onClick={onSubmit}>Join</button>
}
```

Reference: https://react.dev/learn/removing-effect-dependencies#should-this-code-move-to-an-event-handler

---

## 5.8 — Subscribe to the boolean, not the raw value

**Severity:** Medium · **Topics:** derived state, media query

Subscribing to a continuously changing number re-renders on every tick. Subscribe to
the derived boolean instead and re-render only when it actually crosses the threshold.

**Re-renders on every pixel:**

```tsx
function Panel() {
  const width = useWindowWidth() // changes constantly
  const narrow = width < 768
  return <aside className={narrow ? 'narrow' : 'wide'} />
}
```

**Re-renders only when the breakpoint flips:**

```tsx
function Panel() {
  const narrow = useMediaQuery('(max-width: 767px)')
  return <aside className={narrow ? 'narrow' : 'wide'} />
}
```

---

## 5.9 — Update state functionally when it depends on itself

**Severity:** Medium · **Topics:** useState, useCallback, closures

When new state derives from current state, use the updater function form. It dodges
stale closures, drops the state from the dependency array, and keeps the callback
reference stable.

**Needs the state as a dependency — and one path is buggy:**

```tsx
function Cart() {
  const [lines, setLines] = useState(initial)

  // recreated whenever lines changes
  const add = useCallback((more: Line[]) => {
    setLines([...lines, ...more])
  }, [lines])

  // stale closure: always sees the initial lines
  const remove = useCallback((id: string) => {
    setLines(lines.filter(l => l.id !== id))
  }, [])

  return <CartEditor lines={lines} onAdd={add} onRemove={remove} />
}
```

**Stable callbacks, always current state:**

```tsx
function Cart() {
  const [lines, setLines] = useState(initial)

  const add = useCallback((more: Line[]) => {
    setLines(curr => [...curr, ...more])
  }, [])

  const remove = useCallback((id: string) => {
    setLines(curr => curr.filter(l => l.id !== id))
  }, [])

  return <CartEditor lines={lines} onAdd={add} onRemove={remove} />
}
```

**Reach for the functional form** for any update based on current state, inside
`useCallback`/`useMemo`, in event handlers, and after `await`. **Direct updates are
fine** for static values (`setCount(0)`), values from arguments (`setName(next)`), or
anything independent of the previous state.

---

## 5.10 — Initialize expensive state lazily

**Severity:** Medium · **Topics:** useState, initialization

Pass a function to `useState` for costly initial values. Without it, the initializer
runs on every render even though only the first result is kept.

**Runs on every render:**

```tsx
function Catalog({ items }: { items: Item[] }) {
  // rebuilt on each render, including when query changes
  const [index, setIndex] = useState(buildIndex(items))
  const [query, setQuery] = useState('')
  return <Results index={index} query={query} />
}

function Settings() {
  // JSON.parse runs every render
  const [prefs, setPrefs] = useState(
    JSON.parse(localStorage.getItem('prefs') || '{}'),
  )
  return <Form prefs={prefs} onChange={setPrefs} />
}
```

**Runs once:**

```tsx
function Catalog({ items }: { items: Item[] }) {
  const [index, setIndex] = useState(() => buildIndex(items))
  const [query, setQuery] = useState('')
  return <Results index={index} query={query} />
}

function Settings() {
  const [prefs, setPrefs] = useState(() => {
    const raw = localStorage.getItem('prefs')
    return raw ? JSON.parse(raw) : {}
  })
  return <Form prefs={prefs} onChange={setPrefs} />
}
```

Use lazy init for storage reads, index/map building, DOM reads, and heavy transforms.
For plain primitives (`useState(0)`), prop pass-through (`useState(props.value)`), or
trivial literals (`useState({})`), the function form is unnecessary.

---

## 5.11 — Wrap non-urgent updates in a transition

**Severity:** Medium · **Topics:** transitions, startTransition

Mark frequent, low-priority updates as transitions so React can interrupt them and
keep input responsive.

**Every scroll blocks the UI:**

```tsx
function ScrollSpy() {
  const [y, setY] = useState(0)
  useEffect(() => {
    const onScroll = () => setY(window.scrollY)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])
}
```

**Updates yield to user input:**

```tsx
import { startTransition } from 'react'

function ScrollSpy() {
  const [y, setY] = useState(0)
  useEffect(() => {
    const onScroll = () => startTransition(() => setY(window.scrollY))
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])
}
```

---

## 5.12 — Keep transient values in a ref

**Severity:** Medium · **Topics:** useRef, transient state

For values that change rapidly but don't need to drive a render — pointer position,
timer ticks, in-flight flags — store them in a ref. Writing a ref never triggers a
render. Reserve state for things the UI actually displays.

**Re-renders on every mouse move:**

```tsx
function Cursor() {
  const [x, setX] = useState(0)

  useEffect(() => {
    const onMove = (e: MouseEvent) => setX(e.clientX)
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [])

  return <div style={{ position: 'fixed', top: 0, left: x, width: 8, height: 8 }} />
}
```

**No re-render; the DOM is nudged directly:**

```tsx
function Cursor() {
  const xRef = useRef(0)
  const dotRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      xRef.current = e.clientX
      const node = dotRef.current
      if (node) node.style.transform = `translateX(${e.clientX}px)`
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [])

  return (
    <div
      ref={dotRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: 8,
        height: 8,
        transform: 'translateX(0px)',
      }}
    />
  )
}
```
