# tells.md — Signatures of machine-generated design

These are the patterns the model falls back on when it tries to "look designed." Treat each as banned by default; permit it only when the brief explicitly calls for it. Grouped by where they surface.

## Surface and CSS reflexes
- **No outer glows or neon halos** as a default. Use a thin inner border or a softly tinted shadow instead.
- **No pure black** (`#000000`). Use off-black — a deep zinc or warm charcoal.
- **No over-saturated accents.** Pull saturation down so the accent sits with the neutrals rather than vibrating against them.
- **No gradient-filled large headlines** as decoration.
- **No custom JS mouse cursors.** Dated, hostile to accessibility, and bad for performance.

## Type tells
- **The neutral workhorse sans as the automatic default** is a tell — choose something with more intent first (override path in the main file).
- **Oversized headlines that only shout.** Build hierarchy with weight and color, not raw point size.
- **Serif reached for because a brief "feels creative."** Serif belongs to genuinely editorial/luxury/publication work, not dashboards or generic modern brands.

## Layout and spacing tells
- **Three identical feature cards in a row.** The canonical machine layout. Replace with a two-column zigzag, an asymmetric grid, a scroll-pinned section, or a horizontal-scroll strip.
- **Floating elements with awkward, unaligned gaps.** Spacing should be intentional and rhythmic; nothing parked at a random offset.
- **The split-header** — a giant left headline with a small explainer paragraph floating in the top-right corner, aligned to nothing. Stack the explainer under the headline, or build a real aligned two-column header.

## Fabricated content ("placeholder-person" effect)
- **Generic names** ("John Doe", "Jane Smith", "Sarah Chen"). Use believable, locale-appropriate names.
- **Generic avatars** (the egg silhouette, a user-icon glyph). Use real photo placeholders or specific styling.
- **Suspiciously round numbers** ("99.99%", "50%", "1,000,000"). Use organic, slightly messy values when the data is illustrative — and mark illustrative data as such.
- **Startup-slop brand names** ("Acme", "Nexus", "Cloudly", "SmartFlow"). Invent names that sound like they could be real and fit the context.
- **Filler verbs** ("Elevate", "Unleash", "Seamless", "Next-Gen", "Revolutionize"). Use concrete language.

## Asset and component tells
- **Hand-drawn SVG icons.** Use a real icon family (Phosphor / Hugeicons / Radix / Tabler); never draw paths yourself.
- **Hand-drawn decorative SVG illustrations** as a default — fine only for a single simple geometric mark the brief asks for.
- **`<div>`-built fake product UI** — fake task lists, terminals, dashboards assembled from styled rectangles. The biggest single tell. Use a real screenshot, a generated image, a real mini-component, or skip the preview.
- **Broken or hotlinked image URLs.** Use a seeded placeholder service with descriptive seeds, generated images, or real assets.
- **Default-state component-library output.** If you adopt a component kit, restyle radii, color, shadow, and type to the project; never ship the out-of-the-box look.

## Patterns that surfaced repeatedly in real generated pages

**Top of page**
- **Version/status labels in the hero** ("v0.6", "BETA", "EARLY ACCESS", "INVITE-ONLY") as default eyebrows. Only for an actual launch/preview brief.
- **"Brand · No. 01"-style micro-meta** sub-eyebrows. Drop them.

**Numbering and micro-labels**
- **Section-number eyebrows** ("00 / INDEX", "001 · Capabilities", "06 · how it works"). Name the topic plainly or omit; don't enumerate.
- **"01 / 4"-style pagination** stamped on images or tiles. If the reader can count, the label is noise.
- **Scroll cues with section numbers** ("Scroll · 001 Capabilities"). A plain arrow or nothing.
- **Date-range eyebrows** ("Index of Work, 2018–2026"). Just name the section.

