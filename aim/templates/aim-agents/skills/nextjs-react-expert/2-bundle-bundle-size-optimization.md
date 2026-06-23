# 2. Trimming the Bundle

> **Severity:** Highest
> **Why it matters:** Bytes shipped on first load decide how soon the page becomes
> interactive and how fast the largest element paints. Smaller bundles are faster
> bundles.

Five techniques: avoid whole-library imports, load code conditionally, defer
non-essential third parties, split heavy components, and warm up bundles ahead of
demand.

---

## 2.1 — Don't import through barrel files

**Severity:** Highest · **Topics:** imports, tree-shaking, barrel files

A *barrel file* is a module that re-exports a whole package (`export * from './x'`).
Import a named symbol from one and the bundler may have to pull in the entire export
graph behind it.

The entry files of big icon and component libraries can re-export thousands of
modules. Just importing one can add hundreds of milliseconds — it slows the dev
server and inflates production cold starts.

**Why tree-shaking won't save you:** a package marked external can't be optimized at
all, and if you bundle it to enable shaking, the build has to walk the whole module
graph, which is slow.

**Costly — drags in the full library:**

```tsx
import { Search, Bell, Trash } from 'lucide-react'
// pulls in the entire icon set behind the barrel

import { Card, Dialog } from '@chakra-ui/react'
// hundreds of components loaded to use two
```

**Cheap — reach straight for the file you need:**

```tsx
import Search from 'lucide-react/dist/esm/icons/search'
import Bell from 'lucide-react/dist/esm/icons/bell'
import Trash from 'lucide-react/dist/esm/icons/trash'
// three small modules instead of the whole pack

import { Card } from '@chakra-ui/react/card'
import { Dialog } from '@chakra-ui/react/dialog'
```

**Or let Next.js rewrite the imports for you (13.5+):**

```js
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@chakra-ui/react'],
  },
}

// keep the readable barrel import — it's transformed to deep imports at build time
import { Search, Bell, Trash } from 'lucide-react'
```

Usual suspects: `lucide-react`, `@mui/material`, `@mui/icons-material`,
`@tabler/icons-react`, `react-icons`, `@headlessui/react`, `@radix-ui/react-*`,
`lodash`, `ramda`, `date-fns`, `rxjs`, `react-use`.

Background: https://vercel.com/blog/how-we-optimized-package-imports-in-next-js

---

## 2.2 — Load modules only when a feature turns on

**Severity:** High · **Topics:** conditional loading, lazy loading

Bulky data files or feature modules should arrive only after the user actually
engages the feature.

```tsx
function ConfettiLayer({ celebrate, onFail }: { celebrate: boolean; onFail: () => void }) {
  const [engine, setEngine] = useState<ConfettiEngine | null>(null)

  useEffect(() => {
    // Load the heavy module the first time confetti is requested, and only in the browser
    if (celebrate && !engine && typeof window !== 'undefined') {
      import('./confetti-engine.js')
        .then(mod => setEngine(mod.createEngine()))
        .catch(onFail)
    }
  }, [celebrate, engine, onFail])

  if (!engine) return null
  return <ConfettiCanvas engine={engine} />
}
```

The `typeof window !== 'undefined'` guard keeps the module out of the server bundle,
which speeds up the build and the server runtime.

---

## 2.3 — Defer non-critical third-party scripts

**Severity:** Medium · **Topics:** third-party scripts, analytics

Analytics, error reporting, and session replay don't gate interaction. Let them load
after hydration instead of riding along in the first chunk.

**Ships with the initial bundle:**

```tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

**Loads after the page hydrates:**

```tsx
import dynamic from 'next/dynamic'

const Analytics = dynamic(
  () => import('@vercel/analytics/react').then(m => m.Analytics),
  { ssr: false },
)

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

---

## 2.4 — Split heavy components with `next/dynamic`

**Severity:** Highest · **Topics:** dynamic import, code splitting

A large component that isn't on screen at first render has no business in the initial
chunk. Lazy-load it.

**The chart library lands in the main chunk, ~250KB:**

```tsx
import { TimeSeriesChart } from './time-series-chart'

function AnalyticsPanel({ data }: { data: Series }) {
  return <TimeSeriesChart series={data} />
}
```

**The chart loads on demand instead:**

```tsx
import dynamic from 'next/dynamic'

const TimeSeriesChart = dynamic(
  () => import('./time-series-chart').then(m => m.TimeSeriesChart),
  { ssr: false },
)

function AnalyticsPanel({ data }: { data: Series }) {
  return <TimeSeriesChart series={data} />
}
```

---

## 2.5 — Warm the bundle on user intent

**Severity:** Medium · **Topics:** preloading, hover/focus intent

You can start downloading a heavy chunk the moment a user signals they're about to
need it, so it's ready by the time they click.

**Prefetch on hover or keyboard focus:**

```tsx
function ChartTrigger({ onOpen }: { onOpen: () => void }) {
  const warm = () => {
    if (typeof window !== 'undefined') {
      void import('./time-series-chart')
    }
  }

  return (
    <button onMouseEnter={warm} onFocus={warm} onClick={onOpen}>
      Show analytics
    </button>
  )
}
```

**Prefetch when a feature flag flips on:**

```tsx
function ExperimentProvider({ children, flags }: Props) {
  useEffect(() => {
    if (flags.analyticsEnabled && typeof window !== 'undefined') {
      void import('./time-series-chart').then(mod => mod.warmup())
    }
  }, [flags.analyticsEnabled])

  return <FlagContext.Provider value={flags}>{children}</FlagContext.Provider>
}
```

The `typeof window !== 'undefined'` check keeps these prefetched modules out of the
server bundle.
