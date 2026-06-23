# Choosing a Pattern

Use the branches below to narrow down a pattern, then sanity-check it against the three questions and the trap list.

## Start From Your Biggest Worry

Pick whichever concern dominates the current decision and follow that branch.

- **Is data access the hard part?**
  - **Yes — complex queries, and tests need to isolate the data layer.** Lean toward a repository, possibly with a unit of work.
    - *Check:* will the underlying data source actually change often? If yes, the indirection earns its keep. If not, going straight through the ORM is probably simpler and just as good.
  - **No — plain CRUD against a single database.** Use the ORM directly. Don't add a layer you won't benefit from.

- **Is the business logic the hard part?**
  - **Yes — rich rules that shift depending on context.** Lean toward domain-driven design.
    - *Check:* do you have actual domain experts to work with? With them, go to full DDD (aggregates, value objects). Without them, stick to partial DDD — behavior-rich entities and clear boundaries, nothing heavier.
  - **No — mostly CRUD with light validation.** A transaction-script style is enough.

- **Do parts of the system need to scale independently?**
  - **Yes.** Microservices are worth their overhead *only if all three* hold: the domain boundaries are genuinely clear, the team is past roughly ten people, and different services really do have different scaling needs. If even one is missing, build a modular monolith and extract services later when the need is proven.
  - **No.** A modular monolith is the right call.

- **Are there real-time demands?**
  - **Yes — instant updates, multiple users staying in sync.** Lean toward an event-driven design backed by a message queue.
    - *Check:* can the system tolerate eventual consistency? If yes, event-driven fits. If not, fall back to synchronous calls with polling.
  - **No — eventual updates are fine.** Plain synchronous REST or GraphQL is enough.

## Three Questions Before Adopting Any Pattern

1. **What exactly does it fix?** Name the specific problem it addresses.
2. **Is there something simpler?** Check whether a lighter approach would do.
3. **Can it wait?** See whether it can be deferred until the need actually materializes.

## Traps to Watch For

| Pattern | How it goes wrong | Lighter starting point |
|---------|-------------------|------------------------|
| Microservices | Splitting too early, before boundaries are clear | Start as a monolith and carve out services later |
| Clean / hexagonal | Abstracting everything up front | Write the concrete version first, extract interfaces later |
| Event sourcing | Reaching for it when it isn't needed | An append-only audit log usually covers the real need |
| CQRS | Adding read/write split with no payoff | Keep a single model |
| Repository | Wrapping trivial CRUD for no reason | Use the ORM directly |
