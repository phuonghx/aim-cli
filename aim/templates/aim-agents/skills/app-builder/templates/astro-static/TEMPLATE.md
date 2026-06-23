---
name: astro-static
description: Guiding principles for an Astro static-site starter — content-driven sites, blogs, documentation.
---

# Astro Static Site Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology |
|-------|------------|
| Framework | Astro 6.x |
| Content | MDX with Content Collections (Content Layer API) |
| Styling | Tailwind CSS v4 (@tailwindcss/vite) |
| Integrations | Sitemap, RSS, SEO |
| Output | static / SSG |

---

## Folder Layout

```
project-name/
├── src/
│   ├── components/      # .astro components
│   ├── content/         # Collection entries (blog/, docs/ as .md / .mdx)
│   ├── layouts/         # Page layouts
│   ├── pages/           # File-based routing (the one reserved dir)
│   ├── styles/
│   │   └── global.css   # @import "tailwindcss";
│   └── content.config.ts # Collection definitions (Content Layer, at the src/ root)
├── public/              # Static assets
├── astro.config.mjs
└── package.json
```

---

## Core Ideas

| Idea | What it means here |
|------|--------------------|
| Content Layer API | collections declared in `src/content.config.ts` with `loader`s (glob/file) and Zod schemas |
| Islands architecture | hydrate only the interactive parts |
| Zero JS by default | plain static HTML unless a component needs more |
| MDX support | Markdown that can render components |

---

## Getting Set Up

1. `npm create astro@latest {{name}}`
2. Add integrations: `npx astro add mdx sitemap`
3. Add Tailwind v4: `npx astro add tailwind` (this pulls in @tailwindcss/vite, not the old @astrojs/tailwind)
4. Declare collections in `src/content.config.ts` with `loader`s and Zod schemas
5. `npm run dev`

---

## Deployment

| Platform | How |
|----------|-----|
| Vercel | auto-detected |
| Netlify | auto-detected |
| Cloudflare Pages | auto-detected |
| GitHub Pages | build-and-deploy action |

---

## Practices Worth Following

- Lean on Content Collections for type safety
- Let pages render statically
- Add islands only where interactivity is genuinely needed
- Optimize images with Astro's Image component
