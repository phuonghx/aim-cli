# Context Templates & Decision Trees

> A thinking aid for web UI design — pick direction from context, then decide the specifics yourself.
> **Treat everything here as a guide to reason with, never a snippet to paste.**
> **Psychology laws (Hick's, Fitts', Miller's, and friends) live in:** [ux-psychology.md](ux-psychology.md)

---

## How to Read This File

The goal is to help you *choose well*, not to hand you finished answers.

- The trees walk you through trade-offs so you weigh options on purpose.
- The templates sketch *shape and intent* — the numbers and colors are yours to set.
- Confirm preferences with the user before you commit to a direction.
- Mix every palette from scratch in HSL for the context at hand; resist pasting hex codes.
- Run your choices past the laws in [ux-psychology.md](ux-psychology.md) before you ship them.

Three habits run through the whole file: **ask when something is ambiguous**, **build fresh palettes instead of reusing fixed values**, and **validate against UX laws**. The diagrams below are scaffolding for your thinking — not locked specifications.

---

## 1. Start Here — Project-Type Tree

Name the kind of product first; that single fork sets the tone for everything after it.

```
  «  WHAT KIND OF THING IS THIS?  »
  ===================================
            |
   .--------+----------.-----------------.
   |                   |                 |
 [ STORE ]        [ PRODUCT ]        [ READING ]
 shop / cart      app / console      blog / site
 catalog          tools / admin      folio / launch
   |                   |                 |
 lead with:        lead with:        lead with:
 • confidence      • usefulness      • narrative
 • next step       • legibility      • feeling
 • momentum        • throughput      • invention
```

`STORE` wants the visitor to *believe and buy*. `PRODUCT` wants them to *work without friction*. `READING` wants them to *feel something and stay*. Everything downstream — color, type, density — bends toward whichever of those three you landed on.

---

## 2. Audience Tree

Once you know *who* shows up, the styling levers shift. Pick the closest match and treat the notes as nudges, not law.

```
  WHO IS THIS FOR?
  ----------------
   |
   +-- Gen Z · roughly 18-25
   |     color ....... loud, saturated, surprising pairings
   |     type ........ oversized, variable, full of attitude
   |     layout ...... thumb-first, stacked, bite-sized
   |     motion ...... lively, playful, interactive
   |     stance ...... real and quick; zero boardroom energy
   |
   +-- Millennials · roughly 26-41
   |     color ....... toned-down, earthen, grown-up
   |     type ........ tidy, legible, doing its job
   |     layout ...... fluid grids, cards, well-sorted
   |     motion ...... gentle, only where it earns its place
   |     stance ...... honest, value-led, built to last
   |
   +-- Gen X · roughly 42-57
   |     color ....... steady, credible, on the safe side
   |     type ........ familiar shapes, plain, no games
   |     layout ...... classic order, nothing surprising
   |     motion ...... sparse, just useful feedback
   |     stance ...... straight-talking, efficient, dependable
   |
   +-- Boomers · 58 and up
   |     color ....... strong contrast, plain, unmistakable
   |     type ........ big sizes, easy on the eyes
   |     layout ...... one path, roomy, no clutter
   |     motion ...... little to none
   |     stance ...... clear, complete, reassuring
   |
   +-- B2B / Enterprise
         color ....... restrained, businesslike
         type ........ clean, table-ready, easy to skim
         layout ...... gridded, sorted, no wasted moves
         motion ...... measured and quiet
         stance ...... expert, outcome-led, tied to ROI
```

---

## 3. Color Tree

Skip the urge to grab a hex value. Start from the *feeling* you're after and narrow down.

```
  WHAT SHOULD PEOPLE FEEL — OR DO?
  ================================
   |
   |-> Safe & dependable
   |     lean toward blues + sober neutrals
   |     >> ask which exact shade reads "us"
   |
   |-> Alive & well
   |     lean toward greens + organic tones
   |     >> ask if it's eco / nature / wellness
   |
   |-> Now & decisive
   |     lean toward warm hues (orange/red) — as accents
   |     >> keep it rare; ask if pressure even fits
   |
   |-> Costly & rare
   |     lean toward deep darks, metallics, a tight set
   |     >> ask where the brand sits in the market
   |
   |-> Fun & inventive
   |     lean toward many hues, odd-couple pairings
   |     >> ask how bold the personality really is
   |
   `-> Quiet & spare
         lean toward neutrals + one lone accent
         >> ask which accent feels on-brand
```

**Work it like this:**

1. Pin down the feeling the page has to carry.
2. Collapse that into one hue family.
3. Check the precise shade with the user.
4. Build the full ramp yourself in HSL — shift hue, saturation, lightness on purpose.

---

## 4. Typography Tree

Let the *kind of content* steer the letterforms.

```
  WHAT IS THE TEXT DOING?
  -----------------------
   |
   |== Dense data (consoles, SaaS)
   |     voice .... sans, crisp, space-thrifty
   |     ramp ..... tight steps (~1.125–1.2)
   |     win ...... skim speed, packing density
   |
   |== Long-form reading (blog, mag)
   |     voice .... serif headlines over a sans body sing
   |     ramp ..... bold jumps (1.333 and up)
   |     win ...... easy reading, clear ranking
   |
   |== New-tech feel (startup, SaaS site)
   |     voice .... geometric or humanist sans
   |     ramp ..... even-handed (~1.25)
   |     win ...... current mood, plain clarity
   |
   |== High-end (fashion, premium)
   |     voice .... refined serif or hairline sans
   |     ramp ..... wide jumps (1.5–1.618)
   |     win ...... polish, breathing room
   |
   `== Lighthearted (kids, games, casual)
         voice .... soft, rounded, friendly faces
         ramp ..... mixed, expressive
         win ...... joy, warmth, still readable
```

**Work it like this:**

1. Name the content kind.
2. Settle on a style *direction*.
3. Ask whether brand fonts already exist.
4. Pick faces that carry that direction.

---

## 5. Store / E-commerce Notes {#e-commerce}

### What matters (guidelines, not gospel)

- **Earn belief early** — what signals that this shop is safe?
- **Point at the action** — where do the buy buttons live?
- **Make it skimmable** — can shoppers size up options fast?

### Thinking about color

```
A storefront usually juggles:
  + a "trust" hue (blues are common) ........ ask first
  + a calm canvas (white / neutral) ......... brand-dependent
  + an action pop (buttons, sales) .......... how urgent is it?
  + status colors (ok / warn / error) ....... conventions are fine
  + the brand's own colors ................... ask what already exists
```

### Thinking about layout

```
  +======================================+
  |  TOP BAR                             |  logo · search · cart
  |  keep the must-do actions in sight   |
  +--------------------------------------+
  |  ASSURANCE STRIP                     |  shipping · returns · secure
  |  give a reason to relax (if real)    |
  +--------------------------------------+
  |  SPOTLIGHT                           |  one offer, one button
  |  a single, unmistakable focus        |
  +--------------------------------------+
  |  AISLES                              |  visual, filterable
  |  let people steer themselves         |
  +--------------------------------------+
  |  THE GOODS                           |  price · stars · quick-add
  |  built for side-by-side compare      |
  +--------------------------------------+
  |  VOICES                              |  reviews · quotes
  |  show why others bought (if you can) |
  +--------------------------------------+
  |  BASEMENT                            |  policies · contact · badges
  |  the fine print and the rest         |
  +======================================+
```

### Laws to lean on

- *Hick's Law* — trim the menu so choices don't paralyze.
- *Fitts' Law* — scale buy buttons to their weight.
- *Social proof* — surface it where it tips a decision.
- *Scarcity* — only if it's true; never manufacture it.

---

## 6. Product / SaaS Dashboard Notes {#saas}

### What matters

- **Data before decor** — readings win over ornament.
- **A calm surface** — keep the mental tax low.
- **Repeatable patterns** — let people predict the next screen.

### Thinking about color

```
A dashboard usually juggles:
  + a base ............. light OR dark (ask which)
  + a surface .......... a half-step off the base
  + one accent ......... reserved for key actions
  + signal colors ...... ok / warn / danger
  + a muted tone ....... for the second-tier stuff
```

### Thinking about layout

```
Three shells worth weighing (none are required):

  SHELL 1 — rail + canvas
    [ nav ]| . . . . . . . |
    [ rail ]| content here |
    fixed side nav, roomy work area

  SHELL 2 — bar + canvas
    [== top nav ==========]
    | wide content below   |
    horizontal nav, extra width to play with

  SHELL 3 — tuck + expand
    [▮]| content . . . . . |
    icon rail that opens on demand, max canvas

  >> ask which navigation shape they prefer
```

### Laws to lean on

- *Hick's Law* — bundle nav items into groups.
- *Miller's Law* — break data into digestible chunks.
- *Cognitive load* — buy calm with whitespace and consistency.

---

## 7. Launch / Landing Page Notes {#landing-page}

### What matters

- **The hero carries it** — the opening view does the heavy lifting.
- **One job** — a single primary call to action.
- **Feeling first** — connect before you pitch.

### Thinking about color

```
A landing page usually juggles:
  + a brand lead ........ hero backdrop or accent
  + a clean second ...... most of the scroll
  + a CTA hue ........... louder than everything else
  + support tones ....... sections, quotes
  + brand colors ........ ask about these up front!
```

### Thinking about structure

```
  o-- NAV ............... lean, with the CTA in view
  |
  o== HERO ============== hook + value + button
  |     the loudest beat of the whole page
  |
  o-- PAIN .............. name the problem they feel
  |
  o-- FIX ............... show how you settle it
  |
  o== EVIDENCE ========== quotes · logos · numbers
  |     give them grounds to believe
  |
  o-- STEPS ............. the how, kept simple
  |
  o-- PRICE ............. if there's a price to name
  |
  o-- DOUBTS ............ answer the obvious objections
  |
  o== CLOSE ============= say the main action again
```

### Laws to lean on

- *Visceral response* — a striking hero buys goodwill.
- *Serial position* — load the key beats at top and bottom.
- *Social proof* — testimonials still pull weight.

---

## 8. Portfolio Notes {#portfolio}

### What matters

- **Show the person** — character beats template.
- **Center the work** — let the projects carry the room.
- **Be hard to forget** — escape the default look.

### Thinking about color

```
A portfolio is personal — plenty of routes:
  + spare ..... neutrals + one signature accent
  + brave ..... color choices nobody expects
  + dark ...... moody, gallery-at-night feel
  + bright .... clean, daylight, professional
  + ask about the personal brand first!
```

### Thinking about structure

```
  [ NAV ] ........ shaped to fit your personality
     |
  [ HELLO ] ...... who you are, what you make
     |             land it; skip the boilerplate
  [ WORK ] ....... the featured pieces
     |             big, visual, worth a click
  [ STORY ] ...... the human behind it
     |             this is what forges a bond
  [ REACH ] ...... an easy way to get in touch
                   plain and direct
```

### Laws to lean on

- *Von Restorff* — the odd-one-out is the one remembered.
- *Reflective layer* — a personal arc builds connection.
- *Emotional pull* — character outranks polish here.

---

## 9. Checklists by Phase

### Before you open a canvas

- [ ] Audience nailed down? (who, precisely)
- [ ] One main goal? (the action that matters)
- [ ] Limits mapped? (time, brand, stack)
- [ ] Real content on hand? (or placeholders flagged)
- [ ] Preferences asked? (color, style, layout)

### Before you lock color

- [ ] Checked with the user?
- [ ] Weighed the context? (industry, mood)
- [ ] Stepped off your usual default?
- [ ] Run a contrast / accessibility pass?

### Before you settle layout

- [ ] Hierarchy obvious at a glance?
- [ ] Primary CTA impossible to miss?
- [ ] Small screens accounted for?
- [ ] Real content fits the frame?

### Before you hand it over

- [ ] Reads premium, not off-the-shelf?
- [ ] Something you'd put your name on?
- [ ] Distinct from your last build?

---

## 10. Sizing the Effort

### Hours — small and contained

```
  · one landing page
  · a slim portfolio
  · a single form
  · one component
```

Approach: few decisions, sharp execution.

### Days — mid-size

```
  · a multi-page site
  · a dashboard with several modules
  · a store category section
  · involved forms
```

Approach: set up tokens, build custom pieces.

### Weeks — large

```
  · a full SaaS product
  · an entire store platform
  · a from-scratch design system
  · multi-step workflows
```

Approach: a real system, written docs, testing.

---

> **Bottom line:** these maps show the *shape and the reasoning*, not the answers — every project earns its own color, type, and layout calls from its own context, so ask the moment something's unclear.
