---
name: monorepo-turborepo
description: Guiding principles for a Turborepo monorepo starter — pnpm workspaces, shared packages.
---

# Turborepo Monorepo Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology |
|-------|------------|
| Build system | Turborepo 2.x |
| Package manager | pnpm |
| Apps | Next.js, Express |
| Packages | shared UI, config, types, utils |
| Language | TypeScript |

---

## Folder Layout

```
project-name/
├── apps/
│   ├── web/             # Next.js app
│   ├── api/             # Express API
│   └── docs/            # Documentation
├── packages/
│   ├── ui/              # Shared components (@repo/ui)
│   ├── config/          # ESLint, TS, Tailwind presets (@repo/config)
│   ├── types/           # Shared types (@repo/types)
│   └── utils/           # Shared utilities (@repo/utils)
├── turbo.json           # the "tasks" key (was "pipeline" before v2)
├── pnpm-workspace.yaml
└── package.json         # must carry a "packageManager" field
```

---

## Core Ideas

| Idea | What it means here |
|------|--------------------|
| Workspaces | declared as globs in `pnpm-workspace.yaml` |
| Task graph | lives in `turbo.json` under `tasks` (NOT `pipeline` — renamed in v2) |
| Caching | task results cached locally and remotely |
| Dependencies | the `workspace:*` protocol, namespaced under `@repo/*` |
| Env mode | v2 is strict — declare each task's `env`/`globalEnv` or caching falls over |

---

## Turbo Tasks (turbo.json)

> `tasks` is the v2 key; `pipeline` was renamed. Migrate with `npx @turbo/codemod rename-pipeline`.

| Task | Depends on |
|------|------------|
| build | ^build (dependencies build first) |
| dev | cache: false, persistent |
| lint | ^build |
| test | ^build |

---

## Getting Set Up

1. Make the root folder
2. `pnpm init`
3. Write `pnpm-workspace.yaml`
4. Write `turbo.json`
5. Add the apps and packages
6. `pnpm install`
7. `pnpm dev`

---

## Everyday Commands

| Command | What it does |
|---------|--------------|
| `pnpm dev` | run every app |
| `pnpm build` | build everything |
| `pnpm --filter @name/web dev` | run one app |
| `pnpm --filter @name/web add axios` | add a dep to one app |

---

## Practices Worth Following

- Keep `apps/` (things you deploy) apart from `packages/` (libraries and shared config)
- Namespace internal packages as `@repo/*` and reference them with `workspace:*`
- Declare entrypoints through the `exports` field — it tree-shakes better than barrel files
- Share tsconfig and eslint out of `packages/config`
- Spell out each task's `env`/`globalEnv` (v2's strict env mode)
- Turn on Turbo remote caching for CI
