---
name: using-git-worktrees
description: Runs parallel work in isolated git worktree checkouts that share one repository, then merges results back. Use when several agents or tasks would otherwise collide in a single working tree, when a hotfix is needed mid-feature without stashing, or when comparing two branches side by side. Covers adding, listing, removing, and pruning worktrees plus cleanup pitfalls.
allowed-tools: Read, Glob, Grep, Bash
effort: low
---

# Using Git Worktrees

> One repo, many checkouts — parallel branches without stashing or cloning.

A worktree is a second working directory backed by the **same** `.git`. Each tree
has its own branch, index, and files, so agents never fight over one checkout.

---

## When to Use

✅ **Good for:**
- Parallel agents each owning a branch (build, refactor, docs at once)
- Urgent hotfix while a feature is half-done — no `git stash` dance
- Reviewing/testing branch B without disturbing branch A
- Long builds: keep working in tree A while tree B compiles

❌ **Not for:**
- A single linear branch (just use the main checkout)
- Editing the *same* branch from two trees (Git forbids it anyway)
- Throwaway one-liners where switching is faster

---

## Core Commands

```bash
# Create a new tree + branch in one step (sibling dir, NOT nested in repo)
git worktree add ../proj-feature -b feature/login

# Attach an existing branch
git worktree add ../proj-hotfix hotfix/crash

# Detached checkout of a tag/commit for inspection
git worktree add --detach ../proj-v1 v1.2.0

# See every tree, its branch, and HEAD
git worktree list

# Remove a tree when done (must be clean, or add --force)
git worktree remove ../proj-feature

# Drop bookkeeping for trees deleted manually from disk
git worktree prune
```

---

## Conventions

| Rule | Why |
|------|-----|
| Put trees as **siblings** (`../proj-feature`), never inside the repo | A nested tree gets swept into Git status and ignore rules |
| **One branch per tree** | Git refuses to check out the same branch twice; keeps ownership clear |
| Name the dir after the branch (`proj-<slug>`) | `git worktree list` becomes self-documenting |
| One agent ↔ one tree | Isolates state; merge happens only at the end |
| Branch off the same base (`-b feat origin/main`) | Predictable, conflict-light merges |

---

## Workflow Example

```bash
# 0. Start from an up-to-date main
git -C ./proj fetch origin

# 1. Spin up two isolated trees for two agents
git -C ./proj worktree add ../proj-api   -b feat/api   origin/main
git -C ./proj worktree add ../proj-ui    -b feat/ui    origin/main

# 2. Each tree installs its OWN deps (not shared — see pitfalls)
( cd ../proj-api && npm ci )
( cd ../proj-ui  && npm ci )

# 3. Agents work in parallel, commit on their branches...

# 4. Merge back from the canonical tree
git -C ./proj merge --no-ff feat/api
git -C ./proj merge --no-ff feat/ui      # resolve conflicts once, here

# 5. Tear down
git -C ./proj worktree remove ../proj-api
git -C ./proj worktree remove ../proj-ui
git -C ./proj worktree prune
```

---

## Pitfalls

- **`node_modules` / build dirs are per-tree.** They are not shared via `.git`;
  run `npm ci` (or equivalent) in each tree. Reusing one folder breaks native
  binaries and lockfile assumptions.
- **Submodules need re-init per tree:** `git submodule update --init --recursive`
  after `worktree add`.
- **Same branch in two trees is blocked.** Use a fresh branch or `--detach`.
- **Deleting a tree's folder by hand** leaves a stale entry — always follow with
  `git worktree prune`.
- **`.env` / local config don't copy.** Recreate secrets and untracked config in
  each tree.
- **Don't delete the main tree** — it owns the shared `.git`; removing it
  orphans every other worktree.
- **Locked trees** (on removable/network drives): `git worktree lock` to prevent
  auto-prune, `unlock` before removing.

---

## Cleanup Checklist

- [ ] Branch merged or intentionally abandoned
- [ ] `git worktree remove <path>` (or `--force` if dirty and discardable)
- [ ] `git worktree prune` to clear stale metadata
- [ ] Delete the now-merged branch: `git branch -d <branch>`
- [ ] `git worktree list` shows only trees you still need

---

> **Remember:** worktrees isolate *files and branches*, not *dependencies*.
> Treat each tree as a full checkout — install, configure, and clean it up on its own.
