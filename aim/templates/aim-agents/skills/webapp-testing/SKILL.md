---
name: webapp-testing
description: An approach to testing web applications end to end, covering route and endpoint discovery, the web testing pyramid, Playwright practice, visual regression, API coverage, test layout, and CI integration. Use it when writing Playwright E2E tests, auditing a web app for untested routes, exercising user flows, or wiring browser tests into a pipeline.
---

# Web App Testing

> Find every route before you test any of them. Untested surface is where regressions hide.

## Automation

| Script | What it does | How to run |
|--------|--------------|------------|
| `scripts/playwright_runner.py` | Loads a page and reports basic health | `python scripts/playwright_runner.py https://example.com` |
| | ...with a full-page screenshot | `python scripts/playwright_runner.py <url> --screenshot` |
| | ...with a quick accessibility pass | `python scripts/playwright_runner.py <url> --a11y` |

**Setup:** `pip install playwright && playwright install chromium`

---

## Audit before you test

### Discover the surface first
- **Routes** -- read `app/`, `pages/`, and router definitions.
- **API endpoints** -- grep for HTTP verbs and route registrations.
- **Components** -- locate the component directories.
- **Features** -- skim the docs for what's supposed to exist.

### Then work through it
1. **Map** every route and endpoint.
2. **Probe** each one to confirm it responds.
3. **Cover** the critical paths with real tests.

---

## The web testing pyramid

```
        /\          End-to-end (a few)
       /  \         critical user journeys
      /----\
     /      \       Integration (some)
    /--------\      API and data flow
   /          \
  /------------\    Component (many)
                    individual UI pieces
```

---

## End-to-end tests

### Prioritize
1. Happy-path user journeys.
2. Sign-in and auth flows.
3. The business-critical actions.
4. Error and failure handling.

### Keep them solid
- Select via `data-testid` rather than brittle CSS or text.
- Wait on elements/conditions instead of fixed sleeps.
- Start each test from clean state so order never matters.
- Assert on what the user sees, not internal wiring.

---

## Working with Playwright

### Building blocks
- **Page Object Model** -- keep page interactions in one place.
- **Fixtures** -- share setup across tests.
- **Web-first assertions** -- they auto-wait, cutting flakiness.
- **Trace Viewer** -- replay a failed run to see what happened.

### Sensible config
- Retry failing tests twice on CI.
- Capture a trace on the first retry.
- Take a screenshot on failure.
- Keep video only when a test fails.

---

## Visual regression

### Where it earns its keep
High value for design systems and marketing pages; moderate for component libraries; low for content that changes every load.

### How to run it
Capture baseline screenshots, diff against them on each change, review the diffs, and accept the ones that reflect intended updates.

---

## API coverage

Test each endpoint across:
- **Status codes** -- success plus the relevant 4xx and 5xx.
- **Response shape** -- conforms to the expected schema.
- **Error messages** -- clear and useful to the caller.
- **Edge cases** -- empty input, oversized input, special characters.

---

## Laying out tests

```
tests/
├── e2e/           # complete user flows
├── integration/   # API and data
├── component/      # UI units
└── fixtures/       # shared data
```

Name files for the feature and the behavior: `login.spec.ts`, `user-can-checkout.spec.ts`.

---

## CI integration

### Pipeline shape
1. Install dependencies.
2. Install the browsers.
3. Run the suite.
4. Upload artifacts (traces, screenshots) for debugging.

### Going faster
- Playwright parallelizes per file by default.
- Shard large suites across machines.
- Use workers to cover multiple browsers at once.

---

## Habits to drop

- Testing implementation -> test observable behavior.
- Hardcoded waits -> rely on auto-waiting.
- Skipped cleanup -> isolate each test.
- Tolerated flakiness -> fix the underlying cause.

---

> End-to-end tests are costly to run and maintain. Spend them on the paths that matter most.
