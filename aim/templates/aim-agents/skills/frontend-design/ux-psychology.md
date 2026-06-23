# UX Psychology Reference

> A working playbook for the mental models behind interface decisions: how people perceive, decide, feel, and trust — and how to design for each.

---

## How to use this file

The sections move from the human side outward to the screen:

1. **Emotion & Cognition** — what the brain does before it reads a single label.
2. **Laws of decision, attention & flow** — the named principles, with their formulas and numbers intact.
3. **Gestalt** — how the eye assembles raw shapes into meaning.
4. **Behavioral levers** — biases that shape what people actually do.
5. **Trust, persuasion & ethics** — earning belief without manipulation.
6. **Audience & palette references** — who you're designing for and what color says.
7. **Pre-ship checklist** — a final pass tied back to every principle.

---

## 1. Emotional Design — Three Levels (Don Norman)

Norman argues that feeling is not decoration layered on top of a product; it is processed in three distinct passes, each running on its own timescale.

```
  level         timing            what the brain asks
  ----------    --------------    -----------------------------
  VISCERAL  →   ~50 ms, reflex    "Does this look right?"
                                  raw aesthetics: color, form, motion

  BEHAVIORAL →  during use        "Does this do what I meant?"
                                  function, speed, predictability

  REFLECTIVE →  after the fact    "What does using this say about me?"
                                  meaning, memory, identity, loyalty
```

A product can win on one level and lose on another. A gorgeous app that fails on the behavioral level frustrates; a flawless-but-soulless tool rarely earns devotion.

### Designing the visceral layer

First impressions are pre-rational. Lead with confident color and motion that *feels* responsive.

```css
.landing-banner {
  background: radial-gradient(circle at top left, #6d28d9, #0f766e);
  color: #f8fafc;
  min-height: 70vh;
}

/* a control that springs to the touch reads as "alive" */
.cta-pill {
  transition: transform 140ms ease, box-shadow 140ms ease;
}
.cta-pill:hover {
  transform: scale(1.04);
  box-shadow: 0 14px 28px -8px rgba(15, 23, 42, 0.45);
}
```

### Designing the behavioral layer

Pleasure here comes from competence: the interface keeps pace and confirms every action.

```javascript
async function handleSubscribe(btn) {
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Adding you…';      // acknowledge the click at once

  try {
    await subscribe();
    btn.textContent = '✓ You are in';    // close the loop with a clear win
  } catch {
    btn.disabled = false;
    btn.textContent = original;          // restore so the user can retry
    flashInlineError('That did not go through — try again?');
  }
}
```

### Designing the reflective layer

This layer is about story and self-image — why the product exists and who the user becomes by choosing it.

```html
<section class="mission">
  <h2>What we stand for</h2>
  <p>Software should give people back their time, not invent new chores.</p>
</section>

<figure class="voice-of-customer">
  <blockquote>"It finally made me feel like a real maker, not a hobbyist."</blockquote>
  <figcaption>— Priya, ceramic studio owner</figcaption>
</figure>
```

---

## 2. Cognitive Load — Budget the Brain's Attention

Working memory is a tiny, expensive resource. Every design choice either spends it or saves it. There are three kinds of load, and only one of them is yours to slash.

| Load type | Where it comes from | Your job |
|-----------|---------------------|----------|
| **Intrinsic** | The unavoidable difficulty of the task itself | Slice it into smaller, sequential steps |
| **Extraneous** | Friction added by the interface | Hunt it down and delete it |
| **Germane** | Mental effort that builds the user's skill | Protect and reward it |

### Five ways to lighten the load

**a) Strip the noise (kills extraneous load).** Decoration that doesn't carry meaning is just static.

```css
/* before: shouting for attention */
.tile--loud {
  border: 3px dashed crimson;
  background: linear-gradient(45deg, #ff0, #f0f, #0ff);
  box-shadow: 0 0 24px gold;
}

/* after: calm enough to actually read */
.tile--quiet {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 8px 24px -12px rgba(2, 6, 23, 0.12);
}
```

