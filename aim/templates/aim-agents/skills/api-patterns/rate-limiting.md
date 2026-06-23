# Rate Limiting

> Keep one noisy caller from degrading the service for everyone.

## What you're guarding against

```
The threats:
├── Credential-stuffing and brute force
├── Backends starved of resources
├── Runaway bills on metered infrastructure
└── A few clients hogging shared capacity
```

## Which algorithm

| Approach | Mechanics | Reach for it when |
|----------|-----------|-------------------|
| **Token bucket** | Allows short bursts, tokens trickle back | The default for most APIs |
| **Sliding window** | Spreads requests evenly over time | You need tight, smooth caps |
| **Fixed window** | One counter reset each interval | Simple needs, easy to ship |

## Telling the client what's left

```
Surface the budget:
├── X-RateLimit-Limit — the ceiling
├── X-RateLimit-Remaining — what's still available
├── X-RateLimit-Reset — when the counter refills
└── Respond with 429 once the caller is over
```
