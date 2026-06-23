# Query Optimization

> Spot the N+1 trap, read the plan, then tune in the right order.

## The N+1 Trap

```
What goes wrong:
├── One query pulls the parent rows
├── Then one extra query fires per parent for its children
└── Hundreds of round trips for what should be one or two

Ways out:
├── JOIN the related rows in a single statement
├── Lean on the ORM's eager-loading to emit that JOIN
├── Batch and cache with a DataLoader (common in GraphQL)
└── Fetch children with one subquery instead of a loop
```

## Read the Plan Before You Touch Anything

```
Diagnose first:
├── Run EXPLAIN ANALYZE on the slow query
├── Hunt for a Seq Scan over a big table
├── Compare the planner's row estimate to reality
└── Note which predicate has no supporting index
```

## Tune in This Order

1. **Add the missing index** — by far the most frequent culprit.
2. **Project only the columns you use** — drop `SELECT *`.
3. **Prefer joins to nested subqueries** where the planner handles them better.
4. **Paginate at the database** so you never haul back full tables.
5. **Cache** results once the query itself is as lean as it gets.