**b) Chunk long flows.** Twelve fields on one screen feels like a wall; the same twelve in groups of three or four feel like a path.

```html
<form>
  <fieldset>
    <legend>About you</legend>
    <!-- name, email, phone -->
  </fieldset>
  <fieldset>
    <legend>Where it ships</legend>
    <!-- address, city, postcode -->
  </fieldset>
</form>
```

**c) Reveal complexity only on demand (progressive disclosure).**

```html
<section class="search-controls">
  <div class="controls-core"><!-- the filters most people need --></div>

  <button type="button" aria-expanded="false" data-toggle="more">
    More filters
  </button>
  <div class="controls-extra" hidden><!-- power-user options live here --></div>
</section>
```

**d) Reuse what people already know.** Familiar layouts cost zero learning.

```text
+ search lives top-center or top-right, behind a magnifier glyph
+ the cart sits top-right
+ green confirms, red warns
+ swipe and pinch behave the way the OS taught them
```

**e) Let the system remember, not the user.** Surface earlier input instead of asking for it twice.

```html
<label>
  Card number
  <input inputmode="numeric" autocomplete="cc-number"
         placeholder="4242 4242 4242 4242">
</label>

<aside class="recap">
  Sending to <strong>Mara Lin · 88 Birch Ave · Portland</strong>
  <a href="#edit">Change</a>
</aside>
```

---

## 3. Laws of Decision, Attention & Flow

These are the named "laws" of UX. They're grouped here by the problem they solve rather than alphabetically. **Formulas and numbers are exact — do not round them away.**

### 3.1 — Cutting decision cost

#### Hick's Law

**Idea:** the more options you offer, the longer a choice takes — and the relationship is logarithmic, not linear.

```
Decision Time = a + b · log₂(n + 1)
   n = how many options are presented
   a = fixed reaction overhead, b = per-option processing cost
```

**Put it to work:**
- Cap primary navigation at **5–7** entries.
- Stage long forms with progressive disclosure instead of dumping everything at once.
- Pre-select a sensible default so "do nothing" is a valid answer.
- Surface the common filters; tuck the rare ones behind "Advanced."

```text
weak:  one menu bar carrying 15 links
solid: 5 clear categories, with the long tail under "More"

weak:  a 20-field form on a single screen
solid: a 3-step wizard, 5–7 fields per step
```

#### Occam's Razor

**Idea:** when two designs perform equally, the one carrying fewer assumptions wins. Prefer the simplest thing that works.

**Put it to work:**
- Delete clicks that don't earn their place.
- Hold the line on font and color counts.
- Merge two inputs into one whenever a single field can do the job.
- Write the shortest copy that still lands.
- Cut ornament that serves no goal, and avoid branching paths you don't need.

```text
weak:  "Log in" opens a page → then an email step → then a password step
solid: one modal asks for email and password together

weak:  a single card juggling 5 type sizes and 4 colors
solid: 2 type sizes, 1 accent color
```

### 3.2 — Respecting limited memory & attention

#### Miller's Law

**Idea:** working memory holds roughly **7 ± 2** chunks at once, so package information into chunks.

**Put it to work:**
- Group list items in clusters of about 5–7.
- Keep nav around seven items.
- Break long prose with headings so each segment is its own chunk.
- Format strings the way memory likes them — e.g. a phone number as `555-123-4567`.

```text
hard to hold:   5551234567
easy to hold:   555-123-4567

hard to hold:   one dense, unbroken paragraph
easy to hold:   short paragraphs
                · with bullets
                · under clear subheads
```

#### Von Restorff Effect (a.k.a. the Isolation Effect)

**Idea:** the element that breaks the pattern is the one people remember.

**Put it to work:**
- Give the primary CTA a color nothing else uses.
- Visually crown the recommended pricing tier.
- Flag genuinely new features with a badge.

```css
/* keep the field muted so one button can dominate */
.action { background: #e2e8f0; color: #1e293b; }
.action--key { background: #4338ca; color: #ffffff; }

/* the plan you want chosen wears the spotlight */
.plan { border: 1px solid #e2e8f0; }
.plan--recommended {
  border: 2px solid #4338ca;
  box-shadow: 0 18px 40px -16px rgba(67, 56, 202, 0.55);
}
```

