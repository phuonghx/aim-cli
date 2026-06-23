---
name: verify-changes
description: Establishes that a code change actually behaves correctly by running it and observing real output, rather than concluding it works from reading the source or trusting that it compiles. Applies right after writing a feature, fixing a bug, or refactoring, and whenever someone asks whether a change works, to test it, or to confirm a fix. The aim is execution-backed evidence — commands run and results captured — not the writing of new functionality.
---

# Verify Changes

Existing code and working code are not the same thing. Reading a function tells you what
it looks like; running it tells you what it does. This skill is about closing that gap with
evidence you can point to.

## The distinction that matters

```text
Inspecting:  "the function is right there, so it should work"      -> not verified
Assuming:    "the types line up, so it must be correct"            -> not verified
Executing:   "I ran it; here is the output; it works, because X"   -> verified
```

Only the third kind counts. Everything else is a hypothesis.

## How to verify

### 1. Pin down what changed

- Which files did you touch?
- What behavior should now be different?
- What was the original requirement or bug?

### 2. Match the change to a method

| Kind of change | How you prove it works |
|---|---|
| Bug fix | Re-run the exact scenario that failed; confirm it no longer does |
| New feature | Drive the feature end to end; confirm the output matches intent |
| Refactor | Run the existing tests; confirm nothing regressed |
| API change | Call the endpoint; confirm the response shape and status |
| UI change | Render the component; confirm what appears on screen |
| Config change | Load the app with it; confirm the new values take effect |
| Build / infra | Run the build or pipeline; confirm it completes |

### 3. Actually run it

```bash
# JavaScript / TypeScript project
npm run build                 # does it compile?
npm test                      # do the tests pass?
npm run dev                   # does it boot?

# Smoke-test a single module
node -e "require('./src/parser'); console.log('module loads')"

# Hit an HTTP endpoint
curl -s http://localhost:3000/api/orders | jq .

# Exercise a CLI
python -m mytool --check
```

### 4. Write down the evidence

```markdown
## Verification

Changed
- src/orders/total.ts — corrected rounding on multi-currency carts

Ran
- npm run build, npm test, manual curl against /api/orders

Result
- Build: compiled clean
- Tests: 58 passed, 0 failed
- Runtime: server boots; /api/orders returns the expected JSON
- Edge case: empty cart returns 0, not NaN

Still open
- Load behavior under concurrency not yet measured
```

State plainly what you could *not* verify — unknown-but-named beats silently-skipped.

## Checklists by project shape

**Web app**

- [ ] Build compiles
- [ ] Linter is clean
- [ ] Test suite passes
- [ ] Dev server starts
- [ ] Affected pages render
- [ ] Browser console is free of errors

**API / backend**

- [ ] Service starts cleanly
- [ ] Changed routes return correct payloads
- [ ] Failure cases return the right status codes
- [ ] Database queries actually execute

**CLI / script**

- [ ] Runs without throwing
- [ ] Output matches what you expected
- [ ] Bad input is handled gracefully
- [ ] Help and usage text are accurate

## Excuses that hide bugs

| Excuse | Why it fails | Do this instead |
|---|---|---|
| "It should work" | No evidence behind it | Run it and show the output |
| "The happy path is fine" | Bugs cluster at the edges | Drive the error paths too |
| "It compiles, so it's done" | Compiling is not correctness | Check runtime behavior |
| "Too trivial to test" | Small changes still break things | Verify it anyway |

## Pairs well with

| After a change from | Verify by |
|---|---|
| A frontend / UI task | Rendering it and watching the console |
| An API / backend task | Calling the endpoints and inspecting responses |
| A database / schema task | Running the migration and querying the data |
| Adding tests | Running the suite and checking coverage |
