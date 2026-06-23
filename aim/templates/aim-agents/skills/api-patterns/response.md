# Response Format

> Whatever shape you pick, apply it the same way on every route.

## Pick a body shape

```
One of these, consistently:
├── Wrapped envelope — { success, data, error }
├── Bare resource — return the object directly
└── Hypermedia — HAL or JSON:API with links
```

## What belongs in an error

```
A useful error carries:
├── A stable code clients can branch on
├── A message safe to show a person
├── Field-level detail to aid debugging
├── A request ID so support can trace it
└── Nothing from the internals — no stack traces or SQL
```

## Ways to paginate

| Style | Best for | The catch |
|-------|----------|-----------|
| **Offset** | Small sets, jump-to-page | Slows down over large tables |
| **Cursor** | Big or live datasets | No arbitrary page jumps |
| **Keyset** | Latency-sensitive paths | Needs a sortable, indexed key |

### Questions to settle first

1. How big does the result set get?
2. Do callers need to land on an arbitrary page?
3. Is the underlying data shifting while it's read?