#### Serial Position Effect

**Idea:** the start of a sequence (primacy) and its end (recency) stick; the middle blurs.

**Put it to work:**
- Anchor the most important nav items at the first and last positions.
- Lead and close lists with the things that matter.
- Front-load the critical fields in a form.
- On a long page, repeat the CTA at top and bottom.

```text
nav order:   Home | (the rest) | Contact

long page:   CTA in the hero
             ...content...
             CTA again at the foot of the page
```

#### Jakob's Law

**Idea:** people spend the bulk of their time on *other* sites, so they expect yours to behave like the rest of the web.

**Put it to work:**
- Place search and cart where people already look for them.
- Lean on icons whose meaning is settled (a magnifier means search).
- Say "Log in," not "Enter the Portal."
- Make the logo a route home from the top-left.
- Honor native gestures — a right-swipe should feel like going back.
- Keep status colors conventional: red for error, green for success.

```text
weak:  clicking the logo lands you on an "About Us" page
solid: the logo always returns you home

weak:  a star icon stands in for "Delete"
solid: a trash-can icon means "Delete"
```

#### Law of the Focal Point

**Idea:** whatever stands out the most grabs the eye first — so decide deliberately what that is.

**Put it to work:**
- Seat your core value proposition at the visual focal point.
- Reserve one high-energy "action" hue for a neutral interface.
- Add a whisper of motion to the CTA to pull the gaze.
- Make the single most important number the largest type on the page.
- Use weight for hierarchy: bold headers, regular body.
- Point with arrows — or with a photographed face whose gaze leads to the button.

```text
weak:  a home page with five same-size, same-color buttons
solid: one big "Get started" in a vivid color

weak:  "Total revenue" set in the same size as "Build number"
solid: "Total revenue" in huge bold figures, dead center up top
```

### 3.3 — Moving complexity off the user

#### Tesler's Law (Conservation of Complexity)

**Idea:** every system holds an irreducible amount of complexity. You can't erase it — you can only decide whether the user or the software absorbs it.

**Put it to work:**
- Let the backend handle formatting (currency, dates).
- Auto-detect the card brand, or the city from a postcode.
- Pre-fill what a returning user already gave you.
- Show only the fields that prior answers make relevant.
- Ship smart defaults for routine settings.
- Offer SSO so account creation costs almost nothing.

```text
weak:  the user types "USD $" ahead of every price they enter
solid: the app prepends "$" based on their region

weak:  the user manually picks "Visa" vs. "Mastercard"
solid: the brand is inferred from the first digits typed
```

#### Postel's Law (Robustness Principle)

**Idea:** be strict in what you emit, generous in what you accept.

**Put it to work:**
- Don't reject input over a stray space or dash.
- Parse dates whether they arrive as `DD/MM/YYYY` or `MM/DD/YYYY`.
- Trim leading and trailing whitespace silently.
- Fall back to a default avatar when none was uploaded.
- Tolerate typos and offer "Did you mean…?"
- Work across the browsers and devices people actually use.

```text
weak:  a phone number is refused because it contains a space
solid: the space is accepted and quietly stripped

weak:  the user must type "January," never "01" or "Jan"
solid: the date field understands all three
```

### 3.4 — Time, speed & perceived performance

#### Parkinson's Law

**Idea:** a task swells to fill whatever time you give it — so give it less.

**Put it to work:**
- Autosave so completion doesn't drag.
- Trim the number of steps in any conversion funnel.
- Label things clearly so nobody hovers around hunting for meaning.
- Validate in real time so errors don't waste a round trip.
- Offer an "Express" path for people who already know the ropes.
- Cap input length to keep answers focused.

```text
weak:  a 10-page signup where wandering off loses everything
solid: one-tap sign-in with Google or Apple

weak:  an open-ended "write your bio" box with no end in sight
solid: "Suggested bios" that finish the job in seconds
```

