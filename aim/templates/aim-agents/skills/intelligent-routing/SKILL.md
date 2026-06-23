---
name: intelligent-routing
description: Reads each incoming request and quietly dispatches it to the specialist agent or agents best suited to it, so the user never has to name an agent by hand. It classifies intent, detects the domains involved, gauges complexity, and either invokes one specialist, chains a few, or escalates to an orchestrator. Use it when a request spans several domains or the right specialist is not obvious; it stays active by default and yields to any explicit agent the user names.
---

# Intelligent Routing

Treat every request the way a good project manager would: read it, figure out which expert should own it, and hand it over — without making the user learn the org chart. Routing happens silently and continuously; the user just gets the right specialist's answer.

## The Flow For Every Request

Before producing any reply, run a quick mental pass:

```
incoming request
   → read the intent (what kind of ask is this?)
   → tag the domains it touches
   → judge how big it is
   → pick the agent(s) and apply their expertise
```

Done well, this costs almost nothing and saves the round-trips that come from a generalist guessing at a specialist's job.

## Picking The Agent

Match the request's signal words to a specialist. The right-hand column says whether to act immediately or pause for a quick confirmation first.

| The ask is about | Tell-tale words | Send it to | Act now? |
|------------------|-----------------|-----------|---------|
| Sign-in / accounts | login, auth, signup, password | `security-auditor` + `backend-specialist` | yes |
| A UI piece | button, card, layout, style | `frontend-specialist` | yes |
| A mobile surface | screen, navigation, gesture, touch | `mobile-developer` | yes |
| An HTTP route | endpoint, route, GET, POST | `backend-specialist` | yes |
| Data layer | schema, migration, query, table | `database-architect` + `backend-specialist` | yes |
| Something broken | error, bug, broken, not working | `debugger` | yes |
| Tests | test, coverage, unit, e2e | `test-engineer` | yes |
| Shipping | deploy, production, CI/CD, docker | `devops-engineer` | yes |
| A security pass | vulnerability, exploit, hardening | `security-auditor` + `penetration-tester` | yes |
| Speed | slow, optimize, latency, cache | `performance-optimizer` | yes |
| Product shaping | requirements, user story, MVP | `product-owner` | yes |
| A whole feature | build, create, implement, new app | `orchestrator` → many agents | confirm first |
| Many domains at once | spans several areas | `orchestrator` → many agents | confirm first |

## The Decision, Step By Step

The routing logic, sketched as pseudo-code:

```javascript
function route(request) {
  const kind     = classify(request);      // question, task, fix, ...
  const domains  = detectDomains(request); // ['security', 'frontend', ...]
  const size     = gauge(domains);         // simple | moderate | complex

  if (kind === 'question')            return null;          // just answer
  if (size === 'simple')              return one(domains[0]);
  if (size === 'moderate')            return few(domains);   // up to 2
  return 'orchestrator';                                     // complex
}
```

## Mapping Words To Domains

For single-domain work, these keyword families point straight at one specialist:

| Domain | Words that signal it | Agent |
|--------|---------------------|-------|
| Security | auth, jwt, password, hash, token | `security-auditor` |
| Frontend | component, react, vue, css, tailwind | `frontend-specialist` |
| Backend | api, server, express, fastapi, node | `backend-specialist` |
| Mobile | react native, flutter, ios, android | `mobile-developer` |
| Database | prisma, sql, mongodb, migration | `database-architect` |
| Testing | jest, vitest, playwright, cypress | `test-engineer` |
| DevOps | docker, kubernetes, ci/cd, nginx | `devops-engineer` |
| Debug | error, crash, bug, issue | `debugger` |
| Performance | lag, optimize, cache, profiling | `performance-optimizer` |
| SEO | meta, sitemap, robots, analytics | `seo-specialist` |
| Game | unity, godot, phaser, multiplayer | `game-developer` |

When the words land in **two or more unrelated domains**, stop routing to a single specialist and escalate to `orchestrator`:

```
"Build a secure login screen with a dark theme"
  → security + frontend
  → orchestrator, which then pulls in
    security-auditor, frontend-specialist, test-engineer
```

## Sizing The Request

| Size | Looks like | Move |
|------|-----------|------|
| Simple | one file, one domain, crisp ask | invoke the one specialist |
| Moderate | two or three files, two domains | chain the relevant specialists |
| Complex | many files or domains, design calls, fuzzy scope | hand to `orchestrator` |

Examples, in order: "restyle the login button" → simple. "add a profile endpoint" → moderate. "build a social app" → complex.

## House Rules

1. **Route without narrating.** Don't announce that analysis is happening — just do it, then name the expertise you're applying.
2. **Name the expertise, briefly.** A single line is enough: "Applying `@frontend-specialist` —" then the answer.
3. **Stay invisible otherwise.** The experience should feel like talking to the right specialist from the start.
4. **An explicit pick always wins.** If the user names an agent, use it and skip the automatic choice.

## Tricky Inputs

| Input | Read | Response |
|-------|------|----------|
| "How does hydration work?" | a question | answer directly, no agent |
| "Make it better" | too vague | ask what "better" means, then route |
| "Add mobile support to the web app" | ambiguous | clarify: responsive web or native app? then route |

## Fitting Into The Wider System

- **Versus an explicit `/orchestrate`:** the user can invoke orchestration by hand, or you detect a complex task and reach for the orchestrator yourself — same destination, no command required.
- **Versus clarification gates:** auto-routing never skips them. A murky task still earns clarifying questions before any agent runs.
- **Versus project-level rules:** an explicit routing rule in the project's configuration outranks this skill. Automatic routing is only the fallback when no such rule exists.

## Cost

Reading and classifying a request adds a small, fixed overhead per turn. It earns that back by cutting the back-and-forth a misrouted request would have caused. The classification is pattern-matching, so it's effectively instant and needs no extra calls — the agent is chosen before the first line of the reply.

## In Short

Automatic routing means specialist-quality answers with zero commands to memorize: intent and domains are read on every turn, the applied expertise is stated plainly, an explicitly named agent always overrides, and anything genuinely complex falls through to the orchestrator. The user gets the expert without having to know the system underneath.
