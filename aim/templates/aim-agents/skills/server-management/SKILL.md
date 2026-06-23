---
name: server-management
description: Frames production server operations as decisions -- which process manager to run, what to monitor and alert on, how to handle logs, and when to scale up versus out. It reasons from symptoms and goals rather than reciting commands, and includes a triage order for incidents. Use it when keeping a service running, configuring a process manager like PM2 or systemd, planning monitoring, or deciding a scaling approach.
---

# Running Servers in Production

Operations is a series of judgment calls, not a list of commands to memorize. The sections below help you reason from goals and symptoms to the right choice for your situation.

## Keeping processes alive

Pick the supervisor that matches what you are running:

| Running | Reach for |
|---------|-----------|
| A Node.js app | PM2 -- clustering and zero-downtime reloads |
| Any Linux service | systemd -- the native init |
| Containerized workloads | Docker or Podman |
| Many services together | Kubernetes or Docker Swarm |

Whatever you choose, it should deliver the same four things: restart automatically after a crash, reload without dropping requests, use every CPU core (clustering), and come back on its own after the host reboots.

## Monitoring

Watch four families of signal:

| Family | Representative metrics |
|--------|------------------------|
| Availability | uptime, health-check status |
| Performance | latency, throughput |
| Errors | error rate, error types |
| Resources | CPU, memory, disk |

Tie each alert to a response so noise does not drown signal: **critical** means act now, **warning** means look into it soon, **info** means review on a normal cadence.

Match the tooling to the budget and need: PM2's built-in metrics or `htop` for something free and simple; Grafana or Datadog for full observability; Sentry for error tracking; UptimeRobot or Pingdom for external uptime checks.

## Logs

Different logs answer different questions -- application logs for debugging and audit, access logs for traffic patterns, error logs for catching failures.

Four practices keep logging useful rather than harmful:

1. Rotate logs so they never fill the disk.
2. Emit structured logs (JSON) so they are machine-parseable.
3. Use levels deliberately -- error, warn, info, debug.
4. Never write secrets or sensitive data to a log.

## Scaling

Read the symptom before reaching for a fix:

| Symptom | First move |
|---------|------------|
| CPU pinned | add instances (scale out) |
| Memory exhausted | add RAM, or hunt the leak |
| Responses slow | profile first, then scale |
| Spiky traffic | autoscaling |

Then choose the shape: **vertical** (a bigger box) is a fast patch for a single instance, **horizontal** (more boxes) is the sustainable distributed answer, and **auto** fits workloads whose traffic varies. Resist scaling a slow service before profiling it -- you may just be paying more for the same bottleneck.

## Health checks

A meaningful health check confirms more than "the process is up":

| Check | What it tells you |
|-------|-------------------|
| HTTP 200 | the service is answering |
| DB reachable | data layer is connected |
| Dependencies reachable | upstream services respond |
| Resources headroom | CPU and memory are not exhausted |

A shallow check (return 200) is enough for a basic liveness probe; a deep check (verify every dependency) suits readiness gating. Let the load balancer's needs decide which.

## Security baseline

| Area | Stance |
|------|--------|
| Access | SSH keys only; disable password login |
| Firewall | open only the ports actually in use |
| Patching | apply security updates on a schedule |
| Secrets | environment variables, not committed files |
| Auditing | log access and configuration changes |

## Triage order

When something breaks, work outward in this sequence so you find the fault fast:

1. Is the process even running?
2. What do the logs say?
3. Are resources exhausted (disk, memory, CPU)?
4. Is the network healthy (ports open, DNS resolving)?
5. Are the dependencies up (database, external APIs)?

## What to avoid

| Avoid | Do instead |
|-------|------------|
| Running services as root | run under a least-privilege user |
| Letting logs grow unbounded | configure rotation |
| Bolting on monitoring later | instrument from day one |
| Restarting by hand | configure auto-restart |
| No backups | keep a regular, tested backup schedule |

A well-run server is uneventful. Boring is the target.
