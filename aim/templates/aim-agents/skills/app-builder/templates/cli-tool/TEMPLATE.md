---
name: cli-tool
description: Guiding principles for a Node.js CLI starter — Commander.js, interactive prompts.
---

# CLI Tool Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology |
|-------|------------|
| Runtime | Node.js 24 (Krypton LTS) |
| Language | TypeScript (ESM) |
| CLI framework | Commander.js (v15, needs Node ≥22.12) |
| Prompts | @inquirer/prompts (modular) |
| Output | chalk plus ora |
| Config | cosmiconfig |

---

## Folder Layout

```
project-name/
├── src/
│   ├── index.ts         # Entry point: #!/usr/bin/env node shebang, wires up Commander
│   ├── commands/        # One file per command (factory functions)
│   ├── lib/             # Core logic, framework-agnostic and testable
│   ├── utils/           # logger (chalk/ora), prompt wrappers
│   └── config.ts        # cosmiconfig loader
├── dist/                # Build output (tsup/tsc)
└── package.json         # "type":"module", "bin":{...}
```

---

## CLI Design Principles

| Principle | What it means |
|-----------|---------------|
| Subcommands | group related actions together |
| Options | flags that carry sensible defaults |
| Interactive | prompt the user when input is missing |
| Non-interactive | honor `--yes`-style flags for scripts |

---

## The Key Pieces

| Piece | Why it's here |
|-------|---------------|
| Commander | parses commands (use a local `new Command()` so it stays testable) |
| @inquirer/prompts | modular interactive prompts (`input`, `select`, `confirm`) |
| Chalk | colored output |
| Ora | spinners and loading states |
| Cosmiconfig | finds config files |

---

## Getting Set Up

1. Make the project folder
2. `npm init -y`, then set `"type": "module"`
3. Install: `npm install commander @inquirer/prompts chalk ora cosmiconfig`
4. Point `bin` at the compiled `./dist/index.js` and keep the `#!/usr/bin/env node` shebang
5. `npm link` to test it locally

---

## Publishing

```bash
npm login
npm publish
```

---

## Practices Worth Following

- Keep `src/index.ts` lean; attach commands with `.addCommand()` factories under `src/commands/`
- Push the real work into `lib/` and `utils/` so commands stay thin, testable wrappers
- Default to ESM; build with tsup or esbuild
- Support both interactive use and non-interactive (`--yes`) runs
- Validate inputs with Zod and exit with proper codes (0 for success, 1 for failure)
- Worth knowing about: @clack/prompts (polished prompts) and citty (a light ESM command framework)
