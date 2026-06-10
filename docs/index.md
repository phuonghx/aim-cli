# AIM Documentation Portal 📚

Welcome to the **AIM (AI Memory/Mind)** documentation portal. AIM is a centralized context, memory, and task manager for AI-native software development.

Choose a guide below to explore:

---

## 📖 Guides & Reference Manuals

### 0. [Interactive Demo Guide (AeroMap)](demo-guide.md)
Explore a pre-configured Google Maps alternative workspace using AIM's CLI and Web UI features.

### 1. [CLI Reference Guide](cli-reference.md)
Detailed usage, parameter options, and command line examples for all AIM subcommands:
* Core lifecycle (`init`, `sync`).
* Task & subtask management (`task create`, `task list`, etc.).
* Team database (`user add`, `user rename`, etc.).
* Tracking spent hours (`time start`, `time stop`, `time report`).
* ASCII Kanban Board and Project Status (`board`, `status`).

### 2. [Web Dashboard User Guide](dashboard.md)
Visual workspace features:
* Interactive drag-and-drop Kanban Board.
* Overhauled Task Details modal (inline title, description textareas, tags management, subtask trees).
* Force-Directed Knowledge Graph representing task and document links.
* Global command palette (`Ctrl+K` search popup).
* User Management registry database.

### 3. [Code Generation Templates Guide](templates-guide.md)
Learn how to scaffold, view, and run templates using YAML configuration and casing helpers (`kebabCase`, `pascalCase`, etc.) to generate consistent files.

### 4. [AI Agent Integration Guide](agent-integration.md)
In-depth instructions on how AIM synchronizes context out-of-the-box with different AI clients:
* **Claude Code:** Project commands and slash commands (`/commit`, `/pr`, etc.).
* **Antigravity:** Planning Mode constraints (`task.md`, `walkthrough.md`) and local Knowledge Items system.
* **Cursor & Windsurf:** Custom styling, glassmorphism, and frameworks instructions.
* **GitHub Copilot:** Project dependency declarations.

---

## 🚀 Quick Start
To get up and running:
1. Initialize AIM in your project:
   ```bash
   aim init
   ```
2. Open the Web Dashboard:
   ```bash
   aim browser
   ```
3. Compile instructions for all AI tools:
   ```bash
   aim sync
   ```
