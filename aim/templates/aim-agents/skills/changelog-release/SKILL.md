---
name: changelog-release
description: Generates a Keep a Changelog file and cuts a Semantic Versioning release. Derives the major/minor/patch bump from Conventional Commit history, maintains the Unreleased section, sorts entries into Added/Changed/Deprecated/Removed/Fixed/Security, then tags vX.Y.Z and drafts release notes. Use when preparing a release, updating CHANGELOG.md, or deciding the next version number.
allowed-tools: Read, Glob, Grep, Edit, Bash
effort: low
---

# Changelog & Release

> Keep a Changelog for humans, SemVer for tooling, Conventional Commits as the source.

---

## Release Flow

```
Collect commits since last tag → Derive bump → Move Unreleased → release →
  Add date + version heading → Tag vX.Y.Z → Generate release notes → Push
```

---

## Changelog Format (Keep a Changelog 1.1.0)

`CHANGELOG.md` lives at repo root, newest version on top, with a live
`[Unreleased]` section you append to as you merge.

```markdown
# Changelog
All notable changes to this project are documented here.
Format: Keep a Changelog. Versioning: Semantic Versioning.

## [Unreleased]

## [1.4.0] - 2026-06-23
### Added
- OAuth login via GitHub (#231)
### Fixed
- Crash when config file is empty (#240)

## [1.3.1] - 2026-05-02
### Security
- Patch path-traversal in file upload (CVE-2026-1234)

[Unreleased]: https://example.com/repo/compare/v1.4.0...HEAD
[1.4.0]: https://example.com/repo/compare/v1.3.1...v1.4.0
[1.3.1]: https://example.com/repo/compare/v1.3.0...v1.3.1
```

### The Six Categories

| Category | Use for |
|----------|---------|
| **Added** | New features |
| **Changed** | Changes to existing behavior |
| **Deprecated** | Soon-to-be-removed features (warn before Removed) |
| **Removed** | Features taken out this release |
| **Fixed** | Bug fixes |
| **Security** | Vulnerability fixes — always call out |

Write entries for **humans**: describe the user-visible effect, not the diff.
Omit empty categories. Link issues/PRs.

---

## Deriving the Version Bump

Read commit subjects since the last tag and map Conventional Commits → SemVer:

| Commit signal | Bump | Example |
|---------------|------|---------|
| `BREAKING CHANGE:` footer or `feat!:` / `fix!:` | **MAJOR** `X` | 1.4.0 → 2.0.0 |
| `feat:` | **MINOR** `Y` | 1.4.0 → 1.5.0 |
| `fix:` / `perf:` | **PATCH** `Z` | 1.4.0 → 1.4.1 |
| `docs:` `chore:` `refactor:` `test:` `ci:` `style:` | none (unless paired with above) | — |

The **highest** signal wins: one `feat!` makes the whole release MAJOR.

```bash
# Commits since the last tag — scan these for the bump
git log "$(git describe --tags --abbrev=0)"..HEAD --pretty=format:'%s%n%b'
```

> **0.y.z pre-1.0:** anything MAY break. Bump MINOR for breaking changes,
> PATCH for everything else, until you commit to 1.0.0.

---

## Mapping Commits → Categories

| Commit type | Changelog category |
|-------------|--------------------|
| `feat:` | Added (or Changed if it alters existing behavior) |
| `fix:` | Fixed |
| `perf:` | Changed |
| breaking (`!` / footer) | Changed or Removed (+ note the migration) |
| `revert:` | Removed / Fixed depending on what was reverted |
| `docs/chore/ci/style/test` | usually omitted from user-facing notes |

---

## Cutting the Release

```bash
VERSION=1.5.0   # decided from the bump table

# 1. CHANGELOG: rename [Unreleased] -> [VERSION] - YYYY-MM-DD, add fresh Unreleased,
#    update the compare links at the bottom. (edit the file)

# 2. Bump the manifest (package.json, pyproject.toml, Cargo.toml, ...)

# 3. Commit the release prep
git commit -am "chore(release): v$VERSION"

# 4. Annotated tag — vX.Y.Z, the 'v' prefix is the common convention
git tag -a "v$VERSION" -m "Release v$VERSION"

# 5. Push commit + tag (a tag push often triggers CI publish)
git push origin main --follow-tags
```

---

## Release Notes

Derive from the new changelog section; lead with what users care about.

```markdown
## v1.5.0
**Highlights:** GitHub OAuth login, faster cold start.

⚠️ Breaking: `--config` now requires an absolute path. See MIGRATION.md.

### Added / Changed / Fixed / Security
<the entries from CHANGELOG.md for this version>

**Full changelog:** v1.4.0...v1.5.0
```

---

## Checklist

- [ ] `[Unreleased]` reflects everything merged since last tag
- [ ] Version bump matches the highest commit signal (MAJOR > MINOR > PATCH)
- [ ] Entries are human-readable and sorted into the six categories
- [ ] Breaking changes flagged + migration noted
- [ ] Manifest version == changelog version == tag
- [ ] Annotated `vX.Y.Z` tag created and pushed with `--follow-tags`
- [ ] Release notes drafted from the changelog section

---

## Pairs With

- **conventional-commits** — the structured history this skill reads to pick the bump.
- **`/pr` flow** — merge feature PRs into `[Unreleased]`; cut the release from `main`.

---

> **Remember:** the changelog is curated, not auto-dumped. Conventional Commits
> decide the *number*; you still write entries a human would want to read.
