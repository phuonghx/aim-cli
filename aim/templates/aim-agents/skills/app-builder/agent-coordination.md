# Coordinating the Agents

How App Builder hands work to its specialist agents and keeps them in sequence.

## The Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   APP BUILDER (Orchestrator)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     PROJECT PLANNER                          │
│  • Carve the work into tasks                                 │
│  • Map out dependencies                                      │
│  • Decide the file layout                                    │
│  • Write {task-slug}.md at the project root (REQUIRED)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              GATE: CONFIRM THE PLAN EXISTS                   │
│  🔴 CHECK: is {task-slug}.md present at the project root?    │
│  🔴 Missing -> HALT -> write the plan file before anything  │
│  🔴 Present -> move on to the specialists                   │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ DATABASE        │ │ BACKEND         │ │ FRONTEND        │
│ ARCHITECT       │ │ SPECIALIST      │ │ SPECIALIST      │
│                 │ │                 │ │                 │
│ • Design schema │ │ • API routes    │ │ • Components    │
│ • Migrations    │ │ • Controllers   │ │ • Pages         │
│ • Seed data     │ │ • Middleware    │ │ • Styling       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 OPTIONAL PARALLEL PASS                       │
│  • Security Auditor -> scan for vulnerabilities             │
│  • Test Engineer -> write unit tests                       │
│  • Performance Optimizer -> inspect the bundle             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DEVOPS ENGINEER                          │
│  • Stand up the environment                                  │
│  • Push a preview deploy                                     │
│  • Run a health check                                        │
└─────────────────────────────────────────────────────────────┘
```

## Order of Operations

| Phase | Agent(s) | Can run in parallel? | Needs first | Gate |
|-------|----------|----------------------|-------------|------|
| 0 | Socratic Gate | No | — | Pose the 3 questions |
| 1 | Project Planner | No | Questions answered | **{task-slug}.md written** |
| 1.5 | **Plan check** | No | {task-slug}.md written | **File confirmed at root** |
| 2 | Database Architect | No | Plan in place | Schema settled |
| 3 | Backend Specialist | No | Schema settled | API routes built |
| 4 | Frontend Specialist | Yes | API partly ready | UI components built |
| 5 | Security Auditor, Test Engineer | Yes | Code in place | Audit and tests clear |
| 6 | DevOps Engineer | No | Everything built | Ready to deploy |

> 🔴 **Do not skip Phase 1.5.** No specialist starts until {task-slug}.md is confirmed at the project root.