#### Doherty Threshold

**Idea:** when the system answers in under **400 ms**, neither human nor machine is left waiting, and productivity jumps.

**Put it to work:**
- Acknowledge clicks with an instant visual change.
- Cover fetches with skeleton screens for perceived speed.
- Update the UI optimistically, before the server confirms.
- Mask tiny delays with micro-animation.
- Pre-fetch the likely next page or asset.
- Paint text first; let heavy hero images arrive after.

```text
weak:  a button that sits dead for 2 seconds after a click
solid: a button that recolors and spins instantly

weak:  a blank white page while data loads
solid: a skeleton sketching where content will land
```

---

## 4. Gestalt — How the Eye Groups Things

Gestalt principles describe the automatic ways perception turns scattered marks into structure. Each comes with a contrast pair.

#### Proximity

Things placed close together read as one group.

- Sit a label right against its input.
- Open up wide margins between unrelated blocks.
- Inside a card, keep text nearer the image than the card's edge.
- Cluster legal links apart from social links in the footer.
- Separate "account" settings from "app" settings.
- Keep address fields together, payment fields together.

```text
weak:  identical large gaps between every line of a form
solid: tight label-to-input spacing, wider gaps between pairs

weak:  a "Submit" button stranded mid-page, far from its form
solid: "Submit" sitting directly beneath the last field
```

#### Similarity

Elements that look alike are read as belonging to the same family.

- One link color, used everywhere links appear.
- One stroke weight across an icon set.
- Matching shape and size for buttons of equal rank.
- A single H2 treatment for every section header.
- One consistent color for every "Delete."
- Hover and active states that behave the same app-wide.

```text
weak:  links appear blue here, green there, bold-black elsewhere
solid: every clickable text element shares one shade of blue

weak:  "Submit" and "Cancel" are the same solid blue button
solid: "Submit" is solid; "Cancel" is an outline (ghost) button
```

#### Common Region

A shared, bounded area binds whatever sits inside it.

- Wrap an image and its title in a card.
- Rule a line between sidebar and main feed.
- Give the footer its own background color.
- Float modals in a distinct box.
- Zebra-stripe table rows.
- Bar the top of the page to bind the nav together.

```text
weak:  article images and text from different stories overlapping
solid: each story sealed in its own card on a tinted background

weak:  a footer sharing the body's exact background
solid: a dark footer that clearly fences off legal links
```

#### Uniform Connectedness

Things tied by a visible connector feel more related than mere neighbors.

- Run a line through the steps of a setup wizard.
- Let a dropdown physically touch the control that opened it.
- Connect chart data points with a line.
- Visually link a toggle to the text it governs.
- Use tree indentation for file hierarchies.
- Tie a "Credit card" radio to the fieldset it reveals.

```text
weak:  steps "1", "2", "3" scattered with nothing joining them
solid: a connecting line that reads them as a sequence

weak:  a dropdown floating detached from its trigger
solid: a dropdown visually fused to the parent button
```

#### Prägnanz (Simplicity)

The mind defaults to the simplest reading of anything ambiguous, because simple costs less effort.

- Use clean, geometric icons for navigation.
- Drop gratuitous 3D and texture.
- Favor plain rectangles and circles over fussy polygons.
- Give primary actions high-contrast silhouettes.
- Make brand marks legible at tiny sizes.
- Keep one clear goal per page so the "mental shape" stays simple.

```text
weak:  a photoreal 3D folder for the "Files" icon
solid: a flat 2D folder outline

weak:  a busy multicolor logo spun as a loader
solid: a single-color ring
```

#### Figure / Ground

Perception splits any scene into a foreground object (figure) and the space behind it (ground).

- Drop a scrim behind modals to pop their content.
- Use shadow to lift the figure above the ground.
- Contrast hard: light type on dark, or the reverse.
- Blur the background to push foreground text forward.
- Let sticky headers hover above scrolling content.
- Raise cards slightly on hover to mark them as the figure.

