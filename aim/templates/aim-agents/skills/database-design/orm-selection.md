# Choosing an ORM or Query Layer

> Weigh runtime constraints against developer ergonomics.

## Routing by Context

```
What dominates the decision?
│
├── Edge target or strict bundle budget
│   └── Drizzle (tiny, reads like SQL)
│
├── Smoothest authoring experience, schema-driven
│   └── Prisma (generated client, migrations, GUI)
│
├── Hand-tuned queries, full control of output
│   └── A typed query builder over raw SQL
│
└── Living in Python
    └── SQLAlchemy 2.0 (first-class async)
```

## How the Options Stack Up

| Tool | Sweet spot | What you give up |
|------|-----------|------------------|
| **Drizzle** | Edge runtimes, TS-native | Younger ecosystem, fewer recipes |
| **Prisma** | Ergonomics, schema tooling | Larger runtime, awkward on edge |
| **Kysely** | Type-safe SQL composition | Migrations are your job |
| **Raw SQL** | Complex, performance-critical paths | Types and safety are manual |
