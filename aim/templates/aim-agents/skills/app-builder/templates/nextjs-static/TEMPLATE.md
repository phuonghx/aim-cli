---
name: nextjs-static
description: A current Next.js 16 / React 19 / Tailwind v4 starter, tuned for landing pages and portfolios.
---

# Next.js Static Site Starter

> The versions below track the stable line as of 2026-05. Pin to the current stable release when you scaffold.

## Stack

| Piece | Technology | Notes |
|-------|------------|-------|
| Framework | Next.js 16+ | App Router, Turbopack, static export |
| Core | React 19 | Server Components, new hooks, the Compiler |
| Language | TypeScript | strict mode |
| Styling | Tailwind CSS v4 | CSS-first config (no JS config), Oxide engine |
| Animation | Framer Motion | layout transitions and gestures |
| Icons | Lucide React | small SVG icon set |
| SEO | Metadata API | Next.js's built-in API (no more next-seo) |

---

## Folder Layout

Tailwind v4 trims this down, since the theme now lives inside CSS.

```
project-name/
├── src/
│   ├── app/
│   │   ├── layout.tsx    # Root SEO metadata
│   │   ├── page.tsx      # Landing page
│   │   ├── globals.css   # Tailwind v4 import + @theme config
│   │   ├── not-found.tsx # Custom 404
│   │   ├── sitemap.ts    # Generated sitemap (metadata convention)
│   │   ├── robots.ts     # Generated robots.txt (metadata convention)
│   │   ├── opengraph-image.tsx # Dynamic OG image
│   │   └── (routes)/     # Route groups (about, contact, …)
│   ├── components/
│   │   ├── layout/       # Header, Footer
│   │   ├── sections/     # Hero, Features, Pricing, CTA
│   │   └── ui/           # Atomic pieces (Button, Card)
│   └── lib/
│       └── utils.ts      # Helpers (cn, formatters)
├── content/              # Markdown / MDX content
├── public/               # Static assets (images, fonts)
├── next.config.ts        # Config in TypeScript
└── package.json
```

---

## Static Export Config

Written in `next.config.ts` rather than `.js` for the type safety.

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',        // required for static hosts (S3, GitHub Pages)
  images: {
    unoptimized: true      // required without a Node.js image-optimization server
  },
  trailingSlash: true,     // smooths over 404s on some hosts; good for SEO
  reactStrictMode: true,
};

export default nextConfig;
```

---

## SEO via the Metadata API

next-seo is retired; set this in `layout.tsx` or `page.tsx`.

```typescript
// src/app/layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    template: '%s | Product Name',
    default: 'Home - Product Name',
  },
  description: 'SEO-friendly description for the landing page.',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://mysite.com',
    siteName: 'My Brand',
  },
};
```

---

## Landing Page Building Blocks

| Section | Job | Suggested component |
|---------|-----|---------------------|
| Hero | the first impression — H1 and primary CTA | `<HeroSection />` |
| Features | what the product does well (grid or bento) | `<FeaturesGrid />` |
| Social proof | partner logos, usage numbers | `<LogoCloud />` |
| Testimonials | what customers say | `<TestimonialCarousel />` |
| Pricing | the plans on offer | `<PricingCards />` |
| FAQ | questions and answers (also helps SEO) | `<Accordion />` |
| CTA | the closing push to convert | `<CallToAction />` |

---

## Animation Recipes (Framer Motion)

| Pattern | Where it fits | How |
|---------|---------------|-----|
| Fade up | headlines and paragraphs | `initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}` |
| Stagger | lists of features or cards | variants with `staggerChildren` |
| Parallax | background art or floating elements | `useScroll` and `useTransform` |
| Micro-interaction | button hovers and taps | `whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}` |

---

## Getting Set Up

1. Spin up the project:
   ```bash
   npx create-next-app@latest my-site --typescript --tailwind --eslint
   # Answer Yes to App Router
   # Answer No to customizing the import alias
   ```

2. Add the extra libraries:
   ```bash
   npm install framer-motion lucide-react clsx tailwind-merge
   # clsx and tailwind-merge tidy up dynamic class handling
   ```

3. Configure Tailwind v4 in `src/app/globals.css`:
   ```css
   @import "tailwindcss";

   @theme {
     --color-primary: #3b82f6;
     --font-sans: 'Inter', sans-serif;
   }
   ```

4. Develop:
   ```bash
   npm run dev --turbopack
   ```

---

## Deployment

| Platform | How | Watch out for |
|----------|-----|---------------|
| Vercel | git push | detects Next.js automatically; best performance |
| GitHub Pages | GitHub Actions | set `basePath` in `next.config.ts` unless you use a custom domain |
| AWS S3 / CloudFront | upload the `out` folder | point the error document at `404.html` |
| Netlify | git push | set the build command to `npm run build` |

---

## Practices Worth Following

- **Server Components first**: leave components on the server by default; add `'use client'` only when you need state (`useState`) or events (`onClick`).
- **Images**: use `<Image />`, but remember `unoptimized: true` for static export, or route through an image CDN (Cloudinary, Imgix).
- **Fonts**: `next/font` (Google Fonts) self-hosts them and heads off layout shift.
- **Responsive**: design mobile-first using Tailwind's `sm:`, `md:`, `lg:` prefixes.
