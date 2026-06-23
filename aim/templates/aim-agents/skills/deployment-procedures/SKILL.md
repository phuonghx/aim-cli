---
name: deployment-procedures
description: Covers the judgment behind safe production releases — choosing a platform, verifying before shipping, watching a rollout, and deciding when to roll back versus fix forward. It teaches reasoning rather than copy-paste commands, since the right move depends on the stack and the change. Reach for it when planning a release, designing a rollback path, or wiring up a delivery pipeline, including with the /deploy workflow.
---

# Deployment Procedures

This skill is about how to reason through a release, not a script to run. Two deployments are never quite the same, so the goal is to internalize the principles and translate them to whatever platform is in front of you. Whenever a step appears, ask why it exists before you perform it.

## Choosing Where To Run It

What you're shipping decides the platform, and the platform decides the mechanics.

```
What kind of thing is this?
├─ Static site / JAMstack ........ Vercel · Netlify · Cloudflare Pages
├─ Ordinary web app
│   ├─ want it managed .......... Railway · Render · Fly.io
│   └─ want full control ........ a VPS with PM2 or Docker
├─ Many small services ........... a container orchestrator
└─ Event-driven / functions ...... edge runtimes · Lambda
```

Each one releases differently:

| Platform | How a release happens |
|----------|----------------------|
| Vercel / Netlify | Push to git, it builds and ships |
| Railway / Render | Git push or a CLI command |
| VPS + PM2 | SSH in and run the steps yourself |
| Docker | Push an image, then orchestrate it |
| Kubernetes | `kubectl apply` the manifests |

## Before You Ship

### Four things to confirm

Group your pre-flight checks into four buckets, and don't proceed until all four are green:

| Bucket | The question it answers |
|--------|------------------------|
| Code health | Do tests pass, is it linted, did someone review it? |
| Build | Does the production build succeed cleanly? |
| Environment | Are env vars present and secrets current? |
| Safety net | Is there a backup and a written rollback path? |

### The pre-flight list

- [ ] Test suite green
- [ ] Reviewed and approved
- [ ] Production build clean
- [ ] Environment variables confirmed
- [ ] Migrations prepared, if any
- [ ] Rollback path written down
- [ ] Team given a heads-up
- [ ] Monitoring open and ready

## The Shape Of A Release

### Five phases

```
PREPARE  → re-check code, build, and config
SNAPSHOT → capture the current state so you can return to it
SHIP     → push the change with dashboards open
INSPECT  → health check, scan logs, walk a key flow
SETTLE   → looks good? lock it in. trouble? roll back.
```

### What each phase is really about

| Phase | The principle |
|-------|--------------|
| Prepare | Untested code never goes out |
| Snapshot | No backup means no way back |
| Ship | Stay and watch; don't push and leave |
| Inspect | Assume nothing works until you've seen it work |
| Settle | Keep a finger on the rollback trigger |

## After It's Live

### What to look at

| Signal | Why it matters |
|--------|---------------|
| Health endpoint | Confirms the process is actually up |
| Error stream | Catches anything new that just appeared |
| Critical flows | Proves the features users depend on still work |
| Latency | Shows response times haven't regressed |

### How long to watch

- **Minutes 0–5** — eyes on it, actively.
- **Around 15 minutes** — it should look steady.
- **At 1 hour** — a last confirming look.
- **Next day** — review the metrics with fresh eyes.

## Rolling Back

### When to pull the trigger

| What you see | What to do |
|--------------|-----------|
| Service is down | Roll back now |
| Errors flooding in | Roll back |
| Latency more than halved | Lean toward rolling back |
| Small, contained glitch | Fix forward if it's quick |

### How, per platform

| Platform | Rollback move |
|----------|--------------|
| Vercel / Netlify | Re-promote the previous deploy |
| Railway / Render | Roll back from the dashboard |
| VPS + PM2 | Restore the snapshot, restart |
| Docker | Re-deploy the prior image tag |
| Kubernetes | `kubectl rollout undo` |

### Principles while rolling back

1. **Restore first, diagnose later** — get users healthy, then investigate.
2. **Change one thing** — a rollback is a single action, not a flurry of edits.
3. **Say what happened** — keep the team in the loop.
4. **Write it up** — do the post-mortem once things are calm.

## When It Breaks At 3 AM

### Order of operations for an outage

1. **Read the symptom** — what is actually failing?
2. **Try the cheap fix** — a restart, if the cause is murky.
3. **Roll back** — if the restart didn't take.
4. **Dig in** — only after service is restored.

### Where to look, in order

| Look at | Usual suspects |
|---------|---------------|
| Logs | Exceptions, stack traces |
| Resources | Disk full, out of memory |
| Network | DNS, firewall, routing |
| Dependencies | Database, third-party APIs |

## Habits To Avoid

| Don't | Do instead |
|-------|-----------|
| Ship Friday afternoon | Ship early in the week |
| Hurry the rollout | Move through the phases |
| Skip the staging pass | Always rehearse first |
| Deploy with no backup | Snapshot before you ship |
| Push and walk away | Stay on it 15+ minutes |
| Bundle many changes | One change at a time |

## A Final Gut-Check

Before you hit go:

- [ ] Am I following the right procedure for this platform?
- [ ] Is a backup in place?
- [ ] Is the rollback path written down?
- [ ] Is monitoring live?
- [ ] Does the team know?
- [ ] Have I left myself time to watch it afterward?

## Carrying It Forward

1. Many small releases beat one large one.
2. Gate risky changes behind feature flags.
3. Automate the steps you repeat.
4. Keep a record of every deployment.
5. After anything goes wrong, find out why.
6. Rehearse a rollback before the day you depend on it.

Every release carries risk. You shrink that risk through preparation, never through speed.
