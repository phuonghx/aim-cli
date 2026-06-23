---
name: python-patterns
description: Guides Python design decisions -- framework choice, async-vs-sync, typing strategy, project layout, and error handling -- by reasoning from the project's needs rather than copying snippets. It explains when async helps, when Pydantic earns its place, and how to keep logic out of the view layer. Use it when writing Python services, choosing between FastAPI, Django, and Flask, or structuring a Python codebase.
---

# Python Design Decisions

This is about reasoning, not memorization. Two projects rarely want the same answer, so avoid defaulting to one framework or one concurrency model. Where the requirements are ambiguous, name the trade-off and ask before deciding.

## Choosing a web framework

Let the kind of application steer the choice:

- **API-first or microservices:** FastAPI -- async-native, fast, modern.
- **Full-stack app, CMS, or heavy admin:** Django -- everything is included.
- **Small tool, script, or teaching example:** Flask -- minimal and flexible.
- **Serving ML/AI models:** FastAPI -- Pydantic models, async, uvicorn.
- **Background processing:** a queue like Celery alongside any of the above.

How they compare:

| | FastAPI | Django | Flask |
|--|---------|--------|-------|
| Sweet spot | APIs, services | full-stack, CMS | small, learning |
| Async | native | views/ORM (partial) | via extensions |
| Admin UI | build it | built in | via extensions |
| ORM | bring your own | Django ORM | bring your own |
| Ramp-up | gentle | moderate | gentle |

Worth asking first: API-only or full-stack? Do you need an admin? Is the team comfortable with async? What infrastructure already exists?

## Async or sync

Reach for `async def` when the work waits on the outside world and concurrency matters: database round-trips, HTTP calls, file I/O, lots of simultaneous connections, real-time features, service-to-service chatter -- and you are on an ASGI stack.

Stay with plain `def` when the work computes rather than waits, when the codebase or its libraries are blocking, when it is a simple script, or when the team is not yet fluent in async.

The rule of thumb:

```
Waiting on something external  ->  async
Burning CPU                    ->  sync, and parallelize with multiprocessing
```

Three things to avoid: blending sync and async without care, calling blocking libraries from async code, and forcing async onto CPU-bound work where it only adds overhead.

When you do go async, pick libraries that are actually async:

| Need | Library |
|------|---------|
| HTTP client | httpx |
| PostgreSQL | asyncpg |
| Redis | `redis.asyncio` |
| File I/O | aiofiles |
| ORM | SQLAlchemy 2.0 (async) or Tortoise |

## Type hints

Type the surfaces others depend on -- function parameters, return values, class attributes, and anything public. You can let inference handle local variables, throwaway scripts, and most test bodies.

A few patterns worth recognizing:

```python
from typing import Callable, Optional

# May be absent
def find_account(uid: int) -> Optional[Account]: ...

# One of several shapes
def render(payload: str | bytes) -> None: ...

# Typed collections
def list_orders() -> list[Order]: ...
def price_table() -> dict[str, float]: ...

# A function passed in
def transform(fn: Callable[[bytes], str]) -> str: ...
```

Bring in **Pydantic** when you need runtime guarantees: request/response models, settings and config, data validation, and serialization. You get checks at runtime, an auto-generated JSON schema, native FastAPI support, and readable error messages.

## Project layout

Scale the structure to the project:

```
Script / small tool          Mid-size API                 Larger application
---------------------        ----------------------       ----------------------
main.py                      app/                         src/
helpers.py                     __init__.py                  myapp/
requirements.txt              main.py                        core/
                              models/                        api/
                              routes/                        services/
                              services/                      models/
                              schemas/                       ...
                            tests/                       tests/
                            pyproject.toml               pyproject.toml
```

Inside an API, organize either by layer or by feature:

```
By layer                         By feature
--------                         ----------
routes/      (endpoints)         users/
services/    (business logic)      routes.py
models/      (DB models)           service.py
schemas/     (Pydantic)            schemas.py
deps/        (shared deps)       billing/
                                   ...
```

Feature-based grouping tends to age better once the project has several distinct domains.

## Django specifics

Modern Django supports async views, async middleware, partial async ORM access, and ASGI deployment. Lean on it for outbound API calls, WebSockets via Channels, high-concurrency endpoints, and kicking off background work.

Idioms that keep Django projects healthy:

```
Models   ->  keep them fat, keep views thin; put query logic in custom managers;
             share common fields through abstract base classes
Views    ->  class-based for involved CRUD, function-based for simple endpoints,
             viewsets when using DRF
Queries  ->  select_related() for foreign keys, prefetch_related() for many-to-many,
             only() to fetch specific columns; watch for N+1
```

## FastAPI specifics

**`async def` vs `def` inside FastAPI.** Use `async def` with async drivers, async HTTP clients, and I/O-bound handlers. Use plain `def` for blocking work or sync drivers -- FastAPI runs those in a threadpool for you, so a sync handler will not block the loop.

**Dependencies.** Inject database sessions, the current user, configuration, and shared resources through the dependency system. It makes handlers testable (swap a dependency in tests), keeps wiring tidy, and cleans up automatically when you use a `yield` dependency.

**Pydantic is built in.** The request model validates the body before your code runs; the return type defines the response shape.

```python
@app.post("/accounts")
async def open_account(data: AccountCreate) -> AccountOut:
    # `data` arrives already validated
    ...
```

## Background tasks

Match the tool to the job:

| Tool | Fits |
|------|------|
| FastAPI `BackgroundTasks` | quick, in-process, fire-and-forget |
| Celery | distributed, retries, complex workflows |
| ARQ | async, Redis-backed |
| RQ | simple Redis queue |
| Dramatiq | actor model, lighter than Celery |

```
In-process BackgroundTasks  ->  short work, no persistence, same process
Celery / ARQ / friends      ->  long jobs, retry logic, distributed workers,
                                a durable queue, multi-step pipelines
```

## Error handling

In a service, raise domain-specific exceptions where the problem is found, register handlers that turn them into a consistent response, and log without leaking internals. The flow: services throw meaningful errors, handlers catch and translate them, the caller receives a clean payload.

Every error response should carry a stable code (for programmatic handling), a human-readable message, and field-level details where they apply -- and never a stack trace.

## Testing

Aim coverage at what matters:

| Layer | Focus | Tools |
|-------|-------|-------|
| Unit | business logic | pytest |
| Integration | endpoints | pytest + httpx/TestClient |
| E2E | full flows | pytest + a real DB |

Async tests use `pytest-asyncio`:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_accounts():
    async with AsyncClient(app=app, base_url="http://test") as c:
        resp = await c.get("/accounts")
        assert resp.status_code == 200
```

Common fixtures to factor out: a database session, a test client, an authenticated user with a token, and seeded sample data.

## Before you write code

- [ ] Asked about framework preference?
- [ ] Chose the framework for *this* context, not by reflex?
- [ ] Settled async vs sync?
- [ ] Decided how far to take type hints?
- [ ] Picked a project layout?
- [ ] Planned the error-handling approach?
- [ ] Considered whether background tasks are needed?

## Traps to avoid

Steer clear of: reaching for Django on a small API where FastAPI fits better, calling sync libraries from async code, skipping type hints on public surfaces, parking business logic in routes or views, letting N+1 queries slip through, and mixing async and sync carelessly.

Instead: choose by context, confirm the async requirements, validate with Pydantic, keep routes thin and push logic into services and repositories, and test the paths that matter.

The patterns are here to inform a decision for your specific situation -- think about what serves the application, do not transcribe.