```text
weak:  a popup with no shadow or border, dissolving into the page
solid: a modal with a drop shadow over a dimmed overlay

weak:  white text dropped straight onto a busy photo
solid: white text over a dark semi-transparent scrim
```

---

## 5. Behavioral Levers — What People Actually Do

Knowing how minds skew lets you design with the grain of human behavior. Use these honestly (see §7 for the ethics line).

#### Zeigarnik Effect

Unfinished business lingers in memory more than finished business.

- Show "Profile 60% complete" bars.
- Tease the next lesson in a course path.
- Keep a visible list of features still unexplored.
- Persist an unread-message badge.
- Surface the next step the instant one is done.
- Nudge with "Finish your order" cart reminders.

```text
weak:  silent onboarding that never says what remains
solid: a checklist reading "3 of 5 done"

weak:  a checkmark even after a video was half-watched
solid: a progress ring that stays half-full until it's finished
```

#### Goal Gradient Effect

Effort accelerates the closer a reward looks.

- Grant artificial advancement — two stamps free on the loyalty card.
- Split a 10-field form into two 5-field stretches.
- Celebrate the halfway mark.
- Show exactly how close the next tier or reward is.
- Use breadcrumbs to signal nearness to the finish.
- Let the loading animation speed up near 100%.

```text
weak:  a progress bar starting at 0%, a daunting climb
solid: a bar opening at 20% because they've "already started"

weak:  a checkout where "Final review" ambushes as a surprise step 5
solid: "Shipping › Payment › Almost done!"
```

#### Peak-End Rule

People score an experience by its most intense moment and its ending — not by the average of every second.

- Make "Order confirmed" a moment worth remembering.
- Drop confetti or a signature animation at the point of value.
- End support chats on a genuinely helpful note.
- Even cancellations deserve a clean, graceful exit.
- Close the first session on a clear win.
- Turn the 404 into something playful and useful.

```text
weak:  after a 20-minute tax flow, the app just says "Submitted"
solid: a "Congratulations!" screen summarizing the refund

weak:  a game that ends with plain "Game Over" text
solid: a results screen with high scores and a flourish
```

#### Aesthetic-Usability Effect

People assume good-looking things work better.

- Polished visuals buy goodwill that papers over small bugs.
- Consistent, high-quality imagery signals competence.
- Beautiful interfaces hold attention longer.
- Pretty UIs make wait times more forgivable.
- Clean design makes complex tools feel approachable.
- People bond emotionally with products they find beautiful.

```text
weak:  a bank app with crooked text and clashing 90s color
solid: a sleek, modern bank app with fluid motion

weak:  pixelated, low-res stock photography
solid: crisp, custom brand illustration
```

#### Anchoring

The first number you show colors every judgment that follows.

- Display the original price with a strikethrough.
- Park a costly "Enterprise" tier where eyes land first.
- Tag a "Most popular" option up front.
- Announce "Save 20%" before revealing the final price.
- "Limit 12 per customer" hints the item is valuable.
- Open with a high suggested donation.

```text
weak:  showing only "$49"
solid: showing "$99  $49 (50% off)"

weak:  sorting laptops cheapest-first
solid: leading with a high-end "Pro" so the rest look like deals
```

#### Social Proof

People take cues from what others are doing.

- "Join 50,000+ others."
- Star ratings and verified testimonials.
- A "Trusted by" wall of partner logos.
- Live nudges: "Sarah bought this 5 minutes ago."
- "300 people are viewing this right now."
- Awards and security seals.

```text
weak:  a signup page with nothing but a form
solid: a signup page reading "Join 2 million designers"

weak:  faceless, nameless reviews
solid: reviews with a face, a name, and a "Verified buyer" tag
```

#### Scarcity

What's rare feels more valuable; what's plentiful feels cheap.

- "Only 2 left in stock."
- A live countdown on a sale.
- Invite-only betas or exclusive tiers.
- Limited "Summer edition" runs.
- "Back in stock soon — pre-order now."
- "In high demand — 10 carts hold this."

```text
weak:  a sale that never ends, no timer in sight
solid: a "Deal of the day" with a ticking clock

weak:  availability shown with no stock count
solid: "Only 3 left at this price!"
```

