---
name: database-design
description: Guides data-layer decisions for application backends, covering schema modeling, index strategy, ORM and database engine selection, query tuning, and migration planning. Applies when shaping a new schema, weighing storage engines or ORMs, planning safe migrations, diagnosing slow queries, or touching Prisma, Drizzle, Kysely, or raw SQL files. Emphasizes reasoning from the workload rather than reaching for one-size-fits-all defaults.
---

# Database Design

> **Reason about the workload first. Patterns follow from requirements, not habit.**

## Load Reference Files On Demand

Each topic lives in its own file. Open only the ones the current task touches.

| File | Covers | Open it when |
|------|--------|--------------|
| `database-selection.md` | Engine trade-offs across Postgres, Neon, Turso, SQLite, and friends | Picking where data lives |
| `orm-selection.md` | Drizzle, Prisma, Kysely, raw SQL | Picking how code talks to the DB |
| `schema-design.md` | Normalization, keys, relationships, soft deletes | Modeling tables |
| `indexing.md` | Index families and composite ordering | Speeding up reads |
| `optimization.md` | N+1, query plans, tuning order | Hunting down slow queries |
| `migrations.md` | Expand/contract, online changes, managed engines | Evolving a live schema |

## Runtime Helper

A lightweight checker flags common Prisma/Drizzle schema smells. Run it; don't read it.

```
python scripts/schema_validator.py <project_path>
```

---

## Guiding Mindset

- Surface the user's constraints (scale, latency, hosting) before committing to an engine.
- Match the tool to the actual access patterns of *this* project.
- Treat Postgres as a strong option, not an automatic one — a smaller store often fits better.

---

## Pre-Build Questions

Work through these (or ask) before writing any DDL:

- [ ] Have database preferences been confirmed with the user?
- [ ] Is the engine choice justified by this project's needs?
- [ ] Does the target runtime (edge, serverless, container) shape the decision?
- [ ] Is there an index plan for the expected queries?
- [ ] Are the relationships and their cardinalities settled?

---

## Mistakes to Steer Clear Of

❌ Reaching for Postgres on a tiny app where embedded SQLite would do
❌ Leaving frequently-filtered columns unindexed
❌ Shipping `SELECT *` to production paths
❌ Dumping structured fields into a JSON blob out of laziness
❌ Letting ORM relation loads fan out into N+1 query storms
