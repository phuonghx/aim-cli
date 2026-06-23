# 6. Rendering Performance

> **Severity:** Medium
> **Why it matters:** These techniques reduce the work the browser does to lay out and
> paint — animation cost, long-list rendering, hydration flashes, and conditional
> rendering footguns.

Nine techniques.

---

## 6.1 — Animate a wrapper, not the SVG itself

**Severity:** Low · **Topics:** SVG, CSS animation

Many browsers don't GPU-accelerate CSS animations applied directly to SVG elements.
Wrap the SVG in a `<div>` and animate that instead.

**Animates the SVG directly — no hardware acceleration:**

```tsx
function Spinner() {
  return (
    <svg className="animate-spin" width="24" height="24" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" stroke="currentColor" />
    </svg>
  )
}
```

**Animates the wrapper — GPU-accelerated:**

```tsx
function Spinner() {
  return (
    <div className="animate-spin">
      <svg width="24" height="24" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke="currentColor" />
      </svg>
    </div>
  )
}
```

This holds for every transform/transition (`transform`, `opacity`, `translate`,
`scale`, `rotate`). The wrapper gives the browser a layer it can composite on the GPU.

---

## 6.2 — `content-visibility` for long lists

**Severity:** High · **Topics:** CSS, content-visibility, long lists

`content-visibility: auto` lets the browser skip layout and paint for off-screen
items until they scroll into view.

```css
.feed-row {
  content-visibility: auto;
  contain-intrinsic-size: 0 96px; /* reserve space so the scrollbar stays stable */
}
```

```tsx
function Feed({ posts }: { posts: Post[] }) {
  return (
    <div className="overflow-y-auto h-screen">
      {posts.map(post => (
        <div key={post.id} className="feed-row">
          <Avatar user={post.author} />
          <p>{post.body}</p>
        </div>
      ))}
    </div>
  )
}
```

With 1,000 rows, the browser does layout/paint for only the handful on screen,
slashing initial render cost.

---

## 6.3 — Hoist static JSX out of the render path

**Severity:** Low · **Topics:** JSX, static elements

JSX written inside a component is rebuilt every render. If it never changes, define it
once outside the component.

**Rebuilt on every render:**

```tsx
function Placeholder() {
  return <div className="animate-pulse h-16 bg-slate-200" />
}

function Panel({ loading }: { loading: boolean }) {
  return <div>{loading && <Placeholder />}</div>
}
```

**Created once, reused:**

```tsx
const placeholder = <div className="animate-pulse h-16 bg-slate-200" />

function Panel({ loading }: { loading: boolean }) {
  return <div>{loading && placeholder}</div>
}
```

This matters most for big static SVGs, which are costly to recreate. (The React
Compiler hoists static JSX for you when enabled.)

---

## 6.4 — Trim SVG coordinate precision

**Severity:** Low · **Topics:** SVG, SVGO

Excess decimal places in path data inflate file size for no visual gain. The right
precision depends on the viewBox, but trimming is almost always worth it.

**Over-precise:**

```svg
<path d="M 12.847362 24.193847 L 48.382910 60.748213" />
```

**One decimal place:**

```svg
<path d="M 12.8 24.2 L 48.4 60.7" />
```

**Automate it:**

```bash
npx svgo --precision=1 --multipass logo.svg
```

---

## 6.5 — Avoid hydration mismatch *and* flicker for stored values

**Severity:** Medium · **Topics:** SSR, hydration, localStorage

Content driven by client-only storage (theme, preferences) can either break SSR or
flash the wrong value after hydration. Inject a tiny synchronous script that fixes the
DOM before React hydrates and you sidestep both.

**Breaks SSR — `localStorage` doesn't exist on the server:**

```tsx
function ThemeScope({ children }: { children: ReactNode }) {
  const theme = localStorage.getItem('theme') || 'light' // throws on the server
  return <div className={theme}>{children}</div>
}
```

**Flickers — renders default first, then corrects after hydration:**

