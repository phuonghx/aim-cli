---
name: batch-operations
description: A disciplined workflow for applying one repeated change across many files at once — codebase-wide renames, adding imports everywhere, bumping versions, or migrating an API call. It stresses previewing the impact, executing the sweep, and verifying afterward. Reach for it on repetitive multi-file edits, not isolated single-file work.
---

# Sweeping Changes Across Many Files

When the same edit needs to land in dozens of places, treat it as a controlled operation: scope it, preview it, run it, then prove nothing broke.

## Is This the Right Tool?

Fits well:
- Renaming a symbol everywhere it appears
- Dropping a shared import into a whole folder
- Synchronizing a version string across manifest files
- Stamping the same boilerplate onto a set of similar modules
- Swapping a deprecated call for its replacement repo-wide

Poor fit:
- A change confined to one file (edit it directly)
- Edits that differ from file to file (do them one by one)
- Anything needing case-by-case reasoning per file (delegate per area)

---

## The Four-Step Loop

### Step 1 — Pin Down the Change

Write the operation explicitly before touching anything:

```
Match:    [the exact token or pattern]
Becomes:  [the exact replacement]
Within:   [glob of files in scope, e.g. "lib/**/*.js"]
Skip:     [files to leave alone, e.g. "**/*.spec.js"]
```

### Step 2 — Look Before You Leap

Always enumerate the impact first. Never start replacing blind.

```bash
# Which files contain it?
grep -rl 'oldName' lib --include='*.js'

# How many hits per file (drop the zero-hit files)?
grep -rc 'oldName' lib --include='*.js' | grep -v ':0$'

# See the actual lines, with line numbers
grep -rn 'oldName' lib --include='*.js'
```

> **Hard rule:** surface the list of affected files to the user before you modify a single one.

### Step 3 — Run the Sweep

Plain text substitution:

```bash
# Linux / macOS
find lib -name '*.js' -exec sed -i 's/oldName/newName/g' {} +

# Windows (PowerShell)
Get-ChildItem -Path lib -Recurse -Filter *.js |
  ForEach-Object { (Get-Content $_) -replace 'oldName','newName' | Set-Content $_ }
```

Anything beyond a flat find/replace — inserting imports, wrapping blocks, reordering — should go through the Edit tool per file, processed in a stable order (alphabetical, or following the dependency chain) so the run is reproducible.

### Step 4 — Confirm It Held

```bash
# No leftovers — this should print nothing
grep -rl 'oldName' lib --include='*.js'

# Spot-check that the new form landed correctly
grep -rn 'newName' lib --include='*.js' | head -5

# Let the build and suite catch anything subtle
npm run build && npm test
```

---

## Recurring Sweep Recipes

| Change | What it looks like |
|---|---|
| **Rebind an import** | `import { Old }` everywhere becomes `import { New }` |
| **Bump a version** | `"version": "2.3.0"` synced across every manifest |
| **Re-export a symbol** | Append `export { Thing }` to each barrel file |
| **Retire a call** | `oldApi(...)` swapped for `newApi(...)` |
| **Prepend a banner** | License header added atop each source file |
| **Shift a type style** | `interface Foo {` rewritten as `type Foo = {` |

---

## Guard Rails

1. **Preview is mandatory** — list every file before editing it.
2. **Start clean** — commit or `git stash` first so the sweep is reversible.
3. **Mind the tests** — test files often want a different treatment than source; scope them out unless intended.
4. **Validate every run** — a build plus the test suite after each sweep.
5. **Report the diff** — finish with a list of touched files and what changed in each.
