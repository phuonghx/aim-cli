# AIM Control Hub Roadmap & Implementation Plan

This document details the upcoming development plan and feature recommendations for the AIM CLI and Control Hub Dashboard.

---

## 📅 Roadmap Overview

| Phase | Goal | Focus |
|---|---|---|
| **Phase 1** | DX Quality & Real-Time Sync | `taste-skill` lint verification, Live synchronization |
| **Phase 2** | SDD Integration & Automation | Interactive Spec check, Git hook triggers |
| **Phase 3** | Advanced Visualizations | 3D Graph visualization, Multi-agent panel |

---

## 🛠️ Detailed Feature Plans

### 1. Phase 1: DX Quality & Real-Time Sync (Short-Term)

#### Feature A: Built-in `taste-skill` Linter
* **PM Goal (Product Value)**:
  * Automatically audit frontend components for "AI slop" tells (e.g. mesh gradients, Inter-only fonts, bad layout padding) to protect production styling quality.
* **Dev Specs (Technical Implementation)**:
  * Add `aim lint --taste` CLI command.
  * Implement parser hooks scanning HTML, CSS, and JS files for:
    - Text wrapping on CTAs (desktop CTA width audits).
    - Multi-line italic displays that clip descenders.
    - Too many "eyebrows" (uppercase wide-tracking label above headers - max 1 per 3 sections).
    - Radial purple glow gradients.
  * Integrate this CLI linter into the local Git pre-commit hook.

#### Feature B: WebSockets/SSE Live Sync
* **PM Goal (Product Value)**:
  * Remove manual dashboard refreshes. When a developer or background AI agent edits task files, the dashboard must immediately update in real-time.
* **Dev Specs (Technical Implementation)**:
  * Implement an Server-Sent Events (SSE) server endpoint `/api/events` inside `aim/browser_server.py`.
  * Integrate Python's `watchdog` to monitor `.ai-context/tasks/`, `.ai-context/memories.json`, and `docs/`.
  * Establish a frontend event subscriber (`new EventSource('/api/events')`) that triggers DOM replacement on file updates.

---

### 2. Phase 2: SDD Integration & Automation (Medium-Term)

#### Feature C: Interactive SDD Spec Cockpit
* **PM Goal (Product Value)**:
  * View spec documents, requirements, and compliance checklists side-by-side with code and tasks. Track test coverage and validation outcomes visually.
* **Dev Specs (Technical Implementation)**:
  * Introduce `/api/specs` API route parsing markdown files from `.ai-context/specs/`.
  * Present checkboxed verification points in a dedicated "Specifications" tab on the dashboard.
  * Expose a button to execute test scripts (`pytest`, `npm test`) and stream raw logs via SSE console panels.

#### Feature D: Local Git-Hook Trigger Command
* **PM Goal (Product Value)**:
  * Accelerate local integration checks, helping developers confirm task definitions and lint criteria before they push code to remote repositories.
* **Dev Specs (Technical Implementation)**:
  * Implement `aim hooks install` command to automatically write pre-commit or pre-push hook shell scripts into `.git/hooks/`.
  * Execute standard `aim status` or verification tests, halting push commands on unresolved tasks or failing tests.

---

### 3. Phase 3: Advanced Visualizations (Long-Term)

#### Feature E: High-Fidelity 3D Dependency Graph
* **PM Goal (Product Value)**:
  * Provide visual clarity on task dependencies, documentation links, and user ownership, making it easy to identify blocker tasks.
* **Dev Specs (Technical Implementation)**:
  * Transition from static SVG renders to Three.js / Canvas 3D graphs.
  * Support node types: `task`, `doc`, `user`, `memory` with custom 3D mesh tags.
  * Enable graph filtering by priority, status, and assignee.