#### Authority

Opinions carry more weight when they come from a credible source.

- "Expert-verified," with a real professional headshot.
- Trust seals (ISO, HIPAA, recognized security marks).
- "As seen in…" press logos.
- Endorsements from leaders the audience respects.
- Confident, precise, accurate copy.
- "Established 1950" to signal longevity.

```text
weak:  a health post bylined "Admin"
solid: "Reviewed by Dr. Jane Okoro, Cardiologist"

weak:  a security app that names no certifications
solid: "ISO 27001 Certified" displayed plainly
```

#### Loss Aversion

The sting of losing something outweighs the pleasure of gaining its equal.

- "Don't lose your discount."
- "Your trial ends soon — keep your data."
- "Once it's gone, it's gone."
- "Don't leave the items in your cart behind."
- "500 points earned — don't let them expire."
- "30-day money-back guarantee" reframes the spend as risk-free.

```text
weak:  "Click here for a $10 coupon"
solid: "You have $10 waiting — use it before midnight"

weak:  "Cancel your subscription"
solid: "Cancel and you'll lose access to 50 saved projects"
```

#### False-Consensus Effect

We assume our own tastes and habits are more typical than they are.

- You are not the user — test with the real audience.
- Pair qualitative interviews with quantitative analytics.
- Run blind design reviews to defuse personal favoritism.
- Trust documented personas over gut feeling.
- Recruit testers across demographics and abilities.
- Read heatmaps for what people *actually* do.

```text
weak:  a designer declaring a feature "intuitive" without a test
solid: an A/B test revealing which version users prefer

weak:  English-only because "everyone speaks English"
solid: localization driven by real location data
```

#### Curse of Knowledge

Once you understand something, it's hard to imagine not understanding it — and you over-assume shared context.

- Drop jargon; write plainly.
- Build tutorials that assume zero prior knowledge.
- Explain dense terms in tooltips.
- Hide advanced settings behind progressive disclosure.
- Pair icons with text labels rather than trusting icons alone.
- Stock a thorough FAQ for newcomers.

```text
weak:  "Exception: Null Pointer at 0x0045"
solid: "Something went wrong — try refreshing"

weak:  navigating with terms like "S3 bucket instances"
solid: plain language like "File storage"
```

#### Stepping Stone (Foot-in-the-Door)

A small "yes" makes a later, larger "yes" far more likely.

- Ask for an email before ever asking for a card.
- Pose one light preference ("Dark mode?") ahead of registration.
- Open with a few quick yes/no questions.
- Hand over a free tool or PDF before pitching a subscription.
- Invite a photo upload first, the full bio later.
- Offer a low-cost tripwire before the main product.

```text
weak:  "Start free trial" that demands a card immediately
solid: collect email and password first, then offer the trial

weak:  a survey dumping all 50 questions on one screen
solid: a survey opening with a single easy yes/no
```

---

## 6. Building Trust

Trust is assembled from many small signals placed where doubt arises.

### Categories of trust signal

| Category | What it includes | How it shows up |
|----------|------------------|-----------------|
| **Security** | SSL, encryption, seals | A visible padlock and security marks on forms |
| **Social proof** | Reviews, testimonials, logos | Ratings, customer photos, partner brands |
| **Transparency** | Policies, pricing, contact | Plain links, no hidden fees, a real address |
| **Professionalism** | Craft and consistency | Nothing broken, branding held steady |
| **Authority** | Certifications, awards, press | "As seen in…", recognized credentials |

### Where the signals go

```
  ╔══════════════════════════════════════════════════════╗
  ║ HEADER    strip: "Free shipping · 30-day returns ·   ║
  ║           Secure checkout"                            ║
  ╠══════════════════════════════════════════════════════╣
  ║ HERO      headline social proof: "Trusted by 10,000+"║
  ╠══════════════════════════════════════════════════════╣
  ║ PRODUCT   reviews in view, security marks nearby     ║
  ╠══════════════════════════════════════════════════════╣
  ║ CHECKOUT  payment icons + SSL seal + guarantee       ║
  ╠══════════════════════════════════════════════════════╣
  ║ FOOTER    contact details, policies, certifications  ║
  ╚══════════════════════════════════════════════════════╝
```

