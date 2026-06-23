# Picking a Database Engine

> Let the workload pick the engine. There is no universal default.

## Routing by Requirement

```
Start from the dominant requirement:
│
├── Rich relational semantics (joins, constraints, transactions)
│   ├── You manage the host        → PostgreSQL
│   └── You want it managed         → Neon, Supabase
│
├── Latency that must be tiny at the edge
│   └── Turso (SQLite replicated to the edge)
│
├── Embedding vectors / semantic lookup
│   └── PostgreSQL with the pgvector extension
│
├── Tiny footprint, single binary, local-first
│   └── SQLite
│
└── Spread across regions at scale
    └── CockroachDB, PlanetScale, or Turso
```

## How the Options Stack Up

| Engine | Sweet spot | What you give up |
|--------|-----------|------------------|
| **PostgreSQL** | Deep feature set, gnarly queries | You own the operational burden |
| **Neon** | Postgres without servers, branchable | Inherits Postgres's surface area |
| **Turso** | Edge reads, minimal latency | Bound by SQLite's feature limits |
| **SQLite** | Local, embedded, zero setup | One writer at a time |
| **PlanetScale** | MySQL-compatible, horizontal scale | Foreign keys are opt-in per database |

## Clarifying Questions

1. Where will this run — container, serverless, or edge?
2. How elaborate are the read queries likely to get?
3. Does serverless or edge latency drive the decision?
4. Will the app do similarity / vector search?
5. Is multi-region presence a hard requirement?
