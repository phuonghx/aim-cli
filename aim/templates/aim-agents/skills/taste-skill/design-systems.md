# design-systems.md — Foundations, install lines, and sources

Open this when picking what to build on. Two honesty rules govern everything here:

1. **If the brief maps to a real product system, use the official package** — install it, theme it, don't rebuild its CSS by hand and don't import its tokens only to override most of them.
2. **One system per project.** Never mix two component libraries in one tree.

---

## When the brief maps to a real system

| The brief reads like… | Use | Why |
|---|---|---|
| Microsoft / enterprise SaaS | `@fluentui/react-components` (or the web-components build) | Official Fluent, Microsoft tokens, accessibility handled |
| Google/Material-flavored product | `@material/web` + Material 3 tokens | Official, theme-able through Material Theming |
| IBM-style enterprise analytics | `@carbon/react` + `@carbon/styles` | Mature data-density patterns |
| Shopify admin surface | Polaris (web components / React) | Required for Shopify app UI |
| Atlassian / Jira-style product | `@atlaskit/*` + `@atlaskit/tokens` | Official Atlassian system |
| GitHub-style devtool or community page | `@primer/css` (product) or `@primer/react-brand` (marketing) | Official Primer |
| UK public-sector service | `govuk-frontend` | Expected by regulation |
| US public-sector / trust-first | `uswds` | Same |
| Quick local-business / agency MVP | Bootstrap 5.3 | Plain, fast, dependable |
| Modern accessible React base | `@radix-ui/themes` | Primitives plus a polished theme |
| Modern SaaS where you own the components | shadcn/ui (`npx shadcn@latest add …`) | You own the code; never ship the default look |
| Tailwind-based modern SaaS / AI marketing | Tailwind v4 utilities + `dark:` | Sensible default for small-team builds |

---

## When the brief is an aesthetic, not a system

No single package owns these. Build with native CSS plus a utility framework and one maintained component set, and label borrowed inspiration honestly in comments.

| Aesthetic | Honest implementation |
|---|---|
| Glass / frosted | `backdrop-filter`, layered borders, highlight overlays; solid fallback under `prefers-reduced-transparency` |
| Bento tile grid | CSS Grid with mixed cell spans; no library owns it |
| Brutalist | Native CSS, mono type, raw borders |
| Editorial / magazine | Serif type, asymmetric grid, generous whitespace |
| Dark / technical | Mono plus an accent, terminal motifs |
| Aurora / mesh gradient | Layered radial gradients or SVG |
| Kinetic type | CSS animation, scroll-driven animation, GSAP for hijacks |
| "Liquid Glass" | An **Apple-platform** material. There is no official web package. Any web version is a labeled frosted-glass approximation (see end of file) |

---

## Install commands

```bash
# Material Web (Material 3)
npm install @material/web

# Fluent UI React (v9)
npm install @fluentui/react-components
# Fluent UI web components (framework-free)
npm install @fluentui/web-components @fluentui/tokens

# IBM Carbon
npm install @carbon/react @carbon/styles

# Radix Themes
npm install @radix-ui/themes

# shadcn/ui (you own the component code)
npx shadcn@latest init
npx shadcn@latest add button card badge separator input

# Primer — product UI / marketing UI
npm install --save @primer/css
npm install @primer/react-brand

# GOV.UK Frontend
npm install govuk-frontend

# USWDS
npm install uswds

# Atlassian (Atlaskit)
yarn add @atlaskit/css-reset @atlaskit/tokens @atlaskit/button @atlaskit/badge @atlaskit/section-message @atlaskit/card

# Bootstrap 5.3
npm install bootstrap

# Shopify Polaris web components (Shopify apps only) — add to the app HTML head:
#   <meta name="shopify-api-key" content="%SHOPIFY_API_KEY%" />
#   <script src="https://cdn.shopify.com/shopifycloud/polaris.js"></script>
```

Confirm any package is in `package.json` before importing it; if it is missing, emit the install line first.

---

## Canonical sources (consult before reinventing)

