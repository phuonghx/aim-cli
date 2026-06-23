# Generating Questions Dynamically

> **The core idea:** a question's job is to expose an *architectural consequence*, not to fill in a form.
>
> If asking it doesn't change a concrete implementation decision — one that moves cost, complexity, or timeline — it doesn't belong.

---

## 🧠 The Four Principles

### 1 — A question should reveal what's at stake

Weak questions collect facts. Strong ones make the downstream consequences visible:

```markdown
❌ Thin:  "What login method do you want?"
✅ Sharp: "Should accounts be email + password, or sign-in through a provider
           like Google or GitHub?

   What rides on it:
   - Email/password → you own password resets, hashing, and any 2FA later
   - Provider sign-in → OAuth wiring + profile mapping, but less you control

   The tension: account security vs. build time vs. how much friction users feel"
```

### 2 — Establish the frame before the details

Where a request sits decides which questions are even worth asking:

| Frame | Aim the questions at |
|-------|----------------------|
| **Greenfield** (from zero) | Foundations: language/runtime, where it's hosted, expected scale |
| **Adding to something** | Seams with existing code, conventions to match, what might break |
| **Refactor** | The motive — speed? readability? — and exactly what hurts today |
| **Bug hunt** | Observed symptoms → likely cause → a reliable way to reproduce |

### 3 — Ask only the questions that cut paths

**The test:** each question must collapse a branch in the road. One that leaves every option open is noise.

```
Before asking:
├── Route A: ship the simple version (~5 min)
├── Route B: add the middle layer  (~15 min)
└── Route C: build the full thing  (~1 hr)

After asking:
└── Route A locked in (~5 min)
```

A question that doesn't shrink that tree → **cut it.**

### 4 — Let answers replace assumptions

```markdown
❌ Guessing: "They'll probably want SendGrid for email."
✅ Asking:   "Which email service should handle delivery?

   SendGrid  → mature API, generous free tier, deliverability tooling
   Postmark  → transactional-first, fast, premium pricing
   Resend    → developer-friendly, modern SDK, newer ecosystem"
```

---

## 📋 The Generation Algorithm

```
INPUT: the request + its frame (greenfield / addition / refactor / bug hunt)
│
├── STEP 1 — Read it apart
│   ├── Domain     (commerce, auth, real-time, content, …)
│   ├── Features   (the stated ones and the ones they imply)
│   └── Scale cues (user counts, data size, request frequency)
│
├── STEP 2 — Find the forks
│   ├── Must be settled before any code   → blocking
│   ├── Safe to settle later              → deferrable
│   └── Ripples through the architecture  → high-leverage
│
├── STEP 3 — Rank them
│   ├── P0 — blocking      (work cannot start without an answer)
│   ├── P1 — high-leverage (shapes >~30% of the build)
│   ├── P2 — moderate      (touches specific features)
│   └── P3 — optional      (edge cases, polish)
│
└── STEP 4 — Shape each one
    ├── What    — the question itself
    ├── Why     — its effect on the implementation
    ├── Options — real trade-offs, not a bare A/B
    └── Default — what proceeds if no answer comes
```

---

## 🎯 Question Banks by Domain

### Commerce

| Question | What hangs on it | Trade-off |
|----------|------------------|-----------|
| **One seller or a marketplace?** | Many sellers → commissions, seller dashboards, payment splits | +reach, −complexity |
| **Track stock levels?** | Implies stock tables, reservations, low-stock alerts | +accuracy, −build time |
| **Digital goods or shipped goods?** | Digital → secure download links, no logistics | Physical → carrier APIs + tracking |
| **Recurring or one-off charges?** | Subscriptions → billing cycles, proration, failed-payment recovery | +revenue, −complexity |

### Authentication

| Question | What hangs on it | Trade-off |
|----------|------------------|-----------|
| **Provider sign-in too?** | OAuth integration vs. owning the reset/recovery flow | +convenience, −control |
| **Roles and permissions?** | Permission tables, enforcement layer, admin screens | +safety, −build time |
| **Second factor?** | TOTP or SMS plumbing, backup codes, recovery path | +safety, −friction |
| **Confirm email addresses?** | Tokens, an email sender, resend handling | +trust, −signup friction |

