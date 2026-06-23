# Choosing an API Style

> Three paradigms, one decision: REST, GraphQL, or tRPC. Pick by context.

## Start from the consumer

The single most useful question is *who calls this and from how many places*.
Everything else follows from that answer.

```
Who consumes it?
│
├─ Open to the world / many unknown clients
│     → REST described by OpenAPI (broadest reach, easiest to cache)
│
├─ Rich, linked data feeding several different UIs
│     → GraphQL (each client asks for exactly its fields)
│
├─ One TypeScript codebase, front and back together
│     → tRPC (the types flow straight through, no contract to sync)
│
├─ Streaming or push-style updates
│     → WebSocket, documented with AsyncAPI
│
└─ Service-to-service inside your own walls
      → gRPC when speed matters, REST when simplicity does
```

## Side by side

| Dimension | REST | GraphQL | tRPC |
|-----------|------|---------|------|
| Sweet spot | Open/public APIs | Data-heavy apps | TS-only stacks |
| Ramp-up cost | Small | Moderate | Small for TS teams |
| Fetching too much/little | Frequent | Designed away | Designed away |
| Where types come from | Hand-written specs | The schema itself | Inferred end to end |
| Caching story | Built into HTTP | Needs effort | Lives in the client |

## Questions worth answering first

1. Who are the callers, and do you control all of them?
2. Is the client written in TypeScript?
3. How tangled are the relationships in the data?
4. Does HTTP-level caching buy you a lot here?
5. Is this surface exposed publicly or kept internal?
