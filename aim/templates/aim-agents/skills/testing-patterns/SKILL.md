---
name: testing-patterns
description: Guidance for building dependable test suites, covering the test pyramid, the arrange-act-assert structure, when to pick unit versus integration versus end-to-end tests, mocking strategy, test organization and naming, and test-data techniques. Use it when writing or reviewing tests, choosing a testing approach or framework, or deciding what and how to mock.
---

# Testing Patterns

> Reliable tests describe behavior clearly and fail for one understandable reason.

---

## The test pyramid

Lots of fast, narrow tests at the bottom; a few slow, broad ones at the top.

```
        /\          End-to-end (a few)
       /  \         critical journeys only
      /----\
     /      \       Integration (some)
    /--------\      APIs, DB queries, service seams
   /          \
  /------------\    Unit (many)
                    functions and classes
```

---

## Arrange, Act, Assert

Every test reads in three beats:

- **Arrange** -- set up the data and preconditions.
- **Act** -- run the one thing under test.
- **Assert** -- check the result against expectations.

---

## Choosing a test type

- **Unit** -- pure logic and functions; runs in milliseconds; lots of them.
- **Integration** -- how pieces talk to each other (API, database, services); moderate speed; a meaningful number.
- **End-to-end** -- complete user journeys through the real stack; slow; reserved for what truly matters.

---

## Unit tests

### What makes a good one
- **Quick** -- well under ~100ms each.
- **Self-contained** -- no network, disk, or shared state.
- **Deterministic** -- identical result on every run.
- **Self-verifying** -- asserts the outcome; no eyeballing.
- **Written alongside the code**, not bolted on later.

### Where to aim them
Cover business rules, edge cases, and error paths. Don't bother testing framework internals, third-party libraries, or trivial accessors.

---

## Integration tests

### What to exercise
- **API endpoints** -- request in, response out.
- **Database access** -- queries and transactional behavior.
- **External services** -- the contract at the boundary.

### Lifecycle hooks
- **Before all** -- open shared resources (connections, containers).
- **Before each** -- reset to a known state.
- **After each** -- tidy up what the test created.
- **After all** -- release the shared resources.

---

## Mocking

### Mock the edges, not the subject
Replace external APIs, networks, clocks, and randomness so tests stay deterministic. Mock the database in unit tests but use a real one for integration. Never mock the very thing you are testing, and skip mocking trivial pure functions or in-memory stores.

### Vocabulary
- **Stub** -- returns canned values.
- **Spy** -- records how it was called.
- **Mock** -- asserts on expected interactions.
- **Fake** -- a lightweight working substitute (e.g. an in-memory repo).

---

## Organizing tests

### Naming
Name the test after the behavior, so a failure reads like a sentence:
- behavior-first: `returns an error when the email is invalid`
- condition-first: `when the user is not found, ...`
- given/when/then: `given an empty cart, when checkout runs, then it rejects`

### Grouping
- `describe` (or a class) groups related cases.
- `it` / `test` holds a single case.
- shared setup lives in `beforeEach`.

---

## Test data

### Approaches
- **Factories** -- generate objects on demand with sensible defaults.
- **Fixtures** -- fixed, reusable datasets.
- **Builders** -- fluent construction for complex objects.

### Principles
Keep data realistic but minimal, randomize the parts that don't matter (a faker library helps), and reuse common fixtures so intent stays visible.

---

## Worth doing

- One logical assertion per test, so the failure reason is obvious.
- Tests that don't depend on running order.
- Fast suites you'll actually run often.
- Descriptive names that double as documentation.
- Cleanup that prevents leakage between tests.

---

## Worth avoiding

- Asserting on internal implementation instead of observable behavior.
- Copy-pasting setup instead of using factories.
- Sprawling, hard-to-follow setup -- split or simplify it.
- Tolerating flaky tests -- chase the root cause.
- Skipping teardown and leaving state behind.

---

> Tests are documentation. If the suite doesn't make the code's behavior clear, the tests need a rewrite.
