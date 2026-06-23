# Versioning

> Decide how the API will change *before* anyone depends on it.

## Weighing the options

| Strategy | Looks like | The trade |
|----------|-----------|-----------|
| **In the URI** | `/v1/users` | Obvious and cache-friendly |
| **In a header** | `Accept-Version: 1` | Tidy URLs, harder to discover |
| **In the query** | `?version=1` | Trivial to bolt on, looks messy |
| **No versions** | Change carefully in place | Fine internally, risky for public APIs |

## A way to think about it

```
Let the audience decide:
├── Public surface? → put the version in the URI
├── Internal only? → you may not need versions at all
├── GraphQL? → usually skip versions and evolve the schema
├── tRPC? → the shared types already enforce compatibility
```
