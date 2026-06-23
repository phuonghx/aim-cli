# tRPC

> Share types directly between a TypeScript client and server — no contract to keep in sync.

## Is it a fit?

```
Strong fit:
├── TypeScript on the client and the server
├── A single repository holding both
├── Internal dashboards and tooling
├── Teams that want to move fast
└── Type safety treated as a hard requirement

Wrong tool:
├── Clients written in other languages
├── A public API outside developers will call
├── A need to follow REST conventions
└── Backends spread across multiple languages
```

## Why teams reach for it

```
The payoff:
├── No separate schema to author and maintain
├── Types inferred from server to client automatically
├── Editor autocomplete that spans the whole stack
├── Backend changes show up instantly on the front end
└── No build-time code generation in the loop
```

## Where it tends to live

```
Typical pairings:
├── Next.js with tRPC — the most common combo
├── A monorepo with a shared types package
├── Remix with tRPC
└── Effectively any TS front end talking to a TS back end
```
