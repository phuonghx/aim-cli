# Migrations

> Change a live schema in steps so nothing goes dark.

## The Expand / Contract Playbook

```
Every breaking change becomes a sequence of safe ones:
│
├── Introducing a column
│   └── add it nullable → backfill values → tighten to NOT NULL
│
├── Dropping a column
│   └── stop reading it → ship that release → then drop it
│
├── Creating an index on a busy table
│   └── CREATE INDEX CONCURRENTLY so writes keep flowing
│
└── Renaming a column
    └── add the new name → copy the data → cut over → remove the old
```

## Working Principles

- Split anything breaking into incremental, reversible steps.
- Rehearse the migration against a copy of real data first.
- Keep a rollback path ready before you run it.
- Wrap related changes in a transaction where the engine allows.

## Managed Engines Worth Knowing

### Neon — Serverless PostgreSQL

| Capability | Why it helps |
|------------|--------------|
| Scales to zero | You pay only for active use |
| Branch in an instant | Cheap dev and preview environments |
| Genuine PostgreSQL | Drop-in compatibility |
| Autoscaling | Absorbs traffic spikes |

### Turso — SQLite at the Edge

| Capability | Why it helps |
|------------|--------------|
| Edge replicas | Reads land close to the user |
| SQLite under the hood | Simple and familiar |
| Roomy free tier | Easy to start cheaply |
| Spread across regions | Consistent global latency |
