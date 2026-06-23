# Recording Decisions and Their Trade-offs

Every architectural choice worth making is worth writing down — together with what it costs. The two templates below are meant to be copied straight into your docs.

## A Template for Each Component Decision

Work through this for any component where the design isn't obvious:

```markdown
## Decision: [component or choice]

### Context
- **Problem**: what are we actually solving?
- **Constraints**: team size, scale, timeline, budget

### Options Considered
| Option | Upsides | Downsides | Cost | Holds up when |
|--------|---------|-----------|------|---------------|
| Option A | ... | ... | Low | [conditions] |
| Option B | ... | ... | High | [conditions] |

### Decision
**Chosen**: [option]

### Rationale
1. [reason, tied back to a constraint]
2. [reason, tied back to a requirement]

### Trade-offs Accepted
- [what we give up]
- [why that's acceptable here]

### Consequences
- **Upside**: [what we gain]
- **Downside**: [what we take on]
- **Mitigation**: [how we'll keep the downside in check]

### Revisit When
- [the signal that says reconsider this]
```

## A Reusable ADR Template

For decisions significant enough to live as standalone records:

```markdown
# ADR-[number]: [short title]

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-[number]

## Context
What's the problem, and what constraints box us in?

## Decision
What we chose — stated precisely, not vaguely.

## Rationale
Why we chose it, connected to the requirements and constraints.

## Trade-offs
What we're giving up. Be honest about it.

## Consequences
- **Upside**: [benefits]
- **Downside**: [costs]
- **Mitigation**: [how we address the costs]
```

## Where ADRs Live

Keep them together, numbered in sequence, under a dedicated folder:

```
docs/
└── architecture/
    ├── adr-001-pick-the-web-framework.md
    ├── adr-002-relational-over-document-store.md
    └── adr-003-defer-the-repository-layer.md
```
