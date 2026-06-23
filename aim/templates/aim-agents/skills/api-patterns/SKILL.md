---
name: api-patterns
description: Guides API design decisions across REST, GraphQL, and tRPC, covering style selection, response envelopes, versioning, pagination, authentication, rate limiting, and security review. Use it when picking an API paradigm for a given audience, shaping consistent payloads and error formats, planning how an interface will evolve, or auditing endpoints against the OWASP API risks. Not intended for UI or frontend layout work.
---

# API Patterns

> Reason about API design from first principles.
> **The goal is judgment for your situation, not a template to paste.**

## How to use this skill

These notes are split into focused files. Open only the one that maps to the
question in front of you instead of reading everything at once. The table below
is your index.

---

## File index

| File | Covers | Open it when |
|------|--------|--------------|
| `api-style.md` | Picking REST vs GraphQL vs tRPC | Deciding the paradigm |
| `rest.md` | Resource names, verbs, status codes | Laying out a REST surface |
| `response.md` | Payload shape, errors, paging | Shaping what you return |
| `graphql.md` | Schema modeling, fit, hardening | Weighing GraphQL |
| `trpc.md` | Typed TS client/server | Full-stack TypeScript work |
| `versioning.md` | URI / header / query schemes | Planning for change |
| `auth.md` | Tokens, sessions, OAuth, keys | Picking how callers prove identity |
| `rate-limiting.md` | Quotas and throttling | Shielding the service |
| `documentation.md` | OpenAPI and reference docs | Writing the docs |
| `security-testing.md` | OWASP API risks, authz checks | Reviewing for security |

---

## Sibling skills

| If you also need | Reach for |
|------------------|-----------|
| To actually build the endpoints | `@[skills/nodejs-best-practices]` |
| To model the underlying data | `@[skills/database-design]` |
| A deeper security pass | `@[skills/vulnerability-scanner]` |

---

## Pre-flight checklist

Run through these before committing to a design:

- [ ] **Who calls this API, and from where?** (asked, not assumed)
- [ ] **Paradigm chosen for *this* problem** (REST / GraphQL / tRPC)
- [ ] **One response shape, applied everywhere**
- [ ] **A story for how the API changes over time**
- [ ] **Identity and access model decided**
- [ ] **Throttling thought through**
- [ ] **A plan for keeping docs alive**

---

## Traps to avoid

**Stop doing this:**
- Reaching for REST reflexively on every project
- Naming endpoints after actions (e.g. `/fetchUsers`)
- Letting each route return a differently shaped body
- Leaking stack traces or DB errors to callers
- Shipping with no throttling at all

**Do this instead:**
- Let the consumers and constraints pick the paradigm
- Pin down client needs by asking first
- Treat documentation as part of the deliverable
- Map outcomes to the right HTTP codes

---

## Script

| Script | What it does | How to run |
|--------|--------------|------------|
| `scripts/api_validator.py` | Scans endpoints and specs for gaps | `python scripts/api_validator.py <project_path>` |
