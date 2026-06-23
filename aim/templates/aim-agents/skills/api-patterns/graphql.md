# GraphQL

> One typed graph that clients query however they need.

## Is it the right tool?

```
Leans in your favor:
├── Data that's richly linked, not flat
├── Several distinct clients with different needs
├── Consumers that benefit from shaping their own queries
├── Requirements you expect to keep shifting
└── Over-fetching is a real pain point today

Leans against:
├── Plain create/read/update/delete on simple records
├── Workloads dominated by file uploads
├── HTTP caching you'd rather keep leaning on
└── A team with no GraphQL mileage yet
```

## Modeling the schema

```
Guiding ideas:
├── Model a graph of types, not a list of endpoints
├── Evolve the schema in place — avoid hard versions
├── Page through relationships with connection types
├── Name types precisely; resist a catch-all "data" blob
└── Decide deliberately what is nullable and what isn't
```

## Hardening it

```
Close these holes:
├── Deeply nested queries → cap the allowed depth
├── Expensive queries → score each query's cost and reject over budget
├── Batch abuse → bound how many operations per batch
├── Schema snooping → switch introspection off in production
```
