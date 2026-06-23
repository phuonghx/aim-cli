# Worked Architecture Examples

Three end-to-end designs, one per project profile. Each follows the same arc: what was required, what was decided, what was knowingly traded away, and where it can grow next.

---

## Example A — A Solo-Built Booking App (MVP)

A single founder building an appointment-scheduling tool for small studios, racing to launch on a tight budget.

```yaml
What's required:
  - Fewer than 1,000 users at launch
  - One developer doing everything
  - Live within a couple of months
  - Spend as little as possible

What was decided:
  Shape:          A single deployable application (one person, one codebase)
  Framework:      A full-stack web framework so frontend and API live together
  Data access:    Talk to the ORM directly; no repository layer yet
  Auth:           Plain signed tokens rather than a full OAuth setup
  Payments:       A hosted payment provider instead of rolling our own
  Storage:        A relational database, for reliable transactional bookings

What was traded away (and why that's fine):
  - One unit means no piece scales on its own — but with one dev, that flexibility isn't worth its cost yet
  - No repository layer makes some tests harder — straightforward CRUD doesn't justify the indirection
  - Token-only auth means no "sign in with Google" at first — that can be bolted on when someone asks

Where it grows next:
  - Past ~10K users → peel the scheduling engine out into its own service
  - As the team grows → introduce a repository layer for testability
  - When social login is requested → add OAuth alongside the existing tokens
```

---

## Example B — A Team-Built Inventory Platform (SaaS)

A five-to-ten person team building a multi-tenant inventory and ordering platform with distinct areas for billing, accounts, and the core catalog.

```yaml
What's required:
  - Somewhere between 1K and 100K users
  - A team of five to ten developers
  - A product meant to live a year or more
  - Several separate domains: billing, user management, core catalog

What was decided:
  Shape:          A modular monolith — clear internal boundaries, one deployment
  Framework:      A backend framework organized around modules
  Data access:    A repository layer, mainly for testability and swappability
  Domain model:   Partial DDD — entities carry behavior, but no full aggregates yet
  Auth:           OAuth together with signed tokens
  Caching:        A dedicated cache layer for hot reads
  Storage:        A relational database

What was traded away (and why that's fine):
  - Modules still share a process, so some coupling remains — full microservices aren't earned yet
  - Skipping full aggregates keeps the model lighter — there are no dedicated domain experts to justify them
  - Everything starts synchronous; a message queue comes later, only once a real async need appears

Where it grows next:
  - Past ~10 developers → revisit whether microservices now pay off
  - When domains start fighting each other → split out bounded contexts
  - When reads grow heavy → introduce CQRS for the read-dominant paths
```

---

## Example C — A Logistics Tracking System (Enterprise)

A large organization running a freight-tracking system across many teams, with parts of the system under very different load and a need to stay up around the clock.

```yaml
What's required:
  - 100K+ users
  - More than ten developers across multiple teams
  - Several business domains with genuinely different scaling profiles
  - Always-on, 24/7 availability

What was decided:
  Shape:          Microservices, each scaling independently
  Edge:           An API gateway in front of the services
  Domain model:   Full DDD, with aggregates and value objects
  Consistency:    Event-driven, accepting eventual consistency between services
  Messaging:      A streaming message bus for the event backbone
  Auth:           OAuth plus enterprise SSO via SAML
  Storage:        Polyglot persistence — a different store per workload
  Reads:          CQRS applied to the services where it pays off

What operating this demands:
  - A service mesh to manage inter-service traffic
  - Distributed tracing across requests
  - Centralized log aggregation
  - Circuit breakers to contain failures
  - Container orchestration for deployment and scaling
```