**Separators and dots**
- **The middle dot (`·`) as the universal separator** ("foo · bar · baz · qux"). At most one per metadata line; otherwise prefer line breaks, hairlines, or columns.
- **Colored status dots on every nav item / list row / badge.** Allowed only when a dot conveys real semantic state (live availability, server status), used sparingly.

**Typography flourishes**
- **`<br>`-split, italicized headlines** as a default "design move" ("for thirty\<br>*years.*"). Let headlines read naturally first.
- **Vertically rotated text** (a label spun 90°). An agency-portfolio cliché; only for an explicitly experimental brief that needs it compositionally.
- **Crosshair / hairline grid lines as pure decoration.** Use lines only when they organize real content.

**Fake previews**
- **`<div>` fake product UI in the hero** (covered above — the number-one tell).
- **Fake version footers inside fake screenshots** ("v0.6.2-rc.1", "last sync 4s ago"). Adds nothing.

**Marketing-copy tells**
- **"Quietly in use at" / "Quietly trusted by"** social-proof headers. Say "Trusted by" / "Used at", or let the logos stand alone.
- **Performative-craftsman section labels** ("From the field", "Field notes", "On our desks", "Currently on the bench"). Use plain labels ("Testimonials", "Latest writing", "Now working on") or none.
- **Mock-humble industry asides** ("we respect the French ones"-style winks) in body copy.
- **Atmospheric weather/locale/time strips** ("LIS 14:23 · 18°C") in headers or footers — unless the brand is genuinely place- or timezone-defined.
- **Micro-meta sentences under eyebrows** ("Each of these ships today, not a roadmap promise…"). Eyebrow + headline + body is enough.
- **Generic step labels** ("Stage 1 / Stage 2 / Stage 3", "Phase 01 / 02 / 03"). Let the step's actual verb-noun be the label ("Install", "Configure", "Ship").

**Pills, labels, version stamps**
- **Pills/tags overlaid on images** ("Brand · 02", "PLATE · BRAND"). Let the image speak, or caption it directly below the image.
- **Decorative photo-credit captions** ("Field study no. 12 · Ana Reis", "Frame XII · 35mm") under stock/placeholder images. Real credit for a real photographer is fine; pretend credit is not.
- **Version footers on marketing pages** ("v1.4.2", "Build 0048", "last sync 4s ago"). Devtool fixtures, not landing-page content.
- **Live-stock counters as decoration** ("Reservation 412 of 800"). Only for a real limited-run waitlist with real numbers.

**Decoration strips**
- **A mono-caps strip across the hero bottom** ("BRAND. MOTION. SPATIAL.", "DESIGN · BUILD · SHIP"). An agency cliché; allowed only when it carries real navigable links or real status info.
- **A small floating paragraph in the top-right of a section header.** Stack it under the headline or build an aligned two-column header instead.

**Lists, dividers, scoring**
- **A border on both top and bottom of every row** in a long list or spec table. Pick one, use it sparingly; better, switch to a grouped or card layout (see the main file).
- **Filled-track progress/score bars** as comparison visuals on a landing page. Prefer a number plus a small icon, or a thin bar with no background track.

## The em-dash ban (the most-violated tell)

The em-dash (`—`) is the model's signature crutch and the clearest visual tell. It is **completely banned** — there is no "sparingly", no "fine in body copy", no exceptions:
- **Headlines, eyebrows, labels, pills, buttons, captions, nav items:** never. Use a period, a comma, line breaks, or columns.
- **Body copy:** restructure — two sentences with a period, or a comma, parentheses, or a colon.
- **Quote attribution:** a spaced hyphen (` - `) or a line break with a lighter-weight name.
- **The en-dash (`–`) as a separator is banned too.** Ranges use a plain hyphen ("2018-2026", "€40-80k").

The only dash characters permitted in visible text are the regular hyphen `-` (compound words, ranges, dividers) and the minus sign in math (`-5°C`). A single `—` or `–` visible to the reader fails pre-flight and must be rewritten. This is binary because softer phrasings have historically been ignored.
