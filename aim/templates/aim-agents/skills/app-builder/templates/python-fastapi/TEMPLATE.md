---
name: python-fastapi
description: Guiding principles for a FastAPI REST API starter — SQLAlchemy, Pydantic, Alembic.
---

# FastAPI API Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology |
|-------|------------|
| Framework | FastAPI |
| Language | Python 3.12+ (3.14 is the current stable) |
| ORM | SQLAlchemy 2.0 (async) |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Auth | JWT plus passlib |

---

## Folder Layout

> Organized by domain rather than by file type — it scales better once an app grows past trivial. Every domain owns its own router, schemas, models, and service.

```
project-name/
├── alembic/             # Migrations
├── src/
│   ├── auth/
│   │   ├── router.py    # APIRouter
│   │   ├── schemas.py   # Pydantic models
│   │   ├── models.py    # SQLAlchemy models
│   │   ├── service.py   # Business logic
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── posts/           # Same shape, one per domain
│   ├── config.py        # Global settings (BaseSettings)
│   ├── database.py      # Async engine / session
│   ├── models.py        # Shared base models
│   ├── exceptions.py    # Global exceptions
│   └── main.py          # FastAPI() + include_router
├── tests/
├── requirements/        # base.txt / dev.txt / prod.txt
├── alembic.ini
└── .env
```

---

## Core Ideas

| Idea | What it means here |
|------|--------------------|
| Domain modules | each feature folder bundles its router, schemas, models, and service |
| Async throughout | async/await everywhere (AsyncSession, async_sessionmaker) |
| Dependency injection | FastAPI's `Depends` covers validation, auth, and the DB session |
| Pydantic v2 | validation and serialization |
| SQLAlchemy 2.0 | async sessions |

---

## How the API Layers Up

| Layer | Owns |
|-------|------|
| Routers | HTTP handling |
| Dependencies | auth and validation |
| Services | business logic |
| Models | database entities |
| Schemas | request and response shapes |

---

## Getting Set Up

1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install fastapi uvicorn "sqlalchemy[asyncio]" alembic pydantic pydantic-settings`
4. Create `.env`
5. `alembic upgrade head`
6. `uvicorn src.main:app --reload`

---

## Practices Worth Following

- Go async everywhere (AsyncSession, async dependencies; wrap any sync SDK in `run_in_threadpool`)
- Prefer per-module `BaseSettings` over one giant config object
- Validate with Pydantic v2
- Use SQLAlchemy 2.0 async sessions
- Keep Alembic migrations static, reversible, and named with clear slugs
- Test with pytest-asyncio, mocking through `dependency_overrides`