### Real-time

| Question | What hangs on it | Trade-off |
|----------|------------------|-----------|
| **Push (sockets) or pull (polling)?** | Sockets → connection state, horizontal scaling | Polling → simpler, laggier |
| **How many concurrent clients?** | <100 → one box; >1k → pub/sub layer; >10k → dedicated infra | +scale, −complexity |
| **Keep message history?** | Persistence tables, storage spend, pagination | +experience, −storage |
| **Transient or durable?** | Transient → in-memory; durable → write before broadcast | +reliability, −latency |

### Content / CMS

| Question | What hangs on it | Trade-off |
|----------|------------------|-----------|
| **WYSIWYG or Markdown?** | Rich editing → sanitizing, XSS surface | Markdown → simpler, no live preview |
| **Draft-then-publish?** | Status flags, scheduling jobs, version history | +control, −complexity |
| **Handle uploads?** | Upload routes, storage backend, image processing | +capability, −build time |
| **More than one language?** | Translation tables, editor UI, fallback rules | +audience, −complexity |

---

## 📐 Question Template

```markdown
For your [DOMAIN] [FEATURE] request:

## 🔴 BLOCKING (decide before we start)

### 1. **[THE DECISION]**

**Question:** [specific and answerable]

**Why it matters:**
- [the architectural ripple]
- [what moves: cost / complexity / timeline / scale]

**Options:**
| Option | Upside | Downside | Fits when |
|--------|--------|----------|-----------|
| A | [+] | [-] | [scenario] |
| B | [+] | [-] | [scenario] |

**Default if silent:** [the fallback + why]

---

## 🟡 HIGH-LEVERAGE (shapes the build)

### 2. **[THE DECISION]**
[same shape]

---

## 🟢 OPTIONAL (edge cases)

### 3. **[THE DECISION]**
[same shape]
```

---

## 🔄 Questioning in Waves

### Wave 1 — before any code (3–5 questions)
Only the **blocking** decisions. Don't start until they're answered.

### Wave 2 — once a skeleton exists
As the shape emerges, raise the follow-ups:
- "This brings in [edge case]. Handle it now or park it?"
- "We've gone with [pattern]. Should [next feature] follow suit?"

### Wave 3 — once it works
With functionality in place:
- "There's a bottleneck at [spot]. Tune it now or leave it?"
- "Worth refactoring [area], or ship as-is?"

---

## 🎭 Worked Example, Start to Finish

```
REQUEST: "Build a habit-tracking app"

STEP 1 — Read it apart
├── Domain: personal productivity / behavior tracking
├── Features: define habits, daily check-ins, streaks, reminders
├── Implied: accounts, a dashboard, recurring schedules
└── Scale: modest per user, but heavy daily write frequency

STEP 2 — Find the forks
├── Blocking:      where data lives, account model, how reminders fire
├── High-leverage: streak/schedule data model, offline behavior
└── Deferrable:    social sharing, analytics charts, gamified badges

STEP 3 — Rank them

P0 (blocking):
1. Data + sync model → drives architecture, offline story, cost
2. Reminder delivery → drives infra (push vs. local notifications)
3. Account model     → drives effort, UX, multi-device support

P1 (high-leverage):
4. Schedule flexibility → simple daily vs. arbitrary recurrence rules
5. Offline-first       → local cache + sync vs. always-online

P2 (deferrable):
6. Social / accountability buddies → separate subsystem, push to v2
7. Insight charts                  → reporting layer, push to v2

STEP 4 — Shape the output
```

---

## 📊 The Output (Example)