- **Material Web** — material-web.dev/theming/material-theming, m3.material.io/develop/web, github.com/material-components/material-web
- **Fluent UI** — fluent2.microsoft.design/get-started/develop, learn.microsoft.com/fluent-ui/web-components, github.com/microsoft/fluentui
- **Carbon** — carbondesignsystem.com, the React and web-components tutorials there, github.com/carbon-design-system/carbon
- **Shopify Polaris** — shopify.dev/docs/api/app-home/web-components, polaris-react.shopify.com/components, github.com/Shopify/polaris-react
- **Atlassian** — atlassian.design/get-started/develop, atlassian.design/tokens/design-tokens, atlaskit.atlassian.com
- **Primer** — primer.style, github.com/primer/css, github.com/primer/brand
- **GOV.UK** — design-system.service.gov.uk, github.com/alphagov/govuk-frontend
- **USWDS** — designsystem.digital.gov/documentation/developers, github.com/uswds/uswds
- **Bootstrap** — getbootstrap.com/docs/5.3
- **Tailwind** — tailwindcss.com/docs/dark-mode, tailwindcss.com/blog/tailwindcss-v4
- **Radix** — radix-ui.com/themes/docs, github.com/radix-ui/themes
- **shadcn/ui** — ui.shadcn.com/docs, github.com/shadcn-ui/ui
- **Native CSS / W3C** — MDN for `backdrop-filter`, `prefers-color-scheme`, `prefers-reduced-motion`, CSS Grid, and scroll-driven animations; drafts.csswg.org/scroll-animations-1
- **Apple materials** — developer.apple.com/design/human-interface-guidelines/materials and the Liquid Glass / SwiftUI Material developer docs (Apple platforms)

---

## Apple "Liquid Glass" — honest web approximation

**What is real:** Apple documents Liquid Glass as a dynamic *material for Apple platforms*, inside its Human Interface Guidelines and developer docs. Its native implementation belongs to Apple's platform APIs and system components.

**What is not real:** there is no Apple-issued `liquid-glass.css` for ordinary websites. A web version layers `backdrop-filter`, transparency, borders, highlight gradients, and motion — that is *web frosted-glass*, not Apple's material. Label it as an approximation in comments, and always keep enough contrast to read it without the blur.

```css
/* Web frosted-glass approximation — NOT Apple's Liquid Glass material. */
.glass-approx {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border-radius: 999px;
  border: 1px solid rgb(255 255 255 / 0.32);
  background:
    linear-gradient(135deg, rgb(255 255 255 / 0.30), rgb(255 255 255 / 0.08)),
    rgb(255 255 255 / 0.12);
  backdrop-filter: blur(24px) saturate(180%) contrast(1.05);
  -webkit-backdrop-filter: blur(24px) saturate(180%) contrast(1.05);
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / 0.48),
    inset 0 -1px 0 rgb(255 255 255 / 0.12),
    0 18px 60px rgb(0 0 0 / 0.18);
}

/* Top-edge highlight to fake refraction. */
.glass-approx::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  border-radius: inherit;
  pointer-events: none;
  background:
    radial-gradient(circle at 20% 0%, rgb(255 255 255 / 0.55), transparent 34%),
    linear-gradient(90deg, rgb(255 255 255 / 0.18), transparent 42%, rgb(255 255 255 / 0.14));
}

/* Inner hairline for a crisp edge. */
.glass-approx::after {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: inherit;
  border: 1px solid rgb(255 255 255 / 0.14);
  pointer-events: none;
}

@media (prefers-color-scheme: dark) {
  .glass-approx {
    border-color: rgb(255 255 255 / 0.18);
    background:
      linear-gradient(135deg, rgb(255 255 255 / 0.16), rgb(255 255 255 / 0.04)),
      rgb(15 23 42 / 0.42);
    box-shadow:
      inset 0 1px 0 rgb(255 255 255 / 0.22),
      0 18px 60px rgb(0 0 0 / 0.42);
  }
}

/* Accessibility fallback: drop the blur, keep it readable. */
@media (prefers-reduced-transparency: reduce) {
  .glass-approx {
    background: rgb(255 255 255 / 0.96);
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
  }
}
```

`prefers-reduced-transparency` support is uneven — test it, and never rely on the blur alone for legibility.
