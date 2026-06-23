# Contributing to AIM

Thanks for your interest in improving AIM. This guide covers how to set up a
development environment, the conventions we follow, and what we expect in a pull
request.

AIM is a zero-dependency Python CLI (Python 3.8+). Please keep the runtime
dependency-free: the standard library only.

## Development setup

Clone the repository, create a virtual environment, and install the package in
editable mode:

```bash
git clone https://github.com/phuonghx/aim-cli.git
cd aim-cli

python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\Activate.ps1       # Windows (PowerShell)

pip install -e .
```

The editable install puts the `aim` command on your `PATH`, so changes to the
source are picked up immediately.

## Running tests

We use `pytest`. Run the full suite from the repository root:

```bash
pytest -q
```

Please add tests for any behavior you add or change, and make sure the suite is
green before opening a pull request.

## Linting

We use `ruff`. Lint the package and tests before committing:

```bash
ruff check aim tests
```

The lint gate is intentionally high-signal (syntax errors, undefined names,
bare excepts, unused imports). Keep it clean.

## Working on skills

Skills are part of the unified context that AIM compiles into per-tool
instruction files. After adding or editing a skill, validate it with the
built-in linter:

```bash
aim lint
```

Fix any issues `aim lint` reports before submitting. This keeps the compiled
output (CLAUDE.md, AGENTS.md, .cursorrules, .windsurfrules, GEMINI.md, and
.github/copilot-instructions.md) consistent and valid.

## Branches and commits

Create a topic branch off `main`:

```bash
git switch -c feat/short-description
```

We follow [Conventional Commits](https://www.conventionalcommits.org/) for
commit messages. Use one of the common types and a concise, imperative summary:

```
feat: add MCP server health check
fix(install): keep quotes when probing the Scripts directory
docs: clarify dashboard token usage
test: cover doctor drift detection
chore: bump ruff configuration
```

Common types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.

## Pull request checklist

Before opening a pull request, please confirm:

- [ ] The change is focused and described clearly (link any related issue).
- [ ] `pytest -q` passes.
- [ ] `ruff check aim tests` is clean.
- [ ] `aim lint` passes if you touched any skills.
- [ ] New or changed behavior is covered by tests.
- [ ] Documentation is updated if behavior or usage changed.
- [ ] Commits follow Conventional Commits.
- [ ] No new runtime dependencies were introduced.

## Code of Conduct

This project is governed by our
[Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to
uphold it.
