---
name: app-builder
description: Turns plain-language app requests into working full-stack projects. It infers the kind of application being asked for, picks a sensible technology stack, lays out the folder structure, and hands work off to specialist agents. Reach for it when starting a brand-new project, deciding which frameworks to use, or generating an initial scaffold. Drives the /create flow.
---

# App Builder

Orchestrates new-application work end to end: it reads what the user wants, settles on a stack, sketches the file layout, and delegates the build to specialist agents.

## Read Only What You Need

Do not load every file in this folder. Consult the map below, open the one or two pages that match the task at hand, and skip the rest.

| File | What it covers | Open it when |
|------|----------------|--------------|
| `project-detection.md` | Mapping request wording to a project type | Kicking off a new build |
| `tech-stack.md` | Recommended stack plus swap-in options | Settling on technologies |
| `agent-coordination.md` | The agent pipeline and the order they run | Running multi-agent work |
| `scaffolding.md` | Folder layout and the files that anchor it | Generating the project skeleton |
| `feature-building.md` | Scoping changes, recovering from errors | Extending a project that already exists |
| `templates/SKILL.md` | The full template catalog | Scaffolding from a starter |

---

## Starter Templates (13)

Each template is a ready-made starting point for one kind of project. Open the single template that fits; do not read them all.

| Template | Stack | Best for |
|----------|-------|----------|
| [nextjs-fullstack](templates/nextjs-fullstack/TEMPLATE.md) | Next.js + Prisma | Full-stack web app |
| [nextjs-saas](templates/nextjs-saas/TEMPLATE.md) | Next.js + Stripe | Subscription product |
| [nextjs-static](templates/nextjs-static/TEMPLATE.md) | Next.js + Framer Motion | Marketing / landing page |
| [nuxt-app](templates/nuxt-app/TEMPLATE.md) | Nuxt 4 + Pinia | Vue full-stack app |
| [express-api](templates/express-api/TEMPLATE.md) | Express + JWT | REST backend |
| [python-fastapi](templates/python-fastapi/TEMPLATE.md) | FastAPI | Python backend |
| [react-native-app](templates/react-native-app/TEMPLATE.md) | Expo + Zustand | Mobile app |
| [flutter-app](templates/flutter-app/TEMPLATE.md) | Flutter + Riverpod | Cross-platform mobile |
| [electron-desktop](templates/electron-desktop/TEMPLATE.md) | Electron + React | Desktop app |
| [chrome-extension](templates/chrome-extension/TEMPLATE.md) | Chrome MV3 | Browser extension |
| [cli-tool](templates/cli-tool/TEMPLATE.md) | Node.js + Commander | Command-line tool |
| [monorepo-turborepo](templates/monorepo-turborepo/TEMPLATE.md) | Turborepo + pnpm | Multi-package repo |
| [astro-static](templates/astro-static/TEMPLATE.md) | Astro + MDX | Blog / docs site |

---

## Specialist Agents

| Agent | Responsibility |
|-------|----------------|
| `project-planner` | Breaks work into tasks and maps dependencies |
| `frontend-specialist` | Pages and UI components |
| `backend-specialist` | APIs and business rules |
| `database-architect` | Schema and migrations |
| `devops-engineer` | Deploy and preview |

---

## Worked Example

```
Request: "Build me an Instagram-style app where people post photos and like them"

How App Builder responds:
1. Classify the request -> photo-sharing social app
2. Choose a stack -> Next.js + Prisma + Cloudinary + Clerk
3. Draft the plan:
   - Schema: users, posts, likes, follows
   - API surface: auth, posts, likes, follows
   - Screens: feed, profile, upload
   - Components: PostCard, Feed, LikeButton
4. Dispatch the specialist agents
5. Surface progress along the way
6. Boot the preview
```

---

## Visual Dashboard Integration

The App Builder can be run visually via the **App Builder Tab** in the AIM Control Hub Dashboard.

1. Navigate to the App Builder tab in the browser dashboard.
2. Select one of the 13 starter templates from the grid.
3. Configure target project name, description, and destination path.
4. Click **Generate Project & Link Task** to scaffold the folder structure and automatically create an AIM task linked to the project setup.
5. Use the `/aim-task` and `/aim-docs` slash commands inside chat, or the dashboard Task Board, to track and implement the generated project checklist.
