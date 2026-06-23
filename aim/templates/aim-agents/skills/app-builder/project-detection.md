# Detecting the Project Type

Read a user's request, work out what they want built, and route it to the right starter.

## Wording-to-Type Lookup

Scan the request for any of these cues; each points to a project type and its matching starter.

| Cues in the request | Project type | Starter |
|---------------------|--------------|---------|
| blog, post, article | Blog | astro-static |
| e-commerce, product, cart, payment | Online store | nextjs-saas |
| dashboard, panel, admin, management | Admin dashboard | nextjs-fullstack |
| api, backend, service, rest | API service | express-api |
| python, fastapi, django | Python API | python-fastapi |
| mobile, android, ios, react native | Mobile app (RN) | react-native-app |
| flutter, dart | Mobile app (Flutter) | flutter-app |
| portfolio, personal, cv, resume | Portfolio | nextjs-static |
| crm, customer, sales | CRM | nextjs-fullstack |
| saas, subscription, stripe | SaaS | nextjs-saas |
| landing, promo, marketing | Landing page | nextjs-static |
| docs, documentation | Documentation | astro-static |
| extension, plugin, chrome | Browser extension | chrome-extension |
| desktop, electron | Desktop app | electron-desktop |
| cli, command line, terminal | CLI tool | cli-tool |
| monorepo, workspace | Monorepo | monorepo-turborepo |

## How to Work Through a Request

```
1. Split the request into words
2. Pull out the meaningful cues
3. Land on a project type
4. Note anything the request leaves unsaid -> pass it to the planner / orchestrator
5. Recommend a stack
```

## Breaking Ties

A request can trip more than one cue. Take, for instance, "a CLI to manage my e-commerce products" — it fires both `cli` and `e-commerce`. Apply these rules top to bottom and stop at the first one that decides it.

| Order | Rule | Worked example |
|-------|------|----------------|
| 1 | **The delivery platform beats the subject area.** A named platform (mobile, desktop, cli, extension) wins over a web or business domain (e-commerce, crm, blog). | "CLI to manage e-commerce" -> **cli-tool**; e-commerce is just the data it touches, not what ships |
| 2 | **The main noun beats its modifiers.** Whatever noun names the thing being built outweighs the words describing it. | "a **dashboard** for my Shopify store" -> **nextjs-fullstack**; the dashboard is the deliverable, Shopify is background |
| 3 | **Still a tie? Ask.** When nothing above settles it, do not guess. Put the candidates to the user at the Socratic Gate (Phase 0) and let them pick. | "an app for my shop" -> ask whether they mean web, mobile, or desktop |
