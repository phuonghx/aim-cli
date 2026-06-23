# Pattern Catalog

A fast side-by-side reference. For each pattern: where it fits, where it doesn't, and how much it costs to carry.

## Getting At Data

| Pattern | Fits when | Skip it when | Cost |
|---------|-----------|--------------|------|
| **Active Record** | Simple CRUD and quick prototypes | Queries get complex or data spans several sources | Low |
| **Repository** | You need testability or multiple data sources | It's plain CRUD on one database | Medium |
| **Unit of Work** | Multi-step transactions that must commit together | Operations are simple and independent | High |
| **Data Mapper** | A rich domain plus performance demands | Straightforward CRUD | High |

## Handling Business Logic

| Pattern | Fits when | Skip it when | Cost |
|---------|-----------|--------------|------|
| **Transaction Script** | Simple, procedural CRUD flows | Rules get genuinely complex | Low |
| **Table Module** | Logic naturally works over record sets | The domain needs rich, per-object behavior | Low |
| **Domain Model** | Business logic is involved | It's mostly CRUD | Medium |
| **Full DDD** | A complex domain with experts to guide it | The domain is simple or there are no experts | High |

## Distributed Systems

| Pattern | Fits when | Skip it when | Cost |
|---------|-----------|--------------|------|
| **Modular Monolith** | Small team, boundaries still fuzzy | Distinct contexts clearly need to scale separately | Medium |
| **Microservices** | Parts scale differently and the team is large | Small team and a simple domain | Very High |
| **Event-Driven** | Real-time behavior and loose coupling | Simple flows that demand strong consistency | High |
| **CQRS** | Reads and writes diverge in shape or performance | Same model serves both, plain CRUD | High |
| **Saga** | Transactions span multiple services | One database with simple ACID is enough | High |

## API Styles

| Pattern | Fits when | Skip it when | Cost |
|---------|-----------|--------------|------|
| **REST** | Standard resource-oriented CRUD | You need real-time push or deep graph queries | Low |
| **GraphQL** | Flexible queries for many differing client shapes | Simple CRUD where caching matters most | Medium |
| **gRPC** | Fast internal service-to-service calls | Public or browser-facing APIs | Medium |
| **WebSocket** | Pushing updates to clients in real time | Plain request/response | Medium |

---

## One Rule to Fall Back On

**Start with the simplest thing; let complexity prove it's needed before you add it.**

- You can layer a pattern in later.
- Taking one out is the hard direction.
- When the choice is a toss-up, take the simpler one.
