---
name: documentation-templates
description: Provides starting structures and conventions for the documents a project usually needs — READMEs, per-endpoint API references, doc comments, changelogs, decision records, and machine-readable files for AI agents. Each template is a skeleton to adapt, paired with guidance on what belongs where. Use it when authoring or restructuring any of these documents and you want a sound layout to build from.
---

# Documentation Templates

The layouts below are scaffolds. Drop in your project's specifics and prune whatever doesn't apply — a template that survives untouched usually means it wasn't read.

## The README

### Sections, in the order readers want them

A reader scanning a new repo asks a predictable sequence of questions. Order the sections to answer them in that order:

| Section | The question it answers |
|---------|------------------------|
| Name + tagline | What even is this? |
| Quick start | How do I run it in five minutes? |
| Features | What can it actually do? |
| Configuration | How do I tune it? |
| API reference | Where are the details? |
| Contributing | How do I pitch in? |
| License | What am I allowed to do? |

### Skeleton

```markdown
# ProjectName

One sentence on what it does.

## Quick Start

[The fewest steps to a running instance]

## Features

- Does X
- Does Y

## Configuration

| Variable | Meaning | Default |
|----------|---------|---------|
| PORT     | Listen port | 8080 |

## Docs

- [API reference](./docs/api.md)
- [Architecture](./docs/architecture.md)

## License

Apache-2.0
```

## API Reference

### One block per endpoint

```markdown
## GET /orders/:id

Fetch a single order.

**Path params**
| Name | Type | Required | Meaning |
|------|------|----------|---------|
| id   | string | yes | Order identifier |

**Responses**
- 200 — the order object
- 404 — no order with that id

**Example**
[A real request and its response]
```

## Doc Comments

### The JSDoc / TSDoc shape

```typescript
/**
 * One line on what this does.
 *
 * @param amount - The charge in cents
 * @returns The created receipt
 * @throws PaymentError - if the card is declined
 *
 * @example
 * const receipt = charge(1999);
 */
```

### Comment the why, skip the what

| Worth a comment | Skip it |
|-----------------|---------|
| The reason behind a rule | Restating the code |
| A tricky algorithm | Line-by-line narration |
| Surprising behavior | Code that reads plainly |
| The contract a caller relies on | Internal mechanics |

## Changelog

Following the Keep a Changelog convention:

```markdown
# Changelog

## [Unreleased]
### Added
- A new export endpoint

## [2.1.0] - 2026-03-15
### Added
- CSV import
### Changed
- Bumped the parser library
### Fixed
- Off-by-one in pagination
```

## Architecture Decision Record

```markdown
# ADR-007: [short title]

## Status
Proposed · Accepted · Superseded

## Context
What forces are pushing us to decide?

## Decision
What did we choose?

## Consequences
What do we gain, and what do we give up?
```

## Documentation For AI Agents

### An llms.txt outline

A compact map that crawlers and agents can read fast:

```markdown
# ProjectName
> The one-sentence goal.

## Core files
- [src/main.ts]: entry point
- [src/routes/]: HTTP handlers
- [docs/]: long-form docs

## Concepts
- Tenant: a billing boundary
- Job: one unit of background work
```

### Making docs friendly to retrieval

When the docs will be chunked and indexed, structure helps the index:

- A clean H1 → H2 → H3 ladder
- Data shapes shown as JSON or YAML
- Flows drawn with Mermaid
- Sections that stand on their own without surrounding context

## What Makes Any Doc Good

| Quality | Why it pays off |
|---------|----------------|
| Scannable | Headings, lists, and tables let readers jump |
| Example-led | A snippet beats a paragraph of description |
| Layered | Easy path first, deep detail after |
| Current | A stale doc misleads worse than no doc |

Treat every template here as a first draft. The project's real needs decide what stays.
