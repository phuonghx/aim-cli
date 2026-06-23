---
name: code-review-graph
description: An MCP server that parses a codebase into an AST graph (Tree-sitter into SQLite) so an assistant can fetch only the files in a change's blast radius instead of reading everything. It cuts token use on large repos and supports dead-code detection, refactor previews, and architecture maps. Best on big or multi-repo projects; little benefit on small ones with isolated edits.
---

# Code Review Graph — Structural Context over Brute-Force Reading

Instead of letting an assistant read an entire directory to understand a change, hand it a structural map. The graph returns only the files actually connected to what you touched.

## What It Is

`code-review-graph` runs as an MCP server. It uses **Tree-sitter** to parse source into an abstract syntax tree, stores the resulting nodes and relationships in **SQLite**, and answers context queries from that graph. Ask "what does changing this file affect?" and it returns the impacted files — the **blast radius** — rather than the whole tree.

The token savings track codebase size:

| Repo | What to expect |
|------|----------------|
| Huge monorepo (10K+ files) | Largest win — only a sliver gets read |
| Mid-size app (1–5K files) | Solid reduction on cross-file changes |
| Small project (<200 files) | Marginal — graph upkeep can outweigh it |

Scoping to the blast radius also trims noise, which tends to sharpen review focus. Treat any cited multiplier as illustrative and measure on your own repo.

## Deciding Whether to Use It

**Lean in when** the repo is 500+ files, changes routinely span modules, monthly token spend is meaningful, or you live in monorepo / microservice / cross-package territory.

**Skip it when** the repo is under ~200 files with self-contained edits, the code leans heavily on dynamic tricks (reflection, runtime codegen, dynamic imports), or you want zero maintenance — the graph must stay in sync to be useful.

**Benchmark first when** you're in the 200–500 file range or mixing static and dynamic patterns; test on representative commits before committing.

## Opt-In Bootstrap

On a mid-to-large project, confirm availability before depending on it:

1. Is the tool installed? `Get-Command code-review-graph` (Windows) or `which code-review-graph` (Unix).
2. Does a `.code-review-graph/` directory already exist in the workspace?
3. Installed but no index? Ask before running `code-review-graph build` — it scans the whole project.
4. Not installed and the project is large? Offer to `pip install code-review-graph` and build a local map, but never install or build without the user agreeing.

## The Pipeline

```
parse  -> Tree-sitter turns source into ASTs (19 languages)
store  -> nodes and edges land in a SQLite graph
trace  -> BFS walks edges to compute a change's blast radius
serve  -> MCP hands the graph to the assistant
```

**Nodes** represent files, functions, methods, classes, imports, and tests. **Edges** capture relationships — calls, imports, test-covers-function, class-extends-class. **Metadata** keeps name, type, path, and line span per node. Notably, only structure is stored — no source text lives in the graph.

**Languages:** Python, TypeScript, JavaScript, Go, Rust, Java, C#, Ruby, Kotlin, Swift, PHP, C/C++, Vue SFC, Solidity, Dart, R, Perl, Lua, and Jupyter/Databricks notebooks.

## Setup

Prerequisites: Python 3.9+, pip or pipx, an MCP-aware client, and a git-tracked repo for incremental updates.

```bash
# install (pick one)
pipx install code-review-graph     # isolated, recommended
uvx code-review-graph install      # no permanent install
pip install code-review-graph      # global

# wire up your editor, then restart it
code-review-graph install                         # auto-detect clients
code-review-graph install --platform cursor       # or target one

# build the first graph
cd /your/project && code-review-graph build

# keep it fresh (incremental, ~1s per change)
code-review-graph watch
# or update by hand
code-review-graph update
```

Rough build times: ~500 files in well under a minute, ~5K files in a few minutes, ~27K files in roughly ten. After install, verify the server shows up in your client's MCP list.

## What You Can Do With It

- **Blast-radius scoping (the main event):** automatic once the server is live — the assistant pulls the impacted files instead of the directory. A change to `auth/middleware.py` returns a dozen connected files rather than two hundred.
- **Risk scoring:** `code-review-graph detect-changes` ranks uncommitted edits by dependent count, missing test coverage, and whether they sit on a critical path — flagging the risky ones before review.
- **Dead code:** nodes with no incoming edges (no callers, importers, or tests) surface as removal candidates on mature code.
- **Refactor preview:** `code-review-graph rename preview --from Old --to New` lists every affected file and warns where dynamic string references could slip past static analysis.
- **Architecture map:** `code-review-graph visualize` clusters modules via community detection — handy for onboarding and spotting over-coupling.
- **Docs:** `code-review-graph wiki` emits a markdown overview of modules, public APIs, and coverage.

## Configuration

Create `.code-review-graphignore` (gitignore syntax) and exclude noise so the graph stays meaningful:

```
dist/**
build/**
.next/**
node_modules/**
vendor/**
generated/**
*.generated.ts
*.min.js
```

For microservices, register extra repos so the server serves cross-repo context:

```bash
code-review-graph register /path/to/other/repo
code-review-graph repos
```

## Known Gaps

| Gap | Why it matters | What to do |
|-----|----------------|-----------|
| Dynamic imports (`import(buildPath())`) | Edges invisible to the parser | Note manually or accept over-prediction |
| Reflection (signals, `getattr`, Java reflection) | Missed edges | An LSP-based tool handles these better |
| Runtime-generated code (`eval`, templates) | Unparseable statically | Exclude or accept the gap |
| Cross-language calls | No edges between runtimes | Multi-repo registration partially helps |
| Stale graph (no watch) | Outdated relationships | Run `update` first, or just use watch mode |
| TS path aliases (`@/...`) | May need tsconfig resolution | Confirm the resolver covers your setup |

## How It Fits a Workflow

Pair it with related practices: a blast-radius graph trims **input** context while output discipline trims verbosity; precise file lists let you dispatch focused workers; a clean session per task keeps things tight; and saving key decisions carries them forward. A good rhythm: fresh session per task → graph pre-filters to the blast radius → summarize finished phases → persist decisions → minimal tokens, maximal focus.

**Habits that pay off:** keep watch mode on, exclude generated files, measure a before/after week on your own repo, and register every repo in a microservice setup.