### Trust patterns in CSS

```css
/* a reassurance chip — sharp corners read as "precise" */
.assurance-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #ecfdf5;          /* soft green = safe */
  color: #047857;
  border-radius: 3px;
  font-size: 13px;
}

/* mark a form as protected before anyone types into it */
.protected-fields::before {
  content: '🔒 Encrypted form';
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  color: #047857;
}

/* a testimonial — generous radius reads as "friendly" */
.review-card {
  display: flex;
  gap: 16px;
  padding: 22px;
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 6px 18px -10px rgba(2, 6, 23, 0.18);
}
.review-card__face {
  width: 46px;
  height: 46px;
  border-radius: 50%;          /* a real photo beats initials */
  object-fit: cover;
}
```

---

## 7. Persuasion — and the Ethical Line

The same lever can inform or deceive. The difference is whether the claim is true and whether the user keeps their agency.

| Lever | Honest use | Dark pattern (don't) |
|-------|------------|----------------------|
| **Scarcity** | Real stock counts | Fake "almost gone" timers |
| **Social proof** | Genuine reviews | Invented testimonials |
| **Authority** | Real credentials | Misleading seals |
| **Urgency** | True deadlines | Manufactured FOMO |
| **Commitment** | Saving real progress | Guilt-tripping confirm-shaming |

### Nudges that stay on the right side

**Smart default** — pre-select the option most people want, while leaving the choice open.

```html
<fieldset>
  <legend>Choose a billing cycle</legend>
  <label><input type="radio" name="cycle" value="monthly"> Monthly</label>
  <label><input type="radio" name="cycle" value="yearly" checked>
    Yearly — save 20%</label>
</fieldset>
```

**Anchor** — frame the discount against a real reference price.

```html
<p class="pricing">
  <span class="pricing__was">$99</span>
  <span class="pricing__now">$79</span>
  <span class="pricing__off">You save 20%</span>
</p>
```

**Social proof** — true, current activity.

```html
<div class="live-ping">
  <img class="live-ping__face" src="/avatars/jonas.jpg" alt="">
  <span>Jonas in Berlin just signed up</span>
</div>
<p class="tally">Used by 50,000+ designers and counting</p>
```

**Progress + commitment** — show how near the finish is.

```html
<div class="meter" role="progressbar" aria-valuenow="60"
     aria-valuemin="0" aria-valuemax="100">
  <div class="meter__fill" style="width:60%"></div>
</div>
<small>60% there — one short step left</small>
```

---

## 8. Designing for Generations

Treat these as starting hypotheses to validate, never as boxes people must fit. Birth-year ranges are the standard cohort definitions.

### Gen Z — born 1997–2012

```
  who they are
    · grew up digital, think mobile-first
    · prize authenticity and diversity
    · skim fast; learn visually

  how to design for them
    · color ......... bold, saturated, gradient-forward
    · type .......... large, variable, willing to experiment
    · layout ........ vertical scroll, built for the phone
    · motion ........ quick, gamified, gesture-driven
    · content ....... short video, memes, stories
    · trust ......... peers outrank institutions
```

### Millennials — born 1981–1996

```
  who they are
    · buy experiences over objects
    · research before committing
    · socially conscious
    · price-aware but quality-minded

  how to design for them
    · color ......... muted pastels, earth tones
    · type .......... clean, legible sans-serif
    · layout ........ responsive, card-based
    · motion ........ smooth and purposeful
    · content ....... value-led, transparent
    · trust ......... reviews, ethics, stated values
```

### Gen X — born 1965–1980

```
  who they are
    · independent and self-reliant
    · efficiency over flash
    · wary of marketing spin
    · comfortable enough with tech

  how to design for them
    · color ......... professional, steady
    · type .......... familiar, conservative
    · layout ........ clear hierarchy, traditional
    · motion ........ functional, never showy
    · content ....... direct, fact-based
    · trust ......... proven expertise and track record
```

### Baby Boomers — born 1946–1964

```
  who they are
    · detail-oriented
    · loyal once trust is earned
    · value personal service
    · less confident with tech

  how to design for them
    · color ......... high contrast, simple palette
    · type .......... large (18px+), strong contrast
    · layout ........ simple, linear, roomy
    · motion ........ minimal, with explicit feedback
    · content ....... thorough and complete
    · trust ......... phone numbers, real humans
```

---

## 9. Emotion → Color

A quick map from the feeling you want to the hues that tend to carry it.

| Feeling | Typical hues | Common domain |
|---------|--------------|---------------|
| Trust | Blue, green | Finance |
| Excitement | Red, orange | Sales |
| Calm | Blue, soft green | Wellness |
| Luxury | Black, gold | Premium |
| Creativity | Teal, pink | Art |
| Energy | Yellow, orange | Sports |
| Nature | Green, brown | Eco |
| Happiness | Yellow, orange | Kids |
| Sophistication | Gray, navy | Corporate |
| Urgency | Red | Errors |

---

## 10. Pre-Ship Psychology Checklist

Walk this before launch; each item ties back to a principle above.

**Decisions & flow**
- [ ] **Hick's Law** — navigation kept to ~7 choices; decision fatigue reduced where it counts.
- [ ] **Occam's Razor** — every non-essential visual and functional element removed.
- [ ] **Parkinson's Law** — fast paths (one-click checkout, express setup) in place to shorten tasks.
- [ ] **Tesler's Law** — complexity shifted from the user to the system wherever feasible.
- [ ] **Postel's Law** — inputs accepted in varied formats without throwing errors.

**Memory & attention**
- [ ] **Miller's Law** — content chunked into digestible units of 5–7.
- [ ] **Von Restorff** — the primary CTA visibly outranks everything else.
- [ ] **Serial Position** — the most critical items sit at the start or end of lists.
- [ ] **Jakob's Law** — standard web conventions honored throughout.
- [ ] **Gestalt** — related items grouped by proximity or sealed in a common region.
- [ ] **Prägnanz** — icons and shapes recognizable at a glance.
- [ ] **Figure/Ground** — the focused element reads clearly (shadows, scrims on modals).

**Speed & feedback**
- [ ] **Doherty Threshold** — feedback lands within 400ms; skeleton screens cover fetches.
- [ ] **Feedback states** — every interactive element has hover, active, and success states.

**Motivation & behavior**
- [ ] **Zeigarnik** — incomplete tasks carry visual cues (progress bars, badges).
- [ ] **Goal Gradient** — users get a head start (e.g. 20% pre-filled) toward completion.
- [ ] **Peak-End** — the closing "success" moment delivers a beat of delight.
- [ ] **Stepping Stone** — the funnel opens with a low-friction ask (email only).
- [ ] **Loss Aversion** — copy stresses what users keep, not only what they gain.
- [ ] **Anchoring** — pricing is framed so the target choice reads as a clear value.

**Trust, persuasion & inclusion**
- [ ] **Aesthetic-Usability** — fidelity is high enough to earn early trust.
- [ ] **Authority & trust** — security marks, reviews, and credentials are visible.
- [ ] **Social Proof** — real numbers or testimonials appear at decision points.
- [ ] **Scarcity & urgency** — if used at all, they are genuine and ethical.
- [ ] **False-Consensus** — tested with real users, not just the internal team.
- [ ] **Curse of Knowledge** — copy is jargon-free and clear to a first-timer.
- [ ] **Cognitive load** — extraneous noise minimized; the interface stays calm.
- [ ] **Emotional design** — palette and imagery trigger the intended visceral response.
- [ ] **Accessibility** — contrast ratios meet WCAG, and the site is fully navigable by keyboard and screen reader.

---

**Takeaway:** design for the brain you're actually serving — bound by memory, swayed by feeling, and quick to trust what's clear — and the interface mostly designs itself.