```
For your habit-tracking app:

## 🔴 BLOCKING (decide before we start)

### 1. **Data Storage & Sync Model**

**Question:** Where do habits and check-ins live, and do they sync across devices?

**Why it matters:**
- Moves: architecture, offline behavior, ongoing hosting cost
- Daily writes add up fast: 500 users × 5 habits × 1 check-in/day = 2,500 writes/day

**Options:**
| Option | Cost shape | Offline | Complexity | Fits when |
|--------|-----------|---------|------------|-----------|
| **Local-only (SQLite)** | None | Full | Low | Single-device MVP |
| **Firebase / Firestore** | Usage-based | Built-in sync | Low–Med | Multi-device, quick start |
| **Postgres + API** | Server cost | Needs custom sync | Medium | Full control, scaling later |
| **Supabase** | Free tier + usage | Good | Low | Small scale, batteries included |

**Default if silent:** Supabase (multi-device sync without much setup)

---

### 2. **Reminder Delivery**

**Question:** How do users get nudged to log a habit?

**Why it matters:**
- Moves: required infrastructure, reliability, battery/permission concerns
- Server push needs a backend + device tokens; local notifications don't

**Options:**
| Option | Complexity | Reliability | Fits when |
|--------|------------|-------------|-----------|
| **Local notifications** | Low | Device-bound | MVP, on-device scheduling |
| **Push (FCM/APNs)** | High | Server-controlled | Cross-device, server-driven timing |
| **Email reminders** | Medium | Inbox-dependent | Web-first, no mobile app |

**Default if silent:** Local notifications (no backend needed for MVP)

---

### 3. **Account Model**

**Question:** Do users need accounts, or does the app work anonymously?

**Why it matters:**
- Moves: build effort, multi-device support, data durability

**Options:**
| Option | Effort | Multi-device | Data safety | Fits when |
|--------|--------|--------------|-------------|-----------|
| **No account (local)** | Lowest | None | Lost on uninstall | Fastest MVP |
| **Email/password** | Higher | Yes | Backed up | Full control |
| **Provider sign-in** | Medium | Yes | Backed up | Low-friction launch |
| **Managed auth (Clerk/Supabase)** | Lowest hosted | Yes | Backed up | Quickest path to accounts |

**Default if silent:** Managed auth via Supabase (pairs with the storage default)

---

## 🟡 HIGH-LEVERAGE (shapes the build)

### 4. **Schedule Flexibility**

**Question:** Are habits strictly daily, or can users set custom cadences (3×/week, weekdays, etc.)?

**Why it matters:**
- Daily-only is a single timestamp check; custom recurrence needs a rules engine
- Streak math gets noticeably harder with flexible schedules

**Options:**
| Option | Complexity | Data model | Fits when |
|--------|------------|------------|-----------|
| **Daily only** | Low | One flag per day | MVP, simple habits |
| **Days-of-week** | Medium | Weekday bitmask | Most real use |
| **Full recurrence rules** | High | RRULE-style records | Power users |

**Default if silent:** Days-of-week (covers most cases without an engine)

---

## 🟢 OPTIONAL (push to v2)

### 5. **Accountability / Social**
- A separate subsystem (sharing, friend graphs) unrelated to core tracking
- Suggestion: validate solo tracking first, layer social on afterward

### 6. **Insight Charts**
- A reporting layer on top of the raw log
- Suggestion: start with a plain streak count; add trends once there's data worth charting

---

## 📋 Summary

| Decision | Recommendation | Cost if changed |
|----------|----------------|-----------------|
| Storage | Supabase | +4 hrs to swap backends |
| Reminders | Local notifications | +6 hrs for server push |
| Accounts | Managed auth | −3 hrs vs. rolling your own |
| Schedule | Days-of-week | +4 hrs for full recurrence |
| Social | Defer to v2 | N/A |
| Charts | Defer to v2 | N/A |

**Scope:** the MVP delivers the must-haves above; social and charts land in v2.
```

---

## 🎯 Principles, Recapped

1. **Every question maps to a design decision** — never a fact-gathering exercise.
2. **Make the trade-offs visible** — so the user weighs consequences, not vibes.
3. **Front-load the blockers** — nothing starts until those are answered.
4. **Always carry a default** — silence shouldn't stall the work.
5. **Stay domain-aware** — commerce, auth, and real-time each need their own questions.
6. **Question in waves** — new forks surface as the build takes shape.