```tsx
function ThemeScope({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    const stored = localStorage.getItem('theme')
    if (stored) setTheme(stored) // visible flash on load
  }, [])

  return <div className={theme}>{children}</div>
}
```

**Clean — the inline script sets the class before paint:**

```tsx
function ThemeScope({ children }: { children: ReactNode }) {
  return (
    <>
      <div id="theme-scope">{children}</div>
      <script
        dangerouslySetInnerHTML={{
          __html: `
            (function () {
              try {
                var t = localStorage.getItem('theme') || 'light';
                var el = document.getElementById('theme-scope');
                if (el) el.className = t;
              } catch (e) {}
            })();
          `,
        }}
      />
    </>
  )
}
```

Because the script runs synchronously before the element is shown, the DOM already
carries the right value — no mismatch, no flash. Handy for themes, preferences, and
auth-dependent UI.

---

## 6.6 — Silence *expected* hydration mismatches

**Severity:** Low-medium · **Topics:** hydration, SSR

Some values are legitimately different on server and client — random IDs, current
time, locale/timezone formatting. For those known cases, wrap the dynamic text in an
element with `suppressHydrationWarning`. Don't use it to paper over real bugs, and
don't sprinkle it everywhere.

**Logs a known mismatch warning:**

```tsx
function Clock() {
  return <span>{new Date().toLocaleTimeString()}</span>
}
```

**Suppresses only that expected mismatch:**

```tsx
function Clock() {
  return <span suppressHydrationWarning>{new Date().toLocaleTimeString()}</span>
}
```

---

## 6.7 — Preserve state across show/hide with `<Activity>`

**Severity:** Medium · **Topics:** Activity, visibility

For an expensive subtree that toggles open and closed often, React's `<Activity>`
keeps its DOM and state alive instead of unmounting and rebuilding it.

```tsx
import { Activity } from 'react'

function Drawer({ open }: { open: boolean }) {
  return (
    <Activity mode={open ? 'visible' : 'hidden'}>
      <ExpensivePanel />
    </Activity>
  )
}
```

This avoids both the rebuild cost and the loss of internal state on every toggle.

---

## 6.8 — Render conditionally with a ternary, not `&&`

**Severity:** Low · **Topics:** conditional rendering, falsy values

`&&` leaks falsy left-hand values like `0` and `NaN` into the output. Use an explicit
ternary when the condition can be a renderable falsy value.

**Renders a stray `0`:**

```tsx
function CartBadge({ count }: { count: number }) {
  return <div>{count && <span className="badge">{count}</span>}</div>
  // count === 0 → <div>0</div>
}
```

**Renders nothing at zero:**

```tsx
function CartBadge({ count }: { count: number }) {
  return <div>{count > 0 ? <span className="badge">{count}</span> : null}</div>
  // count === 0 → <div></div>
}
```

---

## 6.9 — Prefer `useTransition` over a manual loading flag

**Severity:** Low · **Topics:** transitions, useTransition

`useTransition` gives you an `isPending` flag and manages the transition lifecycle, so
you don't have to juggle `setLoading(true/false)` by hand.

**Hand-managed loading state:**

```tsx
function Search() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const onSearch = async (q: string) => {
    setLoading(true)
    setResults(await query(q))
    setLoading(false)
  }

  return (
    <>
      <input onChange={e => onSearch(e.target.value)} />
      {loading && <Spinner />}
      <Results items={results} />
    </>
  )
}
```

**Built-in pending state:**

```tsx
import { useState, useTransition } from 'react'

function Search() {
  const [results, setResults] = useState([])
  const [isPending, startTransition] = useTransition()

  const onSearch = (q: string) => {
    startTransition(async () => {
      setResults(await query(q))
    })
  }

  return (
    <>
      <input onChange={e => onSearch(e.target.value)} />
      {isPending && <Spinner />}
      <Results items={results} />
    </>
  )
}
```

`useTransition` resets the pending flag even if the work throws, keeps the UI
interactive during the update, and cancels a superseded transition automatically.

Reference: https://react.dev/reference/react/useTransition
