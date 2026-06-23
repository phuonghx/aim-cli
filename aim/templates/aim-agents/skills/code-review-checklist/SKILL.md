---
name: code-review-checklist
description: A practical checklist for reviewing code across correctness, security, performance, quality, testing, and documentation, plus review patterns specific to AI- and LLM-driven code. It also offers anti-patterns to flag and a tagging convention for review comments. Useful when reviewing a pull request or auditing a change before merge.
---

# Code Review Checklist

A reviewer's running checklist. Walk the categories, flag what's missing, and tag findings by severity.

## Fast Pass

### Does it work?
- [ ] Behaves as intended
- [ ] Edge and boundary cases covered
- [ ] Failures are caught and handled
- [ ] No glaring logic errors

### Is it safe?
- [ ] All external input validated and cleaned
- [ ] No injection paths (SQL, NoSQL, command, etc.)
- [ ] No XSS or CSRF openings
- [ ] No credentials or secrets baked into the source
- [ ] *AI-specific:* guarded against prompt injection where relevant
- [ ] *AI-specific:* model output cleaned before it reaches a sensitive sink

### Is it fast enough?
- [ ] No N+1 query pattern
- [ ] No redundant loops or repeated work
- [ ] Caching applied where it pays off
- [ ] Effect on bundle/artifact size weighed

### Is it clean?
- [ ] Names communicate intent
- [ ] No copy-pasted logic
- [ ] Solid design boundaries respected
- [ ] Abstraction pitched at the right level

### Is it tested?
- [ ] New paths have unit coverage
- [ ] Edge cases exercised
- [ ] Tests are readable and stable

### Is it documented?
- [ ] Tricky logic explained
- [ ] Public interfaces described
- [ ] README refreshed if behavior changed

## Reviewing AI / LLM Code

### Logic and fabrication risk
- [ ] **Reasoning path:** does the logic hold up when traced end to end?
- [ ] **Failure states:** are empty results, timeouts, and partial responses handled?
- [ ] **Outside world:** are assumptions about the filesystem or network actually safe?

### Prompt construction
```javascript
// Weak — raw user text, no structure or guardrails
const reply = await model.complete(userText);

// Strong — explicit role, cleaned input, enforced output shape
const reply = await model.complete({
  role: "You parse invoices into JSON and nothing else.",
  input: clean(userText),
  schema: InvoiceSchema,
});
```

## Smells Worth Flagging

```typescript
// Unexplained literal
if (state === 2) { /* ... */ }
// Named instead
if (state === OrderState.SHIPPED) { /* ... */ }

// Arrow-shaped nesting
if (a) { if (b) { if (c) { /* ... */ } } }
// Flattened with guards
if (!a) return;
if (!b) return;
if (!c) return;
// ...real work

// One enormous function -> several focused ones
// Escape-hatch typing -> precise types
const payload: any = fetchIt();      // avoid
const payload: Invoice = fetchIt();  // prefer
```

## Tagging Your Comments

```
[blocker]  Must fix before merge — e.g. command injection in this handler
[suggest]  Worth improving — memoize this derived value
[nit]      Minor polish — this could be const
[?]        Genuine question — what's the behavior when the list is empty?
```

Use the same prefixes consistently so the author can scan severity at a glance and address blockers first.
