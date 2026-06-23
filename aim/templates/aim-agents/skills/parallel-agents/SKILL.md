---
name: parallel-agents
description: Patterns for driving several specialist agents through one task using the built-in Agent tool, so a problem gets covered from multiple angles within a single session. It explains when to fan work out, how to chain agents and pass findings between them, and how to fold the results into one report. Use it when a job needs two or more specialists or a multi-domain review, including via the /orchestrate or /coordinate workflows.
---

# Parallel Agents

This skill is about marshalling specialist agents through the platform's own Agent tool. Everything stays inside one session and under the host's control — no external scripts, no separate processes to babysit.

## Is Orchestration The Right Call

Reach for it when:
- The work genuinely spans several areas of expertise.
- You want code looked at through security, performance, and quality lenses at once.
- A review needs to cover architecture, security, and testing together.
- A feature touches backend, frontend, and the data layer all at once.

Leave it alone when:
- The task sits squarely in one domain.
- It's a small fix or a quick edit.
- A single agent would clearly suffice.

## Calling Agents

A single specialist:
```
Have the security-auditor review the authentication flow.
```

A chain, one after another:
```
Start with explorer-agent to map the project layout.
Then backend-specialist to review the API surface.
Finally test-engineer to find the coverage gaps.
```

Passing findings down the chain:
```
Have frontend-specialist analyze the React components,
then hand those findings to test-engineer to write matching tests.
```

Picking up where one left off:
```
Resume agent [agentId] and continue with the extra requirements.
```

## Three Orchestration Shapes

### Whole-codebase review
```
explorer-agent → domain specialists → synthesis

1. explorer-agent maps the structure
2. security-auditor judges the security posture
3. backend-specialist weighs API quality
4. frontend-specialist reviews the UI patterns
5. test-engineer measures coverage
6. fold it all into one report
```

### Reviewing a change
```
affected specialists → test-engineer

1. work out which domains the change touches
2. bring in just those specialists
3. test-engineer confirms the change holds
4. consolidate the recommendations
```

### Security audit
```
security-auditor → penetration-tester → synthesis

1. security-auditor does the config and code review
2. penetration-tester probes for live vulnerabilities
3. synthesize with a prioritized fix list
```

## The Specialist Roster

| Agent | Owns | Phrases that summon it |
|-------|------|------------------------|
| `orchestrator` | Coordination | "comprehensive", "multi-perspective" |
| `security-auditor` | Security | "security", "auth", "vulnerabilities" |
| `penetration-tester` | Offensive testing | "pentest", "red team", "exploit" |
| `backend-specialist` | Backend | "API", "server", "Node.js", "Express" |
| `frontend-specialist` | Frontend | "React", "UI", "components", "Next.js" |
| `test-engineer` | Testing | "tests", "coverage", "TDD" |
| `devops-engineer` | DevOps | "deploy", "CI/CD", "infrastructure" |
| `database-architect` | Database | "schema", "Prisma", "migrations" |
| `mobile-developer` | Mobile | "React Native", "Flutter", "mobile" |
| `api-designer` | API design | "REST", "GraphQL", "OpenAPI" |
| `debugger` | Debugging | "bug", "error", "not working" |
| `explorer-agent` | Discovery | "explore", "map", "structure" |
| `documentation-writer` | Docs | "write docs", "README", "API docs" |
| `performance-optimizer` | Performance | "slow", "optimize", "profiling" |
| `project-planner` | Planning | "plan", "roadmap", "milestones" |
| `seo-specialist` | SEO | "SEO", "meta tags", "ranking" |
| `game-developer` | Games | "game", "Unity", "Godot", "Phaser" |

## The Built-In Agents

These ship with the platform and sit alongside the custom roster:

| Agent | Model | Job |
|-------|-------|-----|
| Explore | Haiku | Fast, read-only codebase search |
| Plan | Sonnet | Research while planning |
| General-purpose | Sonnet | Multi-step changes |

Reach for Explore when you just need to find something fast; reach for a custom specialist when you need domain depth.

## Folding It Together

When the agents are done, write one consolidated report rather than stapling their outputs together:

```markdown
## Synthesis

### What was done
[the gist]

### Who found what
| Agent | Finding |
|-------|---------|
| security-auditor | turned up X |
| backend-specialist | flagged Y |

### Recommendations, ranked
1. **Critical** — [from agent A]
2. **Important** — [from agent B]
3. **Optional** — [from agent C]

### Next actions
- [ ] close the critical security hole
- [ ] rework the API endpoint
- [ ] add the missing tests
```

## Habits Worth Keeping

1. **Know the roster** — seventeen specialists are available to orchestrate.
2. **Sequence it sensibly** — discover, then analyze, then build, then test.
3. **Carry context forward** — pass each agent the findings it needs.
4. **One report at the end** — consolidate, don't hand back a pile of separate outputs.
5. **Always verify edits** — loop in test-engineer whenever code changes.

## Why It Works

- **One session** — every agent shares the same context.
- **Self-directed** — the host runs the orchestration on its own.
- **Native** — it plugs into the built-in Explore and Plan agents.
- **Resumable** — earlier agent work can be picked back up.
- **Findings flow** — results move freely from one agent to the next.
