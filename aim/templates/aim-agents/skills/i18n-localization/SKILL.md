---
name: i18n-localization
description: Practices for making an app translatable and adapting it per locale, including extracting hardcoded strings into keys, organizing translation catalogs, keeping languages in sync, locale-aware date and number formatting, and right-to-left layouts. Use it when adding multi-language support, auditing for untranslated text, structuring locale files, or wiring up RTL.
---

# Internationalization and Localization

Two related jobs sit behind multi-language support:

- **Internationalization (i18n)** -- building the app so it *can* be translated: no baked-in text, locale-aware formatting, layouts that flex.
- **Localization (l10n)** -- the per-language work: the actual translations and regional conventions.

A **locale** pairs a language with a region (`en-US`, `tr-TR`, `ar-EG`). **RTL** refers to scripts that flow right to left, such as Arabic and Hebrew.

---

## Is it worth doing here?

Reach for i18n early when the audience is plausibly multilingual; treat it as optional for throwaway or single-market work.

- **Worth it up front** -- public sites, commercial SaaS, anything aimed at more than one country.
- **Judgement call** -- internal tooling, apps that are single-region today but may expand.
- **Skip for now** -- prototypes and personal one-offs.

Retrofitting i18n is painful, so when in doubt, structure for it from the start.

---

## Wiring it into common stacks

### React with react-i18next

```tsx
import { useTranslation } from 'react-i18next';

export function Greeting() {
  const { t } = useTranslation();
  return <h1>{t('greeting.heading')}</h1>;
}
```

### Next.js with next-intl

```tsx
import { useTranslations } from 'next-intl';

export default function LandingPage() {
  const t = useTranslations('Landing');
  return <h1>{t('heading')}</h1>;
}
```

### Python with gettext

```python
from gettext import gettext as _

print(_("Welcome aboard"))
```

---

## Laying out catalog files

Split catalogs by language, then by feature so files stay small and merge-friendly:

```
locales/
├── en/
│   ├── common.json
│   ├── auth.json
│   └── errors.json
├── tr/
│   ├── common.json
│   ├── auth.json
│   └── errors.json
└── ar/            # right-to-left
    └── ...
```

---

## What to do, and what to avoid

**Do**

- Reference every string through a key, never the literal text.
- Scope keys by feature or screen.
- Express plurals through the i18n layer rather than ad-hoc `if` checks.
- Format dates and numbers per locale via the `Intl` APIs.
- Account for RTL from day one.
- Use ICU message syntax for anything with variables or plurals.

**Avoid**

- Literal strings sitting inside components.
- Stitching translated fragments together (word order varies by language).
- Assuming string length is stable -- German often runs ~30% longer.
- Treating RTL as an afterthought.
- Putting more than one language inside a single catalog file.

---

## Frequent snags and fixes

| Snag | Fix |
|------|-----|
| Key absent in a language | Fall back to the default locale |
| Literal text in code | Run the checker script to surface it |
| Wrong date format | `Intl.DateTimeFormat` |
| Wrong number/currency format | `Intl.NumberFormat` |
| Broken plurals | ICU plural rules |

---

## Supporting RTL

Lean on logical CSS properties so a single rule serves both directions, and flip directional icons explicitly:

```css
/* Resolves correctly in both LTR and RTL */
.panel {
  margin-inline-start: 1rem;  /* instead of margin-left */
  padding-inline-end: 1rem;   /* instead of padding-right */
}

[dir="rtl"] .chevron {
  transform: scaleX(-1);
}
```

---

## Pre-ship checklist

- [ ] Every user-visible string goes through a translation key
- [ ] Catalogs exist for each supported language
- [ ] Dates and numbers formatted with `Intl`
- [ ] RTL layout exercised (when an RTL locale is in scope)
- [ ] A fallback locale is configured
- [ ] No literal strings left in components

---

## Script

| Script | What it does | How to run |
|--------|--------------|------------|
| `scripts/i18n_checker.py` | Flags hardcoded strings and out-of-sync catalogs | `python scripts/i18n_checker.py <project_path>` |
